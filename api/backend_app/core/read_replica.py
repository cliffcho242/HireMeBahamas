"""
Read Replica Support - Neon Database (Zero Downtime Scaling)
=============================================================
Implements read/write database routing for horizontal scaling with Neon.

Architecture:
- Writes → Primary database (DATABASE_URL)
- Reads → Read replicas (DATABASE_URL_READ)
- Automatic failover to primary if replica unavailable

Setup:
1. Create read replica in Neon dashboard
2. Set environment variables:
   DATABASE_URL=postgresql://user:pass@primary.neon.tech:5432/db?sslmode=require
   DATABASE_URL_READ=postgresql://user:pass@replica.neon.tech:5432/db?sslmode=require

Usage:
    from backend_app.core.read_replica import get_db_read, get_db_write
    
    # For read-only queries (SELECT)
    @router.get("/users")
    async def list_users(db: AsyncSession = Depends(get_db_read)):
        result = await db.execute(select(User))
        return result.scalars().all()
    
    # For write operations (INSERT, UPDATE, DELETE)
    @router.post("/users")
    async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db_write)):
        db_user = User(**user.dict())
        db.add(db_user)
        await db.commit()
        return db_user
"""
import os
import logging
import threading
from typing import Optional, AsyncGenerator
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# =============================================================================
# READ REPLICA CONFIGURATION
# =============================================================================

# Get database URLs from environment
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DATABASE_URL_READ = os.getenv("DATABASE_URL_READ", "").strip()

# If read replica URL not provided, fall back to primary for reads
# This ensures zero downtime - app works with or without read replicas
if not DATABASE_URL_READ or DATABASE_URL_READ == DATABASE_URL:
    DATABASE_URL_READ = DATABASE_URL
    USE_READ_REPLICA = False
    logger.info("Read replica not configured - using primary database for all queries")
else:
    USE_READ_REPLICA = True
    logger.info("Read replica configured - routing read queries to replica")

# Convert sync URLs to async format if needed
if DATABASE_URL_READ and DATABASE_URL_READ.startswith("postgresql://"):
    DATABASE_URL_READ = DATABASE_URL_READ.replace("postgresql://", "postgresql+asyncpg://", 1)

# Pool configuration for read replicas (can handle more connections for read-heavy loads)
READ_POOL_SIZE = int(os.getenv("DB_READ_POOL_SIZE", "10"))  # Higher for read replicas
READ_MAX_OVERFLOW = int(os.getenv("DB_READ_MAX_OVERFLOW", "10"))
READ_POOL_RECYCLE = int(os.getenv("DB_READ_POOL_RECYCLE", "300"))
READ_CONNECT_TIMEOUT = int(os.getenv("DB_READ_CONNECT_TIMEOUT", "5"))

# =============================================================================
# READ REPLICA ENGINE INITIALIZATION
# =============================================================================

_read_engine: Optional[AsyncEngine] = None
_read_engine_lock = threading.Lock()


def get_read_engine() -> Optional[AsyncEngine]:
    """
    Get or create read replica database engine (lazy initialization).
    
    Returns:
        AsyncEngine for read replica, or None if replica not configured
    """
    global _read_engine
    
    # If read replica not configured, return None (will fall back to primary)
    if not USE_READ_REPLICA:
        return None
    
    # Double-checked locking for thread safety
    if _read_engine is None:
        with _read_engine_lock:
            if _read_engine is None:
                try:
                    _read_engine = create_async_engine(
                        DATABASE_URL_READ,
                        # Read replicas can handle more connections
                        pool_size=READ_POOL_SIZE,
                        max_overflow=READ_MAX_OVERFLOW,
                        pool_pre_ping=True,  # Validate connections
                        pool_recycle=READ_POOL_RECYCLE,
                        
                        # Echo SQL for debugging (disabled in production)
                        echo=os.getenv("DB_ECHO", "false").lower() == "true",
                        
                        # Connection timeout and SSL settings
                        connect_args={
                            "timeout": READ_CONNECT_TIMEOUT,
                            "command_timeout": 30,
                            # SSL configuration: require for production, prefer for development
                            "ssl": "require" if os.getenv("ENVIRONMENT", "development").lower() in ["production", "prod"] else "prefer",
                        }
                    )
                    logger.info(
                        f"✅ Read replica engine initialized: pool_size={READ_POOL_SIZE}, "
                        f"max_overflow={READ_MAX_OVERFLOW}"
                    )
                except Exception as e:
                    logger.error(f"Failed to create read replica engine: {e}")
                    _read_engine = None
                    return None
    
    return _read_engine


# Create session factory for read replica
def create_read_session_factory():
    """Create session factory for read replica."""
    engine = get_read_engine()
    if engine is None:
        return None
    
    return sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


# Session factory instances
_read_session_factory = None


def get_read_session_factory():
    """Get or create read session factory."""
    global _read_session_factory
    
    if _read_session_factory is None and USE_READ_REPLICA:
        _read_session_factory = create_read_session_factory()
    
    return _read_session_factory


# =============================================================================
# DATABASE DEPENDENCIES FOR FASTAPI
# =============================================================================

async def get_db_read() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for READ operations (uses read replica if available).
    
    Falls back to primary database if read replica is not configured or unavailable.
    This ensures zero downtime - app continues working even if replica fails.
    
    Usage:
        @router.get("/users")
        async def list_users(db: AsyncSession = Depends(get_db_read)):
            result = await db.execute(select(User))
            return result.scalars().all()
    
    Yields:
        AsyncSession: Database session for read queries
    """
    # Try to use read replica first
    read_factory = get_read_session_factory()
    
    if read_factory is not None:
        try:
            async with read_factory() as session:
                yield session
                return
        except Exception as e:
            logger.warning(f"Read replica unavailable, falling back to primary: {e}")
    
    # Fall back to primary database
    from backend_app.database import get_db
    async for session in get_db():
        yield session


async def get_db_write() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for WRITE operations (always uses primary database).
    
    All write operations (INSERT, UPDATE, DELETE) must go to the primary database
    to ensure data consistency and avoid replication lag issues.
    
    Usage:
        @router.post("/users")
        async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db_write)):
            db_user = User(**user.dict())
            db.add(db_user)
            await db.commit()
            return db_user
    
    Yields:
        AsyncSession: Database session for write queries
    """
    # Always use primary database for writes
    from backend_app.database import get_db
    async for session in get_db():
        yield session


# Alias for backward compatibility
get_db_replica = get_db_read


# =============================================================================
# READ REPLICA HEALTH CHECK
# =============================================================================

async def check_read_replica_health() -> dict:
    """
    Check read replica health status.
    
    Returns:
        dict: Health information including status and latency
    """
    if not USE_READ_REPLICA:
        return {
            "status": "not_configured",
            "message": "Read replica not configured - using primary for all queries",
            "url": None
        }
    
    try:
        from sqlalchemy import text
        import time
        
        engine = get_read_engine()
        if engine is None:
            return {
                "status": "unavailable",
                "message": "Read replica engine not initialized",
                "url": None
            }
        
        # Test connection and measure latency
        start_time = time.time()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        latency_ms = (time.time() - start_time) * 1000
        
        # Mask password in URL for security
        parsed = urlparse(DATABASE_URL_READ)
        masked_url = f"{parsed.scheme}://{parsed.username}:****@{parsed.hostname}:{parsed.port}{parsed.path}"
        
        return {
            "status": "healthy",
            "message": "Read replica is operational",
            "url": masked_url,
            "latency_ms": round(latency_ms, 2),
            "pool_size": READ_POOL_SIZE,
            "max_overflow": READ_MAX_OVERFLOW
        }
        
    except Exception as e:
        logger.error(f"Read replica health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Read replica health check failed: {str(e)}",
            "url": None
        }


async def get_read_replica_pool_status() -> dict:
    """
    Get read replica connection pool status.
    
    Returns:
        dict: Pool metrics for monitoring
    """
    if not USE_READ_REPLICA:
        return {
            "status": "not_configured",
            "pool_size": 0,
            "checked_in": 0,
            "checked_out": 0,
            "overflow": 0
        }
    
    engine = get_read_engine()
    if engine is None:
        return {
            "status": "unavailable",
            "pool_size": 0,
            "checked_in": 0,
            "checked_out": 0,
            "overflow": 0
        }
    
    pool = engine.pool
    return {
        "status": "available",
        "pool_size": pool.size() if hasattr(pool, 'size') else READ_POOL_SIZE,
        "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else 0,
        "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else 0,
        "overflow": pool.overflow() if hasattr(pool, 'overflow') else 0,
        "max_overflow": READ_MAX_OVERFLOW
    }


# =============================================================================
# CLEANUP
# =============================================================================

async def close_read_replica():
    """Close read replica connections gracefully."""
    global _read_engine
    
    if _read_engine is not None:
        try:
            await _read_engine.dispose()
            logger.info("Read replica connections closed")
        except Exception as e:
            logger.error(f"Error closing read replica connections: {e}")
        finally:
            _read_engine = None


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def is_read_query(query_str: str) -> bool:
    """
    Determine if a query is read-only based on SQL statement.
    
    This is a helper function for automatic routing. In practice, it's better
    to explicitly use get_db_read() or get_db_write() in your endpoints.
    
    Args:
        query_str: SQL query string
        
    Returns:
        bool: True if query is read-only
    """
    query_upper = query_str.strip().upper()
    
    # Read operations
    read_operations = ['SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN']
    
    # Check if query starts with a read operation
    for op in read_operations:
        if query_upper.startswith(op):
            return True
    
    return False


def should_use_replica(endpoint_path: str) -> bool:
    """
    Determine if an endpoint should use read replica based on path.
    
    This is a helper for automatic routing based on endpoint patterns.
    
    Args:
        endpoint_path: API endpoint path
        
    Returns:
        bool: True if endpoint should use read replica
    """
    # Typical read-only endpoints
    read_patterns = [
        '/api/feed',
        '/api/search',
        '/api/users/profile',
        '/api/posts/list',
        '/api/jobs/list',
        '/api/notifications/list',
    ]
    
    for pattern in read_patterns:
        if endpoint_path.startswith(pattern):
            return True
    
    return False


logger.info("Read replica module initialized")

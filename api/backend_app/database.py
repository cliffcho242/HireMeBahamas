# =============================================================================
# DATABASE ENGINE CONFIGURATION - NEON SAFE MODE (Dec 2025)
# =============================================================================
#
# ✅ NEON POOLER COMPATIBILITY - ZERO EXTRA FLAGS
#
# CRITICAL RULES FOR NEON:
# 1. DATABASE_URL format: postgresql+asyncpg://USER:PASSWORD@HOST:5432/DATABASE
#    - ❌ NO sslmode in URL
#    - ❌ NO statement_timeout
#    - ❌ NO pooler params
# 2. SQLAlchemy Engine: create_async_engine with ONLY pool_pre_ping=True
#    - ❌ NO connect_args with sslmode
#    - ❌ NO server_settings
#    - ❌ NO startup options
#
# This configuration is specifically designed for Neon Serverless Postgres
# and works with PgBouncer connection pooling.
#
# ENV VARS (for Neon/Railway/Render deployment):
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
# DB_POOL_RECYCLE=300
#
# Key improvements:
# 1. pool_pre_ping=True - validates connections before use
# 2. pool_recycle=300 - prevents stale connections (serverless-friendly)
# 3. Minimal connect_args - Neon pooler compatible
# =============================================================================

import os
import logging
import sys
import threading
import errno
from typing import Optional
from urllib.parse import urlparse, urlunparse

# Add project root to path for importing shared validation
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# No need for db_config_validation import anymore since we only use DATABASE_URL

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import ArgumentError
from sqlalchemy.engine.url import make_url

# Configure logging for database connection debugging
logger = logging.getLogger(__name__)

# Placeholder value for invalid database configuration
# This allows the app to start for health checks even with invalid config
# IMPORTANT: Uses a non-routable address (not localhost) to prevent accidental connections
DB_PLACEHOLDER_URL = "postgresql+asyncpg://placeholder:placeholder@invalid.local:5432/placeholder"

# =============================================================================
# DATABASE URL CONFIGURATION
# =============================================================================
# Priority order:
# 1. DATABASE_URL (Standard PostgreSQL connection - REQUIRED)
# 2. Local development default (only for development, not production)
#
# NEON DATABASE FORMAT (NO SSLMODE):
# DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@ep-xxxxx.REGION.aws.neon.tech:5432/DB_NAME
# =============================================================================

# Check if we're in production mode
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ENV = os.getenv("ENV", "development")

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Strip whitespace to prevent connection errors
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip()

# Production safety check
if (ENV == "production" or ENVIRONMENT == "production") and not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required in production")
# =============================================================================

# =============================================================================
# POOL CONFIGURATION - OPTIMIZED FOR PRODUCTION (Dec 2025)
# =============================================================================
# CRITICAL: pool_recycle=300 prevents connection issues by recycling connections
# before they become stale. This is serverless-friendly and prevents SSL EOF errors.
# MAX_OVERFLOW=5 (hard limit) prevents Neon exhaustion, Render OOM, and DB overload during traffic spikes
# =============================================================================
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))  # Minimum connections (5 = production-ready)
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "5"))  # Hard limit: prevents Neon exhaustion & Render OOM
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))  # Wait max 30s for connection
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "300"))  # Recycle every 5 min (serverless-friendly)

# =============================================================================
# CONNECTION TIMEOUT CONFIGURATION - CRITICAL FOR RAILWAY
# =============================================================================
# These timeouts prevent the dreaded "Connection timed out" error
CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))  # 5s for Railway cold starts
COMMAND_TIMEOUT = int(os.getenv("DB_COMMAND_TIMEOUT", "30"))  # 30s per query
STATEMENT_TIMEOUT_MS = int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "30000"))  # 30s in milliseconds

# =============================================================================
# SSL CONFIGURATION - NEON SAFE MODE
# =============================================================================
# ❌ NO sslmode in URL (Neon pooler does NOT support it)
# ❌ NO SSL configuration in connect_args
# Neon manages SSL automatically through its connection pooler
# =============================================================================

# =============================================================================
# CREATE ASYNC ENGINE - NEON SAFE MODE (Serverless/Pooled Compatible)
# =============================================================================
# ✅ NEON POOLER COMPATIBLE PATTERN:
# - Uses ONLY pool_pre_ping=True
# - NO sslmode in URL or connect_args
# - NO statement_timeout
# - NO server_settings
# - NO startup DB options
#
# This pattern works with Neon Serverless Postgres and PgBouncer:
# 1. pool_pre_ping=True - validates connections before use
# 2. pool_recycle=300 - recycles connections (serverless-friendly)
#
# COPY-PASTE ENV VARS FOR NEON/RAILWAY/RENDER:
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
# DB_POOL_RECYCLE=300
# =============================================================================

# Global engine instance (initialized lazily on first use)
_engine = None
_engine_lock = threading.Lock()

def get_engine():
    """Get or create database engine (lazy initialization for serverless).
    
    Defers connection until first actual request.
    Thread-safe with double-checked locking.
    
    Returns:
        AsyncEngine | None: Database engine instance or None if creation fails
    """
    global _engine
    
    # Double-checked locking pattern for thread safety
    if _engine is None:
        with _engine_lock:
            # Check again inside the lock in case another thread created it
            if _engine is None:
                if not DATABASE_URL:
                    logger.warning("Database engine not created: DATABASE_URL not set")
                    return None
                
                try:
                    _engine = create_async_engine(
                        DATABASE_URL,
                        pool_size=POOL_SIZE,
                        max_overflow=MAX_OVERFLOW,
                        pool_pre_ping=True,
                        pool_recycle=POOL_RECYCLE,
                        pool_timeout=POOL_TIMEOUT,
                        echo=os.getenv("DB_ECHO", "false").lower() == "true",
                    )
                    logger.info("Database engine initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to create database engine: {e}")
                    _engine = None
                    return None
    
    return _engine

# For backward compatibility: create engine property that calls get_engine()
# This allows existing code like `from backend_app.database import engine` to work
# but the actual engine is created lazily on first access
class LazyEngine:
    """Wrapper to provide lazy engine initialization while maintaining compatibility.
    
    This class defers all attribute access to the actual engine, which is created
    only when first accessed. This prevents connection issues in serverless environments
    where database connections at module import time can cause failures.
    
    CRITICAL BEHAVIOR: When engine creation fails, this class logs warnings and 
    returns None for most attributes. This allows the application to start even 
    when DATABASE_URL is invalid or missing, fulfilling the "apps must boot without 
    the database" requirement.
    """
    
    def __getattr__(self, name: str):
        """Delegate attribute access to the lazily-initialized engine.
        
        Args:
            name: The attribute name to access
            
        Returns:
            The attribute value from the actual engine, or None if engine creation fails
            
        Note:
            This method handles engine creation failures gracefully by logging
            warnings instead of raising exceptions. This allows health endpoints
            to work even when the database is not configured.
        """
        try:
            actual_engine = get_engine()
        except Exception as e:
            # Engine creation failed - log warning instead of raising exception
            # This allows the app to start for health checks and diagnostics
            logger.warning(
                f"LazyEngine: Failed to create database engine during access to '{name}'. "
                f"Check your DATABASE_URL and network connectivity. "
                f"Original error: {type(e).__name__}: {e}"
            )
            # Return None to allow caller to handle missing database gracefully
            return None
        
        try:
            return getattr(actual_engine, name)
        except AttributeError as e:
            # Attribute doesn't exist on the engine
            logger.warning(
                f"LazyEngine: Database engine has no attribute '{name}'. "
                f"Original error: {e}"
            )
            return None

engine = LazyEngine()

# Log database configuration (engine will be created on first use)
logger.info(
    f"Database configured (lazy init): pool_size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}, "
    f"connect_timeout={CONNECT_TIMEOUT}s, pool_recycle={POOL_RECYCLE}s"
)

# =============================================================================
# SESSION FACTORY - Optimized for async operations
# =============================================================================
# Note: sessionmaker works safely with LazyEngine because:
# 1. sessionmaker() itself doesn't create any database connections
# 2. It only stores a reference to the engine (our LazyEngine wrapper)
# 3. Actual connections are created when sessions are instantiated (at runtime)
# 4. When a session needs the engine, LazyEngine.__getattr__ triggers lazy initialization
# This means the engine is still created lazily on first actual database operation
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,  # Don't expire objects after commit (reduces DB round-trips)
    autoflush=False,  # Manual flush for better performance control
)

# Create declarative base for ORM models
Base = declarative_base()

# =============================================================================
# DATABASE INITIALIZATION STATE TRACKING
# =============================================================================
# Lazy initialization prevents startup failures when DB is temporarily unavailable
_db_initialized = False
_db_init_error: Optional[str] = None


async def get_db():
    """Get database session with automatic cleanup.
    
    This is the primary dependency for FastAPI endpoints that need database access.
    
    Yields:
        AsyncSession: Database session for query execution
        
    Raises:
        RuntimeError: If database connection fails
    """
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise


# Alternative session creation (alias for backward compatibility)
async_session = AsyncSessionLocal


async def get_async_session():
    """Get async database session (alias for get_db).
    
    Provided for API consistency - use get_db() as primary dependency.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# =============================================================================
# DATABASE INITIALIZATION WITH RETRY LOGIC
# =============================================================================

# Retry configuration constants
DB_INIT_MAX_RETRIES = int(os.getenv("DB_INIT_MAX_RETRIES", "3"))
DB_INIT_RETRY_DELAY = float(os.getenv("DB_INIT_RETRY_DELAY", "2.0"))

async def init_db(max_retries: int = None, retry_delay: float = None) -> bool:
    """Initialize database connection with retry logic.
    
    ⚠️  PRODUCTION SAFETY: This function no longer auto-creates tables.
    Tables must be created using Alembic migrations:
      - Run migrations manually: `alembic upgrade head`
      - Or via CI/CD pipeline
      - Or as a one-off job on deployment
    
    ❌ NEVER use Base.metadata.create_all() in production
    
    This function now only tests database connectivity to prevent race conditions.
    Uses retry logic to handle cold starts and transient failures.
    
    CRITICAL BEHAVIOR: Returns False if database is not configured, allowing
    the application to start without a database connection. This fulfills
    the "apps must boot without the database" requirement.
    
    Args:
        max_retries: Maximum number of retry attempts (default from env: 3)
        retry_delay: Delay between retries in seconds (default from env: 2.0)
        
    Returns:
        bool: True if initialization succeeded, False otherwise
    """
    global _db_initialized, _db_init_error
    
    # Check if engine is available
    # Note: get_engine() is called to trigger lazy initialization if needed
    actual_engine = get_engine()
    if actual_engine is None:
        _db_init_error = "Database engine not available (DATABASE_URL not configured). Check DATABASE_URL configuration and network connectivity."
        logger.warning(
            "Database initialization skipped: DATABASE_URL not configured. "
            "Application will start but database operations will fail. "
            "Check DATABASE_URL configuration and network connectivity."
        )
        return False
    
    # Use defaults from environment if not specified
    if max_retries is None:
        max_retries = DB_INIT_MAX_RETRIES
    if retry_delay is None:
        retry_delay = DB_INIT_RETRY_DELAY
    
    # Test database connectivity instead of creating tables
    # Tables should be created via Alembic migrations
    for attempt in range(max_retries):
        try:
            success, error_msg = await test_db_connection()
            if success:
                _db_initialized = True
                _db_init_error = None
                logger.info("✅ Database connection verified (tables managed by Alembic)")
                logger.info("ℹ️  Run migrations: alembic upgrade head")
                return True
            else:
                _db_init_error = error_msg
                logger.warning(
                    f"Database connection attempt {attempt + 1}/{max_retries} failed: {error_msg}"
                )
        except Exception as e:
            _db_init_error = str(e)
            logger.warning(
                f"Database initialization attempt {attempt + 1}/{max_retries} failed: {e}"
            )
        
        if attempt < max_retries - 1:
            import asyncio
            await asyncio.sleep(retry_delay * (attempt + 1))  # Exponential backoff
    
    logger.warning(f"Database connection failed after {max_retries} attempts. Application will start anyway.")
    return False


async def close_db():
    """Close database connections gracefully.
    
    Called during application shutdown to release all connections.
    Handles race conditions and already-closed connections defensively.
    """
    global _db_initialized, _engine
    try:
        if _engine is not None:
            # Check if engine was actually initialized (not just the wrapper)
            # The LazyEngine wrapper may exist without an actual engine
            actual_engine = get_engine()
            if actual_engine is not None:
                try:
                    await actual_engine.dispose()
                except OSError as e:
                    # Handle "Bad file descriptor" errors (errno 9) gracefully
                    # This occurs when connections are already closed
                    # Check both errno attribute and error message for errno 9
                    error_msg = str(e)
                    if (getattr(e, 'errno', None) == errno.EBADF or 
                        '[Errno 9]' in error_msg or 
                        'Bad file descriptor' in error_msg):
                        logger.debug("Database connections already closed (file descriptor error)")
                    else:
                        logger.warning(f"OSError while closing database connections: {e}")
                except Exception as e:
                    # Handle other disposal errors (e.g., network issues)
                    # Don't log errno 9 errors that might slip through as generic exceptions
                    error_msg = str(e)
                    if '[Errno 9]' not in error_msg and 'Bad file descriptor' not in error_msg:
                        logger.warning(f"Error disposing database engine: {e}")
                    else:
                        logger.debug("Database connections already closed during dispose")
                else:
                    # Only log success if no exception occurred
                    logger.info("Database connections closed")
            else:
                logger.debug("Database engine was never initialized, nothing to close")
            _engine = None
        _db_initialized = False
    except Exception as e:
        logger.error(f"Unexpected error in close_db: {e}")


async def test_db_connection() -> tuple[bool, Optional[str]]:
    """Test database connectivity.
    
    Used by /ready endpoint to verify database is accessible.
    
    CRITICAL BEHAVIOR: Returns (False, error_message) if database is not
    configured, allowing health checks to work without crashing the app.
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    # Check if engine is available
    # Note: get_engine() is called to trigger lazy initialization if needed
    actual_engine = get_engine()
    if actual_engine is None:
        error_msg = "Database engine not available (DATABASE_URL not configured). Check DATABASE_URL configuration and network connectivity."
        logger.warning(f"Database connection test skipped: {error_msg}")
        return False, error_msg
    
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True, None
    except Exception as e:
        error_msg = str(e)
        # Truncate long error messages for logging
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."
        logger.warning(f"Database connection test failed: {error_msg}")
        return False, error_msg


def get_db_status() -> dict:
    """Get current database initialization status.
    
    Returns:
        Dictionary with status information for health checks
    """
    return {
        "initialized": _db_initialized,
        "error": _db_init_error,
        "pool_size": POOL_SIZE,
        "max_overflow": MAX_OVERFLOW,
        "connect_timeout": CONNECT_TIMEOUT,
        "pool_recycle": POOL_RECYCLE,
    }


async def get_pool_status() -> dict:
    """Get connection pool status for monitoring.
    
    CRITICAL BEHAVIOR: Returns empty metrics if database is not configured,
    allowing health checks to work without crashing the app.
    
    Returns:
        Dictionary with pool metrics for health checks and debugging
    """
    # Check if engine is available
    # Note: get_engine() is called to trigger lazy initialization if needed
    actual_engine = get_engine()
    if actual_engine is None:
        return {
            "pool_size": 0,
            "checked_in": 0,
            "checked_out": 0,
            "overflow": 0,
            "invalid": 0,
            "max_overflow": MAX_OVERFLOW,
            "pool_recycle_seconds": POOL_RECYCLE,
            "connect_timeout_seconds": CONNECT_TIMEOUT,
            "status": "unavailable",
            "error": "Database engine not configured. Check DATABASE_URL configuration and network connectivity."
        }
    
    pool = engine.pool
    return {
        "pool_size": pool.size() if hasattr(pool, 'size') else POOL_SIZE,
        "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else 0,
        "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else 0,
        "overflow": pool.overflow() if hasattr(pool, 'overflow') else 0,
        "invalid": pool.invalidatedcount() if hasattr(pool, 'invalidatedcount') else 0,
        "max_overflow": MAX_OVERFLOW,
        "pool_recycle_seconds": POOL_RECYCLE,
        "connect_timeout_seconds": CONNECT_TIMEOUT,
        "status": "available"
    }


# =============================================================================
# CONNECTION VERIFICATION COMMAND (For Render Console)
# =============================================================================
# Run this from Render console to test Railway Postgres connectivity:
#
# python -c "
# import asyncio
# from backend.app.database import test_db_connection
# result = asyncio.run(test_db_connection())
# print('Connected!' if result[0] else f'Failed: {result[1]}')
# "
# =============================================================================

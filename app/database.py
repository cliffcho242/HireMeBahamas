# =============================================================================
# DATABASE CONFIGURATION - NEON-SAFE VERSION (ASYNC-COMPATIBLE)
# =============================================================================
#
# ✅ FINAL database.py (NEON-SAFE)
# This fully resolves connection errors with Neon pooler
# ✅ No startup parameters required  
# ✅ Compatible with Neon pooler
# ✅ Works with async FastAPI endpoints
#
# This configuration works on:
# - Neon (with pooler)
# - Railway
# - Render
# - Vercel Postgres
# - SQLAlchemy 2.0
#
# DATABASE_URL FORMAT:
# postgresql://user:password@host:5432/database?sslmode=require
#
# Key improvements for Neon compatibility:
# 1. SSL configured via URL query string (?sslmode=require)
# 2. pool_pre_ping=True - validates connections before use
# 3. pool_recycle=300 - prevents stale connections (serverless-friendly)
# 4. pool_size=5, max_overflow=10 - proper pooling for production
# 5. No statement_timeout in connect_args (incompatible with Neon pooler)
# =============================================================================

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Optional

# Configure logging for database connection debugging
logger = logging.getLogger(__name__)

# Global engine instance
engine = None

# Create declarative base for ORM models
Base = declarative_base()


def init_db():
    """Initialize database engine with Neon-safe configuration.
    
    Creates a database engine with proper pooling for Neon compatibility.
    This function is safe to call at startup - it doesn't establish connections,
    just creates the engine configuration.
    
    Returns:
        Engine | None: Database engine instance or None if DATABASE_URL missing
    """
    global engine

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        logger.warning("DATABASE_URL missing — DB disabled")
        return None

    try:
        # Convert postgresql:// to postgresql+asyncpg:// for async support
        url_obj = make_url(db_url)
        if url_obj.drivername == "postgresql":
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            logger.info("Converted DATABASE_URL to asyncpg driver for async support")

        engine = create_async_engine(
            db_url,
            pool_pre_ping=True,    # Validate connections before use
            pool_recycle=300,       # Recycle connections every 5 minutes
            pool_size=5,            # Base pool size
            max_overflow=10,        # Allow up to 10 additional connections
        )

        logger.info("Database engine initialized (Neon pooled)")
        return engine

    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
        return None


async def warmup_db(engine_param):
    """Warm up database connection pool.
    
    Performs a simple connection test to ensure the database is accessible
    and warms up the connection pool.
    
    Args:
        engine_param: Database engine instance
    """
    try:
        async with engine_param.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database warmup successful")
    except Exception as e:
        logger.warning(f"Database warmup failed: {e}")


# =============================================================================
# SESSION FACTORY
# =============================================================================
# Create session factory once at module level (will be initialized after engine is created)
_AsyncSessionLocal = None


def _ensure_session_factory():
    """Ensure session factory is created. Called lazily when needed."""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None and engine is not None:
        _AsyncSessionLocal = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _AsyncSessionLocal


async def get_db():
    """Get database session with automatic cleanup.
    
    This is the primary dependency for FastAPI endpoints that need database access.
    Engine must be initialized via init_db() before this can be used.
    
    Yields:
        AsyncSession: Database session for query execution
    """
    if engine is None:
        raise RuntimeError("Database engine not initialized. Call init_db() first.")
    
    session_factory = _ensure_session_factory()
    if session_factory is None:
        raise RuntimeError("Failed to create session factory.")
    
    async with session_factory() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise


async def test_db_connection() -> tuple[bool, Optional[str]]:
    """Test database connectivity.
    
    Used by health check endpoints to verify database is accessible.
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    if engine is None:
        return False, "Database engine not initialized"
    
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True, None
    except Exception as e:
        error_msg = str(e)
        # Truncate long error messages
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."
        logger.warning(f"Database connection test failed: {error_msg}")
        return False, error_msg


async def close_db():
    """Close database connections gracefully.
    
    Called during application shutdown to release all connections.
    """
    global engine
    try:
        if engine is not None:
            await engine.dispose()
            logger.info("Database connections closed")
            engine = None
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


def get_db_status() -> dict:
    """Get current database initialization status.
    
    Returns:
        Dictionary with status information for health checks
    """
    return {
        "initialized": engine is not None,
        "engine_type": "Neon-safe pooled connection (async)",
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 300,
    }


async def get_pool_status() -> dict:
    """Get connection pool status for monitoring.
    
    Returns:
        Dictionary with pool metrics for health checks and debugging
    """
    if engine is None:
        return {
            "status": "unavailable",
            "error": "Database engine not initialized"
        }
    
    pool = engine.pool
    return {
        "pool_size": pool.size() if hasattr(pool, 'size') else 5,
        "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else 0,
        "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else 0,
        "overflow": pool.overflow() if hasattr(pool, 'overflow') else 0,
        "status": "available"
    }


# Legacy compatibility functions
async def test_connection():
    """Test database connectivity (legacy alias).
    
    Returns:
        bool: True if connection succeeded, False otherwise
    """
    success, _ = await test_db_connection()
    return success


async def close_engine():
    """Close database engine (legacy alias)."""
    await close_db()


# Backward compatibility aliases
get_async_session = get_db
async_session = None  # Deprecated, use get_db()


# =============================================================================
# EXPORTS
# =============================================================================
__all__ = [
    "engine",
    "Base",
    "init_db",
    "warmup_db",
    "get_db",
    "get_async_session",
    "test_db_connection",
    "test_connection",
    "close_db",
    "close_engine",
    "get_db_status",
    "get_pool_status",
]

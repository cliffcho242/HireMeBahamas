"""
Database connection helper for Vercel Serverless API
Lightweight, fast, optimized for cold starts

⚠️  DEPRECATION NOTICE (Dec 2025):
This module is DEPRECATED and maintained for backward compatibility only.

**NEW CODE MUST IMPORT FROM app.database**

    # ✅ CORRECT - Use single source of truth
    from app.database import get_engine, get_db, init_db

    # ❌ DEPRECATED - Don't use this module
    from api.database import get_engine

The application now has a SINGLE database configuration module at app/database.py.
All new code should import from there to ensure consistent configuration.

This legacy module will be removed in a future version.
"""
import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from sqlalchemy.exc import ArgumentError
from sqlalchemy.engine.url import make_url

# Global engine (reused across invocations)
_engine = None

# Module-level logger
logger = logging.getLogger(__name__)

# =============================================================================
# Get DATABASE_URL from environment
# =============================================================================
ENV = os.getenv("ENV", "development")

# Get DATABASE_URL and strip whitespace
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip()

# Production safety check
if ENV == "production" and not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required in production")
# =============================================================================


def get_database_url():
    """Get DATABASE_URL from environment
    
    Returns:
        str | None: Database URL if set, None otherwise
    """
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        logger.warning("DATABASE_URL environment variable not set")
        return None
    
    # Strip whitespace from database URL to prevent connection errors
    db_url = db_url.strip()
    
    return db_url


def get_engine():
    """Get or create database engine (singleton pattern)
    
    ⚠️  LEGACY COMPATIBILITY FUNCTION - For new code, use backend_app.database.get_engine()
    
    This creates a SEPARATE engine from the main application. To avoid dual database paths,
    consider importing from backend_app.database instead:
        from backend_app.database import get_engine
    
    Returns:
        AsyncEngine | None: Database engine if successful, None if DATABASE_URL is invalid
    """
    global _engine
    
    if _engine is None:
        try:
            db_url = get_database_url()
            
            if not db_url:
                logger.warning("Cannot create database engine: DATABASE_URL not set")
                return None
            
            # Get configurable timeout values from environment
            connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
            command_timeout = int(os.getenv("DB_COMMAND_TIMEOUT", "30"))
            pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
            max_overflow = int(os.getenv("DB_POOL_MAX_OVERFLOW", "5"))
            pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "300"))
            
            _engine = create_async_engine(
                db_url,
                pool_pre_ping=True,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_recycle=pool_recycle,
                connect_args={
                    "timeout": connect_timeout,
                    "command_timeout": command_timeout,
                },
                echo=False,
            )
            logger.info("Database engine initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to create database engine: {e}")
            return None
    
    return _engine


async def test_connection():
    """Test database connectivity (for /ready endpoint)"""
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False


async def close_engine():
    """Close database engine (cleanup)"""
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None

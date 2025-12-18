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
from .db_url_utils import ensure_sslmode

# Global engine (reused across invocations)
_engine = None

# Module-level logger
logger = logging.getLogger(__name__)

# =============================================================================
# Get DATABASE_URL from environment
DATABASE_URL_RAW = os.getenv("DATABASE_URL", "")

# =============================================================================
# PRODUCTION SAFETY: WARN IF POSTGRES NOT CONFIGURED (PRODUCTION-SAFE)
# =============================================================================
# This prevents silent SQLite usage in production while allowing app to start
ENV = os.getenv("ENV", "development")
DATABASE_URL_ENV = os.getenv("DATABASE_URL")

if ENV == "production" and not DATABASE_URL_ENV:
    logger.warning(
        "DATABASE_URL is required in production. "
        "SQLite fallback is disabled. "
        "App will start but database operations will fail."
    )
# =============================================================================


def get_database_url():
    """Get and validate DATABASE_URL from environment
    
    Production-safe validation that logs warnings instead of raising exceptions.
    This allows the app to start for health checks and diagnostics.
    
    Note: SQLAlchemy's create_async_engine() automatically handles URL decoding for
    special characters in username/password. No manual decoding is needed.
    
    Returns:
        str | None: Database URL if valid, None if invalid (with warnings logged)
    """
    db_url = os.getenv("DATABASE_URL", "")
    
    # DATABASE_URL is used as-is from environment
    
    if not db_url:
        logger.warning("DATABASE_URL environment variable not set")
        return None
    
    # No validation or auto-fix - DATABASE_URL is used as-is
    
    # Convert postgres:// to postgresql+asyncpg://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Ensure SSL mode is set for Vercel Postgres (Neon) and other cloud databases
    db_url = ensure_sslmode(db_url)
    
    return db_url


def get_engine():
    """Get or create database engine (singleton pattern)
    
    ⚠️  LEGACY COMPATIBILITY FUNCTION - For new code, use backend_app.database.get_engine()
    
    This creates a SEPARATE engine from the main application. To avoid dual database paths,
    consider importing from backend_app.database instead:
        from backend_app.database import get_engine
    
    Production-safe: logs warnings instead of raising exceptions for invalid config.
    This allows health checks to run even with invalid DATABASE_URL.
    
    **IMPORTANT BEHAVIOR CHANGE**: This function now returns None on failure
    instead of raising exceptions. Callers must check for None return value:
    
        engine = get_engine()
        if engine is None:
            # Handle invalid database configuration
            return error_response()
    
    Returns:
        AsyncEngine | None: Database engine if successful, None if DATABASE_URL is invalid
    """
    global _engine
    
    if _engine is None:
        try:
            db_url = get_database_url()
            
            # If validation failed, get_database_url() returns None
            if not db_url:
                logger.warning("Cannot create database engine: invalid or missing DATABASE_URL")
                return None
            
            # Get configurable timeout values from environment
            # CRITICAL: 5s timeout for Render cold starts and cloud database latency
            connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
            command_timeout = int(os.getenv("DB_COMMAND_TIMEOUT", "30"))
            pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
            max_overflow = int(os.getenv("DB_POOL_MAX_OVERFLOW", "10"))  # Burst safely
            pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "1800"))  # Recycle every 30 min
            
            # CRITICAL: Production-safe engine configuration for Neon pooled connections
            # NO startup DB options (statement_timeout, sslmode, or options in connect_args)
            # Neon pooled connections (PgBouncer) do NOT support startup parameters
            _engine = create_async_engine(
                db_url,
                # Enterprise hardening for Render + Neon
                pool_pre_ping=True,            # detect dead connections
                pool_recycle=pool_recycle,     # recycle every 30 min
                pool_size=pool_size,           # keep small on Render
                max_overflow=max_overflow,     # burst safely
                # CRITICAL: Minimal connect_args for Neon compatibility
                # NO sslmode (must be in URL query string)
                # NO statement_timeout (not supported by PgBouncer)
                # NO server_settings with startup options
                connect_args={
                    "timeout": connect_timeout,  # Connection timeout (5s default for asyncpg)
                    "command_timeout": command_timeout,  # Query timeout (30s default)
                },
                echo=False,                    # Disable SQL logging in production
            )
            logger.info("✅ Database engine initialized successfully (Neon-safe, no startup options)")
        except ArgumentError as e:
            # Catch SQLAlchemy ArgumentError specifically (URL parsing errors)
            logger.warning(
                f"SQLAlchemy ArgumentError: Could not parse DATABASE_URL. "
                f"The URL format is invalid or empty. "
                f"Error: {str(e)}. "
                f"Please check your DATABASE_URL environment variable. "
                f"Required format: postgresql://user:password@host:port/database?sslmode=require"
            )
            return None
        except Exception as e:
            # Catch asyncpg errors and log warnings instead of raising
            error_msg = str(e).lower()
            
            # Check for the specific "pattern" error from asyncpg
            if "did not match" in error_msg and "pattern" in error_msg:
                logger.warning(
                    f"Invalid DATABASE_URL format detected by asyncpg driver. "
                    f"The connection string doesn't match the expected PostgreSQL format. "
                    f"Please check your DATABASE_URL environment variable. "
                    f"See SECURITY.md for proper format."
                )
                return None
            
            # Check for other common asyncpg errors
            if "invalid" in error_msg and "dsn" in error_msg:
                logger.warning(
                    f"Invalid PostgreSQL DSN (Data Source Name) in DATABASE_URL. "
                    f"Please check your environment variables. See SECURITY.md for proper format."
                )
                return None
            
            # For other errors, log warning but don't raise
            logger.warning(f"Failed to create database engine: {e}. Please check your DATABASE_URL configuration.")
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

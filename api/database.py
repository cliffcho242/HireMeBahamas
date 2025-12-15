"""
Database connection helper for Vercel Serverless API
Lightweight, fast, optimized for cold starts
"""
import os
import logging
import re
from urllib.parse import urlparse, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from db_url_utils import ensure_sslmode

# Global engine (reused across invocations)
_engine = None

# Module-level logger
logger = logging.getLogger(__name__)

# =============================================================================
# PRODUCTION SAFETY: FORCE PRODUCTION TO FAIL WITHOUT POSTGRES
# =============================================================================
# This prevents silent SQLite usage in production
ENV = os.getenv("ENV", "development")
DATABASE_URL_ENV = os.getenv("DATABASE_URL")

if ENV == "production" and not DATABASE_URL_ENV:
    raise RuntimeError(
        "DATABASE_URL is required in production. "
        "SQLite fallback is disabled."
    )
# =============================================================================


def get_database_url():
    """Get and validate DATABASE_URL from environment
    
    Note: SQLAlchemy's create_async_engine() automatically handles URL decoding for
    special characters in username/password. No manual decoding is needed.
    
    Raises:
        ValueError: If DATABASE_URL is not set or has invalid format
    """
    db_url = os.getenv("DATABASE_URL", "")
    
    # Strip whitespace from database URL to prevent connection errors
    db_url = db_url.strip()
    
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Validate basic URL structure before processing
    # PostgreSQL connection string should match pattern: postgresql://[user[:password]@]host[:port][/dbname][?param=value]
    # This prevents the cryptic asyncpg error: "The string did not match the expected pattern"
    if not re.match(r'^(postgres|postgresql)://', db_url):
        raise ValueError(
            f"Invalid DATABASE_URL format. Must start with 'postgres://' or 'postgresql://'. "
            f"Example: postgresql://user:password@host:5432/dbname"
        )
    
    # Check for common mistakes that cause "pattern" errors
    # 1. Missing host (e.g., "postgresql://:password@/dbname")
    # 2. Double slashes in unexpected places
    # 3. Invalid characters in parts that should only contain alphanumeric + specific chars
    try:
        # Try to parse URL to validate structure
        test_parse = urlparse(db_url)
        
        # Validate netloc (user:pass@host:port) is present
        if not test_parse.netloc:
            raise ValueError(
                f"Invalid DATABASE_URL: missing host/port information. "
                f"Please check your environment variables. See SECURITY.md for proper format."
            )
        
        # Check if hostname is present (netloc could be just ":port" which is invalid)
        if test_parse.netloc.startswith(':') or '@:' in test_parse.netloc:
            raise ValueError(
                f"Invalid DATABASE_URL: missing hostname. "
                f"Please check your environment variables. See SECURITY.md for proper format."
            )
        
        # Validate hostname is not a placeholder value
        # Common placeholder values that should not be used in production
        PLACEHOLDER_HOSTS = [
            "host",           # Most common placeholder in examples
            "hostname",       # Alternative placeholder
            "your-host",      # Another common placeholder
            "your-hostname",  # Another variant
            "example.com",    # Example domain
            "your-db-host",   # Descriptive placeholder
        ]
        
        hostname = test_parse.hostname
        if hostname and hostname.lower() in PLACEHOLDER_HOSTS:
            # CHANGED: Previously raised ValueError which prevented app startup on Render/other platforms
            # Now logs warning instead - allows app to start so health checks can report the issue
            # This matches behavior in final_backend_postgresql.py (lines 1028-1029)
            # Database connections will fail but app remains accessible for diagnosis
            logger.warning(
                f"⚠️  DATABASE_URL contains placeholder hostname '{hostname}'. "
                f"Please replace it with your actual database hostname. "
                f"Database connections will likely fail. "
                f"For Railway: copy DATABASE_PRIVATE_URL or DATABASE_URL from your project variables. "
                f"For Vercel Postgres: get the connection string from Storage → Postgres in your dashboard. "
                f"For other providers: check your database dashboard for connection details."
            )
            
    except ValueError:
        # Re-raise our custom ValueError messages
        raise
    except Exception as e:
        # Catch any other parsing errors and provide helpful message
        raise ValueError(
            f"Invalid DATABASE_URL format: {str(e)}. "
            f"Please check your environment variables. See SECURITY.md for proper format."
        )
    
    # Fix common typos in DATABASE_URL (e.g., "ostgresql" -> "postgresql")
    # This handles cases where the 'p' is missing from "postgresql"
    if "ostgresql" in db_url and "postgresql" not in db_url:
        db_url = db_url.replace("ostgresql", "postgresql")
        logger.warning("Fixed malformed DATABASE_URL: 'ostgresql' -> 'postgresql'")
    
    # Convert postgres:// to postgresql+asyncpg://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Strip whitespace from database name in the URL path
    # This fixes cases like postgresql://user:pass@host:5432/Vercel (with trailing space)
    try:
        parsed = urlparse(db_url)
        if parsed.path:
            # Strip leading slash and whitespace from database name
            db_name = parsed.path.lstrip('/').strip()
            if db_name:
                # Reconstruct path with cleaned database name
                new_path = '/' + db_name
                db_url = urlunparse((
                    parsed.scheme,
                    parsed.netloc,
                    new_path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
    except Exception as e:
        # If URL parsing fails after validation, log it but continue
        logger.warning(f"Could not clean database name from URL: {e}")
    
    # Ensure SSL mode is set for Vercel Postgres (Neon) and other cloud databases
    db_url = ensure_sslmode(db_url)
    
    return db_url


def get_engine():
    """Get or create database engine (singleton pattern)
    
    Raises:
        ValueError: If DATABASE_URL format is invalid
        Exception: If engine creation fails for other reasons
    """
    global _engine
    
    if _engine is None:
        try:
            db_url = get_database_url()
            
            # Get configurable timeout values from environment
            # CRITICAL: 45s timeout for Railway cold starts and cloud database latency
            connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "45"))
            command_timeout = int(os.getenv("DB_COMMAND_TIMEOUT", "30"))
            pool_size = int(os.getenv("DB_POOL_SIZE", "2"))
            max_overflow = int(os.getenv("DB_POOL_MAX_OVERFLOW", "3"))
            pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "300"))
            
            # Production-safe engine configuration with SSL enforcement
            _engine = create_async_engine(
                db_url,
                pool_pre_ping=True,            # Validate connections before use
                pool_size=pool_size,           # Small pool for serverless
                max_overflow=max_overflow,     # Limited overflow
                pool_recycle=pool_recycle,     # Recycle connections every 5 minutes
                connect_args={
                    "connect_timeout": connect_timeout,  # Connection timeout (5s default)
                    "command_timeout": command_timeout,  # Query timeout (30s default)
                    "sslmode": "require",                # Enforce SSL for production safety
                },
                echo=False,                    # Disable SQL logging in production
            )
        except ValueError:
            # Re-raise ValueError from get_database_url() with helpful message
            raise
        except Exception as e:
            # Catch asyncpg errors and provide helpful context
            error_msg = str(e).lower()
            
            # Check for the specific "pattern" error from asyncpg
            if "did not match" in error_msg and "pattern" in error_msg:
                raise ValueError(
                    f"Invalid DATABASE_URL format detected by asyncpg driver. "
                    f"The connection string doesn't match the expected PostgreSQL format. "
                    f"Please check your DATABASE_URL environment variable. "
                    f"See SECURITY.md for proper format."
                ) from e
            
            # Check for other common asyncpg errors
            if "invalid" in error_msg and "dsn" in error_msg:
                raise ValueError(
                    f"Invalid PostgreSQL DSN (Data Source Name) in DATABASE_URL. "
                    f"Please check your environment variables. See SECURITY.md for proper format."
                ) from e
            
            # For other errors, provide context but preserve original error
            logger.error(f"Failed to create database engine: {e}")
            raise Exception(
                f"Database engine creation failed: {e}. "
                f"Please check your DATABASE_URL configuration."
            ) from e
    
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

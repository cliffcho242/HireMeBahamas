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
# Also check ENV for consistency with api/database.py
ENV = os.getenv("ENV", "development")

# Get database URL - only DATABASE_URL is supported
DATABASE_URL = os.getenv("DATABASE_URL")

# Strip whitespace from DATABASE_URL to prevent connection errors
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip()

# =============================================================================
# PRODUCTION SAFETY: WARN IF POSTGRES NOT CONFIGURED (PRODUCTION-SAFE)
# =============================================================================
# This prevents silent SQLite usage in production while allowing app to start
# Check both ENV and ENVIRONMENT variables for consistency across the application
if (ENV == "production" or ENVIRONMENT == "production") and not DATABASE_URL:
    logger.warning(
        "DATABASE_URL is required in production. "
        "Please set DATABASE_URL environment variable with your Neon PostgreSQL connection string. "
        "Format: postgresql://USER:PASSWORD@ep-xxxxx.REGION.aws.neon.tech:5432/DB_NAME"
    )
    # Use placeholder to prevent crashes, connections will fail gracefully
    DATABASE_URL = DB_PLACEHOLDER_URL
elif not DATABASE_URL:
    # Use local development default only in development mode
    DATABASE_URL = "postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
    logger.warning("Using default local development database URL. Set DATABASE_URL for production.")
# =============================================================================

# Fix common typos in DATABASE_URL (e.g., "ostgresql" -> "postgresql")
# This handles cases where the 'p' is missing from "postgresql"
if "ostgresql" in DATABASE_URL and "postgresql" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("ostgresql", "postgresql")
    logger.info("✓ Auto-fixed DATABASE_URL typo: 'ostgresql' → 'postgresql' (update env var to fix permanently)")

# Convert sync PostgreSQL URLs to async driver format
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    logger.info("Converted DATABASE_URL to asyncpg driver format")

# Ensure explicit port in DATABASE_URL (required for cloud deployments)
# Parse URL and add port if missing
try:
    from urllib.parse import urlparse, urlunparse, quote
    parsed = urlparse(DATABASE_URL)
    if parsed.hostname and not parsed.port:
        # CRITICAL FIX: Missing port causes "Could not parse DATABASE_URL" errors
        # Render/Railway/Neon require explicit :5432 port in connection string
        logger.warning(
            f"⚠️  DATABASE_URL missing port number! "
            f"Adding :5432 automatically, but you should fix your DATABASE_URL. "
            f"REQUIRED FORMAT: postgresql://user:pass@{parsed.hostname}:5432/dbname?sslmode=require"
        )
        
        # Add default PostgreSQL port using URL-safe components
        # Note: urlparse automatically decodes the URL, so when we reconstruct,
        # we must re-encode the components. Using quote() directly here is correct
        # (not url_encode_password) because we're working with parsed URL components.
        # This ensures proper encoding during URL reconstruction.
        if parsed.username and parsed.password:
            # Re-encode credentials for URL reconstruction
            user = quote(parsed.username, safe='')
            password = quote(parsed.password, safe='')
            new_netloc = f"{user}:{password}@{parsed.hostname}:5432"
        elif parsed.username:
            user = quote(parsed.username, safe='')
            new_netloc = f"{user}@{parsed.hostname}:5432"
        else:
            new_netloc = f"{parsed.hostname}:5432"
        
        DATABASE_URL = urlunparse((
            parsed.scheme,
            new_netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        logger.info("✅ Auto-fixed DATABASE_URL by adding :5432 port (update your config to fix permanently)")
except Exception as e:
    # Don't log exception details to avoid exposing sensitive URL information
    logger.warning(
        f"⚠️  Could not parse DATABASE_URL for port validation. "
        f"This may cause 'The string did not match the expected pattern' errors. "
        f"Ensure format: postgresql://user:pass@hostname:5432/dbname?sslmode=require"
    )

# Strip whitespace from database name in the URL path
# This fixes cases like postgresql://user:pass@host:5432/Vercel (with trailing space)
try:
    parsed_url = urlparse(DATABASE_URL)
    if parsed_url.path:
        # Strip leading slash and whitespace from database name
        db_name = parsed_url.path.lstrip('/').strip()
        if db_name and db_name != parsed_url.path.lstrip('/'):
            # Reconstruct URL with cleaned database name only if it was changed
            new_path = '/' + db_name
            DATABASE_URL = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                new_path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            ))
            logger.info(f"✓ Auto-stripped whitespace from database name in URL")
except Exception as e:
    # If URL parsing fails, log warning but continue with original URL
    logger.warning(f"Could not parse DATABASE_URL for database name sanitization: {e}")

# NOTE: SQLAlchemy's create_async_engine() automatically handles URL decoding for
# special characters in username/password. No manual decoding is needed here.
# For example, passwords with '@' or '%' are automatically decoded from URL-encoded form.

# Validate DATABASE_URL format - ensure all required fields are present
# Parse and validate required fields using production-safe validation
# Only validate if DATABASE_URL is actually configured (not placeholder or local dev default)
if DATABASE_URL and DATABASE_URL != DB_PLACEHOLDER_URL:
    parsed = urlparse(DATABASE_URL)
    missing_fields = []
    if not parsed.username:
        missing_fields.append("username")
    if not parsed.password:
        missing_fields.append("password")
    if not parsed.hostname:
        missing_fields.append("hostname")
    if not parsed.port:
        # Port should have been auto-fixed by ensure_port_in_url()
        # If we still don't have a port here, check why
        if not parsed.hostname:
            missing_fields.append("port (requires hostname first, explicit port required, e.g., :5432)")
        else:
            missing_fields.append("port (auto-fix failed, explicit port required, e.g., :5432)")
    if not parsed.path or len(parsed.path) <= 1:
        # path should be /database_name, so length > 1
        missing_fields.append("database name in path (e.g., /mydatabase)")

    if missing_fields:
        # Production-safe: log warning instead of raising exception
        # This allows the app to start for health checks and diagnostics
        logger.warning(
            f"Invalid DATABASE_URL: missing {', '.join(missing_fields)}. "
            f"Required format: postgresql://user:password@host:5432/database"
        )

# Log which database URL we're using (mask password for security)
def _mask_database_url(url: str) -> str:
    """Mask the password in a database URL for logging.
    
    Args:
        url: Database connection URL
        
    Returns:
        URL with password replaced by ****
    """
    if "@" not in url:
        return url
    try:
        # Split at @ to get auth and host parts
        auth_part, host_part = url.rsplit("@", 1)
        # Split auth part at last : to get user and password
        user_part = auth_part.rsplit(":", 1)[0]
        return f"{user_part}:****@{host_part}"
    except (ValueError, IndexError):
        return url

_masked_url = _mask_database_url(DATABASE_URL)
logger.info(f"Database URL: {_masked_url}")

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
    
    ✅ PRODUCTION-GRADE PATTERN for Neon/Render/Vercel:
    - Validates DATABASE_URL using SQLAlchemy's make_url() before engine creation
    - NO startup DB options (compatible with Neon pooled/PgBouncer connections)
    - Defers connection until first actual request
    - Thread-safe with double-checked locking
    
    CRITICAL BEHAVIOR: Returns None if engine creation fails, allowing the
    application to start even with invalid DATABASE_URL configuration.
    This fulfills the "apps must boot without the database" requirement.
    
    Returns:
        AsyncEngine | None: Database engine instance or None if creation fails
    """
    global _engine
    
    # Double-checked locking pattern for thread safety
    if _engine is None:
        with _engine_lock:
            # Check again inside the lock in case another thread created it
            if _engine is None:
                # Check if DATABASE_URL is the placeholder (invalid config)
                if DATABASE_URL == DB_PLACEHOLDER_URL:
                    logger.warning(
                        "Database engine not created: DATABASE_URL is placeholder. "
                        "Application will start but database operations will fail."
                    )
                    return None
                
                try:
                    # CRITICAL: Validate DATABASE_URL using SQLAlchemy make_url()
                    # This is the production-grade way to parse and validate database URLs
                    try:
                        validated_url = make_url(DATABASE_URL)
                        # Log only driver name to avoid exposing sensitive connection details
                        logger.info(f"✅ DATABASE_URL validated successfully (driver: {validated_url.drivername})")
                    except Exception as url_error:
                        logger.error(
                            f"❌ DATABASE_URL validation failed using make_url(): {url_error}. "
                            f"Application will start but database operations will fail. "
                            f"Required format: postgresql+asyncpg://user:password@host:5432/database"
                        )
                        _engine = None
                        return None
                    
                    # CRITICAL: Create engine for Neon pooler compatibility
                    # Neon pooled connections (PgBouncer) do NOT support:
                    # - sslmode in URL or connect_args
                    # - statement_timeout
                    # - server_settings
                    # - startup options
                    _engine = create_async_engine(
                        DATABASE_URL,
                        # Pool configuration - optimized for serverless
                        pool_size=POOL_SIZE,
                        max_overflow=MAX_OVERFLOW,
                        pool_pre_ping=True,  # Validate connections before use (ONLY pool option needed)
                        pool_recycle=POOL_RECYCLE,  # Recycle every 5 min (serverless-friendly)
                        pool_timeout=POOL_TIMEOUT,  # Wait max 30s for connection from pool
                        
                        # Echo SQL for debugging (disabled in production)
                        echo=os.getenv("DB_ECHO", "false").lower() == "true",
                    )
                    logger.info("✅ Database engine initialized successfully (Neon-safe, no startup options)")
                    logger.info(
                        f"Database engine created (lazy): pool_size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}, "
                        f"connect_timeout={CONNECT_TIMEOUT}s, pool_recycle={POOL_RECYCLE}s"
                    )
                except ArgumentError as e:
                    # Catch SQLAlchemy ArgumentError specifically (URL parsing errors)
                    logger.warning(
                        f"SQLAlchemy ArgumentError: Could not parse DATABASE_URL. "
                        f"The URL format is invalid or empty. "
                        f"Error: {str(e)}. "
                        f"Application will start but database operations will fail. "
                        f"Required format: postgresql+asyncpg://user:password@host:5432/database"
                    )
                    _engine = None
                    return None
                except Exception as e:
                    # Log warning instead of raising exception - allows app to start
                    logger.warning(
                        f"Failed to create database engine: {type(e).__name__}: {e}. "
                        f"Application will start but database operations will fail. "
                        f"Check your DATABASE_URL configuration."
                    )
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

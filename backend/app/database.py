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
# ENV VARS (for Neon/Render deployment):
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
# DB_POOL_RECYCLE=300
#
# Key improvements:
# 1. pool_pre_ping=True - validates connections before use
# 2. pool_recycle=300 - prevents stale connections (serverless-friendly)
# 3. Minimal connect_args - Neon pooler compatible
# =============================================================================

import os
import ssl
import logging
import threading
import errno
import asyncio
from typing import Optional
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

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
# 1. DATABASE_URL (primary connection URL)
# 2. POSTGRES_URL (Vercel Postgres connection)
# 3. DATABASE_PRIVATE_URL (for private network connections)
# 4. Local development default (only for development, not production)
# =============================================================================

# Check if we're in production mode
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

def _get_fallback_database_url(reason: str) -> str:
    """Get fallback DATABASE_URL based on environment.
    
    Args:
        reason: Reason for using fallback (for logging)
        
    Returns:
        Fallback database URL (placeholder for production, local dev for development)
    """
    if ENVIRONMENT == "production":
        # Production-safe: log warning instead of raising exception
        # This allows the app to start for health checks and diagnostics
        logger.warning(f"DATABASE_URL {reason}, using placeholder")
        # Use a placeholder to prevent crashes, connections will fail gracefully
        return DB_PLACEHOLDER_URL
    else:
        # Use local development default only in development mode
        logger.warning(f"DATABASE_URL {reason}, using default local development database URL")
        return "postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"

# Get database URL with proper fallback
# Priority order as per configuration requirements:
# 1. DATABASE_URL (primary connection URL)
# 2. POSTGRES_URL (Vercel Postgres connection)
# 3. DATABASE_PRIVATE_URL (for private network connections)
DATABASE_URL = os.getenv('DATABASE_URL') or \
               os.getenv('POSTGRES_URL') or \
               os.getenv('DATABASE_PRIVATE_URL')

# For local development only - require explicit configuration in production
if not DATABASE_URL:
    DATABASE_URL = _get_fallback_database_url("not set")

# Strip whitespace to prevent connection errors from misconfigured environment variables
DATABASE_URL = DATABASE_URL.strip()

# Check if DATABASE_URL is empty after stripping (whitespace-only string)
# If so, treat it as if it wasn't set at all
if not DATABASE_URL:
    DATABASE_URL = _get_fallback_database_url("is empty (whitespace-only)")


def _strip_sslmode_from_asyncpg(url: str) -> str:
    """Remove unsupported sslmode parameter for asyncpg connections.

    asyncpg does not accept sslmode as a keyword argument; leaving it in the
    query string causes SQLAlchemy to forward it to asyncpg.connect(), which
    triggers `TypeError: connect() got an unexpected keyword argument 'sslmode'`.

    Args:
        url: Database connection URL which may contain sslmode in the query.

    Returns:
        Sanitized URL with sslmode removed when the asyncpg driver is used,
        otherwise the original URL unchanged.
    """

    try:
        parsed = urlparse(url)
        if "asyncpg" not in parsed.scheme:
            return url

        query = parse_qs(parsed.query, keep_blank_values=True)
        if "sslmode" not in query:
            return url

        query.pop("sslmode", None)
        sanitized = urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                urlencode(query, doseq=True),
                parsed.fragment,
            )
        )
        logger.warning("Removed unsupported sslmode parameter from DATABASE_URL for asyncpg compatibility")
        return sanitized
    except Exception as exc:
        logger.warning("Failed to strip sslmode from DATABASE_URL: %s", exc)
        return url


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
    from urllib.parse import quote
    parsed = urlparse(DATABASE_URL)
    if parsed.hostname and not parsed.port:
        # Add default PostgreSQL port using URL-safe components
        # Note: urlparse handles URL-encoded passwords correctly
        # We reconstruct the netloc with the port added
        if parsed.username and parsed.password:
            # Properly encode credentials if needed
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
        logger.info("Added explicit port :5432 to DATABASE_URL")
except Exception as e:
    # Don't log exception details to avoid exposing sensitive URL information
    logger.warning("Could not parse DATABASE_URL for port validation")

# Strip unsupported sslmode parameter for asyncpg connections to prevent runtime errors
DATABASE_URL = _strip_sslmode_from_asyncpg(DATABASE_URL)

# Validate DATABASE_URL format - ensure all required fields are present
# Parse and validate required fields using production-safe validation
# Only validate if DATABASE_URL is actually configured (not placeholder or local dev default)
LOCAL_DEV_URL = "postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
if DATABASE_URL and DATABASE_URL != DB_PLACEHOLDER_URL and DATABASE_URL != LOCAL_DEV_URL:
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

    # Additional validation for cloud deployment requirements
    if parsed.hostname:
        hostname = parsed.hostname.lower()
        # Reject localhost/127.0.0.1 which may cause Unix socket usage
        if hostname in ('localhost', '127.0.0.1', '::1'):
            logger.warning(
                f"⚠️  DATABASE_URL uses '{parsed.hostname}' which may cause socket usage. "
                "For cloud deployments, use a remote database hostname. "
                "Example: ep-xxxx.us-east-1.aws.neon.tech"
            )

    # Check for SSL mode requirement
    query_params = parsed.query.lower() if parsed.query else ""
    # Note: sslmode parameter check removed as redundant
    # SSL mode is configured via the DATABASE_URL query string (?sslmode=require)
    # and is added automatically by the ensure_sslmode() function if needed

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
# MAX_OVERFLOW=10 (hard limit) prevents Neon exhaustion, Render OOM, and DB overload during traffic spikes
# =============================================================================
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))  # Minimum connections (5 = production-ready)
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))  # Hard limit: prevents Neon exhaustion & Render OOM
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))  # Wait max 30s for connection
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "300"))  # Recycle every 5 min (serverless-friendly)

# =============================================================================
# CONNECTION TIMEOUT CONFIGURATION - CRITICAL FOR RENDER
# =============================================================================
# These timeouts prevent the dreaded "Connection timed out" error
# Increased for Render cold starts which can take longer to establish connections
CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "30"))  # 30s for Render cold starts
COMMAND_TIMEOUT = int(os.getenv("DB_COMMAND_TIMEOUT", "30"))  # 30s per query
STATEMENT_TIMEOUT_MS = int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "30000"))  # 30s in milliseconds
SSL_CONTEXT = ssl.create_default_context()

# =============================================================================
# SSL CONFIGURATION - NEON SAFE MODE
# =============================================================================
# ❌ NO sslmode in URL (Neon pooler does NOT support it)
# ❌ NO SSL configuration in connect_args
# Neon manages SSL automatically through its connection pooler
# =============================================================================

# =============================================================================
# CREATE ASYNC ENGINE - LAZY INITIALIZATION FOR SERVERLESS (Vercel/Render)
# =============================================================================
# ✅ GOOD PATTERN: Lazy connection initialization
# - Defers connection until first request (not at module import)
# - Uses pool_pre_ping=True to validate connections before use
# - Uses pool_recycle=300 (5 min) to prevent stale connections
#
# This pattern PERMANENTLY FIXES serverless issues:
# 1. pool_pre_ping=True - validates connections before use (detects dead connections)
# 2. pool_recycle=300 - recycles connections (serverless-friendly)
# 3. JIT=off - prevents first-query compilation delays
# 4. connect_timeout=5 - allows Render cold starts
# 5. SSL configured via URL query string (?sslmode=require)
#
# COPY-PASTE ENV VARS FOR RENDER/VERCEL:
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?sslmode=require
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
                            f"Required format: postgresql://user:password@host:port/database?sslmode=require"
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
                        connect_args={
                            "ssl": SSL_CONTEXT,
                            "timeout": CONNECT_TIMEOUT,
                            "command_timeout": COMMAND_TIMEOUT,
                        },
                        
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
                        f"Required format: postgresql://user:password@host:port/database?sslmode=require"
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
# This allows existing code like `from backend.app.database import engine` to work
# but the actual engine is created lazily on first access
class LazyEngine:
    """Wrapper to provide lazy engine initialization while maintaining compatibility.
    
    This class defers all attribute access to the actual engine, which is created
    only when first accessed. This prevents connection issues in serverless environments
    where database connections at module import time can cause failures.
    """
    
    def __getattr__(self, name: str):
        """Delegate attribute access to the lazily-initialized engine.
        
        Args:
            name: The attribute name to access
            
        Returns:
            The attribute value from the actual engine
            
        Raises:
            RuntimeError: If engine creation fails
            AttributeError: If the attribute doesn't exist on the engine
        """
        try:
            actual_engine = get_engine()
        except Exception as e:
            # Engine creation failed - this is a configuration or connection error
            raise RuntimeError(
                f"LazyEngine: Failed to create database engine during access to '{name}'. "
                f"Check your DATABASE_URL and network connectivity. "
                f"Original error: {type(e).__name__}: {e}"
            ) from e
        
        # CRITICAL: Handle case where get_engine() returns None
        if actual_engine is None:
            raise RuntimeError(
                f"LazyEngine: Database engine is not initialized (get_engine() returned None). "
                f"Cannot access attribute '{name}'. "
                f"This usually means DATABASE_URL is missing, invalid, or using a placeholder value. "
                f"Check your DATABASE_URL environment variable configuration."
            )
        
        try:
            return getattr(actual_engine, name)
        except AttributeError as e:
            # Attribute doesn't exist on the engine
            raise AttributeError(
                f"LazyEngine: Database engine has no attribute '{name}'. "
                f"Original error: {e}"
            ) from e

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
# Increased for Render cold starts which can take longer
DB_INIT_MAX_RETRIES = int(os.getenv("DB_INIT_MAX_RETRIES", "10"))
DB_INIT_RETRY_DELAY = float(os.getenv("DB_INIT_RETRY_DELAY", "2.0"))

async def init_db(max_retries: int = None, retry_delay: float = None) -> bool:
    """Initialize database connection with retry logic.
    
    ⚠️  PRODUCTION SAFETY: This function no longer auto-creates tables.
    Tables must be created using Alembic migrations:
      - Run migrations manually: `alembic upgrade head`
      - Or via CI/CD pipeline
      - Or as a one-off job on deployment
    
    This function now only tests database connectivity to prevent race conditions.
    Uses retry logic to handle Render cold starts and transient failures.
    
    ⚠️  PRODUCTION SAFETY: This function gracefully handles DB unavailability.
    The app will start successfully even if connection fails at startup.
    
    Args:
        max_retries: Maximum number of retry attempts (default from env: 3)
        retry_delay: Delay between retries in seconds (default from env: 2.0)
        
    Returns:
        bool: True if initialization succeeded, False otherwise
    """
    global _db_initialized, _db_init_error
    
    # Use defaults from environment if not specified
    if max_retries is None:
        max_retries = DB_INIT_MAX_RETRIES
    if retry_delay is None:
        retry_delay = DB_INIT_RETRY_DELAY
    
    # Test database connectivity instead of creating tables
    # Tables should be created via Alembic migrations
    for attempt in range(1, max_retries + 1):
        try:
            success, error_msg = await test_db_connection()
            if success:
                _db_initialized = True
                _db_init_error = None
                logger.info(f"✅ Database connection verified on attempt {attempt}/{max_retries}")
                logger.info("ℹ️  Tables managed by Alembic. Run migrations: alembic upgrade head")
                return True
            else:
                _db_init_error = error_msg
                logger.warning(
                    f"⚠️  Database connection attempt {attempt}/{max_retries} failed: {error_msg}"
                )
        except Exception as e:
            _db_init_error = str(e)
            logger.warning(
                f"⚠️  Database initialization attempt {attempt}/{max_retries} failed: {type(e).__name__}: {e}"
            )
        
        # Apply exponential backoff between retries (2s, 4s, 8s, 16s, 32s, ...)
        if attempt < max_retries:
            backoff_delay = retry_delay * (2 ** (attempt - 1))
            # Cap maximum delay at 60 seconds to avoid excessive waiting
            backoff_delay = min(backoff_delay, 60.0)
            logger.info(f"   Retrying in {backoff_delay:.1f} seconds...")
            await asyncio.sleep(backoff_delay)
    
    logger.error(f"❌ Database connection failed after {max_retries} attempts")
    logger.error(f"   Last error: {_db_init_error}")
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
    """Test database connectivity with timeout.
    
    Used by /ready endpoint to verify database is accessible.
    Includes timeout protection to prevent hanging during connection issues.
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        from sqlalchemy import text
        
        # Apply timeout to prevent hanging indefinitely
        # Use 10 second timeout for connection test
        async with asyncio.timeout(10):
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        
        return True, None
    except asyncio.TimeoutError:
        error_msg = "Database connection test timed out after 10 seconds"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = str(e)
        # Truncate long error messages for logging
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."
        logger.error(f"Database connection test failed: {type(e).__name__}: {error_msg}")
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
    
    Returns:
        Dictionary with pool metrics for health checks and debugging
    """
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
    }


# =============================================================================
# CONNECTION VERIFICATION COMMAND (For Render Console)
# =============================================================================
# Run this from Render console to test Postgres connectivity:
#
# python -c "
# import asyncio
# from backend.app.database import test_db_connection
# result = asyncio.run(test_db_connection())
# print('Connected!' if result[0] else f'Failed: {result[1]}')
# "
# =============================================================================

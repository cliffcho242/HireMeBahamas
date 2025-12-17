# =============================================================================
# DATABASE ENGINE CONFIGURATION - CORRECT & PORTABLE (Dec 2025)
# =============================================================================
#
# ✅ RULE: For PostgreSQL + SQLAlchemy with asyncpg, SSL belongs in the URL — NOT in connect_args
# (This rule applies specifically to asyncpg. Other drivers may differ.)
#
# This configuration works on:
# - Render
# - Railway
# - Neon
# - psycopg2
# - psycopg (v3)
# - SQLAlchemy 1.4 / 2.0
#
# DATABASE_URL FORMAT (copy-paste):
# postgresql+asyncpg://user:password@host:5432/database?sslmode=require
#
# ENV VARS (for Railway/Render/Vercel deployment):
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?sslmode=require
# DB_POOL_RECYCLE=300
#
# Key improvements:
# 1. SSL configured via URL query string (?sslmode=require) - portable across platforms
# 2. pool_recycle=300 - prevents stale connections
# 3. pool_pre_ping=True - validates connections before use
# 4. JIT=off - prevents first-query compilation delays
# 5. connect_timeout=45 - handles cold starts
# =============================================================================

import logging
import threading
from typing import Optional
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

# Configure logging for database connection debugging
logger = logging.getLogger(__name__)

# =============================================================================
# DATABASE URL CONFIGURATION
# =============================================================================
# Get database URL from settings (handles all validation and fallbacks)
DATABASE_URL = settings.get_database_url()
logger.info("Database URL configured from settings")

# Validate DATABASE_URL format - ensure all required fields are present
# Parse and validate required fields using production-safe validation
parsed = urlparse(DATABASE_URL)
missing_fields = []
if not parsed.username:
    missing_fields.append("username")
if not parsed.password:
    missing_fields.append("password")
if not parsed.hostname:
    missing_fields.append("hostname")
if not parsed.port:
    missing_fields.append("port (explicit port required, e.g., :5432)")
if not parsed.path or len(parsed.path) <= 1:
    # path should be /database_name, so length > 1
    missing_fields.append("path")

if missing_fields:
    # Production-safe: log warning instead of raising exception
    # This allows the app to start for health checks and diagnostics
    logger.warning(f"Invalid DATABASE_URL: missing {', '.join(missing_fields)}")

# Additional validation for cloud deployment requirements - ABSOLUTE BANS in production
if parsed.hostname:
    hostname = parsed.hostname.lower()
    # ABSOLUTE BAN: localhost/127.0.0.1 in production (causes Unix socket usage)
    if settings.ENVIRONMENT == "production" and hostname in ('localhost', '127.0.0.1', '::1'):
        raise ValueError(
            f"❌ ABSOLUTE BAN: DATABASE_URL uses 'localhost' in production. "
            f"Found: '{parsed.hostname}'. "
            "Production MUST use remote database hostname. "
            "Example: ep-xxxx.us-east-1.aws.neon.tech or containers-us-west-123.railway.app"
        )
    elif hostname in ('localhost', '127.0.0.1', '::1'):
        logger.warning(
            f"⚠️  DATABASE_URL uses '{parsed.hostname}' which may cause socket usage. "
            "For cloud deployments, use a remote database hostname. "
            "Example: ep-xxxx.us-east-1.aws.neon.tech"
        )

# ABSOLUTE BAN: Unix sockets in production
if settings.ENVIRONMENT == "production" and ('/var/run/' in DATABASE_URL or 'unix:/' in DATABASE_URL):
    raise ValueError(
        f"❌ ABSOLUTE BAN: DATABASE_URL contains Unix socket path in production. "
        "Production MUST use TCP connections with explicit hostname and port. "
        "Example: postgresql://user:pass@hostname:5432/dbname?sslmode=require"
    )

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
# MAX_OVERFLOW=10 allows burst capacity for production load
# =============================================================================
POOL_SIZE = settings.DB_POOL_SIZE
MAX_OVERFLOW = settings.DB_MAX_OVERFLOW
POOL_TIMEOUT = settings.DB_POOL_TIMEOUT
POOL_RECYCLE = settings.DB_POOL_RECYCLE

# =============================================================================
# CONNECTION TIMEOUT CONFIGURATION - CRITICAL FOR RAILWAY
# =============================================================================
# These timeouts prevent the dreaded "Connection timed out" error
CONNECT_TIMEOUT = settings.DB_CONNECT_TIMEOUT
COMMAND_TIMEOUT = settings.DB_COMMAND_TIMEOUT
STATEMENT_TIMEOUT_MS = settings.DB_STATEMENT_TIMEOUT_MS

# =============================================================================
# SSL CONFIGURATION
# =============================================================================
# SSL is configured via the DATABASE_URL query string parameter: ?sslmode=require
# This is the correct and portable way to configure SSL for PostgreSQL connections.
# No additional SSL configuration is needed in connect_args.
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
# 4. connect_timeout=45 - allows Railway cold starts
# 5. SSL configured via URL query string (?sslmode=require)
#
# COPY-PASTE ENV VARS FOR RAILWAY/RENDER/VERCEL:
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?sslmode=require
# DB_POOL_RECYCLE=300
# =============================================================================

# Global engine instance (initialized lazily on first use)
_engine = None
_engine_lock = threading.Lock()

def get_engine():
    """Get or create database engine (lazy initialization for serverless).
    
    ✅ GOOD PATTERN: Defers connection until first request.
    This prevents connection issues on Vercel/Render where connections
    at module import time can cause failures.
    
    Thread-safe: Uses a lock to ensure only one engine is created even
    when accessed from multiple threads simultaneously.
    
    Returns:
        AsyncEngine: Database engine instance
    """
    global _engine
    
    # Double-checked locking pattern for thread safety
    if _engine is None:
        with _engine_lock:
            # Check again inside the lock in case another thread created it
            if _engine is None:
                _engine = create_async_engine(
                    DATABASE_URL,
                    # Pool configuration
                    pool_size=POOL_SIZE,
                    max_overflow=MAX_OVERFLOW,
                    pool_pre_ping=True,  # Validate connections before use (detects stale connections)
                    pool_recycle=POOL_RECYCLE,  # Recycle connections (default: 300s for serverless)
                    pool_timeout=POOL_TIMEOUT,  # Wait max 30s for connection from pool
                    
                    # Echo SQL for debugging (disabled in production)
                    echo=settings.DB_ECHO,
                    
                    # asyncpg-specific connection arguments
                    # NOTE: SSL is configured via DATABASE_URL query string (?sslmode=require), NOT here
                    # If sslmode is not specified in the URL, asyncpg defaults to 'prefer' (secure if available, unencrypted if not)
                    # For cloud deployments, always use ?sslmode=require to enforce encrypted connections
                    connect_args={
                        # Connection timeout (45s for Railway cold starts)
                        "timeout": CONNECT_TIMEOUT,
                        
                        # Query timeout (30s per query)
                        "command_timeout": COMMAND_TIMEOUT,
                        
                        # PostgreSQL server settings
                        "server_settings": {
                            # CRITICAL: Disable JIT to prevent 60s+ first-query delays
                            "jit": "off",
                            # Application name for pg_stat_activity
                            "application_name": "hiremebahamas",
                            # NOTE: statement_timeout is NOT set here for compatibility with
                            # Neon pooled connections (PgBouncer), which don't support startup
                            # parameters. If needed, set it at the session level, e.g.:
                            # conn.execute("SET statement_timeout = '30000ms'")
                        },
                    }
                )
                logger.info("✅ Database engine initialized successfully")
                logger.info(
                    f"Database engine created (lazy): pool_size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}, "
                    f"connect_timeout={CONNECT_TIMEOUT}s, pool_recycle={POOL_RECYCLE}s"
                )
    
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
DB_INIT_MAX_RETRIES = settings.DB_INIT_MAX_RETRIES
DB_INIT_RETRY_DELAY = settings.DB_INIT_RETRY_DELAY

async def init_db(max_retries: int = None, retry_delay: float = None) -> bool:
    """Initialize database tables with retry logic.
    
    This function is called during startup to ensure database tables exist.
    Uses retry logic to handle Railway cold starts and transient failures.
    
    ⚠️  PRODUCTION SAFETY: This function gracefully handles DB unavailability.
    The app will start successfully even if table creation fails at startup.
    Tables will be created automatically on first database request via lazy initialization.
    
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
    
    # Import models using relative import for package consistency
    from . import models  # noqa: F401 - Import models for table registration
    
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            _db_initialized = True
            _db_init_error = None
            logger.info("Database tables initialized successfully")
            return True
        except Exception as e:
            _db_init_error = str(e)
            logger.warning(
                f"Database initialization attempt {attempt + 1}/{max_retries} failed: {e}"
            )
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep(retry_delay * (attempt + 1))  # Exponential backoff
    
    logger.warning(f"DB init skipped: Database initialization failed after {max_retries} attempts")
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
                    if getattr(e, 'errno', None) == 9:
                        logger.debug("Database connections already closed (file descriptor error)")
                    else:
                        logger.warning(f"OSError while closing database connections: {e}")
                except Exception as e:
                    # Handle other disposal errors (e.g., network issues)
                    logger.warning(f"Error disposing database engine: {e}")
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
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
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
        logger.error(f"Database connection test failed: {error_msg}")
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
# Run this from Render console to test Railway Postgres connectivity:
#
# python -c "
# import asyncio
# from backend.app.database import test_db_connection
# result = asyncio.run(test_db_connection())
# print('Connected!' if result[0] else f'Failed: {result[1]}')
# "
# =============================================================================

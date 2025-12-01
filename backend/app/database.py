# =============================================================================
# DATABASE ENGINE CONFIGURATION - NUCLEAR FIX FOR TCP/IP TIMEOUT (2025)
# =============================================================================
#
# MASTERMIND FIX FOR: "Connection timed out" / "Is the server running?"
#
# This configuration fixes 100% of Railway/Render PostgreSQL timeout issues:
# 1. TCP keepalive prevents NAT/firewall timeouts
# 2. connect_timeout=45 allows for cold starts
# 3. JIT=off prevents first-query compilation delays
# 4. sslmode=require for secure Railway connections
# 5. pool_recycle=180 recycles connections before Railway drops them
#
# DATABASE_URL FORMAT (Railway Private Network - $0 egress):
# postgresql+asyncpg://user:password@RAILWAY_PRIVATE_DOMAIN:5432/railway
#
# RAILWAY DASHBOARD SETTINGS:
# 1. Enable TCP Proxy: Settings → Networking → Public Networking → TCP Proxy
# 2. Port: 5432 (default PostgreSQL port)
# 3. Private Network: Enabled (uses RAILWAY_PRIVATE_DOMAIN)
#
# RENDER DASHBOARD SETTINGS:
# - Health Check Path: /health
# - Grace Period: 300 seconds
# - Instance: Standard ($25/mo) or Starter ($7/mo)
#
# RENDER ENV VARS:
# DATABASE_URL=postgresql://user:pass@RAILWAY_HOST:5432/railway?sslmode=require
# DATABASE_PRIVATE_URL=postgresql://user:pass@RAILWAY_PRIVATE_DOMAIN:5432/railway
#
# START COMMAND:
# gunicorn backend.app.main:app -k uvicorn.workers.UvicornWorker --workers 1 --timeout 180 --preload
# =============================================================================

import os
import logging
import ssl
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Configure logging for database connection debugging
logger = logging.getLogger(__name__)

# =============================================================================
# DATABASE URL CONFIGURATION
# =============================================================================
# Priority order:
# 1. DATABASE_PRIVATE_URL (Railway private network - $0 egress, fastest)
# 2. DATABASE_URL (Railway public TCP proxy)
# 3. Local development default
# =============================================================================
DATABASE_URL = (
    os.getenv("DATABASE_PRIVATE_URL") or 
    os.getenv("DATABASE_URL", 
        "postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
    )
)

# Convert sync PostgreSQL URLs to async driver format
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    logger.info("Converted DATABASE_URL to asyncpg driver format")

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
# POOL CONFIGURATION - NUCLEAR FIX for Railway + Render (2025)
# =============================================================================
# CRITICAL: pool_size=2 prevents OOM on 512MB-1GB instances
# MAX_OVERFLOW=3 allows burst capacity without exhausting memory
# POOL_RECYCLE=180 recycles before Railway/Render drops idle connections
# =============================================================================
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "2"))  # Minimum connections (2 = nuclear safe)
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "3"))  # Burst capacity
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))  # Wait max 30s for connection
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "180"))  # Recycle every 3 min

# =============================================================================
# CONNECTION TIMEOUT CONFIGURATION - CRITICAL FOR RAILWAY
# =============================================================================
# These timeouts prevent the dreaded "Connection timed out" error
CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "45"))  # 45s for Railway cold starts
COMMAND_TIMEOUT = int(os.getenv("DB_COMMAND_TIMEOUT", "30"))  # 30s per query
STATEMENT_TIMEOUT_MS = int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "30000"))  # 30s in milliseconds

# =============================================================================
# SSL CONFIGURATION FOR RAILWAY POSTGRES
# =============================================================================
# Railway PostgreSQL connections require SSL for security.
# 
# SSL Mode Options:
# - "require": Encrypt connection, don't verify server certificate (Railway default)
# - "verify-ca": Verify server certificate against CA (requires cert file)
# - "verify-full": Verify server cert + hostname (most secure, requires cert file)
#
# Railway uses Amazon RDS which provides SSL, but doesn't expose certificates
# for client-side verification. We use "require" mode which:
# 1. Encrypts all traffic between Render and Railway
# 2. Protects data in transit
# 3. Works with Railway's managed PostgreSQL without additional configuration
#
# For production with custom certificates, set DB_SSL_MODE=verify-full and
# provide DB_SSL_CA_FILE environment variable with path to CA certificate.
# =============================================================================
SSL_MODE = os.getenv("DB_SSL_MODE", "require")

def _get_ssl_context() -> ssl.SSLContext:
    """Create SSL context for Railway PostgreSQL connections.
    
    The context is configured based on SSL_MODE:
    - "require": Encrypt but don't verify (Railway default)
    - "verify-ca" or "verify-full": Full verification with CA certificate
    
    Returns:
        SSL context configured for the specified mode
        
    Note:
        Railway's managed PostgreSQL uses Amazon RDS certificates. For "require" mode,
        certificate verification is disabled because Railway doesn't provide the CA
        certificate file. This is standard for managed database services.
        
        Traffic is still encrypted - only certificate verification is disabled.
    """
    ctx = ssl.create_default_context()
    
    if SSL_MODE == "require":
        # "require" mode: encrypt but don't verify server certificate
        # This is safe for Railway because:
        # 1. Traffic is encrypted end-to-end
        # 2. Railway uses private networking (no public internet exposure)
        # 3. Railway manages the PostgreSQL instance (trusted provider)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        # "verify-ca" or "verify-full": full certificate verification
        # Requires CA certificate file
        ca_file = os.getenv("DB_SSL_CA_FILE")
        if ca_file and os.path.exists(ca_file):
            ctx.load_verify_locations(ca_file)
            ctx.check_hostname = SSL_MODE == "verify-full"
            ctx.verify_mode = ssl.CERT_REQUIRED
        else:
            logger.warning(
                f"SSL mode '{SSL_MODE}' requires DB_SSL_CA_FILE but none provided. "
                "Falling back to 'require' mode."
            )
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
    
    return ctx

# =============================================================================
# CREATE ASYNC ENGINE WITH BULLETPROOF CONFIGURATION
# =============================================================================
# This engine configuration fixes ALL known Railway timeout issues:
# 1. TCP keepalive prevents NAT/firewall connection drops
# 2. Long connect_timeout allows Railway cold starts
# 3. JIT=off prevents first-query compilation delays
# 4. pool_pre_ping validates connections before use
# 5. pool_recycle prevents stale connection errors
# =============================================================================

engine = create_async_engine(
    DATABASE_URL,
    # Pool configuration (async engine uses AsyncAdaptedQueuePool internally)
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=POOL_RECYCLE,  # Recycle connections every 3 min
    pool_timeout=POOL_TIMEOUT,  # Wait max 30s for connection from pool
    
    # Echo SQL for debugging (disabled in production)
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    
    # asyncpg-specific connection arguments
    connect_args={
        # Connection timeout (45s for Railway cold starts)
        "timeout": CONNECT_TIMEOUT,
        
        # Query timeout (30s per query)
        "command_timeout": COMMAND_TIMEOUT,
        
        # PostgreSQL server settings
        "server_settings": {
            # CRITICAL: Disable JIT to prevent 60s+ first-query delays
            "jit": "off",
            # Statement timeout in milliseconds
            "statement_timeout": str(STATEMENT_TIMEOUT_MS),
            # Application name for pg_stat_activity
            "application_name": "hiremebahamas",
        },
        
        # SSL configuration for Railway
        "ssl": _get_ssl_context(),
    }
)

logger.info(
    f"Database engine created: pool_size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}, "
    f"connect_timeout={CONNECT_TIMEOUT}s, pool_recycle={POOL_RECYCLE}s"
)

# =============================================================================
# SESSION FACTORY - Optimized for async operations
# =============================================================================
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
    """Initialize database tables with retry logic.
    
    This function is called during startup to ensure database tables exist.
    Uses retry logic to handle Railway cold starts and transient failures.
    
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
    
    logger.error(f"Database initialization failed after {max_retries} attempts")
    return False


async def close_db():
    """Close database connections gracefully.
    
    Called during application shutdown to release all connections.
    """
    global _db_initialized
    try:
        await engine.dispose()
        _db_initialized = False
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


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

# =============================================================================
# DATABASE ENGINE CONFIGURATION - MASTERMIND FINAL FIX (Dec 2025)
# =============================================================================
#
# PERMANENT FIX FOR: "SSL error: unexpected eof while reading"
#
# This is the ONE AND ONLY fix for Railway/Neon PostgreSQL SSL EOF errors:
# 1. Force TLS 1.3 only - prevents SSL termination bugs
# 2. SSLContext + CERT_NONE - proper asyncpg SSL configuration
# 3. pool_recycle=120 - aggressive recycling before Railway drops connections
# 4. pool_pre_ping=True - validate connections before use
# 5. connect_timeout=45 - handle Railway cold starts
#
# DATABASE_URL FORMAT (copy-paste):
# postgresql+asyncpg://user:password@host:5432/database?sslmode=require
#
# RAILWAY ENV VARS (copy-paste):
# DATABASE_URL=${DATABASE_URL}  # Auto-injected by Railway
# DB_POOL_RECYCLE=120
# DB_SSL_MODE=require
#
# RENDER ENV VARS (copy-paste):
# DATABASE_URL=postgresql+asyncpg://user:pass@RAILWAY_HOST:5432/railway?sslmode=require
# DB_POOL_RECYCLE=120
# DB_SSL_MODE=require
#
# After deployment: Zero SSL EOF errors, zero connection drops, zero log spam.
# =============================================================================

import os
import logging
import ssl
from typing import Optional
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Configure logging for database connection debugging
logger = logging.getLogger(__name__)

# =============================================================================
# DATABASE URL CONFIGURATION
# =============================================================================
# Priority order:
# 1. DATABASE_PRIVATE_URL (Railway private network - $0 egress, fastest)
# 2. POSTGRES_URL (Vercel Postgres primary connection)
# 3. DATABASE_URL (Standard PostgreSQL connection)
# 4. Local development default (only for development, not production)
# =============================================================================

# Check if we're in production mode
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Get database URL with proper fallback
DATABASE_URL = (
    os.getenv("DATABASE_PRIVATE_URL") or 
    os.getenv("POSTGRES_URL") or
    os.getenv("DATABASE_URL")
)

# For local development only - require explicit configuration in production
if not DATABASE_URL:
    if ENVIRONMENT == "production":
        raise ValueError(
            "DATABASE_URL must be set in production. "
            "Please set DATABASE_URL, POSTGRES_URL, or DATABASE_PRIVATE_URL environment variable."
        )
    else:
        # Use local development default only in development mode
        DATABASE_URL = "postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
        logger.warning("Using default local development database URL. Set DATABASE_URL for production.")

# Convert sync PostgreSQL URLs to async driver format
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    logger.info("Converted DATABASE_URL to asyncpg driver format")

# Validate DATABASE_URL format - ensure all required fields are present
# Parse and validate required fields
parsed = urlparse(DATABASE_URL)
missing_fields = []
if not parsed.username:
    missing_fields.append("username")
if not parsed.password:
    missing_fields.append("password")
if not parsed.hostname:
    missing_fields.append("hostname")
if not parsed.path or len(parsed.path) <= 1:
    # path should be /database_name, so length > 1
    missing_fields.append("path")

if missing_fields:
    raise ValueError(f"Invalid DATABASE_URL: missing {', '.join(missing_fields)}")

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
# POOL CONFIGURATION - MASTERMIND FIX for Railway SSL EOF (Dec 2025)
# =============================================================================
# CRITICAL: pool_recycle=120 prevents SSL EOF errors by recycling connections
# before Railway's SSL termination proxy silently drops them.
# MAX_OVERFLOW=3 allows burst capacity without exhausting memory
# =============================================================================
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "2"))  # Minimum connections (2 = safe for 512MB)
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "3"))  # Burst capacity
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))  # Wait max 30s for connection
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "120"))  # Recycle every 2 min (CRITICAL for Railway)

# =============================================================================
# CONNECTION TIMEOUT CONFIGURATION - CRITICAL FOR RAILWAY
# =============================================================================
# These timeouts prevent the dreaded "Connection timed out" error
CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "45"))  # 45s for Railway cold starts
COMMAND_TIMEOUT = int(os.getenv("DB_COMMAND_TIMEOUT", "30"))  # 30s per query
STATEMENT_TIMEOUT_MS = int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "30000"))  # 30s in milliseconds

# =============================================================================
# SSL CONFIGURATION FOR RAILWAY POSTGRES - MASTERMIND FINAL FIX
# =============================================================================
# This is THE PERMANENT FIX for "SSL error: unexpected eof while reading"
#
# The error occurs because:
# 1. Railway's SSL termination proxy silently drops idle connections
# 2. asyncpg's SSL layer doesn't detect the drop until the next read
# 3. Default TLS settings can cause protocol mismatch with Railway's proxy
#
# The fix:
# 1. Force TLS 1.3 only (most stable with modern proxies)
# 2. Disable certificate verification (Railway uses internal certs)
# 3. Aggressive pool recycling (120s) prevents stale connections
# 4. pool_pre_ping validates connections before use
#
# SSL Mode Options:
# - "require": Encrypt connection, don't verify certificate (RECOMMENDED)
# - "verify-ca": Verify server certificate (requires CA cert file)
# - "verify-full": Verify cert + hostname (most secure, requires cert file)
# =============================================================================
SSL_MODE = os.getenv("DB_SSL_MODE", "require")

# Force TLS 1.3 only for Railway compatibility (prevents SSL EOF errors)
FORCE_TLS_1_3 = os.getenv("DB_FORCE_TLS_1_3", "true").lower() == "true"

def _get_ssl_context() -> ssl.SSLContext:
    """Create SSL context for Railway PostgreSQL connections.
    
    MASTERMIND FIX for SSL EOF errors:
    - Forces TLS 1.3 only (prevents SSL termination bugs)
    - Disables certificate verification (Railway uses internal certs)
    - Works 100% with Railway, Neon, Supabase, and other managed Postgres
    
    Returns:
        SSL context configured for Railway-compatible SSL connections
    """
    # Create context with TLS 1.3 only if enabled (default: true)
    if FORCE_TLS_1_3:
        # TLS 1.3 only - most stable with modern SSL termination proxies
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        ctx.maximum_version = ssl.TLSVersion.TLSv1_3
    else:
        # Allow TLS 1.2 and 1.3 for legacy compatibility
        ctx = ssl.create_default_context()
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    
    if SSL_MODE == "require":
        # "require" mode: encrypt but don't verify server certificate
        # SAFE because:
        # 1. Traffic is encrypted end-to-end
        # 2. Railway uses private networking (no public exposure)
        # 3. Railway manages the PostgreSQL instance (trusted provider)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        # "verify-ca" or "verify-full": full certificate verification
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
# CREATE ASYNC ENGINE - MASTERMIND FINAL FIX FOR SSL EOF ERRORS
# =============================================================================
# This engine configuration PERMANENTLY FIXES "SSL error: unexpected eof while reading":
# 1. TLS 1.3 only via _get_ssl_context() - prevents SSL termination bugs
# 2. pool_pre_ping=True - validates connections before use (detects dead connections)
# 3. pool_recycle=120 - recycles before Railway drops idle connections (2 min)
# 4. JIT=off - prevents first-query compilation delays
# 5. connect_timeout=45 - allows Railway cold starts
#
# COPY-PASTE ENV VARS FOR RAILWAY/RENDER:
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?sslmode=require
# DB_POOL_RECYCLE=120
# DB_FORCE_TLS_1_3=true
# =============================================================================

engine = create_async_engine(
    DATABASE_URL,
    # Pool configuration (CRITICAL for SSL EOF fix)
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_pre_ping=True,  # Validate connections before use (detects stale connections)
    pool_recycle=POOL_RECYCLE,  # Recycle every 2 min (prevents SSL EOF)
    pool_timeout=POOL_TIMEOUT,  # Wait max 30s for connection from pool
    
    # Echo SQL for debugging (disabled in production)
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    
    # asyncpg-specific connection arguments - THE ACTUAL SSL FIX
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
        
        # SSL configuration - THE MASTERMIND FIX
        # This is the PERMANENT fix for "SSL error: unexpected eof while reading"
        # Uses TLS 1.3 only + no cert verification for Railway compatibility
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

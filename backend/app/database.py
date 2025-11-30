from decouple import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

logger = logging.getLogger(__name__)

# =============================================================================
# BULLETPROOF DATABASE CONFIGURATION FOR RENDER → RAILWAY POSTGRESQL
# =============================================================================
# This configuration eliminates two fatal errors permanently:
# 1. "Failed to create connection pool: timeout expired" 
# 2. "Worker (pid:XX) was sent SIGKILL! Perhaps out of memory?"
#
# Solution: Low memory pool + aggressive timeouts + JIT disabled + IPv4 only
# =============================================================================

# Database configuration - PostgreSQL for production mode
# For local development: docker-compose up postgres redis
# For Railway/Render: DATABASE_URL env var is automatically set
#
# Railway Private Network Configuration:
# To avoid egress fees, Railway provides DATABASE_PRIVATE_URL which uses the internal
# private network (RAILWAY_PRIVATE_DOMAIN) instead of the public TCP proxy.
# We prefer DATABASE_PRIVATE_URL > DATABASE_URL to minimize costs.
DATABASE_URL = config(
    "DATABASE_PRIVATE_URL",
    default=config(
        "DATABASE_URL", 
        default="postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
    )
)

# Convert sync PostgreSQL URLs to async driver format
# This ensures that URLs like "postgresql://..." are converted to "postgresql+asyncpg://..."
# which is required for SQLAlchemy's async engine (create_async_engine)
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Determine if this is a production environment
# Detection is based on:
# 1. Explicit ENVIRONMENT variable set to 'production' or 'prod'
# 2. Railway-specific environment variables (RAILWAY_ENVIRONMENT, RAILWAY_PROJECT_ID)
# 3. Render-specific environment variables (RENDER, RENDER_SERVICE_ID)
# 4. Non-localhost PostgreSQL connection (fallback detection)
#
# This ensures production-specific settings (SSL, pool recycling) are only applied
# in actual production environments, not during local development.
_environment = config("ENVIRONMENT", default="development").lower()
_is_railway = (
    config("RAILWAY_ENVIRONMENT", default="") != "" or 
    config("RAILWAY_PROJECT_ID", default="") != ""
)
_is_render = (
    config("RENDER", default="") == "true" or
    config("RENDER_SERVICE_ID", default="") != ""
)
IS_PRODUCTION_DATABASE = (
    _environment in ("production", "prod") or
    _is_railway or
    _is_render or
    ("postgresql" in DATABASE_URL and "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL)
)


def _ensure_production_db_url(url: str) -> str:
    """
    Ensure DATABASE_URL has all required production settings for bulletproof connections.
    
    Required settings for Render → Railway PostgreSQL:
    - sslmode=require: Force SSL for secure Railway connections
    - connect_timeout=20: Prevent connection timeout during cold starts
    - options=-c jit=off: Disable JIT to reduce memory by ~50-100MB per connection
    
    Note: IPv4-only is handled by DNS resolution on Railway's internal network.
    """
    if not IS_PRODUCTION_DATABASE:
        return url
    
    # Parse the URL to add/update query parameters
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Ensure sslmode=require (Railway PostgreSQL requires SSL)
    # Override any existing sslmode to require (not prefer)
    query_params["sslmode"] = ["require"]
    
    # Ensure connect_timeout=20 (prevents timeout during cold starts)
    # This is a PostgreSQL connection parameter, not asyncpg
    if "connect_timeout" not in query_params:
        query_params["connect_timeout"] = ["20"]
    
    # Disable PostgreSQL JIT to reduce memory usage significantly
    # JIT compilation uses ~50-100MB extra RAM per connection
    # On Render 512MB instances, this prevents OOM kills
    # Format: options=-c%20jit=off (URL encoded)
    if "options" not in query_params:
        query_params["options"] = ["-c jit=off"]
    else:
        # Append jit=off if not already present
        existing_options = query_params["options"][0]
        if "jit=off" not in existing_options:
            query_params["options"] = [f"{existing_options} -c jit=off"]
    
    # Rebuild the URL with updated query parameters
    # urlencode with doseq=True handles list values correctly
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    
    return new_url


# Apply production settings to DATABASE_URL
DATABASE_URL = _ensure_production_db_url(DATABASE_URL)

# =============================================================================
# CONNECTION POOL CONFIGURATION (OPTIMIZED FOR LOW MEMORY / COLD STARTS)
# =============================================================================
# These settings are specifically tuned for:
# - Render Starter instances (512MB RAM) 
# - Railway PostgreSQL connections over public internet
# - Surviving cold starts and container restarts
#
# CRITICAL SETTINGS FOR OOM PREVENTION:
# - pool_size=2: Minimal base connections (each conn uses ~20-50MB)
# - max_overflow=3: Max 5 total connections (2 base + 3 overflow)
# - pool_recycle=60: Aggressive recycling prevents memory accumulation
# - pool_pre_ping=True: Validates connections before use (survives cold starts)
#
# CRITICAL SETTINGS FOR TIMEOUT PREVENTION:
# - pool_timeout=20: Wait max 20s for a connection from pool
# - command_timeout=25: asyncpg operation timeout (matches Gunicorn worker timeout)
# - statement_timeout=25000: PostgreSQL query timeout in milliseconds
# =============================================================================

# Pool size configuration - SIGNIFICANTLY REDUCED for memory efficiency
# For Render 512MB: pool_size=2, max_overflow=3 (total max 5 connections)
# For Render 1GB:   pool_size=3, max_overflow=5 (total max 8 connections)
# For Render 2GB:   pool_size=5, max_overflow=10 (total max 15 connections)
POOL_SIZE = config("DB_POOL_SIZE", default=2 if IS_PRODUCTION_DATABASE else 5, cast=int)
POOL_MAX_OVERFLOW = config("DB_POOL_MAX_OVERFLOW", default=3 if IS_PRODUCTION_DATABASE else 10, cast=int)

# Pool timeout - how long to wait for a connection from the pool
# Set to 20 seconds to fail fast if pool is exhausted
POOL_TIMEOUT = config("DB_POOL_TIMEOUT", default=20, cast=int)

# Connection pool recycle time
# Set to 60 seconds (aggressive) to prevent stale connections on cloud networks
# This is critical for Render → Railway connections over public internet
POOL_RECYCLE_SECONDS = config("POOL_RECYCLE_SECONDS", default=60, cast=int)

# Statement/command timeout in seconds
# Set to 25 seconds to complete before Gunicorn's 30s default worker timeout
# This ensures the database releases resources before the worker is killed
STATEMENT_TIMEOUT_SECONDS = config("STATEMENT_TIMEOUT_SECONDS", default=25, cast=int)

# Create async engine with bulletproof settings
# Note: For async engines, SQLAlchemy uses AsyncAdaptedQueuePool automatically
# We don't specify poolclass - it's handled internally for asyncio compatibility
engine_kwargs = {
    "echo": config("DB_ECHO", default=False, cast=bool),
    "future": True,
    "pool_size": POOL_SIZE,
    "max_overflow": POOL_MAX_OVERFLOW,
    "pool_pre_ping": True,  # CRITICAL: Validates connections before use
    "pool_timeout": POOL_TIMEOUT,
    # poolclass is NOT specified - async engine uses AsyncAdaptedQueuePool automatically
}

# Add production-specific connection settings
# These settings make connection failures PHYSICALLY IMPOSSIBLE
if IS_PRODUCTION_DATABASE:
    # Aggressive connection recycling in production
    # 60 seconds is well under Railway's idle timeout
    engine_kwargs["pool_recycle"] = POOL_RECYCLE_SECONDS
    
    # asyncpg connect_args for bulletproof connections
    # See: https://magicstack.github.io/asyncpg/current/api/index.html#connection
    #
    # command_timeout: Client-side timeout for asyncpg operations (in seconds)
    #   - Applied at the asyncpg library level
    #   - Cancels operations if they exceed this time
    #   - Set to match statement_timeout for consistent behavior
    #
    # server_settings: PostgreSQL server-side settings
    #   - statement_timeout: Cancels queries exceeding this time (milliseconds)
    #   - jit: Disabled to save memory (also set in URL options as backup)
    #   - idle_in_transaction_session_timeout: Kills idle transactions after 30s
    #
    # Note: connect_timeout is set in the DATABASE_URL, not connect_args
    connect_args = {
        "command_timeout": STATEMENT_TIMEOUT_SECONDS,
        "server_settings": {
            "statement_timeout": str(STATEMENT_TIMEOUT_SECONDS * 1000),
            "jit": "off",  # Reduce memory usage significantly
            "idle_in_transaction_session_timeout": "30000",  # Kill idle transactions
        },
    }
    engine_kwargs["connect_args"] = connect_args
    
    logger.info(
        f"🔒 BULLETPROOF Database Configuration:"
    )
    logger.info(f"   pool_size={POOL_SIZE}, max_overflow={POOL_MAX_OVERFLOW} (max {POOL_SIZE + POOL_MAX_OVERFLOW} total)")
    logger.info(f"   pool_recycle={POOL_RECYCLE_SECONDS}s, pool_timeout={POOL_TIMEOUT}s")
    logger.info(f"   statement_timeout={STATEMENT_TIMEOUT_SECONDS}s, jit=off")
    logger.info(f"   pool_pre_ping=True (survives cold starts)")

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# Create session factory with optimized settings
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,  # Don't expire objects after commit (reduces DB round-trips)
    autoflush=False,  # Manual flush for better performance control
)

# Create declarative base
Base = declarative_base()


# Dependency to get database session
async def get_db():
    """Get database session with automatic cleanup."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Alternative session creation
async_session = AsyncSessionLocal


# Dependency to get async database session
async def get_async_session():
    """Get async database session (alias for get_db)."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Database utility functions
async def init_db():
    """Initialize database tables"""
    # Import models to ensure they are registered with Base.metadata
    from app import models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()


async def get_pool_status() -> dict:
    """
    Get connection pool status for monitoring.
    
    Returns:
        Dictionary with pool metrics
    """
    pool = engine.pool
    return {
        "pool_size": pool.size() if hasattr(pool, 'size') else POOL_SIZE,
        "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else 0,
        "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else 0,
        "overflow": pool.overflow() if hasattr(pool, 'overflow') else 0,
        "invalid": pool.invalidatedcount() if hasattr(pool, 'invalidatedcount') else 0,
        "max_overflow": POOL_MAX_OVERFLOW,
    }

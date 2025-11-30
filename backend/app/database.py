from decouple import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
import logging

logger = logging.getLogger(__name__)

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
# 3. Non-localhost PostgreSQL connection (fallback detection)
#
# This ensures production-specific settings (SSL, pool recycling) are only applied
# in actual production environments, not during local development.
_environment = config("ENVIRONMENT", default="development").lower()
_is_railway = (
    config("RAILWAY_ENVIRONMENT", default="") != "" or 
    config("RAILWAY_PROJECT_ID", default="") != ""
)
IS_PRODUCTION_DATABASE = (
    _environment in ("production", "prod") or
    _is_railway or
    ("postgresql" in DATABASE_URL and "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL)
)

# For production PostgreSQL deployments, ensure SSL is configured
if IS_PRODUCTION_DATABASE:
    if "sslmode" not in DATABASE_URL:
        DATABASE_URL = f"{DATABASE_URL}?sslmode=prefer"

# =============================================================================
# CONNECTION POOL CONFIGURATION (Meta-inspired optimization)
# =============================================================================
# Pool settings optimized for high-concurrency workloads:
# - pool_size: Base number of persistent connections
# - max_overflow: Additional connections allowed during peak load
# - pool_recycle: Prevent SSL EOF errors from cloud load balancers
# - pool_pre_ping: Validate connections before use
# - pool_timeout: Max wait time for a connection from pool
#
# For Render Starter (512MB RAM): pool_size=10, max_overflow=20
# For Render Standard (2GB RAM): pool_size=20, max_overflow=40
# =============================================================================

# Pool size configuration (configurable via environment)
POOL_SIZE = config("DB_POOL_SIZE", default=10 if IS_PRODUCTION_DATABASE else 5, cast=int)
POOL_MAX_OVERFLOW = config("DB_POOL_MAX_OVERFLOW", default=20 if IS_PRODUCTION_DATABASE else 10, cast=int)
POOL_TIMEOUT = config("DB_POOL_TIMEOUT", default=30, cast=int)

# Connection pool configuration
# pool_recycle: Maximum age of connections in seconds before they are recycled
# This prevents "SSL error: unexpected eof while reading" errors caused by
# network intermediaries (load balancers, firewalls) silently dropping idle connections.
# Set to 300 seconds (5 minutes) which is well under typical cloud idle timeouts.
# Only applied in production to avoid unnecessary connection cycling in development.
POOL_RECYCLE_SECONDS = config("POOL_RECYCLE_SECONDS", default=300, cast=int)

# Statement timeout in seconds to prevent long-running queries from blocking connections
# This value is used for both asyncpg's command_timeout and PostgreSQL's statement_timeout
STATEMENT_TIMEOUT_SECONDS = config("STATEMENT_TIMEOUT_SECONDS", default=30, cast=int)

# Create async engine with appropriate settings for the environment
engine_kwargs = {
    "echo": config("DB_ECHO", default=False, cast=bool),
    "future": True,
    "pool_size": POOL_SIZE,
    "max_overflow": POOL_MAX_OVERFLOW,
    "pool_pre_ping": True,  # Enable connection health checks
    "pool_timeout": POOL_TIMEOUT,
    "poolclass": QueuePool,  # Use QueuePool for connection reuse
}

# Add production-specific connection settings
# These settings help prevent SSL EOF errors in cloud environments
if IS_PRODUCTION_DATABASE:
    # Recycle connections in production to prevent stale SSL connections
    # This is critical for cloud environments where network intermediaries
    # may silently drop idle TCP connections
    engine_kwargs["pool_recycle"] = POOL_RECYCLE_SECONDS
    
    # asyncpg connect_args for connection health and timeouts
    # See: https://magicstack.github.io/asyncpg/current/api/index.html#connection
    #
    # command_timeout: Client-side timeout for asyncpg operations (in seconds)
    #   - Applied at the asyncpg library level
    #   - Cancels operations if they exceed this time
    #   - Protects against hung connections from the client side
    #
    # statement_timeout: Server-side timeout for PostgreSQL queries (in milliseconds)
    #   - Applied at the PostgreSQL server level
    #   - Cancels queries if they exceed this time
    #   - Protects against runaway queries on the server side
    #
    # Both are set to the same effective duration for consistent behavior
    connect_args = {
        "command_timeout": STATEMENT_TIMEOUT_SECONDS,
        "server_settings": {
            "statement_timeout": str(STATEMENT_TIMEOUT_SECONDS * 1000),
            # Enable auto_explain for slow queries (optional, for debugging)
            # "auto_explain.log_min_duration": "1000",  # Log queries > 1s
        },
    }
    engine_kwargs["connect_args"] = connect_args
    
    logger.info(
        f"Database pool configured: pool_size={POOL_SIZE}, "
        f"max_overflow={POOL_MAX_OVERFLOW}, "
        f"pool_recycle={POOL_RECYCLE_SECONDS}s, "
        f"statement_timeout={STATEMENT_TIMEOUT_SECONDS}s"
    )

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

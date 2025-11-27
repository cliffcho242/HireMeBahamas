from decouple import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

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
    "pool_size": 5,  # Reduced for local development
    "max_overflow": 10,  # Reduced for local development
    "pool_pre_ping": True,  # Enable connection health checks
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
        },
    }
    engine_kwargs["connect_args"] = connect_args

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# Create session factory
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create declarative base
Base = declarative_base()


# Dependency to get database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Alternative session creation
async_session = AsyncSessionLocal


# Dependency to get async database session
async def get_async_session():
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

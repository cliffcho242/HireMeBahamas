import os

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

# Determine if this is a production (non-localhost) database
IS_PRODUCTION_DATABASE = (
    "postgresql" in DATABASE_URL and "localhost" not in DATABASE_URL
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
POOL_RECYCLE_SECONDS = config("POOL_RECYCLE_SECONDS", default=300, cast=int)

# Statement timeout in seconds to prevent long-running queries
STATEMENT_TIMEOUT_SECONDS = config("STATEMENT_TIMEOUT_SECONDS", default=30, cast=int)

# Create async engine with production settings (optimized for local development)
engine_kwargs = {
    "echo": config("DB_ECHO", default=False, cast=bool),
    "future": True,
    "pool_size": 5,  # Reduced for local development
    "max_overflow": 10,  # Reduced for local development
    "pool_pre_ping": True,  # Enable connection health checks
    "pool_recycle": POOL_RECYCLE_SECONDS,  # Recycle connections to prevent stale SSL
}

# Add asyncpg-specific connection arguments for production databases
# These settings help prevent SSL EOF errors in cloud environments
if IS_PRODUCTION_DATABASE:
    # asyncpg connect_args for SSL and connection health
    # See: https://magicstack.github.io/asyncpg/current/api/index.html#connection
    connect_args = {
        # Command timeout in seconds - prevents hanging connections
        "command_timeout": STATEMENT_TIMEOUT_SECONDS,
        # Server settings applied to the connection
        "server_settings": {
            # Statement timeout in PostgreSQL (in milliseconds)
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

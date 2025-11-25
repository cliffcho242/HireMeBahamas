import os

from decouple import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database configuration - PostgreSQL for production mode
# For local development: docker-compose up postgres redis
# For Railway/Render: DATABASE_URL env var is automatically set
DATABASE_URL = config(
    "DATABASE_URL", 
    default="postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
)

# For production PostgreSQL deployments, ensure SSL is configured
if "postgresql" in DATABASE_URL and "localhost" not in DATABASE_URL:
    if "sslmode" not in DATABASE_URL:
        DATABASE_URL = f"{DATABASE_URL}?sslmode=prefer"

# Create async engine with production settings (optimized for local development)
engine_kwargs = {
    "echo": config("DB_ECHO", default=False, cast=bool),
    "future": True,
    "pool_size": 5,  # Reduced for local development
    "max_overflow": 10,  # Reduced for local development
    "pool_pre_ping": True,  # Enable connection health checks
}

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

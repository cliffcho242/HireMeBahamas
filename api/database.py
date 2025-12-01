"""
FastAPI + Vercel Postgres Database Configuration
IMMORTAL VERSION - 2025
"""
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Get Vercel Postgres connection string (NON_POOLING for serverless)
DATABASE_URL = os.getenv(
    "POSTGRES_URL_NON_POOLING",
    os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
)

# Convert postgresql:// to postgresql+asyncpg://
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine optimized for Vercel Serverless
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,
    connect_args={
        "timeout": 30,
        "command_timeout": 30,
        "server_settings": {
            "jit": "off",
            "application_name": "vercel_fastapi"
        }
    }
)

# Async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base for models
Base = declarative_base()


async def get_db():
    """Dependency for FastAPI endpoints"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

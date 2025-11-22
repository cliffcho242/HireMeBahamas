import os

from decouple import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database configuration - Use SQLite for development
DATABASE_URL = config("DATABASE_URL", default="sqlite+aiosqlite:///./hiremebahamas.db")

# For production PostgreSQL, ensure SSL is configured
if "postgresql" in DATABASE_URL and "localhost" not in DATABASE_URL:
    if "sslmode" not in DATABASE_URL:
        DATABASE_URL = f"{DATABASE_URL}?sslmode=prefer"

# For SQLite with aiosqlite, add WAL mode and foreign keys support
if DATABASE_URL.startswith("sqlite"):
    # Ensure WAL mode is enabled for SQLite
    if "?" not in DATABASE_URL:
        DATABASE_URL = f"{DATABASE_URL}?journal_mode=WAL&foreign_keys=ON"
    else:
        DATABASE_URL = f"{DATABASE_URL}&journal_mode=WAL&foreign_keys=ON"

# Create async engine
engine_kwargs = {
    "echo": config("DB_ECHO", default=False, cast=bool),
    "future": True,
}

# Add connection pool settings only for non-SQLite databases
if not DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update(
        {
            "pool_size": 10,
            "max_overflow": 20,
        }
    )

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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()

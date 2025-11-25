import os

from decouple import config
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database configuration - Use SQLite for development
DATABASE_URL = config("DATABASE_URL", default="sqlite+aiosqlite:///./hiremebahamas.db")

# For production PostgreSQL, ensure SSL is configured
if "postgresql" in DATABASE_URL and "localhost" not in DATABASE_URL:
    if "sslmode" not in DATABASE_URL:
        DATABASE_URL = f"{DATABASE_URL}?sslmode=prefer"

# Create async engine
engine_kwargs = {
    "echo": config("DB_ECHO", default=False, cast=bool),
    "future": True,
}

# Configure database-specific settings
if "sqlite" in DATABASE_URL:
    # For SQLite, use connect_args to enable WAL mode
    # Note: aiosqlite handles these through connection initialization
    engine_kwargs["connect_args"] = {
        "check_same_thread": False,
    }
else:
    # Add connection pool settings only for non-SQLite databases
    engine_kwargs.update(
        {
            "pool_size": 10,
            "max_overflow": 20,
        }
    )

engine = create_async_engine(DATABASE_URL, **engine_kwargs)


# Enable WAL mode for SQLite connections
if "sqlite" in DATABASE_URL:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Set SQLite pragmas on connection"""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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

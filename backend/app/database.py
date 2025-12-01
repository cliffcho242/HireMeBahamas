# =============================================================================
# DATABASE ENGINE CONFIGURATION - NUCLEAR FIX FOR 502 BAD GATEWAY (2025)
# =============================================================================
# DATABASE_URL format for Render → Railway Postgres:
# postgresql+asyncpg://user:password@host:port/db?sslmode=require&connect_timeout=30&options=-c%20jit=off
#
# Render Dashboard Settings:
# - Instance Type: Standard ($25/mo) or at minimum Starter ($7/mo)
# - Memory: 1GB minimum (Standard plan)
# - Health Check Path: /health
# - Grace Period: 300s
#
# Start Command:
# gunicorn backend.app.main:app -k uvicorn.workers.UvicornWorker --workers 1 --timeout 180 --keep-alive 5 --preload
# =============================================================================

import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Get DATABASE_URL from environment - prefer private network URL to avoid egress
DATABASE_URL = os.getenv("DATABASE_PRIVATE_URL") or os.getenv("DATABASE_URL", "postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas")

# Convert sync PostgreSQL URLs to async driver format
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Pool configuration constants - optimized for Render Standard (1GB RAM)
# Low pool size prevents connection exhaustion on Railway free tier
POOL_SIZE = 2  # Minimum connections kept open
MAX_OVERFLOW = 3  # Max additional connections under load (total max = 5)

# Create async engine with bulletproof timeout configuration
# These settings prevent 502 Bad Gateway and 173-second login delays
engine = create_async_engine(
    DATABASE_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_pre_ping=True,  # Validate connections before use (prevents stale connection errors)
    pool_recycle=180,  # Recycle connections every 3 min (Railway drops idle connections)
    pool_timeout=30,  # Wait max 30s for connection from pool
    connect_args={
        "timeout": 30,  # Connection establishment timeout (asyncpg parameter)
        "command_timeout": 30,  # Query execution timeout (asyncpg parameter)
        "server_settings": {
            "jit": "off",  # CRITICAL: Disable JIT - causes 60s+ first-query delays
            "statement_timeout": "30000",  # 30 second query timeout (milliseconds)
        },
        "ssl": "require"  # Required for Railway Postgres
    }
)

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
        "max_overflow": MAX_OVERFLOW,
    }

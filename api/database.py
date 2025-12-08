"""
Database connection helper for Vercel Serverless API
Lightweight, fast, optimized for cold starts
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Global engine (reused across invocations)
_engine = None


def get_database_url():
    """Get and validate DATABASE_URL from environment"""
    db_url = os.getenv("DATABASE_URL", "")
    
    # Strip whitespace from database URL to prevent connection errors
    db_url = db_url.strip()
    
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Convert postgres:// to postgresql+asyncpg://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    return db_url


def get_engine():
    """Get or create database engine (singleton pattern)"""
    global _engine
    
    if _engine is None:
        db_url = get_database_url()
        
        # Get configurable timeout values from environment
        connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))
        command_timeout = int(os.getenv("DB_COMMAND_TIMEOUT", "30"))
        pool_size = int(os.getenv("DB_POOL_SIZE", "2"))
        max_overflow = int(os.getenv("DB_POOL_MAX_OVERFLOW", "3"))
        pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "300"))
        
        _engine = create_async_engine(
            db_url,
            pool_size=pool_size,           # Small pool for serverless
            max_overflow=max_overflow,     # Limited overflow
            pool_recycle=pool_recycle,     # Recycle connections every 5 minutes
            pool_pre_ping=True,            # Validate connections before use
            connect_args={
                "timeout": connect_timeout,        # Connection timeout
                "command_timeout": command_timeout, # Query timeout
            },
            echo=False,                    # Disable SQL logging in production
        )
    
    return _engine


async def test_connection():
    """Test database connectivity (for /ready endpoint)"""
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False


async def close_engine():
    """Close database engine (cleanup)"""
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None

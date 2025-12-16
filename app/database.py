"""
Database initialization module for HireMeBahamas
Provides non-blocking database initialization and warmup
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def init_db() -> Optional[object]:
    """Initialize database engine lazily.
    
    Returns the database engine or None if initialization fails.
    This function is designed to be called in a background task,
    so failures are logged but don't crash the application.
    
    Returns:
        Database engine instance or None if initialization fails
    """
    try:
        # Import the actual database module from api.backend_app
        from api.backend_app.database import get_engine
        
        engine = get_engine()
        if engine is None:
            logger.warning("Database engine not available - DATABASE_URL may not be configured")
            return None
            
        logger.info("Database engine initialized successfully")
        return engine
        
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
        return None


async def warmup_db(engine) -> bool:
    """Warm up database connection pool.
    
    Performs a simple connection test to ensure the database is accessible
    and warms up the connection pool.
    
    Args:
        engine: Database engine instance from init_db()
        
    Returns:
        True if warmup succeeded, False otherwise
    """
    if engine is None:
        logger.warning("Cannot warm up database - engine is None")
        return False
        
    try:
        # Import sqlalchemy to test connectivity
        from sqlalchemy import text
        
        # Perform a simple query to test connectivity and warm up the pool
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        
        logger.info("Database warmup: Connection pool ready")
        return True
        
    except Exception as e:
        logger.warning(f"Database warmup failed: {e}")
        return False

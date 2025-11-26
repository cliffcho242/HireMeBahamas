"""
Database health monitoring utilities

Provides health check and connection monitoring for database operations.
Helps diagnose slow queries and connection issues in production.
"""
import logging
import time
from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def check_database_health(db: AsyncSession) -> dict:
    """Check database connection health and performance
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with health status and timing information
    """
    start_time = time.time()
    
    try:
        # Execute a simple query to check connection
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        health_status = {
            "status": "healthy",
            "response_time_ms": duration_ms,
            "message": "Database connection is working"
        }
        
        # Warn if database is slow
        if duration_ms > 1000:
            logger.warning(f"Database health check slow: {duration_ms}ms (>1s threshold)")
            health_status["warning"] = "Database response time is slow"
        
        return health_status
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        
        logger.error(f"Database health check failed after {duration_ms}ms: {type(e).__name__}: {e}")
        
        return {
            "status": "unhealthy",
            "response_time_ms": duration_ms,
            "error": str(e),
            "message": "Database connection failed"
        }


async def log_slow_query_warning(operation: str, duration_ms: int, threshold_ms: int = 1000):
    """Log a warning if a database operation is slow
    
    Args:
        operation: Name of the database operation
        duration_ms: Duration of the operation in milliseconds
        threshold_ms: Threshold in milliseconds for considering an operation slow (default: 1000ms)
    """
    if duration_ms > threshold_ms:
        logger.warning(
            f"SLOW QUERY: {operation} took {duration_ms}ms (>{threshold_ms}ms threshold)"
        )


async def get_database_stats(db: AsyncSession) -> Optional[dict]:
    """Get database statistics for monitoring
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with database statistics or None if PostgreSQL-specific queries fail
    """
    try:
        # Get number of active connections (PostgreSQL specific)
        result = await db.execute(text("""
            SELECT count(*) 
            FROM pg_stat_activity 
            WHERE state = 'active'
        """))
        active_connections = result.scalar()
        
        # Get database size (PostgreSQL specific)
        result = await db.execute(text("""
            SELECT pg_database_size(current_database())
        """))
        db_size_bytes = result.scalar()
        
        return {
            "active_connections": active_connections,
            "database_size_bytes": db_size_bytes,
            "database_size_mb": round(db_size_bytes / (1024 * 1024), 2)
        }
        
    except Exception as e:
        # These are PostgreSQL-specific queries, so they might fail in other databases
        logger.debug(f"Could not get database stats (this is normal for non-PostgreSQL databases): {e}")
        return None

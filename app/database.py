"""
Database module - Single source of truth for database configuration.

This module provides centralized database initialization and connection management.
All database operations should use the engine from this module.

Key features:
- Lazy initialization (no blocking imports)
- SQLAlchemy engine with proper configuration
- SSL configured via DATABASE_URL (not connect_args)
- Production-safe error handling
- Connection warmup for health checks
"""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url

# Module-level logger
logger = logging.getLogger(__name__)

# Global engine instance (initialized lazily)
engine = None


def init_db():
    """
    Initialize database engine with production-safe configuration.
    
    This function creates the SQLAlchemy engine with proper connection pooling
    and timeout settings. It returns None if DATABASE_URL is not configured,
    allowing the application to start without a database connection.
    
    Returns:
        Engine: SQLAlchemy engine instance if successful, None otherwise
    """
    global engine

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        logging.warning("DATABASE_URL missing — DB disabled")
        return None

    try:
        # Parse and validate database URL
        # This handles URL encoding and validation
        url = make_url(db_url)

        # Create engine with production-ready configuration
        # IMPORTANT: SSL is configured via DATABASE_URL (?sslmode=require)
        # NOT in connect_args - this is the correct pattern for asyncpg/psycopg
        engine = create_engine(
            url,
            pool_pre_ping=True,      # Validate connections before use
            pool_recycle=300,        # Recycle connections every 5 minutes
            pool_size=5,             # Minimum pool size
            max_overflow=10          # Maximum overflow connections
        )

        logging.info("Database engine initialized")
        return engine

    except Exception as e:
        logging.warning(f"DB init skipped: {e}")
        return None


def warmup_db(engine):
    """
    Warm up database connection by executing a test query.
    
    This function verifies that the database is reachable and responsive.
    It's useful for health checks and startup validation.
    
    Args:
        engine: SQLAlchemy engine instance
    """
    if engine is None:
        logging.warning("DB warmup skipped: engine is None")
        return
        
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logging.info("Database warmup successful")
    except Exception as e:
        logging.warning(f"DB warmup skipped: {e}")

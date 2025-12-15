"""
Database module for backward compatibility.

This module re-exports all database functionality from app.core.database
to maintain backward compatibility with existing code that imports from app.database.
"""

# Re-export everything from core.database for backward compatibility
from .core.database import (
    Base,
    AsyncSessionLocal,
    async_session,
    engine,
    get_engine,
    get_db,
    get_async_session,
    init_db,
    close_db,
    test_db_connection,
    get_db_status,
    get_pool_status,
)

__all__ = [
    'Base',
    'AsyncSessionLocal',
    'async_session',
    'engine',
    'get_engine',
    'get_db',
    'get_async_session',
    'init_db',
    'close_db',
    'test_db_connection',
    'get_db_status',
    'get_pool_status',
]

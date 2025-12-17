# =============================================================================
# DATABASE ENGINE CONFIGURATION - WRAPPER (DEPRECATED)
# =============================================================================
#
# ⚠️  DEPRECATION NOTICE (Dec 2025):
# This module is DEPRECATED. All database configuration has been consolidated
# into a single source of truth at app/database.py
#
# **NEW CODE MUST IMPORT FROM app.database**
#
#     # ✅ CORRECT - Use single source of truth
#     from app.database import engine, get_db, init_db, warmup_db
#
#     # ❌ DEPRECATED - Don't use this module
#     from api.backend_app.database import engine
#
# This module is maintained for backward compatibility with existing imports
# that use the module alias system (sys.modules['app'] = backend_app).
# It will be removed in a future version.
#
# =============================================================================

# Re-export everything from app.database for backward compatibility
from app.database import (
    # Core exports
    engine,
    Base,
    init_db,
    warmup_db,
    get_db,
    get_async_session,
    async_session,
    
    # Health and monitoring
    test_db_connection,
    test_connection,
    close_db,
    close_engine,
    get_db_status,
    get_pool_status,
)

# Note: This wrapper ensures that code using the old import path
# "from backend_app.database import X" will still work, but will
# actually use the implementation from app.database (single source of truth)

__all__ = [
    "engine",
    "Base",
    "init_db",
    "warmup_db",
    "get_db",
    "get_async_session",
    "async_session",
    "test_db_connection",
    "test_connection",
    "close_db",
    "close_engine",
    "get_db_status",
    "get_pool_status",
]

"""
API routers package - Import-safe design.

This package contains all API router modules. The modules are NOT imported
at package import time to avoid circular dependencies and import-time side effects.

Instead, import routers explicitly with:
    from app.api.analytics import router as analytics_router
    from app.api.auth import router as auth_router
    app.include_router(analytics_router, prefix="/api/analytics")
    app.include_router(auth_router)

This design ensures that:
- Routers are only loaded when actually used
- No import-time database connections or heavy operations
- No circular dependency issues
- Modules can be imported independently for testing
- Avoids large imports that can cause circular imports and startup crashes

Best Practice (✅):
    from app.api.analytics import router as analytics_router
    from app.api.auth import router as auth_router
    from app.api.feed import router as feed_router

Avoid (❌):
    from app.api import analytics, auth, feed, ...
"""

__all__ = [
    'auth',
    'hireme', 
    'jobs',
    'messages',
    'notifications',
    'posts',
    'profile_pictures',
    'reviews',
    'upload',
    'users'
]

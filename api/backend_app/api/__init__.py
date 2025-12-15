"""
API routers package - Import-safe design.

This package contains all API router modules. The modules are NOT imported
at package import time to avoid circular dependencies and import-time side effects.

Instead, import routers explicitly when needed:
    from app.api import auth
    app.include_router(auth.router)

This design ensures that:
- Routers are only loaded when actually used
- No import-time database connections or heavy operations
- No circular dependency issues
- Modules can be imported independently for testing
"""

__all__ = [
    'analytics',
    'auth',
    'debug',
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

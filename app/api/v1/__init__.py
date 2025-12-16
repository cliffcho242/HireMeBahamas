"""
API v1 - Aggregates all API routers with proper tagging
"""
import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Union, Any
from fastapi import APIRouter

def inject_typing_exports(module):
    """Inject typing module exports into a module's namespace.
    
    This is required for Pydantic to properly evaluate forward references
    when modules are aliased. This function is intentionally duplicated here
    (also in api/backend_app/main.py) to avoid circular import issues.
    
    Args:
        module: The module object to inject typing exports into
    """
    module.__dict__['Optional'] = Optional
    module.__dict__['List'] = List
    module.__dict__['Dict'] = Dict
    module.__dict__['Union'] = Union
    module.__dict__['Any'] = Any

# =============================================================================
# MODULE ALIASING SETUP
# =============================================================================
# The backend_app modules use imports like "from app.core.security import X"
# This requires setting up sys.modules aliases so "app" -> "backend_app"
# 
# Why this is needed:
# 1. backend_app was designed to be imported as "app" via sys.modules aliasing
# 2. This allows consistent imports throughout the backend code
# 3. Without this, imports like "from app.database import get_db" would fail
# =============================================================================

# Get the path to the api directory (parent of backend_app)
current_file = Path(__file__).resolve()
app_dir = current_file.parent.parent.parent  # /app/api/v1 -> /app
api_dir = app_dir.parent / "api"  # -> /api

if str(api_dir) not in sys.path:
    sys.path.insert(0, str(api_dir))

# Create comprehensive module alias so "import app" and "from app.core.X" work
# Only set up if not already done (check if 'app' module is properly aliased to backend_app)
if 'app' not in sys.modules or not hasattr(sys.modules.get('app', None), '__path__') or 'backend_app' not in str(getattr(sys.modules.get('app', None), '__file__', '')):
    import backend_app as app_module
    sys.modules['app'] = app_module
    inject_typing_exports(app_module)
    
    # Alias core submodules
    import backend_app.core
    sys.modules['app.core'] = backend_app.core
    inject_typing_exports(backend_app.core)
    
    # Dynamically alias all core submodules
    _core_modules = ['security', 'upload', 'concurrent', 'metrics', 'redis_cache', 
                     'socket_manager', 'cache', 'db_health', 'timeout_middleware', 'rate_limiter', 'environment']
    for _module_name in _core_modules:
        try:
            _module = __import__(f'backend_app.core.{_module_name}', fromlist=[''])
            sys.modules[f'app.core.{_module_name}'] = _module
            inject_typing_exports(_module)
        except ImportError:
            pass
    
    # Alias schemas submodules
    try:
        import backend_app.schemas
        sys.modules['app.schemas'] = backend_app.schemas
        inject_typing_exports(backend_app.schemas)
        
        _schema_modules = ['auth', 'job', 'message', 'post', 'review']
        for _module_name in _schema_modules:
            try:
                _module = __import__(f'backend_app.schemas.{_module_name}', fromlist=[''])
                sys.modules[f'app.schemas.{_module_name}'] = _module
                inject_typing_exports(_module)
            except ImportError:
                pass
    except ImportError:
        pass
    
    # Alias api submodule and its children
    try:
        import backend_app.api
        sys.modules['app.api'] = backend_app.api
        inject_typing_exports(backend_app.api)
        
        _api_modules = ['analytics', 'auth', 'debug', 'feed', 'health', 'hireme', 'jobs', 'messages', 
                        'notifications', 'posts', 'profile_pictures', 'reviews', 'upload', 'users']
        for _module_name in _api_modules:
            try:
                _module = __import__(f'backend_app.api.{_module_name}', fromlist=[''])
                sys.modules[f'app.api.{_module_name}'] = _module
                inject_typing_exports(_module)
            except ImportError:
                pass
    except ImportError:
        pass
    
    # Alias database module
    try:
        import backend_app.database
        sys.modules['app.database'] = backend_app.database
        inject_typing_exports(backend_app.database)
    except ImportError:
        pass
    
    # Alias graphql submodule
    try:
        import backend_app.graphql
        sys.modules['app.graphql'] = backend_app.graphql
        inject_typing_exports(backend_app.graphql)
        
        try:
            import backend_app.graphql.schema
            sys.modules['app.graphql.schema'] = backend_app.graphql.schema
            inject_typing_exports(backend_app.graphql.schema)
        except ImportError:
            pass
    except ImportError:
        pass

# Import all routers from the backend_app
from api.backend_app.api.analytics import router as analytics_router
from api.backend_app.api.auth import router as auth_router
from api.backend_app.api.debug import router as debug_router
from api.backend_app.api.feed import router as feed_router
from api.backend_app.api.health import router as health_router
from api.backend_app.api.hireme import router as hireme_router
from api.backend_app.api.jobs import router as jobs_router
from api.backend_app.api.messages import router as messages_router
from api.backend_app.api.notifications import router as notifications_router
from api.backend_app.api.posts import router as posts_router
from api.backend_app.api.profile_pictures import router as profile_pictures_router
from api.backend_app.api.reviews import router as reviews_router
from api.backend_app.api.upload import router as upload_router
from api.backend_app.api.users import router as users_router

# Create the main v1 router
router = APIRouter(prefix="/api")

# Include all routers with their respective tags
# Tags will automatically organize endpoints in OpenAPI docs
router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
router.include_router(auth_router, tags=["auth"])  # auth router already has /api/auth prefix
router.include_router(debug_router, prefix="/debug", tags=["debug"])
router.include_router(feed_router, prefix="/feed", tags=["feed"])
router.include_router(health_router, tags=["health"])  # health router uses root paths
router.include_router(hireme_router, prefix="/hireme", tags=["hireme"])
router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
router.include_router(messages_router, prefix="/messages", tags=["messages"])
router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
router.include_router(posts_router, prefix="/posts", tags=["posts"])
router.include_router(profile_pictures_router, prefix="/profile-pictures", tags=["profile-pictures"])
router.include_router(reviews_router, prefix="/reviews", tags=["reviews"])
router.include_router(upload_router, prefix="/upload", tags=["uploads"])
router.include_router(users_router, prefix="/users", tags=["users"])

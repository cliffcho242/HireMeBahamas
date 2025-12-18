"""
Vercel Serverless FastAPI Handler - HireMeBahamas (2025)
Full backend migration to Vercel with complete API functionality
"""
import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Union, Any

# Make backend_app importable as "app" for compatibility
# In Vercel serverless, only the api/ directory is packaged
api_dir = Path(__file__).parent
sys.path.insert(0, str(api_dir))


def inject_typing_exports(module):
    """Inject typing module exports into a module's namespace.
    
    This is required for Pydantic to properly evaluate forward references
    when modules are aliased. When Pydantic evaluates forward references,
    it looks in the module's __dict__ for type names like Optional, List, etc.
    
    Note: This function is intentionally defined locally in each entry point file
    rather than imported from a shared utility to avoid circular import issues
    and ensure it's available before any other modules are loaded.
    
    Args:
        module: The module object to inject typing exports into
    """
    module.__dict__['Optional'] = Optional
    module.__dict__['List'] = List
    module.__dict__['Dict'] = Dict
    module.__dict__['Union'] = Union
    module.__dict__['Any'] = Any


# Create comprehensive module alias so "import app" and "from app.core.X" work
import backend_app
sys.modules['app'] = backend_app
inject_typing_exports(backend_app)

# CRITICAL FIX: Also alias all submodules so "from app.core.X" works
# When we do sys.modules['app'] = backend_app, Python doesn't automatically
# resolve app.core to backend_app.core, so we must explicitly alias each submodule
import backend_app.core
sys.modules['app.core'] = backend_app.core
inject_typing_exports(backend_app.core)

# Dynamically alias all core submodules to handle all "from app.core.X" imports
_core_modules = ['security', 'upload', 'concurrent', 'metrics', 'redis_cache', 
                 'socket_manager', 'cache', 'db_health', 'timeout_middleware', 'rate_limiter']
for _module_name in _core_modules:
    try:
        _module = __import__(f'backend_app.core.{_module_name}', fromlist=[''])
        sys.modules[f'app.core.{_module_name}'] = _module
        inject_typing_exports(_module)
    except ImportError:
        # Skip modules that might not be available (graceful degradation)
        pass

# Import the FastAPI app from backend_app
try:
    from backend_app.main import app
    from mangum import Mangum
    
    # Wrap FastAPI app with Mangum for Vercel serverless compatibility
    # lifespan="off" disables startup/shutdown events for serverless
    handler = Mangum(app, lifespan="off")
    
except ImportError as e:
    # Fallback minimal app if backend imports fail
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(
        title="HireMeBahamas API",
        version="1.0.0",
        description="Job platform API for the Bahamas (Fallback Mode)",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    
    # CORS Configuration (Fallback mode - still secure)
    # Use specific origins even in fallback mode for security
    # NOTE: Using allow_credentials=True for production security
    import os
    _is_prod = os.getenv("ENVIRONMENT", "").lower() == "production" or os.getenv("VERCEL_ENV", "").lower() == "production"
    
    # 🚫 SECURITY: No wildcard patterns (*) in production
    if _is_prod:
        _fallback_origins = [
            "https://hiremebahamas.com",
            "https://www.hiremebahamas.com",
            "https://hiremebahamas.vercel.app",
        ]
    else:
        _fallback_origins = [
            "https://hiremebahamas.com",
            "https://www.hiremebahamas.com",
            "https://hiremebahamas.vercel.app",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_fallback_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
    
    @app.get("/api/health", include_in_schema=False)
    @app.head("/api/health", include_in_schema=False)
    @app.get("/health", include_in_schema=False)
    @app.head("/health", include_in_schema=False)
    def health():
        """Instant health check - no database dependency.
        
        Supports both GET and HEAD methods for maximum compatibility.
        
        ✅ NO DATABASE - instant response
        ✅ NO IO - instant response
        ✅ NO async/await - synchronous function
        
        Render kills apps that fail health checks, so this must be instant.
        """
        return JSONResponse({"status": "ok"}, status_code=200)
    
    @app.get("/health/ping", include_in_schema=False)
    @app.head("/health/ping", include_in_schema=False)
    def health_ping():
        """Ultra-fast health ping endpoint
        
        Supports both GET and HEAD methods for maximum compatibility.
        
        🚫 NO database queries
        🚫 NO external service calls
        🚫 NO authentication checks
        Target latency: < 30ms
        """
        return JSONResponse({"status": "ok"}, status_code=200)
    
    @app.get("/")
    @app.head("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "HireMeBahamas API (Fallback Mode)",
            "error": f"Backend import failed: {str(e)}",
            "health": "/health"
        }
    
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")

# Export handler for Vercel
__all__ = ['handler', 'app']

# For local testing
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

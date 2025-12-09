"""
Vercel Serverless FastAPI Handler - HireMeBahamas (2025)
Full backend migration to Vercel with complete API functionality
"""
import sys
import os
from pathlib import Path

# Make backend_app importable as "app" for compatibility
# In Vercel serverless, only the api/ directory is packaged
api_dir = Path(__file__).parent
sys.path.insert(0, str(api_dir))

# Create comprehensive module alias so "import app" and "from app.core.X" work
import backend_app
sys.modules['app'] = backend_app

# CRITICAL FIX: Also alias all submodules so "from app.core.X" works
# When we do sys.modules['app'] = backend_app, Python doesn't automatically
# resolve app.core to backend_app.core, so we must explicitly alias each submodule
import backend_app.core
sys.modules['app.core'] = backend_app.core

# CRITICAL FIX FOR PYDANTIC: Inject typing module exports into aliased modules
# When Pydantic evaluates forward references, it looks in the module's __dict__
# for type names like Optional, List, Dict, etc. Since we're aliasing modules,
# we need to ensure these typing constructs are available in the aliased namespace.
from typing import Optional, List, Dict, Union, Any
backend_app.__dict__['Optional'] = Optional
backend_app.__dict__['List'] = List
backend_app.__dict__['Dict'] = Dict
backend_app.__dict__['Union'] = Union
backend_app.__dict__['Any'] = Any
backend_app.core.__dict__['Optional'] = Optional
backend_app.core.__dict__['List'] = List
backend_app.core.__dict__['Dict'] = Dict
backend_app.core.__dict__['Union'] = Union
backend_app.core.__dict__['Any'] = Any

# Dynamically alias all core submodules to handle all "from app.core.X" imports
_core_modules = ['security', 'upload', 'concurrent', 'metrics', 'redis_cache', 
                 'socket_manager', 'cache', 'db_health', 'timeout_middleware']
for _module_name in _core_modules:
    try:
        _module = __import__(f'backend_app.core.{_module_name}', fromlist=[''])
        sys.modules[f'app.core.{_module_name}'] = _module
        # Also inject typing exports into each submodule
        _module.__dict__['Optional'] = Optional
        _module.__dict__['List'] = List
        _module.__dict__['Dict'] = Dict
        _module.__dict__['Union'] = Union
        _module.__dict__['Any'] = Any
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
        description="Job platform API for the Bahamas (Fallback Mode)"
    )
    
    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/api/health")
    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return JSONResponse({
            "status": "healthy",
            "mode": "fallback",
            "platform": "vercel-serverless",
            "error": str(e)
        })
    
    @app.get("/")
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
    uvicorn.run(app, host="0.0.0.0", port=8000)

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

# Import and alias specific core modules that are commonly used
import backend_app.core.security
sys.modules['app.core.security'] = backend_app.core.security

import backend_app.core.upload
sys.modules['app.core.upload'] = backend_app.core.upload

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

"""
Vercel Serverless FastAPI Handler - HireMeBahamas (2025)
Full backend migration to Vercel with complete API functionality
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Import the FastAPI app from backend
try:
    from app.main import app
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

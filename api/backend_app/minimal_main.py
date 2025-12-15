import logging
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add backend_app to path for imports
backend_app_dir = os.path.dirname(os.path.abspath(__file__))
if backend_app_dir not in sys.path:
    sys.path.insert(0, backend_app_dir)

from core.environment import get_cors_origins

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HireBahamas API",
    description="Job platform API for the Bahamas",
    version="1.0.0",
)

# Configure CORS - exclude localhost in production
# Uses shared environment utility for consistent configuration
_allowed_origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "HireBahamas API is running"}


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to HireBahamas API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Simple auth endpoint for testing
@app.post("/auth/register")
async def register():
    return {"message": "Registration endpoint - ready for implementation"}


@app.post("/auth/login")
async def login():
    return {"message": "Login endpoint - ready for implementation"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8005)

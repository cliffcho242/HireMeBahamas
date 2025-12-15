import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
_is_production = os.getenv("ENVIRONMENT", "").lower() == "production"
_allowed_origins = []
if not _is_production:
    # Localhost only in development
    _allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
else:
    # Production origins
    _allowed_origins = [
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
        "https://*.vercel.app",
    ]

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

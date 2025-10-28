import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import APIs
from .api import auth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting HireMeBahamas API...")
    yield
    # Shutdown
    logger.info("Shutting down HireMeBahamas API...")


# Initialize FastAPI app
app = FastAPI(
    title="HireMeBahamas API",
    description="Job platform API for the Bahamas",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "HireMeBahamas API is running"}


# Include routers (testing one by one)
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
# app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
# app.include_router(messages.router, prefix="/messages", tags=["messages"])
# app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
# app.include_router(upload.router, prefix="/upload", tags=["uploads"])


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to HireMeBahamas API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8005)

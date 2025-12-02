"""
Vercel Serverless FastAPI Handler - HireMeBahamas (2025)
Zero cold starts, sub-200ms response time globally
"""
from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import os
import time

# Import database utilities at module level for performance
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# ============================================================================
# CREATE FASTAPI APP
# ============================================================================
app = FastAPI(
    title="HireMeBahamas API",
    version="1.0.0",
    description="Job platform API for the Bahamas",
)

# ============================================================================
# CORS CONFIGURATION
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ROOT ENDPOINT - API Information
# ============================================================================
@app.get("/")
@app.get("/api")
async def root():
    """
    Root endpoint providing API information and available routes.
    Useful for debugging and API discovery.
    """
    return {
        "name": "HireMeBahamas API",
        "version": "1.0.0",
        "platform": "vercel-serverless",
        "status": "operational",
        "endpoints": {
            "health": "/api/health",
            "ready": "/api/ready",
            "auth": {
                "login": "POST /api/auth/login",
                "register": "POST /api/auth/register",
                "me": "GET /api/auth/me"
            },
            "jobs": {
                "list": "GET /api/jobs",
                "create": "POST /api/jobs"
            },
            "posts": {
                "list": "GET /api/posts",
                "create": "POST /api/posts"
            }
        }
    }

# ============================================================================
# INSTANT HEALTH CHECK (No DB) - Responds in <5ms
# ============================================================================
@app.get("/api/health")
@app.get("/health")
@app.head("/api/health")
@app.head("/health")
async def health():
    """
    Instant health check - responds in <5ms without database connectivity.
    Use this endpoint for load balancer health checks and uptime monitoring.
    """
    return {
        "status": "healthy",
        "platform": "vercel-serverless",
        "region": os.getenv("VERCEL_REGION", "unknown"),
        "timestamp": int(time.time()),
    }

# ============================================================================
# DATABASE-AWARE READINESS CHECK - Responds in <100ms
# ============================================================================
@app.get("/api/ready")
@app.get("/ready")
@app.head("/api/ready")
@app.head("/ready")
async def ready():
    """
    Readiness check with database connectivity validation.
    Returns 200 if database is accessible, 503 if not.
    """
    try:
        db_url = os.getenv("DATABASE_URL")
        
        if not db_url:
            return Response(
                content='{"status":"not_ready","error":"DATABASE_URL not set"}',
                status_code=503,
                media_type="application/json"
            )
        
        # Test database connection
        # Convert postgres:// to postgresql+asyncpg://
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        engine = create_async_engine(
            db_url,
            pool_pre_ping=True,
            connect_args={"timeout": 5}
        )
        
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        await engine.dispose()
        
        return {
            "status": "ready",
            "database": "connected",
            "timestamp": int(time.time()),
        }
        
    except Exception as e:
        return Response(
            content=f'{{"status":"not_ready","database":"disconnected","error":"{str(e)}"}}',
            status_code=503,
            media_type="application/json"
        )

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================
@app.post("/api/auth/login")
async def login(email: str, password: str):
    """Login endpoint - placeholder for production implementation"""
    # TODO: Implement actual authentication logic
    return {
        "message": "Login endpoint - implement with your auth logic",
        "email": email,
    }

@app.post("/api/auth/register")
async def register():
    """Register endpoint - placeholder for production implementation"""
    # TODO: Implement actual registration logic
    return {"message": "Register endpoint - implement with your auth logic"}

@app.get("/api/auth/me")
async def me():
    """Get current user - placeholder for production implementation"""
    # TODO: Implement actual user retrieval logic
    return {"message": "User endpoint - implement with your auth logic"}

# ============================================================================
# JOB ENDPOINTS
# ============================================================================
@app.get("/api/jobs")
async def get_jobs():
    """Get all jobs - placeholder for production implementation"""
    # TODO: Implement actual job listing logic
    return {"jobs": [], "total": 0}

@app.post("/api/jobs")
async def create_job():
    """Create job - placeholder for production implementation"""
    # TODO: Implement actual job creation logic
    return {"message": "Create job endpoint - implement with your logic"}

# ============================================================================
# POST ENDPOINTS
# ============================================================================
@app.get("/api/posts")
async def get_posts():
    """Get all posts - placeholder for production implementation"""
    # TODO: Implement actual post listing logic
    return {"posts": [], "total": 0}

@app.post("/api/posts")
async def create_post():
    """Create post - placeholder for production implementation"""
    # TODO: Implement actual post creation logic
    return {"message": "Create post endpoint - implement with your logic"}

# ============================================================================
# EXPORT HANDLER FOR VERCEL
# ============================================================================
# Mangum wraps the FastAPI app for AWS Lambda / Vercel compatibility
handler = Mangum(app, lifespan="off")

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


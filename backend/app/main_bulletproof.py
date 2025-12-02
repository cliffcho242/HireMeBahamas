"""
FastAPI Main App — Bulletproof Vercel-Ready 2025
Clean JWT Auth with CORS
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import auth router
from app.api.auth_bulletproof import router as auth_router

# Create FastAPI app
app = FastAPI(
    title="HireMeBahamas API",
    version="1.0.0",
    description="Bulletproof JWT Authentication"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "HireMeBahamas API - Bulletproof JWT Auth",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "login": "POST /api/auth/login",
            "register": "POST /api/auth/register",
            "me": "GET /api/auth/me"
        }
    }

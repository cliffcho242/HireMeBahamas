"""
MASTER RENDER/NEON BACKEND — IMMORTAL DEPLOY 2025
Includes: Auth, Jobs, Users, Lazy DB, Health check
"""

import logging
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# -----------------------------
# LAZY DATABASE ENGINE
# -----------------------------
engine = None
logger = logging.getLogger(__name__)


def get_engine():
    global engine
    if engine is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL not set in environment")
        engine = create_engine(database_url, pool_pre_ping=True)
    return engine


def get_db_engine():
    """Backward-compatible alias for get_engine()."""
    return get_engine()


# -----------------------------
# FASTAPI APP
# -----------------------------
app = FastAPI(title="HireMeBahamas Backend")

# -----------------------------
# CORS
# -----------------------------
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if not allowed_origins_env:
    cors_origins = [
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
elif allowed_origins_env == "*":
    cors_origins = ["*"]
else:
    cors_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/health")
@app.head("/health")
def health():
    return PlainTextResponse("ok", status_code=200)


# -----------------------------
# AUTH ROUTES
# -----------------------------
@app.post("/api/auth/login")
async def login(request: Request):
    """
    Example login route
    """
    payload = await request.json()
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Replace with real auth logic
            result = conn.execute(text("SELECT 1"))
            _ = result.fetchone()
            return {"status": "success", "message": "Login simulated", "email": email}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/register")
async def register(request: Request):
    """
    Example register route
    """
    payload = await request.json()
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Replace with real registration logic
            result = conn.execute(text("SELECT 1"))
            _ = result.fetchone()
            return {"status": "success", "message": "Register simulated", "email": email}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# JOBS ROUTES
# -----------------------------
@app.get("/api/jobs")
def get_jobs():
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Replace with real query
            conn.execute(text("SELECT 1"))
            return {"jobs": []}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs")
def create_job():
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Replace with real insertion logic
            result = conn.execute(text("SELECT 1"))
            _ = result.fetchone()
            return {"status": "success", "message": "Job creation simulated"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# USERS ROUTES
# -----------------------------
@app.get("/api/users")
def get_users():
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            return {"users": []}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/users")
def create_user():
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Replace with real insertion logic
            result = conn.execute(text("SELECT 1"))
            _ = result.fetchone()
            return {"status": "success", "message": "User creation simulated"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# GLOBAL ERROR HANDLER
# -----------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception in request", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

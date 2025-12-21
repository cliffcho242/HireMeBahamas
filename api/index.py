"""
MASTER RENDER/NEON BACKEND — IMMORTAL DEPLOY 2025
Includes: Auth, Jobs, Users, Lazy DB, Health check
"""
import logging
import os
import threading

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

# -----------------------------
# LAZY DATABASE ENGINE
# -----------------------------
engine = None
_engine_lock = threading.Lock()


def get_engine():
    """Thread-safe lazy initializer for the shared SQLAlchemy engine."""
    global engine
    if engine is None:
        with _engine_lock:
            if engine is None:
                database_url = os.getenv("DATABASE_URL")
                if not database_url:
                    raise RuntimeError("DATABASE_URL not set in environment")
                engine = create_engine(database_url, pool_pre_ping=True)
    return engine


# -----------------------------
# FASTAPI APP
# -----------------------------
app = FastAPI(title="HireMeBahamas Backend")


# -----------------------------
# CORS
# -----------------------------
_default_origins = [
    "https://hiremebahamas.com",
    "https://www.hiremebahamas.com",
]
_origins_env = os.getenv("ALLOWED_ORIGINS")
allowed_origins = (
    [origin.strip() for origin in _origins_env.split(",") if origin.strip()]
    if _origins_env
    else _default_origins
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)


# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/health")
@app.head("/health")
def health():
    """Lightweight health check that never touches external services."""
    return PlainTextResponse("ok", status_code=200)


# -----------------------------
# AUTH ROUTES
# -----------------------------
@app.post("/api/auth/login")
def login(request: Request):
    """Example login route (placeholder; replace with real authentication)."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Replace with real auth logic
            result = conn.execute(text("SELECT 1"))
            _ = result.fetchone()
            return {"status": "success", "message": "Login simulated"}
    except SQLAlchemyError:
        logger.exception("Database error during login")
        raise HTTPException(status_code=500, detail="Database error")


@app.post("/api/auth/register")
def register(request: Request):
    """Example register route (placeholder; replace with real registration logic)."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Replace with real registration logic
            result = conn.execute(text("SELECT 1"))
            _ = result.fetchone()
            return {"status": "success", "message": "Register simulated"}
    except SQLAlchemyError:
        logger.exception("Database error during registration")
        raise HTTPException(status_code=500, detail="Database error")


# -----------------------------
# JOBS ROUTES
# -----------------------------
@app.get("/api/jobs")
def get_jobs():
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Replace with real query
            result = conn.execute(text("SELECT id, title FROM jobs LIMIT 10"))
            jobs = [{"id": row[0], "title": row[1]} for row in result]
            return {"jobs": jobs}
    except SQLAlchemyError:
        logger.exception("Database error while fetching jobs")
        raise HTTPException(status_code=500, detail="Database error")


@app.post("/api/jobs")
def create_job(request: Request):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Replace with real insertion logic
            result = conn.execute(text("SELECT 1"))
            _ = result.fetchone()
            return {"status": "success", "message": "Job creation simulated"}
    except SQLAlchemyError:
        logger.exception("Database error while creating job")
        raise HTTPException(status_code=500, detail="Database error")


# -----------------------------
# USERS ROUTES
# -----------------------------
@app.get("/api/users")
def get_users():
    engine = get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, username FROM users LIMIT 10"))
            users = [{"id": row[0], "username": row[1]} for row in result]
            return {"users": users}
    except SQLAlchemyError:
        logger.exception("Database error while fetching users")
        raise HTTPException(status_code=500, detail="Database error")


@app.post("/api/users")
def create_user(request: Request):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Replace with real insertion logic
            result = conn.execute(text("SELECT 1"))
            _ = result.fetchone()
            return {"status": "success", "message": "User creation simulated"}
    except SQLAlchemyError:
        logger.exception("Database error while creating user")
        raise HTTPException(status_code=500, detail="Database error")


# -----------------------------
# GLOBAL ERROR HANDLER
# -----------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception in request")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

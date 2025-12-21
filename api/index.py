"""
MASTER RENDER/NEON BACKEND — IMMORTAL DEPLOY 2025
FastAPI + Lazy Postgres + Health check
"""
import asyncio
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
# LAZY DATABASE ENGINE SETUP
# -----------------------------
engine = None
_engine_lock = threading.Lock()
DEBUG = os.getenv("DEBUG", "").lower() == "true"  # Used for safe error responses


def _get_int_env(name: str, default: int) -> int:
    """Safely parse integer environment variables with fallback defaults."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning("Invalid value for %s; using default %s", name, default)
        return default


def get_engine():
    """
    Lazy initialization of the database engine.
    Connects only when called in a request handler.
    """
    global engine
    if engine is None:
        with _engine_lock:
            if engine is None:
                database_url = os.getenv("DATABASE_URL")
                if not database_url:
                    raise RuntimeError(
                        "DATABASE_URL environment variable must be set (Render/Neon connection string required)"
                    )
                pool_size = _get_int_env("DB_POOL_SIZE", 5)
                max_overflow = _get_int_env("DB_MAX_OVERFLOW", 10)
                pool_recycle = _get_int_env("DB_POOL_RECYCLE", 1800)
                pool_timeout = _get_int_env("DB_POOL_TIMEOUT", 30)
                engine = create_engine(
                    database_url,
                    pool_pre_ping=True,
                    pool_size=pool_size,
                    max_overflow=max_overflow,
                    pool_recycle=pool_recycle,
                    pool_timeout=pool_timeout,
                )
    return engine


# -----------------------------
# FASTAPI APP
# -----------------------------
app = FastAPI(title="HireMeBahamas Backend")

# -----------------------------
# CORS (optional)
# -----------------------------
_allowed_origins = os.getenv("ALLOWED_ORIGINS")
if _allowed_origins:
    allowed_origins = [
        origin.strip() for origin in _allowed_origins.split(",") if origin.strip()
    ]
else:
    allowed_origins = ["https://hiremebahamas.com", "https://www.hiremebahamas.com"]
allow_credentials = allowed_origins != ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # configured via ALLOWED_ORIGINS env (defaults to production domains)
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# -----------------------------
# HEALTH CHECK ENDPOINT
# -----------------------------
@app.get("/health")
@app.head("/health")
async def health():
    """
    Render health check — does NOT touch DB
    """
    return PlainTextResponse("ok", status_code=200)


# -----------------------------
# EXAMPLE LOGIN ROUTE
# -----------------------------
@app.post("/api/auth/login")
async def login(request: Request):
    """
    Example login-like endpoint using lazy DB connection (placeholder for real auth)
    """
    def _check_db():
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    try:
        await asyncio.to_thread(_check_db)
        return {"status": "success"}
    except SQLAlchemyError:
        logger.error("Database error during login probe", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="Authentication service temporarily unavailable",
        )


# -----------------------------
# GLOBAL ERROR HANDLER
# -----------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", exc_info=True)
    message = str(exc) if DEBUG else "Internal server error"
    return JSONResponse(
        status_code=500,
        content={"detail": message},
    )

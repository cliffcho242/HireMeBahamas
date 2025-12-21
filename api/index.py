"""
MASTER RENDER/NEON BACKEND — IMMORTAL DEPLOY 2025
FastAPI + Lazy Postgres + Health check
"""
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# -----------------------------
# LAZY DATABASE ENGINE SETUP
# -----------------------------
engine = None


def get_engine():
    """
    Lazy initialization of the database engine.
    Connects only when called in a request handler.
    """
    global engine
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
# CORS (optional)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# HEALTH CHECK ENDPOINT
# -----------------------------
@app.get("/health")
@app.head("/health")
def health():
    """
    Render health check — does NOT touch DB
    """
    return PlainTextResponse("ok", status_code=200)


# -----------------------------
# EXAMPLE LOGIN ROUTE
# -----------------------------
@app.post("/api/auth/login")
def login(request: Request):
    """
    Example login route using lazy DB connection
    """
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            return {"status": "success"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# GLOBAL ERROR HANDLER
# -----------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

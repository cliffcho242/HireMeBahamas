"""
MASTER RENDER/NEON BACKEND — IMMORTAL DEPLOY 2025
Includes: Auth, Jobs, Users, Lazy DB, Health check
"""
import logging
import os
import threading
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

logger = logging.getLogger(__name__)

# -----------------------------
# CORS NORMALIZATION
# -----------------------------
def _normalize_allowed_origins(origins):
    """Ensure canonical domains are always allowed and HTTPS enforced."""
    required = [
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
    ]
    
    # Preserve wildcard behavior exactly
    if any(origin.strip() == "*" for origin in origins):
        return ["*"]
    
    normalized = []
    for origin in origins:
        candidate = origin.strip()
        if not candidate:
            continue
        if candidate.startswith("http://"):
            candidate = "https://" + candidate[len("http://"):]
        if candidate not in normalized:
            normalized.append(candidate)
    
    for domain in required:
        if domain not in normalized:
            normalized.append(domain)
    
    return normalized

# -----------------------------
# CONFIGURATION
# -----------------------------
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY not set in environment")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# -----------------------------
# PASSWORD HASHING
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DUMMY_PASSWORD_HASH: str = pwd_context.hash("placeholder-password")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

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
allowed_origins = _normalize_allowed_origins(allowed_origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # replace with frontend URL in production
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
    """Lightweight health check that never touches external services."""
    return PlainTextResponse("ok", status_code=200)


# -----------------------------
# AUTH ROUTES
# -----------------------------
def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


@app.post("/api/auth/register")
async def register(request: Request):
    """Register a new user with hashed password."""
    engine = get_engine()
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")

    hashed_password = get_password_hash(password)

    try:
        with engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO users (username, password) VALUES (:username, :password)"
                ),
                {"username": username, "password": hashed_password},
            )
            conn.commit()
            return {"status": "success", "message": "User registered"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    except HTTPException:
        raise
    except SQLAlchemyError:
        logger.exception("Database error during registration")
        raise HTTPException(status_code=500, detail="Database error")


@app.post("/api/auth/login")
async def login(request: Request):
    """Authenticate user and return JWT access token."""
    engine = get_engine()
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, password FROM users WHERE username=:username"),
                {"username": username},
            )
            user = result.mappings().first()
            if not user:
                verify_password(password, DUMMY_PASSWORD_HASH)
                raise HTTPException(status_code=401, detail="Invalid credentials")

            if not verify_password(password, user["password"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")

            access_token = create_access_token({"sub": username})
            return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except SQLAlchemyError:
        logger.exception("Database error during login")
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

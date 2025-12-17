# =============================================================================
# DATABASE CONFIGURATION - SINGLE SOURCE OF TRUTH (SYNC VERSION - OPTION A)
# =============================================================================
#
# This module is the SINGLE SOURCE OF TRUTH for all database configuration
# in the HireMeBahamas application. All other database modules should import
# from this module to ensure consistent configuration across the application.
#
# ✅ OPTION A: SYNC DATABASE (CHOSEN)
# - Gunicorn uses sync workers
# - Render has limited memory
# - psycopg2 + sync SQLAlchemy = fastest + safest
# - Async DB adds complexity with no benefit here
#
# ✅ RULE: Never await a sync engine
# ✅ RULE: Never call .connect() on an async engine
#
# This configuration works on:
# - Render (Gunicorn with sync workers)
# - Railway
# - Neon
# - Vercel Postgres
# - SQLAlchemy 1.4 / 2.0
#
# DATABASE_URL FORMAT (copy-paste):
# postgresql://user:password@host:5432/database?sslmode=require
#
# ENV VARS (for Railway/Render/Vercel deployment):
# DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
# DB_POOL_RECYCLE=300
#
# Key improvements:
# 1. SYNC engine (no async/await complexity)
# 2. SSL configured via URL query string (?sslmode=require) - portable across platforms
# 3. pool_recycle=300 - prevents stale connections
# 4. pool_pre_ping=True - validates connections before use
# =============================================================================

import os
import logging
from typing import Optional
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import ArgumentError
from sqlalchemy.engine.url import make_url

# Configure logging for database connection debugging
logger = logging.getLogger(__name__)

# Placeholder value for invalid database configuration
# This allows the app to start for health checks even with invalid config
# IMPORTANT: Uses a non-routable address (not localhost) to prevent accidental connections
DB_PLACEHOLDER_URL = "postgresql://placeholder:placeholder@invalid.local:5432/placeholder"

# =============================================================================
# DATABASE URL CONFIGURATION
# =============================================================================
# Priority order:
# 1. DATABASE_URL (Standard PostgreSQL connection - REQUIRED)
# 2. Local development default (only for development, not production)
#
# NEON DATABASE FORMAT:
# DATABASE_URL=postgresql://USER:ENCODED_PASSWORD@ep-xxxxx.REGION.aws.neon.tech:5432/DB_NAME?sslmode=require
# =============================================================================

# Check if we're in production mode
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
# Also check ENV for consistency
ENV = os.getenv("ENV", "development")

# Get database URL - only DATABASE_URL is supported
DATABASE_URL = os.getenv("DATABASE_URL")

# Strip whitespace from DATABASE_URL to prevent connection errors
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip()

# =============================================================================
# PRODUCTION SAFETY: WARN IF POSTGRES NOT CONFIGURED (PRODUCTION-SAFE)
# =============================================================================
# This prevents silent SQLite usage in production while allowing app to start
# Check both ENV and ENVIRONMENT variables for consistency across the application
if (ENV == "production" or ENVIRONMENT == "production") and not DATABASE_URL:
    logger.warning(
        "DATABASE_URL is required in production. "
        "Please set DATABASE_URL environment variable with your PostgreSQL connection string. "
        "Format: postgresql://USER:PASSWORD@host:5432/DB_NAME?sslmode=require"
    )
    # Use placeholder to prevent crashes, connections will fail gracefully
    DATABASE_URL = DB_PLACEHOLDER_URL
elif not DATABASE_URL:
    # Use local development default only in development mode
    DATABASE_URL = "postgresql://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
    logger.warning("Using default local development database URL. Set DATABASE_URL for production.")
# =============================================================================

# Fix common typos in DATABASE_URL (e.g., "ostgresql" -> "postgresql")
# This handles cases where the 'p' is missing from "postgresql"
if "ostgresql" in DATABASE_URL and "postgresql" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("ostgresql", "postgresql")
    logger.info("✓ Auto-fixed DATABASE_URL typo: 'ostgresql' → 'postgresql' (update env var to fix permanently)")

# Ensure DATABASE_URL uses the correct sync driver format (psycopg2)
# Remove any async driver specifications
if "postgresql+asyncpg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)
    logger.info("Converted DATABASE_URL from asyncpg to sync psycopg2 driver format")

# Strip whitespace from database name in the URL path
# This fixes cases like postgresql://user:pass@host:5432/Vercel (with trailing space)
try:
    parsed_url = urlparse(DATABASE_URL)
    if parsed_url.path:
        # Strip leading slash and whitespace from database name
        db_name = parsed_url.path.lstrip('/').strip()
        if db_name and db_name != parsed_url.path.lstrip('/'):
            # Reconstruct URL with cleaned database name only if it was changed
            new_path = '/' + db_name
            DATABASE_URL = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                new_path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            ))
            logger.info(f"✓ Auto-stripped whitespace from database name in URL")
except Exception as e:
    # If URL parsing fails, log warning but continue with original URL
    logger.warning(f"Could not parse DATABASE_URL for database name sanitization: {e}")

# NOTE: SQLAlchemy's create_async_engine() automatically handles URL decoding for
# special characters in username/password. No manual decoding is needed here.
# For example, passwords with '@' or '%' are automatically decoded from URL-encoded form.

# Validate DATABASE_URL format - ensure all required fields are present
# Parse and validate required fields using production-safe validation
# Only validate if DATABASE_URL is actually configured (not placeholder or local dev default)
if DATABASE_URL and DATABASE_URL != DB_PLACEHOLDER_URL:
    parsed = urlparse(DATABASE_URL)
    missing_fields = []
    if not parsed.username:
        missing_fields.append("username")
    if not parsed.password:
        missing_fields.append("password")
    if not parsed.hostname:
        missing_fields.append("hostname")
    if not parsed.path or len(parsed.path) <= 1:
        # path should be /database_name, so length > 1
        missing_fields.append("path")

    if missing_fields:
        # Production-safe: log warning instead of raising exception
        # This allows the app to start for health checks and diagnostics
        logger.warning(f"Invalid DATABASE_URL: missing {', '.join(missing_fields)}")

# NOTE: SQLAlchemy's create_engine() automatically handles URL decoding for
# special characters in username/password. No manual decoding is needed here.
# For example, passwords with '@' or '%' are automatically decoded from URL-encoded form.

# Log which database URL we're using (mask password for security)
def _mask_database_url(url: str) -> str:
    """Mask the password in a database URL for logging.
    
    Args:
        url: Database connection URL
        
    Returns:
        URL with password replaced by ****
    """
    if "@" not in url:
        return url
    try:
        # Split at @ to get auth and host parts
        auth_part, host_part = url.rsplit("@", 1)
        # Split auth part at last : to get user and password
        user_part = auth_part.rsplit(":", 1)[0]
        return f"{user_part}:****@{host_part}"
    except (ValueError, IndexError):
        return url

_masked_url = _mask_database_url(DATABASE_URL)
logger.info(f"Database URL: {_masked_url}")



# =============================================================================
# CREATE SYNC ENGINE - NO ASYNC/AWAIT (OPTION A)
# =============================================================================
# ✅ SYNC ENGINE PATTERN (Gunicorn + Render + Railway)
# - No async/await complexity
# - Works with Gunicorn sync workers
# - Uses pool_pre_ping=True to validate connections before use
# - Uses pool_recycle=300 (5 min) to prevent stale connections
#
# This pattern is optimal for:
# 1. Gunicorn with sync workers (default on Render/Railway)
# 2. Limited memory environments (Render free tier)
# 3. psycopg2 driver (fastest, most stable)
# 4. pool_pre_ping=True - validates connections before use (detects dead connections)
# 5. pool_recycle=300 - recycles connections (serverless-friendly)
#
# COPY-PASTE ENV VARS FOR RAILWAY/RENDER:
# DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
# DB_POOL_RECYCLE=300
# =============================================================================

# Global engine instance
engine = None

def init_db():
    """Initialize database engine (sync, not async).
    
    ✅ SYNC PATTERN: No await needed
    ✅ Called once at startup in background task
    
    CRITICAL BEHAVIOR: Returns None if engine creation fails, allowing the
    application to start even with invalid DATABASE_URL configuration.
    This fulfills the "apps must boot without the database" requirement.
    
    Returns:
        Engine | None: Database engine instance or None if creation fails
    """
    global engine
    
    # Get DATABASE_URL from environment
    db_url = os.environ.get("DATABASE_URL")
    
    if not db_url:
        logger.warning("DATABASE_URL missing — DB disabled")
        return None
    
    try:
        # Parse and validate URL
        url = make_url(db_url)
        
        # Create sync engine with production-ready settings
        engine = create_engine(
            url,
            pool_pre_ping=True,      # Validate connections before use
            pool_recycle=300,        # Recycle every 5 minutes (serverless-friendly)
            pool_size=5,             # Minimum connections
            max_overflow=10,         # Burst capacity
        )
        
        # Bind SessionLocal to the engine now that it's initialized
        SessionLocal.configure(bind=engine)
        
        logger.info("Database engine initialized (sync)")
        return engine
        
    except Exception as e:
        logger.warning(f"DB init skipped: {e}")
        return None


def get_engine():
    """Get the database engine instance.
    
    Returns:
        Engine | None: Database engine instance or None if not initialized
    """
    return engine

# Log database configuration
logger.info("Database module loaded (sync mode - Option A)")

# Create declarative base for ORM models
Base = declarative_base()


def warmup_db(engine_param):
    """Warm up database connection (sync, not async).
    
    ✅ SYNC PATTERN: No await needed
    
    Args:
        engine_param: Database engine instance
    """
    try:
        with engine_param.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database warmup successful")
    except Exception as e:
        logger.warning(f"Database warmup failed: {e}")


# =============================================================================
# SESSION FACTORY - For dependency injection in FastAPI endpoints
# =============================================================================
# Note: Even though we're using a sync engine, FastAPI endpoints are still async.
# We use a regular sessionmaker and yield sessions in async endpoint dependencies.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=None  # Will be bound when engine is initialized
)


def get_db():
    """Get database session for dependency injection.
    
    ✅ SYNC PATTERN: Returns a generator (not async generator)
    
    Usage in FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    
    Yields:
        Session: Database session for query execution
    """
    # If engine is not initialized, this will fail gracefully
    if engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    # Create session using SessionLocal factory (already bound to engine via configure())
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================================================================
# EXPORTS - Minimal sync API
# =============================================================================

__all__ = [
    "init_db",
    "warmup_db",
    "get_engine",
    "get_db",
    "Base",
]

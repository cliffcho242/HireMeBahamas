# =============================================================================
# DATABASE ENGINE CONFIGURATION - NUCLEAR 2025-PROOF FIX
# =============================================================================
# FINAL DATABASE_URL FORMAT (copy-paste to Railway/Render):
#
# Private Networking (recommended - no egress costs):
#   postgresql://user:pass@postgres.railway.internal:5432/railway?connect_timeout=10&options=-c%20jit%3Doff
#
# Public URL (fallback):
#   postgresql://user:pass@host.railway.app:port/railway?sslmode=require&connect_timeout=10&options=-c%20jit%3Doff
#
# CRITICAL PARAMETERS:
#   - connect_timeout=10: Fail fast on connection issues (not 30s+ defaults)
#   - jit=off: Prevents 60-180s JIT compilation delays on first query
#   - sslmode=require: Required for public connections (optional for private)
# =============================================================================

import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# =============================================================================
# DATABASE URL CONFIGURATION
# =============================================================================
# Priority: DATABASE_PRIVATE_URL > DATABASE_URL > default
# Private networking eliminates egress costs and reduces latency by ~50ms
_raw_url = os.getenv("DATABASE_PRIVATE_URL") or os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
)


def _normalize_database_url(url: str) -> str:
    """
    Normalize DATABASE_URL for asyncpg with nuclear timeout settings.
    
    Ensures:
    - postgresql+asyncpg:// driver prefix
    - connect_timeout=10 (fail fast, not Railway's 30s default)
    - jit=off in options (prevents 60-180s first-query delays)
    """
    # Convert sync driver to async driver
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Parse URL to inject/override query parameters
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    # Ensure connect_timeout is set (fail fast, not 30s default)
    if "connect_timeout" not in params:
        params["connect_timeout"] = [str(CONNECT_TIMEOUT)]
    
    # Ensure jit=off is in options (CRITICAL for cold start performance)
    # Check for exact "jit=" pattern to avoid matching "jitter" or similar
    existing_options = params.get("options", [""])[0]
    if "jit=" not in existing_options and " jit " not in existing_options:
        if existing_options:
            params["options"] = [f"{existing_options} -c jit=off"]
        else:
            params["options"] = ["-c jit=off"]
    
    # Rebuild URL with new query string
    new_query = urlencode(params, doseq=True)
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    
    return normalized


DATABASE_URL = _normalize_database_url(_raw_url)

# =============================================================================
# POOL CONFIGURATION - Optimized for 512MB-1GB RAM
# =============================================================================
# Railway/Render free tier: 512MB RAM, 1 shared vCPU
# Standard tier: 1GB RAM, 1 dedicated vCPU
#
# Conservative settings prevent OOM and connection exhaustion:
POOL_SIZE = 2           # Keep 2 connections warm (minimum for failover)
MAX_OVERFLOW = 3        # Allow 3 burst connections (total max = 5)
POOL_RECYCLE = 180      # Recycle connections every 3 min (Railway drops idle)
POOL_TIMEOUT = 10       # Wait max 10s for connection (fail fast)
CONNECT_TIMEOUT = 10    # Connection establishment timeout
COMMAND_TIMEOUT = 30    # Query execution timeout (generous for complex queries)

# =============================================================================
# SSL CONFIGURATION - Detect private vs public networking
# =============================================================================
# Private networking (*.railway.internal) doesn't require SSL
# Public networking (*.railway.app) requires sslmode=require
_is_private_network = ".railway.internal" in DATABASE_URL or "localhost" in DATABASE_URL
_ssl_mode = None if _is_private_network else "require"

# =============================================================================
# CREATE ASYNC ENGINE - Nuclear 2025-Proof Configuration
# =============================================================================
engine = create_async_engine(
    DATABASE_URL,
    # Pool settings optimized for low-RAM containers
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_pre_ping=True,         # Validate connections before use (prevents stale errors)
    pool_recycle=POOL_RECYCLE,  # Recycle connections every 3 min
    pool_timeout=POOL_TIMEOUT,  # Fail fast if pool exhausted
    
    # Connection arguments for asyncpg
    connect_args={
        "timeout": CONNECT_TIMEOUT,         # Connection establishment timeout
        "command_timeout": COMMAND_TIMEOUT,  # Query execution timeout
        "server_settings": {
            "jit": "off",                    # CRITICAL: Disable JIT compilation
            "statement_timeout": "30000",    # 30s query timeout (milliseconds)
            "idle_in_transaction_session_timeout": "60000",  # 60s idle transaction timeout
        },
        # SSL only for public networking
        **({"ssl": _ssl_mode} if _ssl_mode else {}),
    },
    
    # Echo SQL for debugging (disable in production)
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

# Create session factory with optimized settings
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,  # Don't expire objects after commit (reduces DB round-trips)
    autoflush=False,  # Manual flush for better performance control
)

# Create declarative base
Base = declarative_base()


# Dependency to get database session
async def get_db():
    """Get database session with automatic cleanup."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Alternative session creation
async_session = AsyncSessionLocal


# Dependency to get async database session
async def get_async_session():
    """Get async database session (alias for get_db)."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Database utility functions
async def init_db():
    """Initialize database tables"""
    # Import models to ensure they are registered with Base.metadata
    from app import models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()


async def get_pool_status() -> dict:
    """
    Get connection pool status for monitoring.
    
    Returns:
        Dictionary with pool metrics
    """
    pool = engine.pool
    return {
        "pool_size": pool.size() if hasattr(pool, 'size') else POOL_SIZE,
        "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else 0,
        "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else 0,
        "overflow": pool.overflow() if hasattr(pool, 'overflow') else 0,
        "invalid": pool.invalidatedcount() if hasattr(pool, 'invalidatedcount') else 0,
        "max_overflow": MAX_OVERFLOW,
    }

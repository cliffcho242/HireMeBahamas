# =============================================================================
# DATABASE ENGINE CONFIGURATION - MASTER PLAYBOOK COMPLIANT (Dec 2025)
# =============================================================================
# Stack: FastAPI + Gunicorn + Render + Neon Postgres (POOLED)
# 
# ABSOLUTE LAWS (NEVER BREAK):
# ❌ NEVER pass sslmode as a kwarg in connect_args
# ❌ NEVER use statement_timeout at startup (incompatible with PgBouncer)
# ❌ NEVER touch DB in /health endpoint
# ❌ NEVER use Base.metadata.create_all() in prod
# ❌ NEVER use more than 1 Gunicorn worker
# ❌ NEVER have hardcoded ports
#
# ✅ ALWAYS include sslmode in DATABASE_URL: ?sslmode=require
# ✅ ALWAYS use Neon pooled URL (asyncpg driver)
# ✅ ALWAYS use non-blocking DB boot
# ✅ ALWAYS lazy initialize engine
#
# ✅ CORRECT ENGINE CONFIG:
# engine = create_engine(
#     DATABASE_URL,  # includes ?sslmode=require
#     pool_pre_ping=True,
#     pool_size=5,
#     max_overflow=10,
# )
# =============================================================================

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url

logger = logging.getLogger(__name__)

# Global engine instance (initialized lazily)
engine = None


def init_engine():
    """Initialize database engine (NEON SAFE)
    
    Returns None if DATABASE_URL is missing or invalid.
    Application will start but database operations will fail.
    
    NOTE: This is a simplified template. Production code in database.py
    includes additional sslmode handling for asyncpg compatibility.
    """
    global engine
    
    raw = os.getenv("DATABASE_URL")
    
    if not raw:
        logger.warning("DATABASE_URL missing — DB disabled")
        return None
    
    # CRITICAL: Reject forbidden database startup options
    if "options=" in raw.lower():
        raise RuntimeError("FATAL: Forbidden DB options detected (options parameter)")
    
    try:
        engine = create_engine(
            make_url(raw),
            pool_size=5,
            max_overflow=5,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        logger.info("✅ Database engine initialized (Neon-safe, no startup options)")
        return engine
    except Exception as e:
        logger.warning(f"DB init failed: {e}")
        return None


def warmup(engine):
    """Non-blocking warmup - fails gracefully
    
    Tests connection but doesn't crash if it fails.
    """
    if not engine:
        return
    
    try:
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
        logger.info("✅ Database warmup successful")
    except Exception as e:
        logger.warning(f"DB warmup failed (safe): {e}")

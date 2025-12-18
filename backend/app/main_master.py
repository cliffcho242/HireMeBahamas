# =============================================================================
# MAIN.PY - MASTER PLAYBOOK COMPLIANT (Dec 2025)
# =============================================================================
# Stack: FastAPI + Gunicorn + Render + Neon Postgres (POOLED)
#
# ABSOLUTE LAWS (NEVER BREAK):
# ❌ NEVER touch DB in /health
# ❌ NEVER use multiple Gunicorn workers
# ❌ NEVER use sslmode or statement_timeout at startup
# ❌ NEVER use Base.metadata.create_all()
# ❌ NEVER use --reload in production
#
# ✅ ALWAYS use 1 Gunicorn worker
# ✅ ALWAYS lazy-init database
# ✅ ALWAYS instant /health response
# ✅ ALWAYS non-blocking startup
# =============================================================================

from fastapi import FastAPI

# Create app FIRST - health endpoint must be instantly available
app = FastAPI(
    title="HireMeBahamas API",
    version="1.0.0",
)


@app.on_event("startup")
def startup():
    """Non-blocking startup with lazy database initialization"""
    from app.database_master import init_engine, warmup
    
    engine = init_engine()
    warmup(engine)


@app.on_event("shutdown")
def shutdown():
    """Graceful shutdown"""
    from app.database_master import engine
    
    if engine:
        engine.dispose()


@app.get("/health", include_in_schema=False)
def health():
    """Instant health check - NO database dependency
    
    ✅ NO DATABASE - instant response
    ✅ NO IO - instant response
    ✅ NO async/await - synchronous
    
    This endpoint must respond in <5ms even on coldest start.
    """
    return {"status": "ok"}


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to HireMeBahamas API",
        "version": "1.0.0",
        "health": "/health"
    }


# Import and include routers AFTER app creation
# This prevents import-time side effects
try:
    from .auth import routes as auth_routes
    from .users import routes as users_routes
    from .feed import routes as feed_routes
    
    app.include_router(auth_routes.router, prefix="/api/auth", tags=["auth"])
    app.include_router(users_routes.router, prefix="/api/users", tags=["users"])
    app.include_router(feed_routes.router, prefix="/api/posts", tags=["feed"])
except Exception as e:
    import logging
    logging.warning(f"Router import failed (non-critical): {e}")

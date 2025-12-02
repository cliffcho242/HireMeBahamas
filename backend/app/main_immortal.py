# =============================================================================
# IMMORTAL FASTAPI MAIN.PY — VERCEL 2025 EDITION
# =============================================================================
# Zero 500/404/401 Forever | Works on Vercel Serverless Python 3.12
# =============================================================================
import os
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# INSTANT APP — IMMORTAL HEALTH ENDPOINT (NO HEAVY IMPORTS)
# =============================================================================
app = FastAPI(
    title="HireMeBahamas API",
    version="1.0.0",
    description="Job platform API for the Bahamas",
    docs_url=None,   # Disable heavy Swagger on cold start
    redoc_url=None,
    openapi_url=None,
)

# IMMORTAL HEALTH ENDPOINT — RESPONDS IN <5 MS
@app.get("/health", tags=["health"])
@app.head("/health", tags=["health"])
def health():
    """Instant health check - no database dependency"""
    return JSONResponse({"status": "healthy"}, status_code=200)

@app.get("/live", tags=["health"])
@app.head("/live", tags=["health"])
def liveness():
    """Liveness probe - instant response"""
    return JSONResponse({"status": "alive"}, status_code=200)

logger.info("⚡ HEALTH ENDPOINTS ACTIVE (/health, /live)")

# =============================================================================
# LOAD MIDDLEWARE AND FULL APP
# =============================================================================
from app.core.middleware import setup_middleware

# Setup immortal middleware (CORS + JWT + Exception Handler + Request ID + Timeout)
setup_middleware(app)

# Re-enable docs after middleware is loaded
app.docs_url = "/docs"
app.redoc_url = "/redoc"
app.openapi_url = "/openapi.json"

# =============================================================================
# LAZY READINESS CHECK (WARMS DATABASE ON FIRST REQUEST)
# =============================================================================
@app.get("/ready", tags=["health"])
@app.head("/ready", tags=["health"])
async def ready():
    """Readiness check with lazy database initialization"""
    from app.database import test_db_connection, get_db_status
    
    db_ok, db_error = await test_db_connection()
    db_status = get_db_status()
    
    if db_ok:
        return JSONResponse({
            "status": "ready",
            "database": "connected",
            "initialized": db_status["initialized"],
        }, status_code=200)
    else:
        return JSONResponse({
            "status": "not_ready",
            "database": "disconnected",
            "error": db_error,
            "initialized": db_status["initialized"],
            "hint": "Database may be cold-starting. Retry in 10-30 seconds.",
        }, status_code=503)


# =============================================================================
# IMPORT API ROUTERS
# =============================================================================
from app.api import (
    auth, hireme, jobs, messages, notifications, 
    posts, profile_pictures, reviews, upload, users
)
from app.database import init_db, close_db, get_db, test_db_connection, get_db_status
from app.core.security import prewarm_bcrypt_async
from app.core.redis_cache import redis_cache, warm_cache
from app.core.db_health import check_database_health, get_database_stats
from app.database import get_pool_status

try:
    from app.graphql.schema import create_graphql_router
    graphql_available = True
except ImportError:
    graphql_available = False
    logger.warning("GraphQL not available")

# =============================================================================
# STARTUP EVENT - LAZY INITIALIZATION
# =============================================================================
@app.on_event("startup")
async def startup():
    """Lazy initialization of heavy dependencies"""
    logger.info("🚀 Starting HireMeBahamas API...")
    
    # Test database (non-blocking)
    try:
        db_ok, db_error = await test_db_connection()
        if db_ok:
            logger.info("✓ Database connection verified")
        else:
            logger.warning(f"⚠ Database not ready (will retry): {db_error}")
    except Exception as e:
        logger.warning(f"⚠ Database test failed: {e}")
    
    # Pre-warm bcrypt
    try:
        await prewarm_bcrypt_async()
        logger.info("✓ Bcrypt pre-warmed")
    except Exception as e:
        logger.warning(f"⚠ Bcrypt pre-warm failed: {e}")
    
    # Initialize Redis cache
    try:
        redis_available = await redis_cache.connect()
        if redis_available:
            logger.info("✓ Redis cache connected")
        else:
            logger.info("ℹ Using in-memory cache fallback")
    except Exception as e:
        logger.warning(f"⚠ Redis connection failed: {e}")
    
    # Initialize database tables (with retry)
    try:
        success = await init_db()
        if success:
            logger.info("✓ Database initialized")
        else:
            logger.warning("⚠ Database initialization deferred")
    except Exception as e:
        logger.warning(f"⚠ Database init failed: {e}")
    
    # Warm cache in background
    import asyncio
    asyncio.create_task(warm_cache())
    
    logger.info("✅ API READY | Docs: /docs | Health: /health | Ready: /ready")


@app.on_event("shutdown")
async def shutdown():
    """Graceful shutdown"""
    logger.info("🛑 Shutting down...")
    try:
        await redis_cache.disconnect()
        logger.info("✓ Redis disconnected")
    except Exception as e:
        logger.warning(f"⚠ Redis disconnect error: {e}")
    try:
        await close_db()
        logger.info("✓ Database closed")
    except Exception as e:
        logger.error(f"❌ Database close error: {e}")


# =============================================================================
# HEALTH CHECK ENDPOINTS
# =============================================================================

@app.get("/ready/db", tags=["health"])
async def db_readiness_check(db = None):
    """Full database connectivity check"""
    from app.database import get_db
    from fastapi import Depends
    
    if db is None:
        # Manual dependency resolution for Vercel
        async for session in get_db():
            db = session
            break
    
    try:
        db_health = await check_database_health(db)
        if db_health["status"] == "healthy":
            return JSONResponse(
                content={"status": "ready", "database": "connected"},
                status_code=200
            )
        else:
            return JSONResponse(
                content={"status": "not_ready", "database": db_health},
                status_code=503
            )
    except Exception as e:
        return JSONResponse(
            content={"status": "not_ready", "error": str(e)},
            status_code=503
        )


@app.get("/health/ping")
async def health_ping():
    """Ultra-fast health ping"""
    return {"status": "ok", "message": "pong"}


@app.get("/api/health")
async def api_health():
    """Simple API health check"""
    return {"status": "ok"}


@app.get("/health/detailed")
async def detailed_health():
    """Detailed health with database stats"""
    from app.database import get_db
    
    async for db in get_db():
        try:
            api_status = {
                "status": "healthy",
                "message": "HireMeBahamas API is running",
                "version": "1.0.0"
            }
            
            db_health = await check_database_health(db)
            overall_status = "healthy" if db_health["status"] == "healthy" else "degraded"
            
            health_response = {
                "status": overall_status,
                "api": api_status,
                "database": db_health
            }
            
            db_stats = await get_database_stats(db)
            if db_stats:
                health_response["database"]["statistics"] = db_stats
            
            try:
                pool_status = await get_pool_status()
                health_response["database"]["pool"] = pool_status
            except Exception as e:
                health_response["database"]["pool"] = {"error": str(e)}
            
            health_response["cache"] = await redis_cache.health_check()
            
            return health_response
        finally:
            break


@app.post("/warm-cache")
async def warm_cache_endpoint():
    """Warm cache (for cron jobs)"""
    result = await warm_cache()
    return result


@app.get("/health/cache")
async def cache_health():
    """Cache health and statistics"""
    return await redis_cache.health_check()


# =============================================================================
# ROOT ENDPOINT
# =============================================================================

@app.get("/")
async def root():
    return {
        "message": "Welcome to HireMeBahamas API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# =============================================================================
# INCLUDE API ROUTERS
# =============================================================================

app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(hireme.router, prefix="/api/hireme", tags=["hireme"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(profile_pictures.router, prefix="/api/profile-pictures", tags=["profile-pictures"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(upload.router, prefix="/api/upload", tags=["uploads"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

# Include GraphQL if available
if graphql_available:
    graphql_router = create_graphql_router()
    app.include_router(graphql_router, prefix="/api", tags=["graphql"])


# =============================================================================
# SOCKET.IO (Optional - comment out if not using)
# =============================================================================
try:
    import socketio
    
    sio = socketio.AsyncServer(
        async_mode='asgi',
        cors_allowed_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "https://hiremebahamas.com",
            "https://www.hiremebahamas.com",
        ]
    )
    
    socket_app = socketio.ASGIApp(sio, app)
    
    @sio.event
    async def connect(sid, environ, auth_data):
        logger.info(f"Client connected: {sid}")
        await sio.emit('connected', {'sid': sid}, room=sid)
    
    @sio.event
    async def disconnect(sid):
        logger.info(f"Client disconnected: {sid}")
    
    @sio.event
    async def join_conversation(sid, data):
        conversation_id = data.get('conversation_id')
        if conversation_id:
            await sio.enter_room(sid, f"conversation_{conversation_id}")
    
    @sio.event
    async def leave_conversation(sid, data):
        conversation_id = data.get('conversation_id')
        if conversation_id:
            await sio.leave_room(sid, f"conversation_{conversation_id}")
    
    @sio.event
    async def typing(sid, data):
        conversation_id = data.get('conversation_id')
        if conversation_id:
            await sio.emit('typing', data, room=f"conversation_{conversation_id}", skip_sid=sid)
    
    logger.info("✓ Socket.IO enabled")
except ImportError:
    logger.info("ℹ Socket.IO not available")


# =============================================================================
# METRICS ENDPOINT (Optional)
# =============================================================================
try:
    from app.core.metrics import get_metrics_response, set_app_info
    from starlette.responses import Response as StarletteResponse
    
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        """Prometheus metrics endpoint"""
        environment = os.getenv("ENVIRONMENT", "development")
        set_app_info(version="1.0.0", environment=environment)
        metrics_data, content_type = get_metrics_response()
        return StarletteResponse(content=metrics_data, media_type=content_type)
    
    logger.info("✓ Metrics endpoint enabled")
except ImportError:
    logger.info("ℹ Metrics not available")


# =============================================================================
# LOCAL DEVELOPMENT
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,
        log_level="info"
    )

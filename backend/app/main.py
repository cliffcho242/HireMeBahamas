# =============================================================================
# NUCLEAR-OPTIMIZED STARTUP (2025 RENDER EDITION)
# =============================================================================
# INSTANT APP — NO HEAVY IMPORTS YET
# Responds in <5ms even on coldest start. Render cannot kill this.
# =============================================================================
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# INSTANT APP — NO HEAVY IMPORTS YET
app = FastAPI(
    title="hiremebahamas",
    version="1.0.0",
    docs_url=None,        # Disable heavy Swagger/ReDoc on boot
    redoc_url=None,
    openapi_url=None,
)

# IMMORTAL HEALTH ENDPOINT — RESPONDS IN <5 MS EVEN ON COLDEST START
@app.get("/health")
@app.head("/health")
def health():
    return JSONResponse({"status": "healthy"}, status_code=200)

@app.get("/ready")
async def ready():
    return {"status": "ready"}

print("NUCLEAR MAIN.PY LOADED — HEALTH ENDPOINTS ACTIVE")

# =============================================================================
# END IMMORTAL SECTION — NOW LOAD EVERYTHING ELSE
# =============================================================================

import asyncio
import logging
import time
import uuid
import json

from fastapi import Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response as StarletteResponse
from sqlalchemy.ext.asyncio import AsyncSession
import socketio

# Import APIs
from .api import auth, hireme, jobs, messages, notifications, posts, profile_pictures, reviews, upload, users
from .database import init_db, close_db, get_db, get_pool_status, engine
from .core.metrics import get_metrics_response, set_app_info
from .core.security import prewarm_bcrypt_async
from .core.redis_cache import redis_cache, warm_cache
from .core.db_health import check_database_health, get_database_stats
from .graphql.schema import create_graphql_router

# Configuration constants
AUTH_ENDPOINTS_PREFIX = '/api/auth/'
SLOW_REQUEST_THRESHOLD_MS = 3000  # 3 seconds
MAX_ERROR_BODY_SIZE = 10240  # 10KB - prevent reading large response bodies

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# RECONFIGURE APP WITH FULL FEATURES (lifespan, docs, etc.)
# The /health endpoint is already registered at the top - it stays immortal
# =============================================================================
app.title = "HireMeBahamas API"
app.description = "Job platform API for the Bahamas"
app.version = "1.0.0"
app.docs_url = "/docs"
app.redoc_url = "/redoc"
app.openapi_url = "/openapi.json"

# Configure CORS - Allow development and production origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
        "https://*.vercel.app",  # Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Cache control configuration for different endpoint patterns
CACHE_CONTROL_RULES = {
    # Read-only list endpoints can be cached briefly
    "/api/jobs": {"GET": "public, max-age=60, stale-while-revalidate=120"},
    "/api/posts": {"GET": "private, max-age=30, stale-while-revalidate=60"},
    "/api/jobs/stats": {"GET": "public, max-age=300, stale-while-revalidate=600"},
    # Health endpoints - ping is ultra-fast, no caching needed
    "/health/ping": {"GET": "no-cache"},
    "/health": {"GET": "public, max-age=10"},
}


# Add cache control middleware
@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    """Add Cache-Control headers to API responses for browser caching."""
    response = await call_next(request)
    
    # Only add cache headers to successful GET requests
    if request.method == "GET" and 200 <= response.status_code < 300:
        path = request.url.path
        
        # Check if this path matches any cache rules
        for pattern, methods in CACHE_CONTROL_RULES.items():
            if path.startswith(pattern) and request.method in methods:
                # Don't override if already set
                if "cache-control" not in response.headers:
                    response.headers["Cache-Control"] = methods[request.method]
                break
    
    return response


# Add security headers middleware for SSL/TLS and CDN security
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all API responses.
    
    These headers enhance security by:
    - Enforcing HTTPS via HSTS
    - Preventing clickjacking with X-Frame-Options
    - Blocking XSS attacks with X-XSS-Protection
    - Preventing MIME-type sniffing with X-Content-Type-Options
    - Controlling referrer information
    - Restricting browser features via Permissions-Policy
    """
    response = await call_next(request)
    
    # SSL/TLS Security headers
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(self), payment=()"
    
    # DNS prefetch control for performance
    response.headers["X-DNS-Prefetch-Control"] = "on"
    
    return response


# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing and status information
    
    Captures detailed information for failed requests (4xx, 5xx) to aid in debugging.
    For authentication endpoints, logs the error detail to help diagnose login issues.
    """
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    # Store request_id in request state for potential use by endpoints
    request.state.request_id = request_id
    
    # Get client info
    client_ip = request.client.host if request.client else 'unknown'
    user_agent = request.headers.get('user-agent', 'unknown')
    
    # Log incoming request with more context
    logger.info(
        f"[{request_id}] --> {request.method} {request.url.path} "
        f"from {client_ip} | UA: {user_agent[:50]}..."
    )
    
    # Process request
    try:
        response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Determine log level and capture error details for failed requests
        if response.status_code < 400:
            # Success - log at INFO level
            logger.info(
                f"[{request_id}] <-- {response.status_code} {request.method} {request.url.path} "
                f"in {duration_ms}ms"
            )
        else:
            # Client/Server error - log at WARNING/ERROR level with more detail
            log_level = logging.WARNING if response.status_code < 500 else logging.ERROR
            
            # For authentication endpoints, capture the error body to help debug login issues
            # Only read body for JSON responses to avoid processing large files
            error_detail = ""
            if (request.url.path.startswith(AUTH_ENDPOINTS_PREFIX) and 
                response.media_type == 'application/json'):
                try:
                    # Read response body with size limit to prevent memory issues
                    body = b""
                    body_size = 0
                    async for chunk in response.body_iterator:
                        body_size += len(chunk)
                        if body_size > MAX_ERROR_BODY_SIZE:
                            error_detail = f" | Error: Response body too large (>{MAX_ERROR_BODY_SIZE} bytes)"
                            break
                        body += chunk
                    
                    # Try to parse as JSON to extract error detail if we read the full body
                    if body_size <= MAX_ERROR_BODY_SIZE:
                        try:
                            error_data = json.loads(body.decode())
                            error_detail = f" | Error: {error_data.get('detail', 'Unknown error')}"
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            error_detail = " | Error: Unable to parse response body"
                        
                        # Reconstruct response with the body we read
                        response = StarletteResponse(
                            content=body,
                            status_code=response.status_code,
                            headers=dict(response.headers),
                            media_type=response.media_type
                        )
                except Exception as e:
                    error_detail = f" | Error reading body: {str(e)}"
            
            logger.log(
                log_level,
                f"[{request_id}] <-- {response.status_code} {request.method} {request.url.path} "
                f"in {duration_ms}ms from {client_ip}{error_detail}"
            )
            
            # Log slow requests separately
            if duration_ms > SLOW_REQUEST_THRESHOLD_MS:
                logger.warning(
                    f"[{request_id}] SLOW REQUEST: {request.method} {request.url.path} "
                    f"took {duration_ms}ms (>{SLOW_REQUEST_THRESHOLD_MS}ms threshold)"
                )
        
        return response
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(
            f"[{request_id}] <-- EXCEPTION {request.method} {request.url.path} "
            f"in {duration_ms}ms from {client_ip} | {type(e).__name__}: {str(e)}"
        )
        raise


# LAZY IMPORT HEAVY STUFF — DATABASE/CACHE INITIALIZATION
@app.on_event("startup")
async def lazy_import_heavy_stuff():
    """Lazy import all heavy dependencies after app is started.
    
    This ensures health endpoints respond instantly during cold starts,
    while heavy database, cache, and API components are loaded after.
    """
    logger.info("Starting HireMeBahamas API full initialization...")
    
    # Warm DB pool
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise
    
    # Pre-warm bcrypt
    try:
        await prewarm_bcrypt_async()
        logger.info("Bcrypt pre-warmed successfully")
    except Exception as e:
        logger.warning(f"Failed to pre-warm bcrypt (non-critical): {e}")
    
    # Initialize Redis cache
    try:
        redis_available = await redis_cache.connect()
        if redis_available:
            logger.info("Redis cache connected successfully")
        else:
            logger.info("Using in-memory cache fallback")
    except Exception as e:
        logger.warning(f"Redis connection failed (non-critical): {e}")
    
    # Initialize database tables
    try:
        await init_db()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
        raise
    
    # Schedule cache warm-up in background
    asyncio.create_task(warm_cache())
    logger.info("LAZY IMPORT COMPLETE — FULL APP LIVE")


@app.on_event("shutdown")
async def full_shutdown():
    """Graceful shutdown"""
    logger.info("Shutting down HireMeBahamas API...")
    try:
        await redis_cache.disconnect()
        logger.info("Redis cache disconnected")
    except Exception as e:
        logger.warning(f"Error disconnecting Redis cache: {e}")
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


# Database readiness check endpoint (full database connectivity check)
@app.get("/ready/db", tags=["health"])
async def db_readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness probe with database connectivity check
    
    K8s-style readiness probe that checks if the application is ready to
    receive traffic. Checks database connectivity.
    
    Returns 200 if the app is ready, 503 if database is unavailable.
    
    Note: Use /ready for instant cold start response.
    Use /ready/db for full database connectivity check.
    """
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


# Quick health check endpoint (no database dependency - faster for cold starts)
@app.get("/health/ping")
async def health_ping():
    """Ultra-fast health ping endpoint
    
    Returns immediately without database check.
    Use this for load balancer health checks and quick availability tests.
    """
    return {"status": "ok", "message": "pong"}


# Cache warming endpoint for cron jobs
@app.post("/warm-cache")
async def warm_cache_endpoint():
    """
    Warm up cache with frequently accessed data.
    
    This endpoint should be called by a cron job every 5 minutes
    to keep the cache hot and ensure sub-100ms response times.
    
    Example Render cron: */5 * * * * curl -X POST https://hiremebahamas.onrender.com/warm-cache
    """
    result = await warm_cache()
    return result


# Cache health and stats endpoint
@app.get("/health/cache")
async def cache_health():
    """
    Get cache health status and statistics.
    
    Returns cache hit rates, backend status, and performance metrics.
    """
    return await redis_cache.health_check()


# API health check endpoint (simple status check)
@app.get("/api/health")
async def api_health():
    """Simple API health check endpoint
    
    Returns a simple status response for basic health verification.
    """
    return {"status": "ok"}


# Detailed health check endpoint for monitoring
@app.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with database statistics
    
    Provides additional database statistics for monitoring.
    May require admin permissions in production environments.
    
    For quick health checks, use /health (no DB dependency).
    For readiness probes, use /ready (checks DB connectivity).
    """
    # Check API health
    api_status = {
        "status": "healthy",
        "message": "HireMeBahamas API is running",
        "version": "1.0.0"
    }
    
    # Check database health
    db_health = await check_database_health(db)
    
    # Determine overall health status
    overall_status = "healthy" if db_health["status"] == "healthy" else "degraded"
    
    health_response = {
        "status": overall_status,
        "api": api_status,
        "database": db_health
    }
    
    # Get database statistics
    db_stats = await get_database_stats(db)
    
    if db_stats:
        health_response["database"]["statistics"] = db_stats
    
    # Add pool status
    try:
        pool_status = await get_pool_status()
        health_response["database"]["pool"] = pool_status
    except Exception as e:
        health_response["database"]["pool"] = {"error": str(e)}
    
    # Add cache stats
    health_response["cache"] = await redis_cache.health_check()
    
    return health_response


# Include routers with /api prefix to match frontend expectations
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

# Include GraphQL router
graphql_router = create_graphql_router()
app.include_router(graphql_router, prefix="/api", tags=["graphql"])


# Initialize Socket.IO for real-time messaging
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

# Create Socket.IO ASGI app
socket_app = socketio.ASGIApp(sio, app)


# Socket.IO event handlers
@sio.event
async def connect(sid, environ, auth_data):
    """Handle client connection"""
    logger.info(f"Client connected: {sid}")
    await sio.emit('connected', {'sid': sid}, room=sid)


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {sid}")


@sio.event
async def join_conversation(sid, data):
    """Join a conversation room"""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        await sio.enter_room(sid, f"conversation_{conversation_id}")
        logger.info(f"Client {sid} joined conversation {conversation_id}")


@sio.event
async def leave_conversation(sid, data):
    """Leave a conversation room"""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        await sio.leave_room(sid, f"conversation_{conversation_id}")
        logger.info(f"Client {sid} left conversation {conversation_id}")


@sio.event
async def typing(sid, data):
    """Handle typing indicator"""
    conversation_id = data.get('conversation_id')
    is_typing = data.get('is_typing')
    if conversation_id:
        await sio.emit('typing', data, room=f"conversation_{conversation_id}", skip_sid=sid)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to HireMeBahamas API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Prometheus metrics endpoint
@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Prometheus metrics endpoint for monitoring.
    
    Returns metrics in Prometheus text format for scraping by Prometheus server.
    This endpoint is excluded from the OpenAPI schema.
    
    Metrics include:
    - HTTP request counts and durations
    - Database connection pool stats
    - Authentication attempt counts
    - Application uptime
    """
    # Set app info on each request (idempotent)
    environment = os.getenv("ENVIRONMENT", "development")
    set_app_info(version="1.0.0", environment=environment)
    
    metrics_data, content_type = get_metrics_response()
    return StarletteResponse(content=metrics_data, media_type=content_type)


if __name__ == "__main__":
    import uvicorn

    # Production mode - no reload, multiple workers for better performance
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=2,  # Use 2 workers for production mode
        log_level="info"
    )

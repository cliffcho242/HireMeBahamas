# =============================================================================
# NUCLEAR-OPTIMIZED STARTUP (2025 RENDER EDITION)
# =============================================================================
# INSTANT APP — NO HEAVY IMPORTS YET
# Responds in <5ms even on coldest start. Render cannot kill this.
# =============================================================================
import os
import sys
from typing import Optional, List, Dict, Union, Any


def inject_typing_exports(module):
    """Inject typing module exports into a module's namespace.
    
    This is required for Pydantic to properly evaluate forward references
    when modules are aliased. When Pydantic evaluates forward references,
    it looks in the module's __dict__ for type names like Optional, List, etc.
    
    Note: This function is intentionally defined locally in each entry point file
    rather than imported from a shared utility to avoid circular import issues
    and ensure it's available before any other modules are loaded.
    
    Args:
        module: The module object to inject typing exports into
    """
    module.__dict__['Optional'] = Optional
    module.__dict__['List'] = List
    module.__dict__['Dict'] = Dict
    module.__dict__['Union'] = Union
    module.__dict__['Any'] = Any


# CRITICAL: Set up module path aliases BEFORE any backend_app imports
# This allows imports like "from app.core.security" to work correctly
# when running directly (not through api/index.py)
if 'app' not in sys.modules:
    backend_app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(backend_app_dir)
    
    # Add parent directory to path so we can import backend_app
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Create comprehensive module alias: app -> backend_app
    # CRITICAL FIX: Also alias all submodules so "from app.core.X" works
    import backend_app as app_module
    sys.modules['app'] = app_module
    inject_typing_exports(app_module)
    
    # Alias core submodules explicitly
    import backend_app.core
    sys.modules['app.core'] = backend_app.core
    inject_typing_exports(backend_app.core)
    
    # Dynamically alias all core submodules to handle all "from app.core.X" imports
    _core_modules = ['security', 'upload', 'concurrent', 'metrics', 'redis_cache', 
                     'socket_manager', 'cache', 'db_health', 'timeout_middleware', 'rate_limiter']
    for _module_name in _core_modules:
        try:
            _module = __import__(f'backend_app.core.{_module_name}', fromlist=[''])
            sys.modules[f'app.core.{_module_name}'] = _module
            inject_typing_exports(_module)
        except ImportError:
            # Skip modules that might not be available (graceful degradation)
            pass
    
    # CRITICAL FIX: Alias schemas submodules to fix Pydantic forward reference resolution
    # When Pydantic evaluates forward references like "Optional[str]", it looks for
    # these types in the module's __dict__. Without this, aliased schema modules
    # (app.schemas.*) won't have typing exports available, causing PydanticUndefinedAnnotation errors.
    import backend_app.schemas
    sys.modules['app.schemas'] = backend_app.schemas
    inject_typing_exports(backend_app.schemas)
    
    # Dynamically alias all schema submodules to handle all "from app.schemas.X" imports
    _schema_modules = ['auth', 'job', 'message', 'post', 'review']
    for _module_name in _schema_modules:
        try:
            _module = __import__(f'backend_app.schemas.{_module_name}', fromlist=[''])
            sys.modules[f'app.schemas.{_module_name}'] = _module
            inject_typing_exports(_module)
        except ImportError:
            # Skip modules that might not be available (graceful degradation)
            pass
    
    # CRITICAL FIX: Alias api submodule and its children to support absolute imports
    # This enables "from app.api import X" and "from app.api.auth import Y" patterns
    import backend_app.api
    sys.modules['app.api'] = backend_app.api
    inject_typing_exports(backend_app.api)
    
    # Dynamically alias all api submodules to handle all "from app.api.X" imports
    _api_modules = ['analytics', 'auth', 'debug', 'feed', 'hireme', 'jobs', 'messages', 
                    'notifications', 'posts', 'profile_pictures', 'reviews', 'upload', 'users']
    for _module_name in _api_modules:
        try:
            _module = __import__(f'backend_app.api.{_module_name}', fromlist=[''])
            sys.modules[f'app.api.{_module_name}'] = _module
            inject_typing_exports(_module)
        except ImportError:
            # Skip modules that might not be available (graceful degradation)
            pass
    
    # CRITICAL FIX: Alias database module to support "from app.database import X"
    try:
        import backend_app.database
        sys.modules['app.database'] = backend_app.database
        inject_typing_exports(backend_app.database)
    except ImportError:
        # Database module might not be available in all environments
        pass
    
    # CRITICAL FIX: Alias graphql submodule to support "from app.graphql.X import Y"
    try:
        import backend_app.graphql
        sys.modules['app.graphql'] = backend_app.graphql
        inject_typing_exports(backend_app.graphql)
        
        # Also alias graphql.schema specifically since it's imported
        try:
            import backend_app.graphql.schema
            sys.modules['app.graphql.schema'] = backend_app.graphql.schema
            inject_typing_exports(backend_app.graphql.schema)
        except ImportError:
            pass
    except ImportError:
        # GraphQL module is optional and might not be available
        pass

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
@app.get("/health", include_in_schema=False)
@app.head("/health", include_in_schema=False)
def health():
    """Instant health check - no database dependency.
    
    This endpoint is designed to respond immediately (<5ms) even during
    the coldest start. It does NOT check database connectivity.
    
    Use /ready for database connectivity check.
    
    ✅ CRITICAL: Does NOT touch the database to ensure instant response.
    🚫 NO database queries
    🚫 NO external service calls
    🚫 NO authentication checks
    """
    return JSONResponse({"status": "ok"}, status_code=200)


# LIVENESS PROBE — Kubernetes/Render liveness check
@app.get("/live", tags=["health"])
@app.head("/live", tags=["health"])
def liveness():
    """Liveness probe - instant response, no dependencies.
    
    This endpoint confirms the application process is running and responsive.
    It does NOT check database or external services.
    
    Use this for:
    - Kubernetes livenessProbe
    - Render liveness checks
    - Load balancer health checks
    
    Returns 200 immediately (<5ms) on any successful request.
    """
    return JSONResponse({"status": "alive"}, status_code=200)


@app.get("/ready", tags=["health"])
@app.head("/ready", tags=["health"])
def ready():
    """Readiness check - instant response, no database dependency.
    
    ✅ PRODUCTION-GRADE: This endpoint NEVER touches the database.
    Returns immediately (<5ms) to confirm the application is ready to serve traffic.
    
    For database connectivity checks, use:
    - /ready/db - Full database connectivity check
    - /health/detailed - Comprehensive health check with database statistics
    
    This follows production best practices:
    - Health checks must never touch DB, APIs, or disk
    - Load balancers need instant responses
    - Prevents cascading failures during database issues
    """
    return JSONResponse({
        "status": "ready",
        "message": "Application is ready to serve traffic",
    }, status_code=200)

print("NUCLEAR MAIN.PY LOADED — HEALTH ENDPOINTS ACTIVE (/health, /live, /ready)")

# =============================================================================
# END IMMORTAL SECTION — NOW LOAD EVERYTHING ELSE
# =============================================================================

import asyncio
import logging
import time
import uuid
import json

from fastapi import Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response as StarletteResponse
from sqlalchemy.ext.asyncio import AsyncSession

# Optional Socket.IO support for real-time features
try:
    import socketio
    HAS_SOCKETIO = True
except ImportError:
    HAS_SOCKETIO = False
    socketio = None
    # Logger not available yet, will log later

# Import APIs
from app.api import analytics, auth, debug, feed, hireme, jobs, messages, notifications, posts, profile_pictures, reviews, upload, users
from app.database import init_db, close_db, get_db, get_pool_status, engine, test_db_connection, get_db_status
from app.core.metrics import get_metrics_response, set_app_info
from app.core.security import prewarm_bcrypt_async
from app.core.redis_cache import redis_cache, warm_cache
from app.core.db_health import check_database_health, get_database_stats
from app.core.timeout_middleware import add_timeout_middleware
from app.core.rate_limiter import add_rate_limiting_middleware, get_rate_limiter_stats

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

# GraphQL support (optional - gracefully degrades if strawberry not available)
# Import after logger is configured
HAS_GRAPHQL = False
_graphql_router_factory = None
try:
    from app.graphql.schema import create_graphql_router as _graphql_router_factory
    HAS_GRAPHQL = True
    logger.info("✅ GraphQL support enabled")
except ImportError:
    logger.info(f"ℹ️  GraphQL disabled (optional dependency 'strawberry-graphql' not installed)")
except Exception as e:
    logger.warning(f"⚠️  GraphQL initialization failed (non-critical): {e}")

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

# =============================================================================
# CRITICAL FIX: Request Timeout Middleware (MUST BE FIRST)
# =============================================================================
# This PERMANENTLY FIXES the 198-second login timeout that was literally
# killing the app and losing users. Enforces a 60-second hard timeout on
# all requests (except health checks) to prevent indefinite hangs.
#
# WHY THIS MUST BE FIRST:
# - Timeout must wrap ALL other middleware and request processing
# - If added after other middleware, those middlewares can still hang
# - Must be the outermost layer to enforce timeout on the entire request chain
#
# Configuration via environment variables:
# - REQUEST_TIMEOUT=60 (default: 60 seconds)
# - REQUEST_TIMEOUT_EXCLUDE_PATHS=/health,/live,/ready,/health/ping,/metrics
# =============================================================================
add_timeout_middleware(app, timeout=60)

# =============================================================================
# CRITICAL: Rate Limiting Middleware (DDoS Protection)
# =============================================================================
# Protects the database and API from abuse and DDoS attacks
# - Limits requests per IP address (default: 100 requests per 60 seconds)
# - Uses Redis for distributed rate limiting with in-memory fallback
# - Returns HTTP 429 (Too Many Requests) when limit exceeded
# - Health check endpoints are excluded from rate limiting
#
# Configuration via environment variables:
# - RATE_LIMIT_REQUESTS=100 (default: 100)
# - RATE_LIMIT_WINDOW=60 (default: 60 seconds)
# =============================================================================
add_rate_limiting_middleware(app)

# Configure CORS with credentials support for secure cookie-based authentication
# Production-grade CORS: explicit origins for cookies (required by CORS spec)
from app.core.environment import get_cors_origins
cors_origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,  # Required for HttpOnly cookies
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"],  # Allow clients to access Set-Cookie header
)

# Cache control configuration for different endpoint patterns
CACHE_CONTROL_RULES = {
    # Read-only list endpoints can be cached briefly
    "/api/jobs": {"GET": "public, max-age=60, stale-while-revalidate=120"},
    "/api/posts": {"GET": "private, max-age=30, stale-while-revalidate=60"},
    "/api/jobs/stats": {"GET": "public, max-age=300, stale-while-revalidate=600"},
    # Health endpoints with standard 30-second cache
    "/health/ping": {"GET": "public, max-age=30"},
    "/health": {"GET": "public, max-age=30"},
    "/live": {"GET": "public, max-age=30"},
    "/ready": {"GET": "public, max-age=30"},
    # Default for public GET endpoints
    "*": {"GET": "public, max-age=30"},
}


# Add cache control middleware
@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    """Add Cache-Control headers to API responses for browser caching.
    
    Implements HTTP caching with Cache-Control: public, max-age=30 for public endpoints.
    This improves performance by allowing browsers and CDNs to cache responses for 30 seconds.
    """
    response = await call_next(request)
    
    # Only add cache headers to successful GET requests
    if request.method == "GET" and 200 <= response.status_code < 300:
        path = request.url.path
        
        # Don't override if already set by endpoint
        if "cache-control" not in response.headers:
            cache_control = None
            
            # Check if this path matches any specific cache rules (excluding wildcard)
            for pattern, methods in CACHE_CONTROL_RULES.items():
                if pattern != "*" and path.startswith(pattern) and request.method in methods:
                    cache_control = methods[request.method]
                    break
            
            # Apply wildcard default if no specific pattern matched
            if cache_control is None and "*" in CACHE_CONTROL_RULES:
                if request.method in CACHE_CONTROL_RULES["*"]:
                    cache_control = CACHE_CONTROL_RULES["*"][request.method]
            
            # Apply the cache control header
            if cache_control:
                response.headers["Cache-Control"] = cache_control
    
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


# =============================================================================
# STRICT LAZY INITIALIZATION - NO DATABASE CONNECTIONS AT STARTUP
# =============================================================================
@app.on_event("startup")
async def lazy_import_heavy_stuff():
    """Lazy import all heavy dependencies after app is started.
    
    This ensures health endpoints respond instantly during cold starts,
    while heavy database, cache, and API components are loaded after.
    
    ✅ STRICT LAZY PATTERN (per requirements):
    - 🚫 NO warm-up pings at startup
    - 🚫 NO background keepalive loops
    - 🚫 NO engine.connect() at import time
    - ✅ Database engine created lazily on first actual request
    - ✅ TCP + SSL with pool_pre_ping=True and pool_recycle=300
    
    This prevents ALL database connections until first actual database request.
    """
    logger.info("Starting HireMeBahamas API initialization (NO database connections)...")
    
    # ==========================================================================
    # STEP 1: Pre-warm bcrypt (non-blocking, no database)
    # ==========================================================================
    try:
        await prewarm_bcrypt_async()
        logger.info("Bcrypt pre-warmed successfully")
    except Exception as e:
        # Pre-warming is optional - if it fails, authentication will still work
        # but the first login may be slightly slower
        logger.warning(f"Bcrypt pre-warm skipped (non-critical): {type(e).__name__}")
    
    # ==========================================================================
    # STEP 2: Initialize Redis cache (non-blocking, no database)
    # ==========================================================================
    try:
        redis_available = await redis_cache.connect()
        if redis_available:
            logger.info("Redis cache connected successfully")
        else:
            logger.info("Using in-memory cache fallback")
    except Exception as e:
        logger.warning(f"Redis connection failed (non-critical): {e}")
    
    # ==========================================================================
    # STRICT LAZY INITIALIZATION: NO DATABASE OPERATIONS AT STARTUP
    # ==========================================================================
    # ✅ Database engine is created lazily by LazyEngine wrapper
    # ✅ First connection happens on first actual database request
    # ✅ No test_db_connection() at startup (removed)
    # ✅ No init_db() at startup (removed)
    # ✅ No warm_cache() background task (removed)
    #
    # Database initialization (creating tables) will happen automatically
    # when first endpoint requiring database access is called.
    # This is handled by the lazy engine wrapper and get_db() dependency.
    
    logger.info("LAZY IMPORT COMPLETE — FULL APP LIVE (DB connects on first request)")
    logger.info("Health:   GET /health (instant)")
    logger.info("Liveness: GET /live (instant)")
    logger.info("Ready:    GET /ready (instant)")
    logger.info("Ready:    GET /ready/db (with DB check)")
    logger.info("")
    logger.info("✅ STRICT LAZY PATTERN ACTIVE:")
    logger.info("   - NO database connections at startup")
    logger.info("   - NO warm-up pings")
    logger.info("   - NO background keepalive loops")
    logger.info("   - Database connects on first actual request only")


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


# =============================================================================
# GLOBAL EXCEPTION HANDLER - Catch all unhandled exceptions
# =============================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to catch unhandled exceptions.
    
    This prevents FastAPI from returning generic 500 errors and provides
    meaningful error messages for debugging.
    
    Args:
        request: The incoming request
        exc: The unhandled exception
        
    Returns:
        JSON response with error details
    """
    import traceback
    
    # Get request ID if available
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Log the full exception with traceback
    logger.error(
        f"[{request_id}] Unhandled exception in {request.method} {request.url.path}: "
        f"{type(exc).__name__}: {str(exc)}"
    )
    logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
    
    # Return a user-friendly error response
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please try again later.",
            "error_type": type(exc).__name__,
            "request_id": request_id,
        }
    )


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
def health_ping():
    """Ultra-fast health ping endpoint
    
    ✅ PRODUCTION-GRADE: Database-free, instant response.
    Returns immediately without database check.
    Use this for load balancer health checks and quick availability tests.
    
    ❌ No DB access
    ❌ No external calls
    ❌ No disk access
    Target latency: < 30ms
    """
    return {"status": "ok"}


# Cache warming endpoint for cron jobs
@app.post("/warm-cache")
async def warm_cache_endpoint():
    """
    Warm up cache with frequently accessed data.
    
    This endpoint should be called by a cron job every 5 minutes
    to keep the cache hot and ensure sub-100ms response times.
    
    Example cron job: */5 * * * * curl -X POST https://your-backend-url/warm-cache
    
    For Railway: Use GitHub Actions workflow (scheduled-ping.yml)
    For Vercel: Add to vercel.json cron configuration
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
    
    # Add rate limiter stats
    health_response["rate_limiter"] = get_rate_limiter_stats()
    
    return health_response


# Include routers with /api prefix to match frontend expectations
# Note: auth.router already has prefix="/api/auth" and tags defined in the router itself
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(auth.router)  # Router prefix and tags defined in auth.py
app.include_router(debug.router, prefix="/api/debug", tags=["debug"])
app.include_router(feed.router, prefix="/api/feed", tags=["feed"])
app.include_router(hireme.router, prefix="/api/hireme", tags=["hireme"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(profile_pictures.router, prefix="/api/profile-pictures", tags=["profile-pictures"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(upload.router, prefix="/api/upload", tags=["uploads"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

# Include GraphQL router (if available)
if HAS_GRAPHQL:
    try:
        graphql_router = _graphql_router_factory()
        app.include_router(graphql_router, prefix="/api", tags=["graphql"])
        logger.info("✅ GraphQL router registered at /api/graphql")
    except Exception as e:
        logger.warning(f"⚠️  Failed to register GraphQL router (non-critical): {e}")
else:
    logger.info("ℹ️  GraphQL API not available (optional dependency not installed)")


# Initialize Socket.IO for real-time messaging (if available)
if HAS_SOCKETIO:
    # Allow all origins for Socket.IO to match CORS middleware configuration
    sio = socketio.AsyncServer(
        async_mode='asgi',
        cors_allowed_origins="*"
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
    
    logger.info("✅ Socket.IO initialized for real-time messaging")
else:
    sio = None
    socket_app = app
    logger.info("ℹ️  Socket.IO not available - real-time features disabled")



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
    # Use the correct module path based on whether we're in standalone mode or not
    # When running as: python -m api.backend_app.main
    # Or from Railway/Docker: uvicorn api.backend_app.main:app
    module_path = "api.backend_app.main:socket_app" if HAS_SOCKETIO else "api.backend_app.main:app"
    
    logger.info(f"Starting uvicorn with module: {module_path}")
    uvicorn.run(
        module_path,
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=2,  # Use 2 workers for production mode
        log_level="info"
    )

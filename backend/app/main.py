# =============================================================================
# NUCLEAR-OPTIMIZED STARTUP (2025 RENDER EDITION)
# =============================================================================
# INSTANT APP — NO HEAVY IMPORTS YET
# Responds in <5ms even on coldest start. Render cannot kill this.
# =============================================================================
import os
import importlib
from typing import Optional, List, Dict, Union, Any
from fastapi import FastAPI
from fastapi.responses import JSONResponse


def inject_typing_exports(module):
    """Inject typing module exports into a module's namespace.
    
    This is required for Pydantic to properly evaluate forward references.
    When Pydantic evaluates forward references, it looks in the module's 
    __dict__ for type names like Optional, List, etc.
    
    Args:
        module: The module object to inject typing exports into
    """
    module.__dict__['Optional'] = Optional
    module.__dict__['List'] = List
    module.__dict__['Dict'] = Dict
    module.__dict__['Union'] = Union
    module.__dict__['Any'] = Any

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
    """
    return {"status": "ok"}


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

from fastapi import Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response as StarletteResponse
from sqlalchemy.ext.asyncio import AsyncSession
import socketio

# CRITICAL FIX: Inject typing exports into schema modules for Pydantic forward reference resolution
# This fixes PydanticUndefinedAnnotation errors when Pydantic evaluates forward references
from . import schemas
inject_typing_exports(schemas)

# Inject typing exports into all schema submodules
_schema_modules = ['auth', 'job', 'message', 'post', 'review']
for _module_name in _schema_modules:
    try:
        _module = importlib.import_module(f'.schemas.{_module_name}', package='app')
        inject_typing_exports(_module)
    except ImportError:
        # Skip modules that might not be available (graceful degradation)
        pass

# Import APIs (with nuclear safety net)
try:
    from .api import auth, hireme, jobs, messages, notifications, posts, profile_pictures, reviews, upload, users
    print("✅ API routers imported successfully")
except Exception as e:
    print(f"API router import failed: {e}")
    auth = hireme = jobs = messages = notifications = None
    posts = profile_pictures = reviews = upload = users = None

try:
    from .database import init_db, close_db, get_db, get_pool_status, engine, test_db_connection, get_db_status
    print("✅ Database functions imported successfully")
except Exception as e:
    print(f"DB import failed: {e}")
    init_db = close_db = get_db = get_pool_status = engine = test_db_connection = get_db_status = None

try:
    from .core.metrics import get_metrics_response, set_app_info
    print("✅ Metrics module imported successfully")
except Exception as e:
    print(f"Metrics import failed: {e}")
    get_metrics_response = set_app_info = None

try:
    from .core.security import prewarm_bcrypt_async
    print("✅ Security module imported successfully")
except Exception as e:
    print(f"Security import failed: {e}")
    prewarm_bcrypt_async = None

try:
    from .core.redis_cache import redis_cache, warm_cache
    print("✅ Redis cache (legacy) imported successfully")
except Exception as e:
    print(f"Redis cache (legacy) not available: {e}")
    redis_cache = warm_cache = None
    # Note: Using new cache system from app.core.cache instead

try:
    from .core.db_health import check_database_health, get_database_stats
    print("✅ DB health module imported successfully")
except Exception as e:
    print(f"DB health import failed: {e}")
    check_database_health = get_database_stats = None

# Configuration constants
AUTH_ENDPOINTS_PREFIX = '/api/auth/'
SLOW_REQUEST_THRESHOLD_MS = 3000  # 3 seconds
MAX_ERROR_BODY_SIZE = 10240  # 10KB - prevent reading large response bodies

# Configure logging with more detail
# Check if runtime logs directory exists (e.g., in CI/test environment)
runtime_log_dir = os.getenv('RUNTIME_LOG_DIR', '/tmp/runtime-logs')
log_handlers = [logging.StreamHandler()]

if os.path.exists(runtime_log_dir):
    # Add file handler for runtime logs when directory exists
    runtime_log_file = os.path.join(runtime_log_dir, 'backend-runtime.log')
    try:
        file_handler = logging.FileHandler(runtime_log_file, mode='a')
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        log_handlers.append(file_handler)
        print(f"Runtime logs will be written to: {runtime_log_file}")
    except Exception as e:
        print(f"Warning: Could not create runtime log file: {e}")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=log_handlers
)
logger = logging.getLogger(__name__)

# GraphQL support (optional - gracefully degrades if strawberry not available)
# Import after logger is configured
HAS_GRAPHQL = False
_graphql_router_factory = None
try:
    from .graphql.schema import create_graphql_router as _graphql_router_factory
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

# Configure CORS - Allow development and production origins
# Import environment utilities for consistent production checks
try:
    from .core.environment import get_cors_origins
    _allowed_origins = get_cors_origins()  # Excludes localhost in production
except ImportError:
    # Fallback to manual configuration if import fails
    import os
    _is_prod = os.getenv("ENVIRONMENT", "").lower() == "production" or os.getenv("VERCEL_ENV", "").lower() == "production"
    _allowed_origins = [
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
        "https://*.vercel.app",
    ]
    # ❌ ABSOLUTE BAN: Never allow localhost in production
    if not _is_prod:
        _allowed_origins.extend([
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",  # Vite default
            "http://127.0.0.1:5173",
        ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
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
    
    ENHANCED: Special logging for /api/auth/* to diagnose login issues.
    """
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    # Store request_id in request state for potential use by endpoints
    request.state.request_id = request_id
    
    # Get client info
    client_ip = request.client.host if request.client else 'unknown'
    user_agent = request.headers.get('user-agent', 'unknown')
    
    # Check if this is an auth endpoint
    is_auth_endpoint = request.url.path.startswith(AUTH_ENDPOINTS_PREFIX)
    
    # Enhanced logging for auth endpoints
    if is_auth_endpoint:
        logger.info(
            f"[{request_id}] ============ AUTH REQUEST START ============\n"
            f"  Method: {request.method}\n"
            f"  Path: {request.url.path}\n"
            f"  Client IP: {client_ip}\n"
            f"  User-Agent: {user_agent[:100]}\n"
            f"  Content-Type: {request.headers.get('content-type', 'none')}\n"
            f"  Has Authorization: {bool(request.headers.get('authorization'))}\n"
            f"  Origin: {request.headers.get('origin', 'none')}\n"
            f"  Referer: {request.headers.get('referer', 'none')}"
        )
    else:
        # Log incoming request with more context
        logger.info(
            f"[{request_id}] --> {request.method} {request.url.path} "
            f"from {client_ip} | UA: {user_agent[:50]}..."
        )
    
    # Process request
    try:
        response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Track performance metrics
        try:
            from .core.monitoring import track_request_time
            track_request_time(request.url.path, duration_ms, response.status_code)
        except Exception:
            pass  # Monitoring is non-critical
        
        # Determine log level and capture error details for failed requests
        if response.status_code < 400:
            # Success - log at INFO level
            if is_auth_endpoint:
                logger.info(
                    f"[{request_id}] ============ AUTH REQUEST SUCCESS ============\n"
                    f"  Status: {response.status_code}\n"
                    f"  Path: {request.url.path}\n"
                    f"  Duration: {duration_ms}ms\n"
                    f"  Client IP: {client_ip}\n"
                    f"  Result: LOGIN SUCCESSFUL"
                )
            else:
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
                            
                            # Enhanced logging for auth failures - SANITIZED
                            # Only log non-sensitive error info, never passwords or tokens
                            safe_error_data = {
                                'detail': error_data.get('detail', 'Unknown error'),
                                'status': response.status_code,
                            }
                            
                            logger.error(
                                f"[{request_id}] ============ AUTH REQUEST FAILED ============\n"
                                f"  Status: {response.status_code}\n"
                                f"  Path: {request.url.path}\n"
                                f"  Duration: {duration_ms}ms\n"
                                f"  Client IP: {client_ip}\n"
                                f"  Error Detail: {safe_error_data['detail']}\n"
                                f"  Note: Sensitive data (passwords, tokens) not logged for security"
                            )
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
            
            if not is_auth_endpoint or not error_detail:
                # Only log here if we didn't already log enhanced auth error above
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
        if prewarm_bcrypt_async is not None:
            await prewarm_bcrypt_async()
            logger.info("Bcrypt pre-warmed successfully")
        else:
            logger.warning("Bcrypt pre-warm function not available")
    except Exception as e:
        # Pre-warming is optional - if it fails, authentication will still work
        # but the first login may be slightly slower
        logger.warning(f"Bcrypt pre-warm skipped (non-critical): {type(e).__name__}")
    
    # ==========================================================================
    # STEP 2: Initialize Redis cache (non-blocking, no database)
    # ==========================================================================
    try:
        if redis_cache is not None:
            redis_available = await redis_cache.connect()
            if redis_available:
                logger.info("Redis cache connected successfully")
            else:
                logger.info("Using in-memory cache fallback")
        else:
            logger.info("Redis cache not available")
    except Exception as e:
        logger.warning(f"Redis connection failed (non-critical): {e}")
    
    # ==========================================================================
    # STEP 3: Warm up cache and database connections (optional, non-blocking)
    # ==========================================================================
    try:
        from .core.cache import warmup_cache
        await warmup_cache()
        logger.info("Cache warmup completed")
    except Exception as e:
        logger.debug(f"Cache warmup skipped: {e}")
    
    # ==========================================================================
    # STEP 4: Run performance optimizations (background task)
    # ==========================================================================
    # Run performance optimizations in background to avoid blocking startup
    try:
        from .core.performance import run_all_performance_optimizations
        asyncio.create_task(run_all_performance_optimizations())
        logger.info("Performance optimizations scheduled")
    except Exception as e:
        logger.debug(f"Performance optimizations skipped: {e}")
    
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
        if redis_cache is not None:
            await redis_cache.disconnect()
            logger.info("Redis cache disconnected")
    except Exception as e:
        logger.warning(f"Error disconnecting Redis cache: {e}")
    try:
        if close_db is not None:
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
def health_ping():
    """Ultra-fast health ping endpoint
    
    ✅ PRODUCTION-GRADE: Database-free, instant response.
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
    try:
        if redis_cache is not None:
            health_response["cache"] = await redis_cache.health_check()
        else:
            # Use new cache system
            from .core.cache import _redis_available, _redis_client
            if _redis_available and _redis_client:
                health_response["cache"] = {"status": "healthy", "backend": "redis"}
            else:
                health_response["cache"] = {"status": "healthy", "backend": "in-memory"}
    except Exception as e:
        health_response["cache"] = {"status": "degraded", "error": str(e)}
    
    return health_response


# Performance metrics endpoint
@app.get("/metrics", tags=["monitoring"])
async def get_metrics():
    """Get performance metrics for monitoring
    
    Returns metrics including:
    - Average API response times
    - Cache hit rates
    - Database query statistics
    - Error rates
    - Per-endpoint performance
    
    Target metrics:
    - API response: 50-150ms
    - Cache hit rate: >80%
    - Page load: <1s
    """
    try:
        from .core.monitoring import get_performance_metrics
        return get_performance_metrics()
    except ImportError:
        return {
            "error": "Performance monitoring not available",
            "message": "Install monitoring dependencies to enable this endpoint"
        }


# Include routers with /api prefix to match frontend expectations (with safety checks)
if auth is not None:
    app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
if hireme is not None:
    app.include_router(hireme.router, prefix="/api/hireme", tags=["hireme"])
if jobs is not None:
    app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
if messages is not None:
    app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
if notifications is not None:
    app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
if posts is not None:
    app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
if profile_pictures is not None:
    app.include_router(profile_pictures.router, prefix="/api/profile-pictures", tags=["profile-pictures"])
if reviews is not None:
    app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
if upload is not None:
    app.include_router(upload.router, prefix="/api/upload", tags=["uploads"])
if users is not None:
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


# Initialize Socket.IO for real-time messaging
# Reuse CORS origins from middleware configuration (excludes localhost in production)
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=_allowed_origins  # Uses same origins as CORS middleware
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

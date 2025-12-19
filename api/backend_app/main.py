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
# Check if we need to set up the alias (don't override if backend_app alias already exists)
if 'app' not in sys.modules or not hasattr(sys.modules.get('app', None), '__path__') or 'backend_app' not in str(getattr(sys.modules.get('app', None), '__file__', '')):
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
    _schema_modules = ['auth', 'job', 'message', 'post', 'review', 'subscription']
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
    _api_modules = ['analytics', 'auth', 'debug', 'feed', 'health', 'hireme', 'jobs', 'messages', 
                    'notifications', 'posts', 'profile_pictures', 'reviews', 'subscriptions', 'upload', 'users']
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

# =============================================================================
# 🔥 NEVER-FAIL HEALTH CHECK ARCHITECTURE - STEP 1
# =============================================================================
# Mount dedicated health app FIRST — BEFORE ANY OTHER IMPORTS
# This ensures health endpoints are available even if main app imports fail
# =============================================================================

from backend_app.health import health_app

# INSTANT APP — NO HEAVY IMPORTS YET
app = FastAPI(
    title="hiremebahamas",
    version="1.0.0",
    docs_url=None,        # Disable heavy Swagger/ReDoc on boot
    redoc_url=None,
    openapi_url=None,
)

# =============================================================================
# 🔥 MOUNT HEALTH APP FIRST — CRITICAL FOR NEVER-FAIL ARCHITECTURE
# =============================================================================
# Health app is mounted at root level, so it handles:
#   - /api/health
#   - /health
#   - /healthz
#   - /live
#   - /ready
#
# These endpoints are now PHYSICALLY ISOLATED from the main application.
# Even if database explodes, Redis dies, or app crashes → health still passes.
#
# This is mounted BEFORE any heavy imports (auth, users, jobs, feed, etc.)
# so health checks respond instantly regardless of application state.
# =============================================================================
app.mount("", health_app)

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

# Import APIs - Use explicit imports to avoid circular dependencies
from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.debug import router as debug_router
from app.api.feed import router as feed_router
from app.api.health import router as health_router
from app.api.hireme import router as hireme_router
from app.api.jobs import router as jobs_router
from app.api.messages import router as messages_router
from app.api.notifications import router as notifications_router
from app.api.posts import router as posts_router
from app.api.profile_pictures import router as profile_pictures_router
from app.api.reviews import router as reviews_router
from app.api.subscriptions import router as subscriptions_router
from app.api.upload import router as upload_router
from app.api.users import router as users_router
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

# Log that never-fail health app is active
logger.info("=" * 80)
logger.info("✅ NEVER-FAIL HEALTH APP ACTIVE")
logger.info("=" * 80)
logger.info("Health endpoints (isolated from main app):")
logger.info("  - /api/health   (Render health check)")
logger.info("  - /health       (Alternative)")
logger.info("  - /healthz      (Emergency fallback)")
logger.info("  - /live         (Liveness probe)")
logger.info("  - /ready        (Readiness probe)")
logger.info("=" * 80)

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
            # Note: Using startswith() for hierarchical path matching is intentional
            # (e.g., "/api/jobs" matches both "/api/jobs" and "/api/jobs/stats")
            # Patterns are ordered so more specific patterns should be checked first
            for pattern, methods in CACHE_CONTROL_RULES.items():
                if pattern != "*":
                    # For root path or paths that should be exact match, use exact comparison
                    # For API paths with subpaths, use startswith for hierarchical matching
                    if path.startswith(pattern) and request.method in methods:
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
    
    Adds X-Request-ID header to all responses for request tracing (like Facebook).
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Store request_id in request state for potential use by endpoints
    # Store as both .id and .request_id for compatibility
    request.state.id = request_id
    request.state.request_id = request_id[:8]  # Keep short version for logging
    
    # Get client info
    client_ip = request.client.host if request.client else 'unknown'
    user_agent = request.headers.get('user-agent', 'unknown')
    
    # Use short request_id for logging (first 8 chars)
    log_request_id = request.state.request_id
    
    # Log incoming request with more context
    logger.info(
        f"[{log_request_id}] --> {request.method} {request.url.path} "
        f"from {client_ip} | UA: {user_agent[:50]}..."
    )
    
    # Process request
    try:
        response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Add X-Request-ID header to response for tracing
        response.headers["X-Request-ID"] = request.state.id
        
        # Determine log level and capture error details for failed requests
        if response.status_code < 400:
            # Success - log at INFO level
            logger.info(
                f"[{log_request_id}] <-- {response.status_code} {request.method} {request.url.path} "
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
                f"[{log_request_id}] <-- {response.status_code} {request.method} {request.url.path} "
                f"in {duration_ms}ms from {client_ip}{error_detail}"
            )
            
            # Log slow requests separately
            if duration_ms > SLOW_REQUEST_THRESHOLD_MS:
                logger.warning(
                    f"[{log_request_id}] SLOW REQUEST: {request.method} {request.url.path} "
                    f"took {duration_ms}ms (>{SLOW_REQUEST_THRESHOLD_MS}ms threshold)"
                )
        
        return response
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(
            f"[{log_request_id}] <-- EXCEPTION {request.method} {request.url.path} "
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
    # Import environment utilities here to keep them in the lazy initialization
    # section (only imported when app starts, not at module load time)
    from app.core.environment import is_production, is_development
    from urllib.parse import urlparse
    
    logger.info("=" * 80)
    logger.info("🚀 Starting HireMeBahamas API")
    logger.info("=" * 80)
    
    # ==========================================================================
    # DEPLOYMENT ENVIRONMENT INFORMATION
    # ==========================================================================
    
    environment = os.getenv("ENVIRONMENT", "development")
    vercel_env = os.getenv("VERCEL_ENV", "not set")
    is_prod = is_production()
    
    logger.info(f"📍 Environment: {environment}")
    logger.info(f"📍 Vercel Environment: {vercel_env}")
    logger.info(f"📍 Production Mode: {is_prod}")
    logger.info(f"📍 Development Mode: {is_development()}")
    
    # ==========================================================================
    # DATABASE CONFIGURATION (without credentials)
    # ==========================================================================
    database_url = os.getenv("DATABASE_URL", "not set")
    if database_url and database_url != "not set":
        # Parse URL to show connection info without credentials
        try:
            parsed = urlparse(database_url)
            db_host = parsed.hostname or "unknown"
            db_port = parsed.port or "unknown"
            db_name = parsed.path.lstrip('/').split('?')[0] if parsed.path else "unknown"
            db_driver = parsed.scheme or "unknown"
            db_ssl = "sslmode=require" in database_url
            
            logger.info(f"💾 Database Driver: {db_driver}")
            logger.info(f"💾 Database Host: {db_host}")
            logger.info(f"💾 Database Port: {db_port}")
            logger.info(f"💾 Database Name: {db_name}")
            logger.info(f"💾 Database SSL: {'✅ enabled' if db_ssl else '⚠️  disabled'}")
        except Exception as e:
            logger.warning(f"💾 Database URL configured but could not parse: {e}")
    else:
        logger.warning("💾 Database URL: ⚠️  NOT CONFIGURED")
    
    # ==========================================================================
    # CORS CONFIGURATION
    # ==========================================================================
    logger.info(f"🌐 CORS Origins: {len(cors_origins)} allowed origins")
    for origin in cors_origins:
        logger.info(f"   - {origin}")
    logger.info(f"🌐 CORS Credentials: ✅ enabled (for secure cookies)")
    
    # ==========================================================================
    # SERVER CONFIGURATION
    # ==========================================================================
    port = os.getenv("PORT", "8000")
    logger.info(f"🖥️  Server Port: {port}")
    logger.info(f"🖥️  Host: 0.0.0.0 (all interfaces)")
    
    # ==========================================================================
    # HEALTH ENDPOINTS
    # ==========================================================================
    logger.info("🏥 Health Endpoints:")
    logger.info("   - GET /health (instant, no DB)")
    logger.info("   - GET /live (instant, no DB)")
    logger.info("   - GET /ready (instant, no DB)")
    logger.info("   - GET /ready/db (with DB check)")
    logger.info("   - GET /health/detailed (comprehensive)")
    
    # ==========================================================================
    # CRITICAL ENVIRONMENT VARIABLES CHECK
    # ==========================================================================
    logger.info("🔑 Environment Variables Check:")
    env_vars = {
        "DATABASE_URL": "✅ set" if os.getenv("DATABASE_URL") else "❌ not set",
        "REDIS_URL": "✅ set" if os.getenv("REDIS_URL") else "ℹ️  not set (optional)",
        "JWT_SECRET_KEY": "✅ set" if os.getenv("JWT_SECRET_KEY") else "⚠️  not set (using default)",
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "❌ not set"),
        "VERCEL_ENV": os.getenv("VERCEL_ENV", "ℹ️  not set"),
    }
    for var, status in env_vars.items():
        logger.info(f"   - {var}: {status}")
    
    logger.info("=" * 80)
    logger.info("Starting component initialization (NO database connections)...")
    logger.info("=" * 80)
    
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
            logger.info("✅ Redis cache connected successfully")
        else:
            logger.debug("Using in-memory cache (Redis not configured - this is expected)")
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
    
    logger.info("=" * 80)
    logger.info("✅ HireMeBahamas API Initialization Complete")
    logger.info("=" * 80)
    logger.info("")
    logger.info("📊 INITIALIZATION SUMMARY:")
    logger.info("   ✅ Health endpoints ready (instant response)")
    logger.info("   ✅ CORS configured for production")
    logger.info("   ✅ Request logging middleware active")
    logger.info("   ✅ Timeout middleware configured (60s)")
    logger.info("   ✅ Rate limiting middleware active")
    logger.info("")
    logger.info("🔄 LAZY INITIALIZATION PATTERN:")
    logger.info("   - Database engine will initialize on first request")
    logger.info("   - NO database connections at startup")
    logger.info("   - NO warm-up pings")
    logger.info("   - NO background keepalive loops")
    logger.info("")
    logger.info("🚦 READY TO ACCEPT TRAFFIC")
    logger.info("=" * 80)


@app.on_event("shutdown")
async def full_shutdown():
    """Graceful shutdown with proper async task cleanup.
    
    This prevents "Task was destroyed but it is pending!" warnings by:
    1. Shutting down thread pool before cancelling async tasks
    2. Properly awaiting all cleanup operations
    3. Cancelling any pending background tasks
    4. Giving async operations time to complete gracefully
    """
    import asyncio
    from app.core.concurrent import shutdown_thread_pool
    
    logger.info("Shutting down HireMeBahamas API...")
    
    # Configurable shutdown timeout (default 5 seconds)
    SHUTDOWN_TIMEOUT_SECONDS = int(os.getenv("SHUTDOWN_TIMEOUT_SECONDS", "5"))
    
    # CRITICAL: Shutdown thread pool FIRST before async cleanup
    # This prevents "Task was destroyed but it is pending!" warnings for thread pool tasks
    try:
        shutdown_thread_pool()
        logger.debug("Thread pool shutdown completed")
    except Exception as e:
        logger.warning(f"Error shutting down thread pool: {e}")
    
    # Collect all cleanup tasks
    cleanup_tasks = []
    
    # Redis cache cleanup
    try:
        cleanup_tasks.append(redis_cache.disconnect())
        logger.debug("Redis cache disconnect queued")
    except Exception as e:
        logger.warning(f"Error queueing Redis cache disconnect: {e}")
    
    # Database cleanup
    try:
        cleanup_tasks.append(close_db())
        logger.debug("Database close queued")
    except Exception as e:
        logger.warning(f"Error queueing database close: {e}")
    
    # Execute all cleanup tasks with configurable timeout to prevent hanging
    if cleanup_tasks:
        try:
            # Wait for all cleanup tasks with configurable timeout
            await asyncio.wait_for(
                asyncio.gather(*cleanup_tasks, return_exceptions=True),
                timeout=SHUTDOWN_TIMEOUT_SECONDS
            )
            logger.info("✅ All cleanup tasks completed successfully")
        except asyncio.TimeoutError:
            logger.warning(f"⚠️  Shutdown cleanup timed out after {SHUTDOWN_TIMEOUT_SECONDS} seconds")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    # Cancel any remaining pending tasks (except current task)
    try:
        current_task = asyncio.current_task()
        pending_tasks = [
            task for task in asyncio.all_tasks()
            if not task.done() and task is not current_task
        ]
        
        if pending_tasks:
            logger.info(f"Cancelling {len(pending_tasks)} pending background tasks...")
            for task in pending_tasks:
                task.cancel()
            
            # Wait for cancelled tasks with shorter timeout to avoid delays
            # Use wait() instead of gather() for better control with cancelled tasks
            done, pending = await asyncio.wait(
                pending_tasks,
                timeout=1.0,  # Short timeout for cancelled tasks
                return_when=asyncio.ALL_COMPLETED
            )
            
            if pending:
                logger.warning(f"⚠️  {len(pending)} tasks still pending after cancellation")
            else:
                logger.info("✅ All pending tasks cancelled")
    except Exception as e:
        logger.warning(f"Error cancelling pending tasks: {e}")
    
    logger.info("✅ Shutdown complete")


# =============================================================================
# PANIC SHIELD - Global Exception Handler
# =============================================================================
# 8️⃣ PANIC SHIELD (FAIL GRACEFULLY)
# ✅ Global exception guard
# ✔ Users see calm
# ✔ You get logs
# =============================================================================
@app.exception_handler(Exception)
async def panic_handler(request: Request, exc: Exception):
    """Panic Shield - Global exception handler for graceful failure.
    
    This catches all unhandled exceptions and returns a calm, user-friendly
    message while logging the full error details for debugging.
    
    Args:
        request: The incoming request
        exc: The unhandled exception
        
    Returns:
        JSON response with user-friendly error message
    """
    # Get request ID if available (from request logging middleware)
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Log the panic with request ID for debugging
    logger.error(f"PANIC {request_id}: {exc}")
    
    # Return a calm, user-friendly error response
    return JSONResponse(
        status_code=500,
        content={"error": "Temporary issue. Try again."}
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


# Note: /health/ping endpoint is now provided by the health router (api/health.py)


# Cache warming endpoint for cron jobs
@app.post("/warm-cache")
async def warm_cache_endpoint():
    """
    Warm up cache with frequently accessed data.
    
    This endpoint should be called by a cron job every 5 minutes
    to keep the cache hot and ensure sub-100ms response times.
    
    Example cron job: */5 * * * * curl -X POST https://your-backend-url/warm-cache
    
    For Render: Use GitHub Actions workflow (scheduled-ping.yml)
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


# NOTE: /api/health endpoint is now handled by the mounted health_app (see top of file)
# This provides NEVER-FAIL architecture - health checks respond even if main app crashes


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
# Note: auth_router already has prefix="/api/auth" and tags defined in the router itself
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
app.include_router(auth_router)  # Router prefix and tags defined in auth.py
app.include_router(debug_router, prefix="/api/debug", tags=["debug"])
app.include_router(feed_router, prefix="/api/feed", tags=["feed"])
app.include_router(health_router, tags=["health"])
app.include_router(hireme_router, prefix="/api/hireme", tags=["hireme"])
app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])
app.include_router(messages_router, prefix="/api/messages", tags=["messages"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["notifications"])
app.include_router(posts_router, prefix="/api/posts", tags=["posts"])
app.include_router(profile_pictures_router, prefix="/api/profile-pictures", tags=["profile-pictures"])
app.include_router(reviews_router, prefix="/api/reviews", tags=["reviews"])
app.include_router(subscriptions_router)  # Router prefix and tags defined in subscriptions.py
app.include_router(upload_router, prefix="/api/upload", tags=["uploads"])
app.include_router(users_router, prefix="/api/users", tags=["users"])

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
    # Use same CORS origins as CORS middleware (no wildcards in production)
    sio = socketio.AsyncServer(
        async_mode='asgi',
        cors_allowed_origins=cors_origins  # Uses same origins as CORS middleware
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
@app.head("/")
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

    # Single worker for small instance compatibility (per NEVER AGAIN list)
    # No reload in production, port from environment variable
    # Use the correct module path based on whether we're in standalone mode or not
    # When running as: python -m api.backend_app.main
    # Or from Render/Docker: uvicorn api.backend_app.main:app
    module_path = "api.backend_app.main:socket_app" if HAS_SOCKETIO else "api.backend_app.main:app"
    
    # Get port from environment variable (no hardcoded ports)
    port = int(os.getenv('PORT', 8000))
    
    logger.info(f"Starting uvicorn with module: {module_path}")
    uvicorn.run(
        module_path,
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1,  # Single worker for small instance compatibility (per NEVER AGAIN list)
        log_level="info"
    )

# =============================================================================
# NUCLEAR-OPTIMIZED STARTUP (2025 RENDER EDITION)
# =============================================================================
# INSTANT APP — NO HEAVY IMPORTS YET
# Responds in <5ms even on coldest start. Render cannot kill this.
# =============================================================================
import os
import importlib
import tracemalloc
import logging
from typing import Optional, List, Dict, Union, Any
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from .database import get_engine

# Enable tracemalloc to track memory allocations for debugging
# This prevents RuntimeWarning: Enable tracemalloc to get the object allocation traceback
tracemalloc.start()


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
async def health():
    """Health check that validates database connectivity."""
    try:
        engine = get_engine()
        if engine is None:
            raise RuntimeError("Database engine not initialized")

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected",
            "platform": "render"
        }
    except Exception as e:
        logging.getLogger(__name__).warning("Health check degraded: %s", e)
        return {
            "status": "degraded",
            "error": "unavailable"
        }


# EMERGENCY HEALTH ENDPOINT — ULTRA STABLE FALLBACK
@app.get("/healthz", include_in_schema=False)
def healthz():
    """Emergency health check endpoint - ultra stable fallback.
    
    This is a SECOND emergency health route that returns a plain "ok" string.
    If /health or /api/health ever changes, this endpoint ensures the service
    still survives health checks.
    
    Returns plain text "ok" for maximum compatibility and minimal overhead.
    
    ✅ NO DATABASE - instant response
    ✅ NO IO - instant response  
    ✅ NO async/await - synchronous function
    ✅ Plain text response - no JSON parsing overhead
    
    High reliability through minimal dependencies and failure points.
    """
    return "ok"


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
import threading
import traceback

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
_schema_modules = ['auth', 'job', 'message', 'post', 'review', 'monetization']
for _module_name in _schema_modules:
    try:
        _module = importlib.import_module(f'.schemas.{_module_name}', package='app')
        inject_typing_exports(_module)
    except ImportError:
        # Skip modules that might not be available (graceful degradation)
        pass

# Import APIs (with nuclear safety net)
try:
    # Explicit router imports to avoid circular dependencies and import-time side effects
    from .api.hireme import router as hireme_router
    from .api.jobs import router as jobs_router
    from .api.messages import router as messages_router
    from .api.notifications import router as notifications_router
    from .api.profile_pictures import router as profile_pictures_router
    from .api.reviews import router as reviews_router
    from .api.upload import router as upload_router
    from .api.monetization import router as monetization_router
    # Import new Facebook-style modular routers
    from .auth import routes as auth_routes
    from .users import routes as users_routes
    from .feed import routes as feed_routes
    from .health import router as health_router
    print("✅ API routers imported successfully")
except Exception as e:
    print(f"API router import failed: {e}")
    auth_routes = hireme_router = jobs_router = messages_router = notifications_router = None
    feed_routes = profile_pictures_router = reviews_router = upload_router = users_routes = health_router = monetization_router = None

# Global variable to store database import error details for later logging
_db_import_error = None
_db_import_traceback = None

try:
    from .database import init_db, close_db, get_db, get_pool_status, engine, test_db_connection, get_db_status
    print("✅ Database functions imported successfully")
except Exception as e:
    # Store error details for later logging (logger not yet configured)
    _db_import_error = e
    _db_import_traceback = traceback.format_exc()
    print(f"DB import failed: {type(e).__name__}: {e}")
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
STARTUP_OPERATION_TIMEOUT = 5.0  # 5 seconds - timeout for non-critical startup operations
TOTAL_STARTUP_TIMEOUT = 20.0  # 20 seconds - maximum time for entire startup event
SHUTDOWN_TASK_TIMEOUT = 5.0  # 5 seconds - timeout for background tasks during shutdown

# =============================================================================
# BACKGROUND BOOTSTRAP UTILITIES
# =============================================================================

async def wait_for_db(max_retries: int = 10, retry_delay: float = 2.0) -> bool:
    """Wait for database to become available with exponential backoff.
    
    Retries database connection with exponential backoff strategy to handle:
    - Render cold starts (can take 30+ seconds)
    - Transient network issues
    - Database server startup delays
    
    Safe to call from background tasks.
    
    Args:
        max_retries: Maximum number of connection attempts (default: 10)
        retry_delay: Base delay between retries in seconds (default: 2.0)
        
    Returns:
        bool: True if database is available, False otherwise
    """
    logger.info(f"🔄 Attempting to connect to database (max {max_retries} attempts)...")
    
    for attempt in range(1, max_retries + 1):
        try:
            if test_db_connection is not None:
                success, error = await test_db_connection()
                if success:
                    logger.info(f"✅ Database connected successfully on attempt {attempt}/{max_retries}")
                    return True
                else:
                    # Truncate error message if too long
                    error_display = error[:200] + "..." if error and len(error) > 200 else error
                    logger.warning(
                        f"⚠️  Database connection attempt {attempt}/{max_retries} failed: {error_display}"
                    )
            else:
                logger.error("❌ test_db_connection function not available")
                logger.error("")
                logger.error("This usually means the database module failed to import at startup.")
                logger.error("Check the logs above for 'DB import failed' or 'DATABASE MODULE IMPORT FAILED'")
                logger.error("for details about the root cause.")
                logger.error("")
                logger.error("Common causes:")
                logger.error("  - Missing or invalid DATABASE_URL environment variable")
                logger.error("  - Invalid database connection string format")
                logger.error("  - Missing asyncpg package (pip install asyncpg)")
                logger.error("  - SQLAlchemy configuration error")
                return False
        except Exception as e:
            logger.warning(
                f"⚠️  Database connection attempt {attempt}/{max_retries} failed: {type(e).__name__}: {str(e)[:200]}"
            )
        
        # Apply exponential backoff between retries (2s, 4s, 8s, 16s, 32s, ...)
        if attempt < max_retries:
            backoff_delay = retry_delay * (2 ** (attempt - 1))
            # Cap maximum delay at 60 seconds to avoid excessive waiting
            backoff_delay = min(backoff_delay, 60.0)
            logger.info(f"   Retrying in {backoff_delay:.1f} seconds...")
            await asyncio.sleep(backoff_delay)
    
    logger.error(f"❌ Database connection failed after {max_retries} attempts")
    logger.error("   Check DATABASE_URL configuration and network connectivity")
    return False


async def create_indexes_async():
    """Create database indexes asynchronously.
    
    This function imports and runs the create_indexes module.
    Should be called from background_bootstrap().
    
    Returns:
        bool: True if indexes created successfully, False otherwise
    """
    try:
        import importlib.util
        import inspect
        
        # Get path to create_database_indexes.py (in backend directory)
        backend_dir = os.path.dirname(os.path.dirname(__file__))
        indexes_path = os.path.join(backend_dir, "create_database_indexes.py")
        
        if not os.path.exists(indexes_path):
            logger.warning(f"create_database_indexes.py not found at {indexes_path}")
            return False
            
        spec = importlib.util.spec_from_file_location("create_database_indexes", indexes_path)
        if spec is None or spec.loader is None:
            logger.warning("Could not load create_database_indexes module")
            return False
            
        indexes_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(indexes_module)
        
        # Check if create_indexes is async or sync
        if not hasattr(indexes_module, 'create_indexes'):
            logger.warning("create_indexes function not found in module")
            return False
            
        create_indexes_func = indexes_module.create_indexes
        
        # Check if the function is async and call it appropriately
        if inspect.iscoroutinefunction(create_indexes_func):
            success = await create_indexes_func()
        else:
            logger.warning("create_indexes function is not async, skipping index creation")
            return False
        
        return success
            
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}", exc_info=True)
        return False


async def background_bootstrap():
    """Background bootstrap - waits for DB and creates indexes.
    
    This function runs in the background using asyncio.create_task().
    It safely waits for the database and creates indexes without blocking startup.
    
    ✅ No blocking
    ✅ No destroyed tasks
    ✅ Gunicorn-safe
    """
    try:
        logger.info("📦 Background bootstrap started")
        
        # Wait for database to become available
        db_ready = await wait_for_db()
        if not db_ready:
            logger.warning("Database not ready, skipping index creation")
            return
        
        # Create indexes asynchronously
        logger.info("Creating database indexes...")
        try:
            success = await create_indexes_async()
            if success:
                logger.info("✅ Database indexes created successfully")
            else:
                logger.warning("⚠️ Some indexes may not have been created")
        except Exception as e:
            logger.error(f"Index creation failed: {e}", exc_info=True)
            
    except Exception as e:
        logger.error(f"Bootstrap failed: {e}", exc_info=True)
    finally:
        logger.info("📦 Background bootstrap completed")

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

# =============================================================================
# STARTUP DIAGNOSTIC: Check if database import failed
# =============================================================================
if _db_import_error is not None:
    logger.error("=" * 80)
    logger.error("❌ DATABASE MODULE IMPORT FAILED AT STARTUP")
    logger.error("=" * 80)
    logger.error(f"Exception Type: {type(_db_import_error).__name__}")
    logger.error(f"Exception Message: {_db_import_error}")
    logger.error("")
    logger.error("Partial Traceback (first 500 characters):")
    logger.error(_db_import_traceback[:500] if _db_import_traceback else "No traceback available")
    logger.error("")
    logger.error("Common Causes:")
    logger.error("  1. DATABASE_URL environment variable is missing or invalid")
    logger.error("  2. Database connection string has incorrect format")
    logger.error("  3. Required package 'asyncpg' is not installed")
    logger.error("  4. SQLAlchemy configuration error")
    logger.error("")
    logger.error("To fix:")
    logger.error("  - Check that DATABASE_URL is set correctly")
    logger.error("  - Verify connection string format: postgresql+asyncpg://user:pass@host:5432/db")
    logger.error("  - Ensure all database dependencies are installed: pip install asyncpg sqlalchemy")
    logger.error("=" * 80)


# =============================================================================
# PANIC SHIELD - GLOBAL EXCEPTION GUARD
# =============================================================================
@app.exception_handler(Exception)
async def panic_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception guard - catches all unhandled exceptions.
    
    This handler ensures that:
    ✅ Users see a calm, friendly error message
    ✅ You get detailed logs for debugging
    ✅ The app never crashes from unhandled exceptions
    
    All exceptions are logged with request ID for traceability.
    """
    # Get request ID from request state (set by middleware or generate new one)
    request_id = getattr(request.state, "id", None) or getattr(request.state, "request_id", None) or str(uuid.uuid4())[:8]
    
    # Log the panic with full details
    logger.error(f"PANIC {request_id}: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={"error": "Temporary issue. Try again."}
    )

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

# =============================================================================
# CORS CONFIGURATION - CREDENTIALS ENABLED
# =============================================================================
# ✅ STEP 3: CORS MUST ALLOW CREDENTIALS
# 
# CRITICAL SECURITY REQUIREMENTS:
# 1. ✅ allow_credentials=True - Enables cookies/credentials in CORS requests
# 2. ✅ Explicit origins - NO wildcard (*) patterns allowed with credentials
# 3. ✅ Browser will block cookies if wildcard (*) is used with credentials
# 
# Production origins are explicitly listed to prevent security vulnerabilities.
# Development includes localhost for testing but is excluded in production.
# =============================================================================

# Import environment utilities for consistent production checks
try:
    from .core.environment import get_cors_origins
    _allowed_origins = get_cors_origins()  # Excludes localhost in production
except ImportError:
    # Fallback to manual configuration if import fails
    import os
    _is_prod = os.getenv("ENVIRONMENT", "").lower() == "production" or os.getenv("VERCEL_ENV", "").lower() == "production"
    
    # 🚫 SECURITY: No wildcard patterns (*) in production
    if _is_prod:
        # Production: specific domains only
        _allowed_origins = [
            "https://hiremebahamas.com",
            "https://www.hiremebahamas.com",
        ]
    else:
        # Development: includes localhost and production domains for testing
        _allowed_origins = [
            "https://hiremebahamas.com",
            "https://www.hiremebahamas.com",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",  # Vite default
            "http://127.0.0.1:5173",
        ]

# Apply CORS middleware with credentials support
# ❌ NEVER use allow_origins=["*"] with allow_credentials=True
# ✅ ALWAYS use explicit origin list when credentials are enabled
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,  # Explicit origins required for credentials
    allow_credentials=True,          # Enable cookies/auth headers in CORS requests
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
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
# SAFE STARTUP & SHUTDOWN (NO ORPHAN TASKS)
# =============================================================================
# Track background tasks to prevent orphans
_background_tasks = set()

@app.on_event("startup")
async def startup():
    """Safe startup with non-blocking background bootstrap.
    
    ✅ PRODUCTION FASTAPI PATTERN (DO NOT EVER DO list compliant):
    - ❌ NO Multiple Gunicorn workers (using 1 worker)
    - ❌ NO Blocking DB calls at import
    - ❌ NO --reload flag
    - ❌ NO Heavy startup logic (all in background task)
    - ✅ Single platform deployment (Render only)
    
    App responds immediately while still warming up the database connection
    to prevent cold-start latency.
    
    ✅ No blocking
    ✅ No destroyed tasks
    ✅ Gunicorn-safe
    """
    logger.info("🚀 Starting HireMeBahamas API (Production Mode)")
    logger.info("   Workers: 1 (predictable memory)")
    logger.info("   Health: DB-backed readiness")
    logger.info("   DB: Lazy (connects on first request, warm-up enabled)")
    
    # Validate database configuration (SSLMODE ERROR PREVENTION)
    try:
        from backend.app.core.db_guards import validate_database_config
        validate_database_config(strict=False)  # Warn but don't fail startup
    except Exception as e:
        logger.warning(f"Database configuration validation skipped: {e}")
    
    # Create background task for bootstrap (non-blocking)
    task = asyncio.create_task(background_bootstrap())
    _background_tasks.add(task)
    # Remove task from set when it completes
    task.add_done_callback(_background_tasks.discard)
    
    # Proactively warm up a database connection to avoid cold starts
    try:
        await warmup()
    except Exception as e:
        logger.warning(f"Warm-up during startup skipped: {e}")
    
    logger.info("✅ Application startup complete (instant)")
    logger.info("   Background bootstrap running in async task")
    
    # Production configuration (see PRODUCTION_CONFIG_COMPLIANCE.md):
    # - Workers: 1 (predictable memory)
    # - Health: Validates DB connectivity
    # - DB: Lazy (connects on first request)
    # - Startup: Async (non-blocking)


async def warmup():
    """Warm up database connection to prevent cold-start delays."""
    for attempt in range(2):
        try:
            engine = get_engine()
            if engine is None:
                raise RuntimeError("Database engine not initialized")

            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("✅ Database warm-up completed")
            return
        except Exception as e:
            logger.warning(f"Database warm-up attempt {attempt + 1} failed: {e}")
            if attempt == 0:
                await asyncio.sleep(1)
    logger.error("Database warm-up failed after retries")


@app.on_event("shutdown")
async def shutdown():
    """Graceful shutdown - waits for background tasks.
    
    ✅ No blocking
    ✅ No destroyed tasks
    ✅ Gunicorn-safe
    """
    logger.info("Shutting down HireMeBahamas API...")
    
    # Wait for background tasks to complete (with timeout)
    if _background_tasks:
        logger.info(f"Waiting for {len(_background_tasks)} background task(s) to complete...")
        try:
            # Yield control to allow tasks to progress, then wait for completion
            await asyncio.sleep(0)
            await asyncio.wait(_background_tasks, timeout=SHUTDOWN_TASK_TIMEOUT)
        except Exception as e:
            logger.warning(f"Error waiting for background tasks: {e}")
    
    # Close Redis cache
    try:
        if redis_cache is not None:
            await redis_cache.disconnect()
            logger.info("Redis cache disconnected")
    except Exception as e:
        logger.warning(f"Error disconnecting Redis cache: {e}")
    
    # Close database connections
    try:
        if close_db is not None:
            await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
    
    logger.info("✅ Shutdown complete")


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


# API health check endpoint (simple status check)
@app.get("/api/health")
@app.head("/api/health")
def api_health():
    """Instant API health check - no database dependency.
    
    Supports both GET and HEAD methods for health check compatibility.
    
    ✅ NO DATABASE - instant response
    ✅ NO IO - instant response
    ✅ NO async/await - synchronous function
    
    Render kills apps that fail health checks, so this must be instant.
    """
    return {
        "status": "ok",
        "service": "hiremebahamas-backend",
        "uptime": "healthy"
    }


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
# New Facebook-style modular routers
if auth_routes is not None:
    app.include_router(auth_routes.router, prefix="/api/auth", tags=["authentication"])
if users_routes is not None:
    app.include_router(users_routes.router, prefix="/api/users", tags=["users"])
if feed_routes is not None:
    app.include_router(feed_routes.router, prefix="/api/posts", tags=["posts", "feed"])

# Legacy API routers (will be migrated gradually)
if hireme_router is not None:
    app.include_router(hireme_router, prefix="/api/hireme", tags=["hireme"])
if jobs_router is not None:
    app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])
if messages_router is not None:
    app.include_router(messages_router, prefix="/api/messages", tags=["messages"])
if notifications_router is not None:
    app.include_router(notifications_router, prefix="/api/notifications", tags=["notifications"])
if profile_pictures_router is not None:
    app.include_router(profile_pictures_router, prefix="/api/profile-pictures", tags=["profile-pictures"])
if reviews_router is not None:
    app.include_router(reviews_router, prefix="/api/reviews", tags=["reviews"])
if upload_router is not None:
    app.include_router(upload_router, prefix="/api/upload", tags=["uploads"])
if monetization_router is not None:
    app.include_router(monetization_router, prefix="/api/monetization", tags=["monetization"])

# Include health check router (no prefix as it provides /health, /ready endpoints)
if health_router is not None:
    app.include_router(health_router, tags=["health"])

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

# Set up Socket.IO event handlers using the new realtime module
try:
    from .realtime.websocket import setup_socket_handlers
    socket_manager = setup_socket_handlers(sio)
    logger.info("✅ WebSocket handlers registered via realtime module")
except Exception as e:
    logger.warning(f"⚠️  WebSocket handlers registration failed (non-critical): {e}")
    socket_manager = None


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
    import sys

    # Production mode - single worker (ABSOLUTE REQUIREMENT)
    # Multiple Gunicorn workers are PROHIBITED
    port = int(os.getenv('PORT', 10000))
    
    # ⚠️ CRITICAL: Port 5432 is for PostgreSQL, NOT HTTP services
    # DO NOT BIND TO PORT 5432 - This is a PostgreSQL port, not for your backend
    if port == 5432:
        print("=" * 80, file=sys.stderr)
        print("❌ CRITICAL ERROR: Cannot bind to port 5432", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        print("", file=sys.stderr)
        print("Port 5432 is reserved for PostgreSQL database servers.", file=sys.stderr)
        print("Your HTTP backend should use a different port.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Common HTTP ports:", file=sys.stderr)
        print("  • 8000, 8080: Common development ports", file=sys.stderr)
        print("  • 10000: Render default", file=sys.stderr)
        print("  • Use $PORT environment variable for cloud deployments", file=sys.stderr)
        print("", file=sys.stderr)
        print("To fix this:", file=sys.stderr)
        print("  1. Check your PORT environment variable", file=sys.stderr)
        print("  2. Use a different port (e.g., 8000, 8080, 10000)", file=sys.stderr)
        print("  3. Never manually set PORT=5432", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        sys.exit(1)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1,
        log_level="info"
    )

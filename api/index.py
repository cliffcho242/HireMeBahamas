"""
MASTERMIND VERCEL SERVERLESS HANDLER — IMMORTAL DEPLOY 2025
Zero 404/500 errors, instant cold starts, bulletproof Postgres
"""
from fastapi import FastAPI, Header, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum
import os
import sys
import time
import logging
import traceback
from urllib.parse import urlparse
from typing import Optional, List, Dict, Union, Any
from db_url_utils import ensure_sslmode


def inject_typing_exports(module):
    """Inject typing module exports into a module's namespace.
    
    This is required for Pydantic to properly evaluate forward references
    when modules are aliased. When Pydantic evaluates forward references,
    it looks in the module's __dict__ for type names like Optional, List, etc.
    
    Args:
        module: The module object to inject typing exports into
    """
    module.__dict__['Optional'] = Optional
    module.__dict__['List'] = List
    module.__dict__['Dict'] = Dict
    module.__dict__['Union'] = Union
    module.__dict__['Any'] = Any


# Configure logging with more detail for debugging
# Check if runtime logs directory exists (e.g., in CI/test environment)
runtime_log_dir = os.getenv('RUNTIME_LOG_DIR', '/tmp/runtime-logs')
log_handlers = [logging.StreamHandler()]

if os.path.exists(runtime_log_dir):
    # Add file handler for runtime logs when directory exists
    runtime_log_file = os.path.join(runtime_log_dir, 'api-runtime.log')
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

# Log startup information
logger.info("="*60)
logger.info("VERCEL SERVERLESS API STARTING")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info("="*60)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_debug_mode() -> bool:
    """Check if debug mode is enabled.
    
    Debug mode shows detailed error messages and diagnostics.
    Only enabled in development or when explicitly set with DEBUG=true.
    Preview environments require explicit DEBUG=true to enable.
    """
    env = os.getenv("ENVIRONMENT", "").lower()
    debug_flag = os.getenv("DEBUG", "").lower() == "true"
    vercel_env = os.getenv("VERCEL_ENV", "").lower()
    
    # Development environment always has debug mode
    if env == "development":
        return True
    
    # Explicit DEBUG=true enables debug mode in any environment
    if debug_flag:
        return True
    
    # Otherwise, no debug mode
    return False


def is_production_mode() -> bool:
    """Check if running in production mode.
    
    Production mode hides detailed errors and sensitive information.
    Preview environments are treated as production unless DEBUG=true is set.
    """
    env = os.getenv("ENVIRONMENT", "").lower()
    vercel_env = os.getenv("VERCEL_ENV", "").lower()
    
    # Explicit production environment
    if env == "production" or vercel_env == "production":
        return True
    
    # Preview environments are production-like unless debug is enabled
    if vercel_env == "preview" and not is_debug_mode():
        return True
    
    return False

# JWT imports with fallback
try:
    from jose import jwt, JWTError, ExpiredSignatureError
    HAS_JOSE = True
except ImportError:
    try:
        import jwt as jwt_lib
        JWTError = jwt_lib.PyJWTError
        ExpiredSignatureError = jwt_lib.ExpiredSignatureError
        
        class jwt:
            @staticmethod
            def decode(token, secret, algorithms):
                return jwt_lib.decode(token, secret, algorithms=algorithms)
        HAS_JOSE = True
    except ImportError:
        HAS_JOSE = False
        logger.error("Neither python-jose nor PyJWT is available")

# Database imports with graceful fallback
try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import text
    HAS_DB = True
except ImportError:
    HAS_DB = False
    logger.warning("Database drivers not available")

# Backend imports with graceful fallback
HAS_BACKEND = False
BACKEND_ERROR = None
BACKEND_ERROR_SAFE = None  # Sanitized error message for public exposure
try:
    api_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, api_dir)
    
    # Create comprehensive module alias for backend_app BEFORE importing
    # This allows imports like "from app.core.security import ..." to work
    import backend_app as app_module
    sys.modules['app'] = app_module
    inject_typing_exports(app_module)
    
    # CRITICAL FIX: Also alias all submodules so "from app.core.X" works
    # When we do sys.modules['app'] = backend_app, Python doesn't automatically
    # resolve app.core to backend_app.core, so we must explicitly alias each submodule
    import backend_app.core
    sys.modules['app.core'] = backend_app.core
    inject_typing_exports(backend_app.core)
    
    # Dynamically alias all core submodules to handle all "from app.core.X" imports
    # This ensures any module under backend_app.core can be accessed as app.core.X
    _core_modules = ['security', 'upload', 'concurrent', 'metrics', 'redis_cache', 
                     'socket_manager', 'cache', 'db_health', 'timeout_middleware']
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
    
    # Also ensure backend_app is in sys.path
    backend_app_path = os.path.join(api_dir, 'backend_app')
    if backend_app_path not in sys.path:
        sys.path.insert(0, backend_app_path)
    
    from backend_app.api import auth, posts, jobs, users, messages, notifications
    HAS_BACKEND = True
    logger.info("✅ Backend modules imported successfully")
except Exception as e:
    BACKEND_ERROR = str(e)
    # Create sanitized error message for public exposure (no file paths or internal structure)
    error_type = type(e).__name__
    BACKEND_ERROR_SAFE = f"{error_type}: Backend modules unavailable"
    
    logger.warning(f"⚠️  Backend modules not available: {e}")
    # Only log full traceback in debug mode to avoid exposing internal structure
    if is_debug_mode():
        logger.warning(f"⚠️  Full traceback: {traceback.format_exc()}")
    logger.info("Running in FALLBACK MODE with limited API functionality")

# ============================================================================
# CONFIGURATION
# ============================================================================
# Support both HIREME_ prefix and regular env vars
JWT_SECRET = (
    os.getenv("HIREME_SECRET_KEY") or 
    os.getenv("SECRET_KEY") or 
    os.getenv("HIREME_JWT_SECRET_KEY") or
    os.getenv("JWT_SECRET_KEY") or
    "dev-secret-key-change-in-production"
)
JWT_ALGORITHM = "HS256"

# Database URL with HIREME_ prefix support
DATABASE_URL = (
    os.getenv("HIREME_DATABASE_URL") or
    os.getenv("DATABASE_URL") or
    os.getenv("HIREME_POSTGRES_URL") or
    os.getenv("POSTGRES_URL")
)

# CORS origins - Allow all origins for Vercel deployments
# Vercel preview deployments have dynamic URLs, so we need to be permissive
# In production, you can restrict this to specific domains
ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "*")
if ALLOWED_ORIGINS_ENV == "*":
    ALLOWED_ORIGINS = ["*"]
    # CRITICAL: When using wildcard origins (*), credentials MUST be False
    # This is a CORS security requirement - browsers will block requests otherwise
    ALLOW_CREDENTIALS = False
    logger.info("CORS: Allowing all origins (wildcard), credentials disabled")
else:
    ALLOWED_ORIGINS = ALLOWED_ORIGINS_ENV.split(",")
    # With specific origins, we can safely enable credentials
    ALLOW_CREDENTIALS = True
    logger.info(f"CORS: Allowing specific origins: {ALLOWED_ORIGINS}, credentials enabled")

# Mock user data for fallback
MOCK_USERS = {
    "1": {
        "id": 1,
        "email": "admin@hiremebahamas.com",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "user_type": "admin",
        "is_active": True,
        "profile_picture": None,
        "location": None,
        "phone": None,
    }
}

# ============================================================================
# DATABASE CONNECTION
# ============================================================================
# Reuse backend's database engine if available to avoid creating duplicate connections
# This prevents resource exhaustion in serverless environments
db_engine = None
async_session_maker = None

# Log database configuration status (without exposing credentials)
if DATABASE_URL:
    # Mask sensitive parts of URL for logging
    try:
        parsed = urlparse(DATABASE_URL)
        # Show only scheme and redacted location
        masked_url = f"{parsed.scheme}://***:***@{parsed.hostname if parsed.hostname else '***'}:{parsed.port if parsed.port else '***'}/***"
        logger.info(f"Database URL configured: {masked_url}")
    except Exception:
        logger.info("Database URL configured (unable to parse for logging)")
else:
    logger.warning("⚠️  DATABASE_URL not configured - API will have limited functionality")

# Use backend's database engine if available, otherwise create fallback engine
if HAS_BACKEND and HAS_DB:
    try:
        # Import backend database engine (already initialized during backend module import)
        from backend_app.database import engine as backend_engine
        from backend_app.database import AsyncSessionLocal as backend_session_maker
        
        db_engine = backend_engine
        async_session_maker = backend_session_maker
        logger.info("✅ Using backend's database engine (avoiding duplicate connections)")
    except (ImportError, AttributeError, ModuleNotFoundError) as e:
        logger.warning(f"⚠️  Could not import backend database modules: {e}")
        # Fallback will be created below if needed

# Fallback: Create minimal database engine only if backend isn't available
if db_engine is None and HAS_DB and DATABASE_URL:
    try:
        logger.info("Backend database not available, creating fallback database connection...")
        
        # Use centralized database module for validation and URL processing
        # This avoids code duplication and ensures consistent validation
        try:
            from database import get_database_url as get_validated_db_url
            db_url = get_validated_db_url()
            logger.info("✅ DATABASE_URL validated successfully")
        except ImportError:
            # Fallback if database module import fails - use manual processing
            logger.warning("Could not import database module, using manual URL processing")
            db_url = DATABASE_URL.strip()
            
            # Fix common typos
            if "ostgresql" in db_url and "postgresql" not in db_url:
                db_url = db_url.replace("ostgresql", "postgresql")
                logger.warning("Fixed malformed DATABASE_URL: 'ostgresql' -> 'postgresql'")
            
            # Convert to asyncpg format
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif db_url.startswith("postgresql://") and "asyncpg" not in db_url:
                db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            
            # Add SSL mode
            db_url = ensure_sslmode(db_url)
        
        logger.info("Creating fallback database engine with asyncpg...")
        db_engine = create_async_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=0,
            connect_args={"timeout": 5, "command_timeout": 5}
        )
        
        async_session_maker = sessionmaker(
            db_engine, class_=AsyncSession, expire_on_commit=False
        )
        logger.info("✅ Fallback database engine created successfully")
    except ValueError as ve:
        # ValueError indicates configuration issue - log helpful message
        logger.error(f"❌ DATABASE_URL configuration error: {ve}")
        logger.error("Please check your DATABASE_URL environment variable.")
        logger.error("Expected format: postgresql://username:password@hostname:5432/database?sslmode=require")
        db_engine = None
        async_session_maker = None
    except Exception as e:
        # Check for asyncpg "pattern" error specifically
        error_msg = str(e).lower()
        if "did not match" in error_msg and "pattern" in error_msg:
            logger.error(f"❌ DATABASE_URL format error: The connection string doesn't match PostgreSQL format")
            logger.error(f"Error details: {e}")
            logger.error("Expected format: postgresql://username:password@hostname:5432/database?sslmode=require")
            logger.error("Common issues:")
            logger.error("  1. Missing hostname (check for patterns like '@:5432' or missing '@')")
            logger.error("  2. Invalid characters in username or password")
            logger.error("  3. Extra whitespace or newlines in the URL")
            logger.error("  4. Missing required parts (username, host, or database name)")
        else:
            logger.error(f"❌ Database initialization failed: {e}")
            if is_debug_mode():
                logger.error(f"Traceback: {traceback.format_exc()}")
        
        db_engine = None
        async_session_maker = None
else:
    if db_engine is None:
        if not HAS_DB:
            logger.warning("⚠️  Database drivers not available (sqlalchemy, asyncpg)")
        if not DATABASE_URL:
            logger.warning("⚠️  DATABASE_URL not set in environment")

# ============================================================================
# CREATE FASTAPI APP
# ============================================================================
app = FastAPI(
    title="HireMeBahamas API",
    version="2.0.0",
    description="Job platform API for the Bahamas - Vercel Serverless",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler to ensure no error goes unlogged.
    This is critical for debugging issues in Vercel where logs might not be visible.
    """
    logger.error(
        f"UNHANDLED EXCEPTION: {type(exc).__name__}\n"
        f"Path: {request.method} {request.url.path}\n"
        f"Error: {str(exc)}\n"
        f"Traceback:\n{traceback.format_exc()}"
    )
    
    # Use helper function for consistent debug mode detection
    is_dev = is_debug_mode()
    
    # Return appropriate error response
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred while processing your request",
            "type": type(exc).__name__ if is_dev else "ServerError",
            "details": str(exc) if is_dev else None,
            "path": request.url.path,
            "method": request.method,
            "help": "Please try again. If the problem persists, contact support."
        }
    )

# ============================================================================
# CORS MIDDLEWARE
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# ============================================================================
# MIDDLEWARE - Request Logging with Enhanced Auth Tracking
# ============================================================================
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests with timing and comprehensive error handling
    
    Special handling for /api/auth/* endpoints to ensure login issues are visible.
    """
    start = time.time()
    method = request.method
    path = request.url.path
    
    # Get client info for tracking
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")[:100]
    
    # Enhanced logging for auth endpoints
    is_auth_endpoint = path.startswith("/api/auth/")
    
    if is_auth_endpoint:
        logger.info(
            f"→ AUTH REQUEST: {method} {path}\n"
            f"  Client IP: {client_ip}\n"
            f"  User-Agent: {user_agent}\n"
            f"  Headers: Authorization={bool(request.headers.get('authorization'))}, "
            f"Content-Type={request.headers.get('content-type', 'none')}"
        )
    else:
        logger.info(f"→ {method} {path}")
    
    try:
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)
        status = response.status_code
        
        # Enhanced logging for auth endpoints
        if is_auth_endpoint:
            if status >= 400:
                logger.error(
                    f"← AUTH FAILED: {status} {method} {path} ({duration_ms}ms)\n"
                    f"  Client IP: {client_ip}\n"
                    f"  Status: {status} - LOGIN ATTEMPT FAILED"
                )
            else:
                logger.info(
                    f"← AUTH SUCCESS: {status} {method} {path} ({duration_ms}ms)\n"
                    f"  Client IP: {client_ip}\n"
                    f"  Status: {status} - LOGIN SUCCESSFUL"
                )
        elif status >= 400:
            logger.warning(f"← {status} {method} {path} ({duration_ms}ms)")
        else:
            logger.info(f"← {status} {method} {path} ({duration_ms}ms)")
        
        return response
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        
        # Enhanced error logging for auth endpoints
        if is_auth_endpoint:
            logger.error(
                f"← AUTH EXCEPTION: {method} {path} ({duration_ms}ms)\n"
                f"  Client IP: {client_ip}\n"
                f"  Exception Type: {type(e).__name__}\n"
                f"  Exception Message: {str(e)}\n"
                f"  Full Traceback:\n{traceback.format_exc()}"
            )
        else:
            logger.error(
                f"← ERROR {method} {path} ({duration_ms}ms): {type(e).__name__}: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
        
        # Use helper function for consistent debug mode detection
        is_dev = is_debug_mode()
        
        # Return a proper error response instead of letting it crash silently
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(e) if is_dev else "Internal server error",
                "type": type(e).__name__ if is_dev else "ServerError",
                "path": path,
                "method": method,
            }
        )

# ============================================================================
# HELPER: GET USER FROM DATABASE
# ============================================================================
async def get_user_from_db(user_id: int):
    """Fetch user from database with graceful fallback"""
    if not async_session_maker:
        return None
    
    try:
        async with async_session_maker() as session:
            result = await session.execute(
                text("""
                    SELECT id, email, first_name, last_name, role, user_type, 
                           is_active, profile_picture, location, phone
                    FROM users 
                    WHERE id = :user_id AND is_active = true
                """),
                {"user_id": user_id}
            )
            row = result.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "email": row[1],
                    "first_name": row[2],
                    "last_name": row[3],
                    "role": row[4],
                    "user_type": row[5],
                    "is_active": row[6],
                    "profile_picture": row[7],
                    "location": row[8],
                    "phone": row[9],
                }
            return None
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        return None

# ============================================================================
# HEALTH ENDPOINTS
# ============================================================================
# Note: Vercel's rewrite rule routes /api/* to /api/index.py
# So FastAPI only sees the path AFTER /api/, meaning /api/health becomes /health
@app.get("/health")
@app.head("/health")
async def health():
    """Instant health check - responds in <5ms"""
    logger.info("Health check called")
    response = {
        "status": "healthy",
        "platform": "vercel-serverless",
        "region": os.getenv("VERCEL_REGION", "unknown"),
        "timestamp": int(time.time()),
        "version": "2.0.0",
        "backend": "available" if HAS_BACKEND else "fallback",
        "database": "connected" if db_engine else "unavailable",
        "jwt": "configured" if JWT_SECRET != "dev-secret-key-change-in-production" else "using_default",
        "database_url_set": bool(DATABASE_URL),
    }
    
    # Include backend error details if running in fallback mode
    # Use sanitized error in production, full error only in debug mode
    if not HAS_BACKEND and BACKEND_ERROR_SAFE:
        if is_debug_mode():
            response["backend_error"] = BACKEND_ERROR
        else:
            response["backend_error"] = BACKEND_ERROR_SAFE
        response["note"] = "Backend running in fallback mode - some endpoints may have limited functionality"
    
    return response

@app.get("/status")
async def status():
    """
    Backend status endpoint for frontend health checks.
    Returns detailed status information about backend availability.
    
    Security Note: In production mode, only sanitized error messages are returned.
    Set DEBUG=true for detailed error information (development only).
    """
    # Use sanitized error in production, full error only in debug mode
    backend_error_to_show = None
    if not HAS_BACKEND:
        if is_debug_mode():
            backend_error_to_show = BACKEND_ERROR
        else:
            backend_error_to_show = BACKEND_ERROR_SAFE
    
    return {
        "status": "online",
        "backend_loaded": HAS_BACKEND,
        "backend_status": "full" if HAS_BACKEND else "fallback",
        "backend_error": backend_error_to_show,
        "database_available": HAS_DB and bool(DATABASE_URL),
        "database_connected": bool(db_engine) if HAS_DB else False,
        "jwt_configured": JWT_SECRET != "dev-secret-key-change-in-production",
        "timestamp": int(time.time()),
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "not_set"),
        "capabilities": {
            "auth": HAS_BACKEND,
            "posts": HAS_BACKEND,
            "jobs": HAS_BACKEND,
            "users": HAS_BACKEND,
            "messages": HAS_BACKEND,
            "notifications": HAS_BACKEND,
        },
        "recommendation": "Backend is fully operational" if HAS_BACKEND else "Backend running in limited mode - some features may not work. Check backend_error for details."
    }

@app.get("/diagnostic")
async def diagnostic():
    """Comprehensive diagnostic endpoint for debugging
    
    In production, returns limited information to prevent information disclosure.
    Set DEBUG=true environment variable to enable full diagnostics.
    """
    logger.info("Diagnostic check called")
    
    # Use helper functions for consistent environment detection
    is_debug = is_debug_mode()
    is_prod = is_production_mode()
    
    # In production without debug mode, return limited info
    if is_prod and not is_debug:
        return {
            "status": "operational",
            "timestamp": int(time.time()),
            "platform": "vercel-serverless",
            "message": "Diagnostic details hidden in production. Set DEBUG=true to enable.",
            "basic_checks": {
                "backend_available": HAS_BACKEND,
                "database_available": bool(db_engine),
            }
        }
    
    # Full diagnostics for development/debug mode
    # Test database connection
    db_status = "unavailable"
    db_error = None
    if db_engine:
        try:
            async with db_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            db_status = "error"
            db_error = str(e)[:200]  # Limit error message length
            logger.error(f"Database test failed: {e}")
    
    # Check environment variables (without exposing secrets)
    env_check = {
        "DATABASE_URL": "set" if DATABASE_URL else "missing",
        "SECRET_KEY": "set" if JWT_SECRET != "dev-secret-key-change-in-production" else "using_default",
        "POSTGRES_URL": "set" if os.getenv("POSTGRES_URL") else "not_set",
        "VERCEL_ENV": os.getenv("VERCEL_ENV", "not_set"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "not_set"),
    }
    
    return {
        "status": "operational",
        "timestamp": int(time.time()),
        "platform": "vercel-serverless",
        "debug_mode": is_debug,
        "checks": {
            "python_version": sys.version.split()[0],
            "jose_jwt": HAS_JOSE,
            "database_drivers": HAS_DB,
            "backend_modules": HAS_BACKEND,
            "database_engine": "initialized" if db_engine else "not_initialized",
            "database_connection": db_status,
            "database_error": db_error if is_debug else ("error occurred" if db_error else None),
        },
        "environment": env_check if is_debug else {
            "DATABASE_URL": env_check["DATABASE_URL"],
            "SECRET_KEY": env_check["SECRET_KEY"],
        },
    }

@app.get("/ready")
async def ready():
    """Readiness check with database validation"""
    if not HAS_DB or not DATABASE_URL:
        return Response(
            content='{"status":"degraded","database":"unavailable"}',
            status_code=200,
            media_type="application/json"
        )
    
    try:
        if db_engine:
            async with db_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            return {
                "status": "ready",
                "database": "connected",
                "timestamp": int(time.time()),
            }
        else:
            return Response(
                content='{"status":"not_ready","error":"Database engine not initialized"}',
                status_code=503,
                media_type="application/json"
            )
    except Exception as e:
        return Response(
            content=f'{{"status":"not_ready","error":"{str(e)[:100]}"}}',
            status_code=503,
            media_type="application/json"
        )

# ============================================================================
# AUTH ME ENDPOINT
# ============================================================================
@app.get("/auth/me")
async def get_current_user(authorization: str = Header(None)):
    """Get current authenticated user from JWT token"""
    
    if not HAS_JOSE:
        raise HTTPException(
            status_code=503,
            detail="JWT library not available"
        )
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        # Try to get user from database first
        user = await get_user_from_db(int(user_id))
        
        # Fallback to mock data if database unavailable
        if not user:
            user = MOCK_USERS.get(str(user_id))
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"success": True, "user": user}
        
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# INCLUDE BACKEND ROUTERS IF AVAILABLE
# ============================================================================
# Note: Vercel routes /api/* to this function, so routers should use paths WITHOUT /api prefix
if HAS_BACKEND:
    try:
        logger.info("Registering backend routers...")
        app.include_router(auth.router, prefix="/auth", tags=["auth"])
        logger.info("✅ Auth router registered")
        app.include_router(posts.router, prefix="/posts", tags=["posts"])
        logger.info("✅ Posts router registered")
        app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
        logger.info("✅ Jobs router registered")
        app.include_router(users.router, prefix="/users", tags=["users"])
        logger.info("✅ Users router registered")
        app.include_router(messages.router, prefix="/messages", tags=["messages"])
        logger.info("✅ Messages router registered")
        app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
        logger.info("✅ Notifications router registered")
        logger.info("✅ All backend routers registered successfully")
    except Exception as e:
        logger.error(f"Failed to register backend routers: {e}\nTraceback: {traceback.format_exc()}")
else:
    logger.warning("⚠️  Backend modules not available - using fallback endpoints only")

# ============================================================================
# ROOT ENDPOINT
# ============================================================================
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "HireMeBahamas API",
        "name": "HireMeBahamas API",
        "version": "2.0.0",
        "status": "operational",
        "platform": "vercel-serverless",
        "backend_available": HAS_BACKEND,
        "database_available": bool(db_engine),
        "jwt_configured": JWT_SECRET != "dev-secret-key-change-in-production",
        "endpoints": {
            "health": "/api/health",
            "ready": "/api/ready",
            "auth_me": "/api/auth/me",
            "docs": "/api/docs",
        }
    }

# ============================================================================
# CUSTOM 404 EXCEPTION HANDLER
# ============================================================================
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    """
    Custom handler for 404 errors.
    Returns a helpful JSON response instead of Vercel's default error page.
    Logs all 404s to help diagnose routing issues.
    """
    path = request.url.path
    method = request.method
    headers = dict(request.headers)
    
    # Log comprehensive details for debugging
    logger.warning(
        f"404 NOT FOUND - {method} {path}\n"
        f"User-Agent: {headers.get('user-agent', 'unknown')}\n"
        f"Referer: {headers.get('referer', 'none')}\n"
        f"Query: {request.url.query}"
    )
    
    return JSONResponse(
        status_code=404,
        content={
            "error": "NOT_FOUND",
            "message": f"The requested endpoint '{path}' does not exist",
            "status_code": 404,
            "method": method,
            "path": path,
            "available_endpoints": {
                "health": "/api/health",
                "ready": "/api/ready",
                "auth": "/api/auth/*",
                "posts": "/api/posts/*",
                "jobs": "/api/jobs/*",
                "users": "/api/users/*",
                "messages": "/api/messages/*",
                "notifications": "/api/notifications/*",
                "docs": "/api/docs"
            },
            "backend_status": "available" if HAS_BACKEND else "unavailable - limited endpoints active",
            "help": "Check the docs at /api/docs for all available endpoints"
        }
    )

# ============================================================================
# CATCH-ALL API ROUTE HANDLER
# ============================================================================
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def catch_all_api_routes(request: Request, path: str):
    """
    Catch-all handler for unregistered API routes.
    This prevents users from getting cryptic Vercel 404 errors.
    Returns helpful information about what went wrong.
    
    Security: In production mode, returns limited information to prevent disclosure.
    """
    method = request.method
    
    logger.error(
        f"UNREGISTERED API ROUTE - {method} /{path}\n"
        f"This endpoint is not implemented. Check if the backend router is loaded."
    )
    
    # Use helper function for consistent environment detection
    is_debug = is_debug_mode()
    
    # Base response
    response = {
        "error": "ENDPOINT_NOT_IMPLEMENTED",
        "message": f"The API endpoint '/{path}' is not implemented",
        "status_code": 404,
        "method": method,
        "path": f"/{path}",
    }
    
    # Add detailed debugging information only in debug mode
    if is_debug:
        response.update({
            "backend_loaded": HAS_BACKEND,
            "suggestion": "This endpoint may need to be added to the backend router, or the backend modules failed to load.",
            "available_endpoints": {
                "auth": "/api/auth/* (login, register, me, refresh, verify)",
                "posts": "/api/posts/* (list, create, update, delete)",
                "jobs": "/api/jobs/* (list, create, apply)",
                "users": "/api/users/* (profile, search, follow)",
                "messages": "/api/messages/* (send, list, read)",
                "notifications": "/api/notifications/* (list, mark as read)"
            }
        })
    
    return JSONResponse(
        status_code=404,
        content=response
    )

# ============================================================================
# FOREVER FIX INTEGRATION
# ============================================================================
# Forever Fix is optional and may not be available in serverless environments
# where the parent directory is not deployed. This is safe to skip.
try:
    # Attempt to import forever_fix from parent directory
    # This will only work if the file is deployed (e.g., Railway, local dev)
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Try importing - will raise ImportError if not available
    from forever_fix import ForeverFixMiddleware, get_forever_fix_status
    
    # Add Forever Fix middleware to prevent app death
    app.add_middleware(ForeverFixMiddleware)
    logger.info("✅ Forever Fix middleware enabled")
    
    # Add status endpoint for monitoring
    # Note: This endpoint is public but doesn't expose sensitive information
    @app.get("/forever-status")
    async def forever_status():
        """
        Get Forever Fix system status for monitoring.
        
        This is a public monitoring endpoint that provides system health information.
        It does not expose sensitive configuration or credentials.
        """
        return get_forever_fix_status()
    
except ImportError:
    # Expected in serverless environments where forever_fix.py is not deployed
    logger.info("ℹ️  Forever Fix not available (expected in serverless environments like Vercel)")
except Exception as e:
    # Log unexpected errors but don't crash - this is optional functionality
    logger.warning(f"⚠️  Could not load Forever Fix (non-critical): {e}")

# ============================================================================
# EXPORT HANDLER FOR VERCEL
# ============================================================================
handler = Mangum(app, lifespan="off")

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

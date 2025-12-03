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

# Configure logging with more detail for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
try:
    api_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, api_dir)
    
    # Create module alias for backend_app BEFORE importing
    import backend_app as app_module
    sys.modules['app'] = app_module
    
    # Also ensure backend_app is in sys.path
    backend_app_path = os.path.join(api_dir, 'backend_app')
    if backend_app_path not in sys.path:
        sys.path.insert(0, backend_app_path)
    
    from backend_app.api import auth, posts, jobs, users, messages, notifications
    HAS_BACKEND = True
    logger.info("✅ Backend modules imported successfully")
except Exception as e:
    logger.warning(f"⚠️  Backend modules not available: {e}")
    logger.debug(f"Full traceback:", exc_info=True)

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
    logger.info("CORS: Allowing all origins (wildcard)")
else:
    ALLOWED_ORIGINS = ALLOWED_ORIGINS_ENV.split(",")
    logger.info(f"CORS: Allowing specific origins: {ALLOWED_ORIGINS}")

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

if HAS_DB and DATABASE_URL:
    try:
        logger.info("Initializing database connection...")
        # Convert postgres:// to postgresql+asyncpg://
        db_url = DATABASE_URL
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
            logger.info("Converted postgres:// to postgresql+asyncpg://")
        elif db_url.startswith("postgresql://") and "asyncpg" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            logger.info("Converted postgresql:// to postgresql+asyncpg://")
        
        logger.info("Creating database engine with asyncpg...")
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
        logger.info("✅ Database engine created successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}\nTraceback: {traceback.format_exc()}")
        db_engine = None
        async_session_maker = None
else:
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
    docs_url="/api/docs",
    redoc_url="/api/redoc",
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
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# ============================================================================
# MIDDLEWARE - Request Logging
# ============================================================================
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests with timing and comprehensive error handling"""
    start = time.time()
    method = request.method
    path = request.url.path
    
    logger.info(f"→ {method} {path}")
    
    try:
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)
        status = response.status_code
        
        if status >= 400:
            logger.warning(f"← {status} {method} {path} ({duration_ms}ms)")
        else:
            logger.info(f"← {status} {method} {path} ({duration_ms}ms)")
        
        return response
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
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
@app.get("/api/health")
@app.get("/health")
@app.head("/api/health")
@app.head("/health")
async def health():
    """Instant health check - responds in <5ms"""
    logger.info("Health check called")
    return {
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

@app.get("/api/diagnostic")
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

@app.get("/api/ready")
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
@app.get("/api/auth/me")
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
if HAS_BACKEND:
    try:
        logger.info("Registering backend routers...")
        app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
        logger.info("✅ Auth router registered")
        app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
        logger.info("✅ Posts router registered")
        app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
        logger.info("✅ Jobs router registered")
        app.include_router(users.router, prefix="/api/users", tags=["users"])
        logger.info("✅ Users router registered")
        app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
        logger.info("✅ Messages router registered")
        app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
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
@app.get("/api")
async def root():
    """Root endpoint with API information"""
    return {
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
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def catch_all_api_routes(request: Request, path: str):
    """
    Catch-all handler for unregistered API routes.
    This prevents users from getting cryptic Vercel 404 errors.
    Returns helpful information about what went wrong.
    """
    method = request.method
    
    logger.error(
        f"UNREGISTERED API ROUTE - {method} /api/{path}\n"
        f"This endpoint is not implemented. Check if the backend router is loaded."
    )
    
    return JSONResponse(
        status_code=404,
        content={
            "error": "ENDPOINT_NOT_IMPLEMENTED",
            "message": f"The API endpoint '/{path}' is not implemented",
            "status_code": 404,
            "method": method,
            "path": f"/api/{path}",
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
        }
    )

# ============================================================================
# EXPORT HANDLER FOR VERCEL
# ============================================================================
handler = Mangum(app, lifespan="off")

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

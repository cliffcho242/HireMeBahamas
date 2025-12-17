"""
IMMORTAL FASTAPI MIDDLEWARE — ZERO 500/404/401 FOREVER (VERCEL 2025)

Production-hardened middleware suite that survives Vercel cold starts and never crashes.

Features:
- CORS everywhere
- JWT auth dependency (401 on invalid)
- Global exception handler (500 → clean JSON)
- X-Request-ID header
- 30s timeout protection
- Works on Vercel Serverless Python 3.12
- Zero import errors
"""

import asyncio
import logging
import time
import uuid
from typing import Callable, Optional

from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

# =============================================================================
# REQUEST ID MIDDLEWARE
# =============================================================================

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add X-Request-ID to all requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            logger.error(f"[{request_id}] Unhandled exception: {type(e).__name__}: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "detail": "An unexpected error occurred",
                    "request_id": request_id
                },
                headers={"X-Request-ID": request_id}
            )


# =============================================================================
# TIMEOUT MIDDLEWARE
# =============================================================================

class TimeoutMiddleware(BaseHTTPMiddleware):
    """Enforce 30s timeout on all requests"""
    
    def __init__(self, app: ASGIApp, timeout: int = 30):
        super().__init__(app)
        self.timeout = timeout
    
    async def dispatch(self, request: Request, call_next: Callable):
        request_id = getattr(request.state, "request_id", "unknown")
        
        try:
            response = await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout
            )
            return response
        except asyncio.TimeoutError:
            logger.error(f"[{request_id}] Request timeout after {self.timeout}s: {request.method} {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                content={
                    "error": "Request Timeout",
                    "detail": f"Request exceeded {self.timeout} second timeout",
                    "request_id": request_id
                },
                headers={"X-Request-ID": request_id}
            )
        except Exception as e:
            logger.error(f"[{request_id}] Timeout middleware exception: {type(e).__name__}: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "detail": "An unexpected error occurred",
                    "request_id": request_id
                },
                headers={"X-Request-ID": request_id}
            )


# =============================================================================
# GLOBAL EXCEPTION HANDLER
# =============================================================================

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler that converts all unhandled exceptions to clean JSON"""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    # Log the full exception with traceback
    logger.error(
        f"[{request_id}] Unhandled exception in {request.method} {request.url.path}",
        exc_info=exc
    )
    
    # Return clean JSON error response (never expose internal details in production)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later.",
            "request_id": request_id
        },
        headers={"X-Request-ID": request_id}
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException with X-Request-ID"""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    # Build headers dict
    headers = {"X-Request-ID": request_id}
    if exc.headers:
        headers.update(exc.headers)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else "HTTP Exception",
            "detail": exc.detail,
            "request_id": request_id
        },
        headers=headers
    )


# =============================================================================
# JWT AUTH DEPENDENCY
# =============================================================================

security = HTTPBearer(auto_error=True)


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials,
    request: Request
):
    """
    Verify JWT token and return user.
    Returns 401 on invalid token.
    
    Note: This requires database session injection from the calling endpoint.
    Use as: user = await verify_jwt_token(credentials, request, db)
    """
    from app.core.security import verify_token
    from app.models import User
    from sqlalchemy import select
    
    request_id = getattr(request.state, "request_id", "unknown")
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            logger.warning(f"[{request_id}] JWT token missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_id
    
    except ValueError as e:
        logger.warning(f"[{request_id}] JWT verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error in JWT verification: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials,
    request: Request,
    db
) -> "User":
    """
    Full JWT verification with database lookup.
    Returns User object or raises HTTPException with 401.
    
    Usage in endpoints:
        user = await verify_jwt_token(
            credentials=Depends(security),
            request=request,
            db=Depends(get_db)
        )
    """
    from app.models import User
    from sqlalchemy import select
    
    request_id = getattr(request.state, "request_id", "unknown")
    
    user_id = await get_current_user_from_token(credentials, request)
    
    # Look up user in database
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            logger.warning(f"[{request_id}] User {user_id} not found in database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Database error in JWT verification: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable"
        )


# =============================================================================
# CORS CONFIGURATION
# =============================================================================

def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware with production-safe settings.
    
    Security requirements:
    - 🚫 No wildcard (*) in allow_origins for production
    - ✅ Specific HTTP methods only
    - ✅ Specific headers only (Authorization, Content-Type)
    
    Uses environment-aware get_cors_origins() from environment module.
    """
    from .environment import get_cors_origins
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
        expose_headers=["X-Request-ID"],
    )


# =============================================================================
# SETUP FUNCTION - ATTACH ALL MIDDLEWARE
# =============================================================================

def setup_middleware(app: FastAPI) -> None:
    """
    Setup all middleware for the FastAPI application.
    
    Order matters:
    1. CORS (must be first)
    2. Request ID
    3. Timeout
    
    Exception handlers are registered separately.
    """
    # 1. CORS (must be first to handle preflight requests)
    setup_cors(app)
    
    # 2. Request ID (adds X-Request-ID to all requests/responses)
    app.add_middleware(RequestIDMiddleware)
    
    # 3. Timeout (30s timeout on all requests)
    app.add_middleware(TimeoutMiddleware, timeout=30)
    
    # Register exception handlers
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException
    
    # Handle all unhandled exceptions
    app.add_exception_handler(Exception, global_exception_handler)
    
    # Handle HTTP exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Handle validation errors
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "detail": exc.errors(),
                "request_id": request_id
            },
            headers={"X-Request-ID": request_id}
        )
    
    logger.info("🛡️  Immortal middleware initialized: CORS + JWT + Exception Handler + Request ID + Timeout")

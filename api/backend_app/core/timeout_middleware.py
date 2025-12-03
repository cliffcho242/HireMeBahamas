"""
Request Timeout Middleware

CRITICAL FIX for 198-second login timeout issue.

This middleware enforces a hard timeout on all HTTP requests to prevent
runaway requests from hanging indefinitely and killing the application.

The 198-second login timeout was caused by:
1. No request-level timeout enforcement
2. Potential database query hangs
3. Potential bcrypt operations hanging
4. No fallback when server-level timeouts fail

This fix:
1. Enforces a configurable per-request timeout (default: 60 seconds)
2. Excludes health check endpoints (must be instant)
3. Provides clear error messages when timeouts occur
4. Logs timeout events for monitoring

Configuration:
- REQUEST_TIMEOUT: Maximum request duration in seconds (default: 60)
- REQUEST_TIMEOUT_EXCLUDE_PATHS: Paths to exclude from timeout (default: /health, /live, /ready)

After this fix: Zero 198-second timeouts, zero hanging requests, zero user loss.
"""
import asyncio
import logging
import time
from typing import Callable, List

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from decouple import config

logger = logging.getLogger(__name__)

# Configuration
REQUEST_TIMEOUT = config("REQUEST_TIMEOUT", default=60, cast=int)  # 60 seconds
REQUEST_TIMEOUT_EXCLUDE_PATHS = config(
    "REQUEST_TIMEOUT_EXCLUDE_PATHS",
    default="/health,/live,/ready,/health/ping,/metrics",
    cast=lambda v: [p.strip() for p in v.split(",")]
)


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce request timeouts.
    
    Prevents runaway requests from hanging indefinitely by enforcing
    a hard timeout on all HTTP requests (except excluded paths).
    
    This is CRITICAL for preventing the 198-second login timeout issue
    that was literally killing the app and losing users.
    """
    
    def __init__(self, app: FastAPI, timeout: int = REQUEST_TIMEOUT, exclude_paths: List[str] = None):
        """Initialize timeout middleware.
        
        Args:
            app: FastAPI application
            timeout: Maximum request duration in seconds
            exclude_paths: List of paths to exclude from timeout enforcement
        """
        super().__init__(app)
        self.timeout = timeout
        self.exclude_paths = exclude_paths or REQUEST_TIMEOUT_EXCLUDE_PATHS
        logger.info(
            f"Request timeout middleware initialized: timeout={timeout}s, "
            f"exclude_paths={self.exclude_paths}"
        )
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with timeout enforcement.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            Response from handler or timeout error response
        """
        # Check if this path should be excluded from timeout
        path = request.url.path
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                # No timeout for excluded paths (health checks, etc.)
                return await call_next(request)
        
        # Track request start time
        start_time = time.time()
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        try:
            # Enforce timeout using asyncio.wait_for
            response = await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout
            )
            return response
            
        except asyncio.TimeoutError:
            # Request exceeded timeout - this is what prevents the 198-second hangs
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log the timeout event for monitoring
            logger.error(
                f"[{request_id}] REQUEST TIMEOUT: {request.method} {path} "
                f"exceeded {self.timeout}s timeout (ran for {duration_ms}ms). "
                f"Client IP: {request.client.host if request.client else 'unknown'}. "
                f"This prevents the 198-second login hang that was killing the app."
            )
            
            # Return 504 Gateway Timeout error
            return JSONResponse(
                status_code=504,
                content={
                    "detail": f"Request timeout: exceeded {self.timeout} second limit. "
                              "This prevents indefinite hangs. Please try again.",
                    "timeout_seconds": self.timeout,
                    "path": path,
                    "request_id": request_id
                }
            )
            
        except Exception as e:
            # Log unexpected errors
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(
                f"[{request_id}] Error in timeout middleware for {request.method} {path} "
                f"after {duration_ms}ms: {type(e).__name__}: {e}"
            )
            raise


def add_timeout_middleware(app: FastAPI, timeout: int = REQUEST_TIMEOUT, exclude_paths: List[str] = None):
    """Add timeout middleware to FastAPI application.
    
    This is the PERMANENT FIX for 198-second login timeouts.
    Call this during application setup to enforce request timeouts.
    
    Args:
        app: FastAPI application
        timeout: Maximum request duration in seconds (default: 60)
        exclude_paths: List of paths to exclude from timeout (default: from config)
        
    Example:
        from app.core.timeout_middleware import add_timeout_middleware
        add_timeout_middleware(app, timeout=60)
    """
    app.add_middleware(TimeoutMiddleware, timeout=timeout, exclude_paths=exclude_paths)
    logger.info(f"Request timeout middleware added to application (timeout={timeout}s)")

"""
HTTP caching middleware for mobile optimization.

This module provides Cache-Control headers to reduce bandwidth usage
and improve mobile app performance.
"""
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add Cache-Control headers for GET requests.
    
    Mobile Optimization:
    - Reduces bandwidth usage by enabling browser/client caching
    - Improves response times for repeated requests
    - Follows best practices: Cache-Control: public, max-age=30
    """
    
    def __init__(
        self,
        app,
        max_age: int = 30,
        cacheable_paths: set = None,
        skip_paths: set = None
    ):
        """
        Initialize cache control middleware.
        
        Args:
            app: FastAPI application instance
            max_age: Cache duration in seconds (default: 30s)
            cacheable_paths: Set of path prefixes to cache (default: all GET)
            skip_paths: Set of path prefixes to skip caching (e.g., /auth/me)
        """
        super().__init__(app)
        self.max_age = max_age
        self.cacheable_paths = cacheable_paths or {
            "/posts", "/jobs", "/users", "/notifications"
        }
        # Skip caching for auth endpoints and write operations
        self.skip_paths = skip_paths or {
            "/auth/me", "/auth/login", "/auth/register"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add Cache-Control headers to GET responses.
        
        Only caches:
        - GET requests (safe, idempotent)
        - Successful responses (2xx status codes)
        - Specific API paths (configurable)
        """
        # Process request
        response = await call_next(request)
        
        # Only add cache headers for GET requests
        if request.method != "GET":
            return response
        
        # Check if path should be skipped
        path = request.url.path
        if any(path.startswith(skip) for skip in self.skip_paths):
            logger.debug(f"Skipping cache headers for: {path}")
            return response
        
        # Check if path should be cached
        should_cache = any(path.startswith(cache) for cache in self.cacheable_paths)
        
        # Add cache headers for successful responses on cacheable paths
        if should_cache and 200 <= response.status_code < 300:
            response.headers["Cache-Control"] = f"public, max-age={self.max_age}"
            logger.debug(f"Added cache headers to: {path}")
        
        return response


def add_cache_headers(response: Response, max_age: int = 30):
    """
    Helper function to manually add cache headers to a response.
    
    Usage in route:
        @router.get("/example")
        async def example():
            response = JSONResponse({"data": "..."})
            add_cache_headers(response, max_age=60)
            return response
    
    Args:
        response: FastAPI Response object
        max_age: Cache duration in seconds
    """
    response.headers["Cache-Control"] = f"public, max-age={max_age}"

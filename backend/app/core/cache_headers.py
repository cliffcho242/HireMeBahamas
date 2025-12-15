"""
Advanced Cache Headers for Facebook-Level Performance

Implements sophisticated caching strategies:
- Edge caching with stale-while-revalidate
- Immutable resources for assets
- Dynamic content with short TTLs
- ETags for efficient validation
"""
import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import Response, Request
from starlette.responses import JSONResponse


def generate_etag(content: Any) -> str:
    """Generate ETag from response content."""
    if isinstance(content, (dict, list)):
        content_str = json.dumps(content, sort_keys=True, default=str)
    else:
        content_str = str(content)
    
    return hashlib.md5(content_str.encode()).hexdigest()


def check_etag_match(request: Request, etag: str) -> bool:
    """Check if client's ETag matches current content."""
    if_none_match = request.headers.get("if-none-match")
    return if_none_match == f'"{etag}"' if if_none_match else False


class CacheStrategy:
    """Cache strategy definitions for different content types."""
    
    # Static assets (images, fonts, compiled JS/CSS) - cache forever
    IMMUTABLE = {
        "Cache-Control": "public, max-age=31536000, immutable",
    }
    
    # Public lists that change infrequently (jobs, users list)
    # Cached at edge, revalidate in background
    PUBLIC_LIST = {
        "Cache-Control": "public, max-age=300, stale-while-revalidate=3600",  # 5min cache, 1hr stale
        "CDN-Cache-Control": "public, max-age=300, stale-while-revalidate=3600",
    }
    
    # Dynamic user-specific content (feed, profile)
    # Short cache, no CDN cache
    PRIVATE_DYNAMIC = {
        "Cache-Control": "private, max-age=30, must-revalidate",
    }
    
    # Real-time content (messages, notifications)
    # No caching
    NO_CACHE = {
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    
    # User profile data (public profiles)
    # Cache with validation
    PUBLIC_PROFILE = {
        "Cache-Control": "public, max-age=600, stale-while-revalidate=1800",  # 10min cache, 30min stale
        "CDN-Cache-Control": "public, max-age=600",
    }
    
    # Job posts (public, changes infrequently)
    JOBS = {
        "Cache-Control": "public, max-age=180, stale-while-revalidate=900",  # 3min cache, 15min stale
        "CDN-Cache-Control": "public, max-age=180",
    }
    
    # Posts/Feed (public, changes more frequently)
    POSTS = {
        "Cache-Control": "public, max-age=60, stale-while-revalidate=300",  # 1min cache, 5min stale
        "CDN-Cache-Control": "public, max-age=60",
    }
    
    # API responses that rarely change
    STATIC_API = {
        "Cache-Control": "public, max-age=3600, stale-while-revalidate=7200",  # 1hr cache, 2hr stale
        "CDN-Cache-Control": "public, max-age=3600",
    }


def apply_cache_headers(
    response: Response,
    strategy: Dict[str, str],
    etag: Optional[str] = None,
    vary: Optional[str] = None,
) -> Response:
    """Apply cache headers to a response.
    
    Args:
        response: FastAPI Response object
        strategy: Cache strategy from CacheStrategy class
        etag: Optional ETag for validation
        vary: Optional Vary header (e.g., "Accept-Encoding, Authorization")
    
    Returns:
        Response with cache headers applied
    """
    # Apply cache strategy headers
    for key, value in strategy.items():
        response.headers[key] = value
    
    # Add ETag if provided
    if etag:
        response.headers["ETag"] = f'"{etag}"'
    
    # Add Vary header for proper cache key generation
    if vary:
        response.headers["Vary"] = vary
    else:
        # Default Vary header for API responses
        response.headers["Vary"] = "Accept-Encoding"
    
    # Add Last-Modified header
    response.headers["Last-Modified"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    return response


def create_cached_response(
    content: Any,
    strategy: Dict[str, str],
    status_code: int = 200,
    use_etag: bool = True,
) -> JSONResponse:
    """Create a JSON response with cache headers.
    
    Args:
        content: Response content (dict or list)
        strategy: Cache strategy from CacheStrategy class
        status_code: HTTP status code
        use_etag: Whether to generate and include ETag
    
    Returns:
        JSONResponse with cache headers
    """
    # Generate ETag if requested
    etag = generate_etag(content) if use_etag else None
    
    # Create response
    response = JSONResponse(content=content, status_code=status_code)
    
    # Apply cache headers
    apply_cache_headers(response, strategy, etag=etag)
    
    return response


def handle_conditional_request(
    request: Request,
    content: Any,
    strategy: Dict[str, str],
) -> JSONResponse:
    """Handle conditional requests with ETag validation.
    
    Returns 304 Not Modified if content hasn't changed.
    
    Args:
        request: FastAPI Request object
        content: Response content for ETag generation
        strategy: Cache strategy to apply
    
    Returns:
        JSONResponse (either 304 or 200 with content)
    """
    # Generate ETag for current content
    etag = generate_etag(content)
    
    # Check if client has matching ETag
    if check_etag_match(request, etag):
        # Return 304 Not Modified (no body)
        response = JSONResponse(content=None, status_code=304)
        response.headers["ETag"] = f'"{etag}"'
        for key, value in strategy.items():
            response.headers[key] = value
        return response
    
    # Return full response with content
    return create_cached_response(content, strategy, use_etag=True)


# Compression hint headers for better performance
COMPRESSION_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Compress-Hint": "on",  # Hint to Vercel/CDN to compress
}


def apply_performance_headers(response: Response) -> Response:
    """Apply general performance optimization headers.
    
    These headers improve performance without affecting caching:
    - Enable compression hints
    - Security headers that don't break functionality
    - Connection keep-alive hints
    """
    # Compression and encoding hints
    response.headers.update(COMPRESSION_HEADERS)
    
    # Keep-alive for better connection reuse
    response.headers["Connection"] = "keep-alive"
    
    return response

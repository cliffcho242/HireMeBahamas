"""
API Response Caching for Facebook-Level Performance

Implements intelligent API response caching:
- Automatic cache key generation from request params
- ETags for efficient cache validation
- Vary header support for different user contexts
- Stale-while-revalidate pattern
"""
import hashlib
import json
import logging
from typing import Any, Callable, Optional, Dict
from functools import wraps

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from .cache import get_cached, set_cached, get_cache_key
from .cache_headers import (
    CacheStrategy,
    apply_cache_headers,
    generate_etag,
    check_etag_match,
)

logger = logging.getLogger(__name__)


def cache_api_response(
    ttl: int = 300,
    strategy: Dict[str, str] = CacheStrategy.PUBLIC_LIST,
    use_etag: bool = True,
    vary_on_user: bool = False,
    key_builder: Optional[Callable] = None,
):
    """
    Decorator for caching API responses with ETags and cache headers.
    
    Args:
        ttl: Cache TTL in seconds (default 5 minutes)
        strategy: Cache strategy from CacheStrategy
        use_etag: Whether to use ETags for validation
        vary_on_user: Whether to vary cache by user (for personalized content)
        key_builder: Optional custom cache key builder function
    
    Usage:
        @cache_api_response(ttl=60, strategy=CacheStrategy.POSTS)
        async def get_posts(request: Request, skip: int = 0, limit: int = 20):
            # Your endpoint logic
            return {"posts": [...]}
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(request, *args, **kwargs)
            else:
                # Default cache key from path, query params, and optionally user
                path = request.url.path
                query_params = dict(request.query_params)
                
                if vary_on_user:
                    # Include user ID in cache key for personalized content
                    user_id = getattr(request.state, 'user_id', None)
                    cache_key = get_cache_key('api', path, query_params, user_id)
                else:
                    cache_key = get_cache_key('api', path, query_params)
            
            # Check for cached response
            cached_response = await get_cached(cache_key)
            
            if cached_response is not None:
                # Check ETag if client provided one
                if use_etag and cached_response.get('etag'):
                    etag = cached_response['etag']
                    if check_etag_match(request, etag):
                        # Return 304 Not Modified
                        logger.debug(f"ETag match for {cache_key}, returning 304")
                        response = Response(status_code=304)
                        response.headers['ETag'] = f'"{etag}"'
                        apply_cache_headers(response, strategy)
                        return response
                
                # Return cached content
                logger.debug(f"Cache hit for {cache_key}")
                content = cached_response.get('content')
                
                # Create response with cache headers
                response = JSONResponse(content=content)
                apply_cache_headers(response, strategy)
                
                if use_etag and cached_response.get('etag'):
                    response.headers['ETag'] = f'"{cached_response["etag"]}"'
                response.headers['X-Cache'] = 'HIT'
                
                return response
            
            # Cache miss - execute endpoint
            logger.debug(f"Cache miss for {cache_key}")
            result = await func(request, *args, **kwargs)
            
            # Handle both dict responses and Response objects
            if isinstance(result, Response):
                return result
            
            # Generate ETag if enabled
            etag = generate_etag(result) if use_etag else None
            
            # Cache the response
            cache_data = {
                'content': result,
                'etag': etag,
            }
            await set_cached(cache_key, cache_data, ttl)
            
            # Create response with cache headers
            response = JSONResponse(content=result)
            apply_cache_headers(response, strategy, etag=etag)
            response.headers['X-Cache'] = 'MISS'
            
            return response
        
        return wrapper
    return decorator


def invalidate_api_cache(pattern: str):
    """
    Invalidate API cache entries matching a pattern.
    
    Args:
        pattern: Cache key pattern (e.g., 'api:/api/posts')
    
    Usage:
        # Invalidate all posts cache
        await invalidate_api_cache('api:/api/posts')
        
        # Invalidate specific user's cache
        await invalidate_api_cache(f'api:/api/users/{user_id}')
    """
    from .cache import invalidate_cache
    return invalidate_cache(pattern)


def build_list_cache_key(request: Request, *args, **kwargs) -> str:
    """
    Build cache key for list endpoints with pagination and filters.
    
    Includes: path, skip, limit, and filter parameters
    """
    path = request.url.path
    query_params = dict(request.query_params)
    
    # Sort params for consistent cache keys
    sorted_params = sorted(query_params.items())
    
    return get_cache_key('api', path, *sorted_params)


def build_user_specific_cache_key(request: Request, *args, **kwargs) -> str:
    """
    Build cache key for user-specific content.
    
    Includes: path, user_id, and request parameters
    """
    path = request.url.path
    user_id = getattr(request.state, 'user_id', 'anonymous')
    query_params = dict(request.query_params)
    
    return get_cache_key('api', path, user_id, query_params)


# Pre-configured decorators for common use cases
def cache_public_list(ttl: int = 120):
    """Cache public list endpoints (jobs, users, etc.) for 2 minutes."""
    return cache_api_response(
        ttl=ttl,
        strategy=CacheStrategy.PUBLIC_LIST,
        use_etag=True,
        vary_on_user=False,
    )


def cache_posts(ttl: int = 60):
    """Cache posts/feed for 1 minute with shorter TTL."""
    return cache_api_response(
        ttl=ttl,
        strategy=CacheStrategy.POSTS,
        use_etag=True,
        vary_on_user=False,
    )


def cache_jobs(ttl: int = 180):
    """Cache job listings for 3 minutes."""
    return cache_api_response(
        ttl=ttl,
        strategy=CacheStrategy.JOBS,
        use_etag=True,
        vary_on_user=False,
    )


def cache_profile(ttl: int = 600):
    """Cache user profiles for 10 minutes."""
    return cache_api_response(
        ttl=ttl,
        strategy=CacheStrategy.PUBLIC_PROFILE,
        use_etag=True,
        vary_on_user=False,
    )


def cache_user_feed(ttl: int = 30):
    """Cache personalized user feed for 30 seconds."""
    return cache_api_response(
        ttl=ttl,
        strategy=CacheStrategy.PRIVATE_DYNAMIC,
        use_etag=True,
        vary_on_user=True,
    )

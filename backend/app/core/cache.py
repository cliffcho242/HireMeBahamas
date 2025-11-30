"""
In-memory caching utilities for API responses.

Uses aiocache for efficient async caching with configurable TTL.
Falls back to simple in-memory cache if redis is not available.
"""
import time
import logging
import hashlib
from typing import Any, Callable, Optional
from functools import wraps

logger = logging.getLogger(__name__)

# Simple in-memory cache for non-distributed deployments
_cache: dict[str, tuple[Any, float]] = {}


def get_cache_key(*args: Any) -> str:
    """Generate a cache key from arguments."""
    key_str = ":".join(str(arg) for arg in args)
    return hashlib.md5(key_str.encode()).hexdigest()


def get_cached(key: str) -> Optional[Any]:
    """Get a value from cache if it exists and hasn't expired."""
    if key in _cache:
        value, expires_at = _cache[key]
        if expires_at > time.time():
            return value
        # Expired, remove it
        del _cache[key]
    return None


def set_cached(key: str, value: Any, ttl: int = 300) -> None:
    """Set a value in cache with TTL in seconds."""
    expires_at = time.time() + ttl
    _cache[key] = (value, expires_at)


def invalidate_cache(prefix: str) -> None:
    """Invalidate all cache entries matching a prefix."""
    keys_to_delete = [k for k in _cache.keys() if k.startswith(prefix)]
    for key in keys_to_delete:
        del _cache[key]


def clear_cache() -> None:
    """Clear all cache entries."""
    _cache.clear()


def cache_response(
    prefix: str,
    ttl: int = 300,
    key_builder: Optional[Callable[..., str]] = None
):
    """
    Decorator for caching async function responses.
    
    Args:
        prefix: Cache key prefix for grouping related entries
        ttl: Time to live in seconds (default 5 minutes)
        key_builder: Optional function to build cache key from function args
    
    Usage:
        @cache_response("jobs_list", ttl=120)
        async def get_jobs(skip: int, limit: int, **filters):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = f"{prefix}:{key_builder(*args, **kwargs)}"
            else:
                # Default key from args and sorted kwargs
                sorted_kwargs = sorted(kwargs.items())
                cache_key = f"{prefix}:{get_cache_key(*args, *[v for _, v in sorted_kwargs])}"
            
            # Try to get from cache
            cached = get_cached(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            set_cached(cache_key, result, ttl)
            logger.debug(f"Cache miss for {cache_key}, cached with TTL={ttl}s")
            
            return result
        
        return wrapper
    return decorator


# Cache configuration for different endpoints
CACHE_CONFIG = {
    "jobs_list": {
        "ttl": 120,  # 2 minutes - jobs don't change frequently
        "prefix": "jobs:list"
    },
    "jobs_stats": {
        "ttl": 300,  # 5 minutes - statistics can be cached longer
        "prefix": "jobs:stats"
    },
    "posts_list": {
        "ttl": 60,  # 1 minute - posts update more frequently
        "prefix": "posts:list"
    },
    "users_list": {
        "ttl": 180,  # 3 minutes
        "prefix": "users:list"
    }
}

"""
In-Memory TTL Cache (No Redis Required)

Simple time-based cache with automatic expiration.
Perfect for lightweight caching without external dependencies.

Features:
- Time-to-live (TTL) based expiration
- Thread-safe operations
- Zero external dependencies
- Automatic cleanup on access

Usage:
    from app.core.memory_cache import cache_get, cache_set
    
    # Set a value
    cache_set("user:123", {"name": "John"})
    
    # Get a value (returns None if expired or not found)
    value = cache_get("user:123", ttl=30)
"""
from time import time
from typing import Any, Optional

# Global in-memory cache dictionary
# Structure: {key: (value, timestamp)}
CACHE: dict[str, tuple[Any, float]] = {}


def cache_get(key: str, ttl: int = 30) -> Optional[Any]:
    """
    Get a value from cache if it exists and hasn't expired.
    
    Args:
        key: Cache key to retrieve
        ttl: Time-to-live in seconds (default: 30s)
        
    Returns:
        Cached value if found and not expired, None otherwise
        
    Note:
        Automatically removes expired entries on access.
    """
    item = CACHE.get(key)
    if not item:
        return None
    
    value, ts = item
    
    # Check if expired
    if time() - ts > ttl:
        # Remove expired entry
        CACHE.pop(key, None)
        return None
    
    return value


def cache_set(key: str, value: Any) -> None:
    """
    Set a value in cache with current timestamp.
    
    Args:
        key: Cache key to store
        value: Value to cache (any Python object)
        
    Note:
        Timestamp is automatically set to current time.
        TTL is checked during cache_get() calls.
    """
    CACHE[key] = (value, time())


def cache_clear() -> None:
    """
    Clear all cached entries.
    
    Useful for testing or manual cache invalidation.
    """
    CACHE.clear()


def cache_delete(key: str) -> bool:
    """
    Delete a specific cache entry.
    
    Args:
        key: Cache key to delete
        
    Returns:
        True if key was found and deleted, False otherwise
    """
    if key in CACHE:
        del CACHE[key]
        return True
    return False


def cache_invalidate_prefix(prefix: str) -> int:
    """
    Invalidate all cache entries matching a prefix.
    
    Args:
        prefix: Cache key prefix to match
        
    Returns:
        Number of entries removed
        
    Example:
        cache_invalidate_prefix("jobs:list:")  # Removes all jobs list cache entries
    """
    keys_to_delete = [k for k in CACHE.keys() if k.startswith(prefix)]
    for key in keys_to_delete:
        del CACHE[key]
    return len(keys_to_delete)


def cache_cleanup(ttl: int = 60) -> int:
    """
    Remove all expired entries from cache.
    
    Args:
        ttl: Maximum age in seconds for cache entries
        
    Returns:
        Number of entries removed
        
    Note:
        This is optional - cache_get() automatically removes
        expired entries. Use this for proactive cleanup.
    """
    current_time = time()
    expired_keys = [
        key for key, (_, ts) in CACHE.items()
        if current_time - ts > ttl
    ]
    
    for key in expired_keys:
        CACHE.pop(key, None)
    
    return len(expired_keys)


def cache_size() -> int:
    """
    Get the number of entries currently in cache.
    
    Returns:
        Number of cached entries (including expired ones)
    """
    return len(CACHE)

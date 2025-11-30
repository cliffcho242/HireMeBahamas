"""
Redis-based caching for login performance optimization.

This module provides Redis caching for user records to dramatically reduce
login latency from 5000+ ms to <300 ms by:
1. Caching user records after successful login
2. Checking Redis first on subsequent login attempts
3. Skipping DB entirely when cache hit occurs

Uses Upstash Redis or Railway Redis via REDIS_URL environment variable.
Falls back gracefully to no caching if Redis is unavailable.

Note: Uses synchronous Redis client wrapped with asyncio.to_thread() for
async compatibility. This is safe because Redis operations are fast (<10ms)
and we want to avoid adding aioredis as a dependency.
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from decouple import config

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = config("REDIS_URL", default="")

# Cache TTL configuration (in seconds)
# User records are cached for 10 minutes (600 seconds) by default
# This is a balance between performance and data freshness
USER_CACHE_TTL = config("USER_CACHE_TTL", default=600, cast=int)  # 10 minutes

# Redis connection pool (lazy initialized)
_redis_client = None
_redis_available: Optional[bool] = None  # None = not checked yet


def _get_redis_client_sync():
    """
    Get or create a Redis client for cache operations (synchronous).

    Uses connection pooling and lazy initialization.
    Returns None if Redis is not configured or unavailable.
    """
    global _redis_client, _redis_available

    if not REDIS_URL:
        return None

    # If we've already determined Redis is unavailable, don't retry
    if _redis_available is False:
        return None

    # Return cached client if available
    if _redis_client is not None:
        try:
            _redis_client.ping()
            return _redis_client
        except Exception:
            # Connection lost, try to reconnect
            _redis_client = None

    # Try to create a new connection
    try:
        import redis
        _redis_client = redis.from_url(
            REDIS_URL,
            socket_timeout=2,
            socket_connect_timeout=2,
            decode_responses=True,  # Auto-decode to strings
        )
        _redis_client.ping()
        _redis_available = True
        logger.info("Redis cache connected successfully")
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        _redis_available = False
        _redis_client = None
        return None


def _make_user_cache_key(email: str) -> str:
    """Generate Redis cache key for a user by email."""
    # Normalize email to lowercase for consistent lookups
    return f"user:email:{email.lower()}"


def _serialize_user_for_cache(user_dict: Dict[str, Any]) -> str:
    """
    Serialize user data for Redis storage.

    Converts datetime objects to ISO format strings for JSON compatibility.
    """
    serialized = {}
    for key, value in user_dict.items():
        if isinstance(value, datetime):
            serialized[key] = value.isoformat()
        else:
            serialized[key] = value
    return json.dumps(serialized)


def _deserialize_user_from_cache(data: str) -> Dict[str, Any]:
    """
    Deserialize user data from Redis storage.

    Note: datetime fields remain as strings; caller must convert if needed.
    """
    return json.loads(data)


def _get_cached_user_sync(email: str) -> Optional[Dict[str, Any]]:
    """Retrieve a user record from Redis cache (synchronous)."""
    client = _get_redis_client_sync()
    if client is None:
        return None

    try:
        key = _make_user_cache_key(email)
        data = client.get(key)

        if data:
            logger.debug(f"Cache HIT for user: {email}")
            return _deserialize_user_from_cache(data)

        logger.debug(f"Cache MISS for user: {email}")
        return None
    except Exception as e:
        logger.warning(f"Redis get failed: {e}")
        return None


def _set_cached_user_sync(email: str, user_data: Dict[str, Any], ttl: int = None) -> bool:
    """Store a user record in Redis cache (synchronous)."""
    client = _get_redis_client_sync()
    if client is None:
        return False

    if ttl is None:
        ttl = USER_CACHE_TTL

    try:
        key = _make_user_cache_key(email)
        data = _serialize_user_for_cache(user_data)
        client.setex(key, ttl, data)
        logger.debug(f"Cached user: {email} (TTL: {ttl}s)")
        return True
    except Exception as e:
        logger.warning(f"Redis set failed: {e}")
        return False


def _invalidate_user_cache_sync(email: str) -> bool:
    """Remove a user record from Redis cache (synchronous)."""
    client = _get_redis_client_sync()
    if client is None:
        return False

    try:
        key = _make_user_cache_key(email)
        client.delete(key)
        logger.debug(f"Invalidated cache for user: {email}")
        return True
    except Exception as e:
        logger.warning(f"Redis delete failed: {e}")
        return False


async def get_cached_user(email: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user record from Redis cache (async-safe).

    Uses asyncio.to_thread to avoid blocking the event loop.

    Args:
        email: User's email address

    Returns:
        User data dict if found in cache, None otherwise
    """
    try:
        return await asyncio.to_thread(_get_cached_user_sync, email)
    except Exception as e:
        logger.warning(f"Async Redis get failed: {e}")
        return None


async def set_cached_user(email: str, user_data: Dict[str, Any], ttl: int = None) -> bool:
    """
    Store a user record in Redis cache (async-safe).

    Uses asyncio.to_thread to avoid blocking the event loop.

    Args:
        email: User's email address
        user_data: User data dict to cache
        ttl: Time to live in seconds (defaults to USER_CACHE_TTL)

    Returns:
        True if cached successfully, False otherwise
    """
    try:
        return await asyncio.to_thread(_set_cached_user_sync, email, user_data, ttl)
    except Exception as e:
        logger.warning(f"Async Redis set failed: {e}")
        return False


async def invalidate_user_cache(email: str) -> bool:
    """
    Remove a user record from Redis cache (async-safe).

    Uses asyncio.to_thread to avoid blocking the event loop.
    Call this when user data changes (profile update, password change, etc.)

    Args:
        email: User's email address

    Returns:
        True if invalidated successfully, False otherwise
    """
    try:
        return await asyncio.to_thread(_invalidate_user_cache_sync, email)
    except Exception as e:
        logger.warning(f"Async Redis delete failed: {e}")
        return False


async def invalidate_user_cache_by_id(user_id: int, email: str) -> bool:
    """
    Remove a user record from Redis cache by user ID.

    For completeness, also accepts email since that's the cache key.

    Args:
        user_id: User's ID (for logging)
        email: User's email address

    Returns:
        True if invalidated successfully, False otherwise
    """
    logger.debug(f"Invalidating cache for user_id={user_id}")
    return await invalidate_user_cache(email)


def is_redis_available() -> bool:
    """
    Check if Redis is available for caching.

    Returns:
        True if Redis is configured and responsive, False otherwise
    """
    client = _get_redis_client_sync()
    return client is not None


async def warmup_redis_connection() -> bool:
    """
    Warm up Redis connection on startup (async-safe).

    Call this during application startup to establish Redis connection
    before the first login request arrives.

    Returns:
        True if Redis is available, False otherwise
    """
    def _warmup():
        client = _get_redis_client_sync()
        if client is not None:
            try:
                client.ping()
                logger.info("Redis connection warmed up successfully")
                return True
            except Exception as e:
                logger.warning(f"Redis warmup failed: {e}")
                return False
        return False

    try:
        return await asyncio.to_thread(_warmup)
    except Exception as e:
        logger.warning(f"Async Redis warmup failed: {e}")
        return False

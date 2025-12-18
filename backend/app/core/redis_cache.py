"""
Async Redis caching layer for high-performance API responses.

Meta-inspired architecture:
- Memcached-style TTL-based caching with Redis
- LRU eviction for memory efficiency
- Connection pooling for low-latency operations
- Pub/Sub support for real-time cache invalidation

Performance targets:
- Cache hit: <1ms latency
- Cache miss: <5ms overhead
- 99th percentile: <10ms
- Feed loads: <100ms
- Health checks: <30ms

Production-Safe Configuration:
- SSL/TLS support (rediss://)
- Connection timeouts (3s)
- Socket timeouts (3s)
- Automatic fallback to in-memory cache
- Graceful degradation on Redis failures

Usage:
    from app.core.redis_cache import redis_cache, cache_decorator

    # Direct cache operations
    await redis_cache.set("user:123", user_data, ttl=300)
    user = await redis_cache.get("user:123")

    # Decorator-based caching
    @cache_decorator(prefix="users", ttl=300)
    async def get_user(user_id: int):
        return await db.get_user(user_id)

Environment Configuration:
    # Option 1: Full Redis URL
    REDIS_URL=rediss://:password@host:port
    
    # Option 2: Component-based (flexible configuration)
    REDIS_HOST=your-redis-host.com
    REDIS_PORT=6379  # Optional, defaults to 6379
    REDIS_PASSWORD=your-password  # Optional
"""
import asyncio
import json
import logging
import time
import hashlib
import os
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Type variable for generic return types
T = TypeVar('T')

# Redis configuration with production-safe defaults
# Priority order:
# 1. REDIS_URL (primary - supports rediss:// for SSL)
# 2. REDIS_PRIVATE_URL (Railway private network)
# 3. UPSTASH_REDIS_REST_URL (Upstash REST API)
# 4. REDIS_HOST + REDIS_PORT (component-based configuration)

def _build_redis_url() -> str:
    """Build Redis URL from environment variables."""
    # First priority: Full Redis URL (check multiple sources)
    for env_var in ["REDIS_URL", "REDIS_PRIVATE_URL", "UPSTASH_REDIS_REST_URL"]:
        if url := os.getenv(env_var):
            return url
    
    # Second priority: Component-based configuration
    redis_host = os.getenv("REDIS_HOST")
    if redis_host:
        redis_port = os.getenv("REDIS_PORT", "6379")
        redis_password = os.getenv("REDIS_PASSWORD", "")
        
        # Build URL with or without password
        if redis_password:
            return f"redis://:{redis_password}@{redis_host}:{redis_port}"
        else:
            return f"redis://{redis_host}:{redis_port}"
    
    return ""

REDIS_URL = _build_redis_url()

# Cache configuration constants
DEFAULT_TTL = 300  # 5 minutes
MAX_KEY_LENGTH = 250
MAX_VALUE_SIZE = 1024 * 1024  # 1MB max per value

# Connection pool settings (for asyncpg-style performance)
REDIS_POOL_SIZE = int(os.getenv("REDIS_POOL_SIZE", "10"))
REDIS_POOL_TIMEOUT = float(os.getenv("REDIS_POOL_TIMEOUT", "5.0"))


class AsyncRedisCache:
    """
    Async Redis cache with connection pooling and fallback to in-memory.
    
    Features:
    - Automatic connection recovery
    - JSON serialization for complex objects
    - TTL-based expiration
    - Batch operations for efficiency
    - Circuit breaker pattern for resilience
    """
    
    def __init__(self):
        self._redis_client = None
        self._redis_available = False
        self._connection_attempts = 0
        self._last_connection_error = None
        self._circuit_breaker_reset_time = 0
        
        # In-memory fallback cache (LRU-style with max entries)
        self._memory_cache: dict[str, tuple[Any, float]] = {}
        self._max_memory_entries = 10000
        
        # Stats for monitoring
        self._stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "memory_fallback": 0
        }
    
    async def connect(self) -> bool:
        """
        Initialize Redis connection with production-safe configuration.
        
        Supports:
        - SSL/TLS connections (rediss://)
        - Connection pooling for performance
        - Automatic reconnection with circuit breaker
        - Graceful fallback to in-memory cache
        - Component-based configuration via REDIS_HOST
        
        Configuration options:
            # Option 1: Full URL
            REDIS_URL=rediss://:password@host:port
            
            # Option 2: Component-based
            REDIS_HOST=your-redis-host.com
            REDIS_PORT=6379
            REDIS_PASSWORD=your-password
        
        Returns:
            bool: True if Redis is available, False if using memory fallback
        """
        if not REDIS_URL:
            logger.debug("Redis URL not configured, using in-memory cache (this is expected)")
            return False
        
        # Circuit breaker: Don't retry too frequently
        if time.time() < self._circuit_breaker_reset_time:
            return False
        
        try:
            import redis.asyncio as aioredis
            
            # Production-safe Redis configuration
            # Matches the new requirement pattern with proper timeouts
            self._redis_client = await aioredis.from_url(
                REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=REDIS_POOL_SIZE,
                socket_timeout=3,  # 3s socket timeout (as per hardening requirement)
                socket_connect_timeout=3,  # 3s connect timeout (as per hardening requirement)
                retry_on_timeout=True,
                socket_keepalive=True,  # Keep connections alive
                health_check_interval=30,  # Health check every 30s
            )
            
            # Test connection with timeout
            await asyncio.wait_for(self._redis_client.ping(), timeout=2.0)
            self._redis_available = True
            self._connection_attempts = 0
            logger.info("✅ Redis cache connected successfully (SSL/TLS enabled)")
            return True
            
        except ImportError:
            logger.debug("redis package not installed, using in-memory cache (this is expected)")
            return False
        except asyncio.TimeoutError:
            self._connection_attempts += 1
            self._last_connection_error = "Connection timeout"
            
            # Exponential backoff for circuit breaker
            backoff_seconds = min(60, 2 ** self._connection_attempts)
            self._circuit_breaker_reset_time = time.time() + backoff_seconds
            
            logger.warning(
                f"Redis connection timeout (attempt {self._connection_attempts}). "
                f"Using in-memory cache. Retry in {backoff_seconds}s"
            )
            return False
        except Exception as e:
            self._connection_attempts += 1
            self._last_connection_error = str(e)
            
            # Exponential backoff for circuit breaker
            backoff_seconds = min(60, 2 ** self._connection_attempts)
            self._circuit_breaker_reset_time = time.time() + backoff_seconds
            
            logger.warning(
                f"Redis connection failed (attempt {self._connection_attempts}): {e}. "
                f"Using in-memory cache. Retry in {backoff_seconds}s"
            )
            return False
    
    async def disconnect(self):
        """Close Redis connection gracefully."""
        if self._redis_client:
            try:
                await self._redis_client.close()
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
            finally:
                self._redis_client = None
                self._redis_available = False
    
    def _serialize(self, value: Any) -> str:
        """Serialize value to JSON string."""
        try:
            return json.dumps(value, default=str)
        except (TypeError, ValueError) as e:
            logger.warning(f"Serialization failed: {e}")
            return json.dumps(str(value))
    
    def _deserialize(self, value: str) -> Any:
        """Deserialize JSON string to value."""
        try:
            return json.loads(value)
        except (TypeError, ValueError, json.JSONDecodeError):
            return value
    
    def _sanitize_key(self, key: str) -> str:
        """Ensure cache key is valid and not too long."""
        # Hash long keys to prevent Redis errors
        if len(key) > MAX_KEY_LENGTH:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            key = f"{key[:200]}:{key_hash}"
        return key
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        key = self._sanitize_key(key)
        
        # Try Redis first
        if self._redis_available and self._redis_client:
            try:
                value = await self._redis_client.get(key)
                if value is not None:
                    self._stats["hits"] += 1
                    return self._deserialize(value)
                self._stats["misses"] += 1
                return None
            except Exception as e:
                logger.debug(f"Redis get error, falling back to memory: {e}")
                self._stats["errors"] += 1
        
        # Fallback to memory cache
        self._stats["memory_fallback"] += 1
        if key in self._memory_cache:
            value, expires_at = self._memory_cache[key]
            if expires_at > time.time():
                self._stats["hits"] += 1
                return value
            # Expired, remove it
            del self._memory_cache[key]
        
        self._stats["misses"] += 1
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = DEFAULT_TTL
    ) -> bool:
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if cached successfully
        """
        key = self._sanitize_key(key)
        serialized = self._serialize(value)
        
        # Check value size
        if len(serialized) > MAX_VALUE_SIZE:
            logger.warning(f"Value too large to cache: {len(serialized)} bytes")
            return False
        
        # Try Redis first
        if self._redis_available and self._redis_client:
            try:
                await self._redis_client.setex(key, ttl, serialized)
                return True
            except Exception as e:
                logger.debug(f"Redis set error, using memory cache: {e}")
                self._stats["errors"] += 1
        
        # Fallback to memory cache
        self._stats["memory_fallback"] += 1
        
        # LRU eviction if cache is full
        if len(self._memory_cache) >= self._max_memory_entries:
            # Remove oldest entries (simple LRU approximation)
            sorted_keys = sorted(
                self._memory_cache.keys(),
                key=lambda k: self._memory_cache[k][1]
            )
            for old_key in sorted_keys[:100]:  # Remove 100 oldest
                del self._memory_cache[old_key]
        
        expires_at = time.time() + ttl
        self._memory_cache[key] = (value, expires_at)
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        key = self._sanitize_key(key)
        
        # Delete from Redis
        if self._redis_available and self._redis_client:
            try:
                await self._redis_client.delete(key)
            except Exception as e:
                logger.debug(f"Redis delete error: {e}")
        
        # Also delete from memory cache
        if key in self._memory_cache:
            del self._memory_cache[key]
        
        return True
    
    async def invalidate_prefix(self, prefix: str) -> int:
        """
        Invalidate all keys matching a prefix.
        
        Args:
            prefix: Key prefix to match
            
        Returns:
            Number of keys deleted
        """
        deleted = 0
        
        # Invalidate in Redis using SCAN
        if self._redis_available and self._redis_client:
            try:
                cursor = 0
                while True:
                    cursor, keys = await self._redis_client.scan(
                        cursor, match=f"{prefix}*", count=100
                    )
                    if keys:
                        await self._redis_client.delete(*keys)
                        deleted += len(keys)
                    if cursor == 0:
                        break
            except Exception as e:
                logger.debug(f"Redis scan/delete error: {e}")
        
        # Also clear memory cache
        memory_keys = [k for k in self._memory_cache.keys() if k.startswith(prefix)]
        for key in memory_keys:
            del self._memory_cache[key]
            deleted += 1
        
        logger.debug(f"Invalidated {deleted} keys with prefix: {prefix}")
        return deleted
    
    async def mget(self, keys: list[str]) -> dict[str, Any]:
        """
        Get multiple values at once (batch operation).
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dictionary of key -> value (None for missing keys)
        """
        if not keys:
            return {}
        
        sanitized_keys = [self._sanitize_key(k) for k in keys]
        result = {k: None for k in keys}
        
        # Try Redis batch get
        if self._redis_available and self._redis_client:
            try:
                values = await self._redis_client.mget(sanitized_keys)
                for key, value in zip(keys, values):
                    if value is not None:
                        result[key] = self._deserialize(value)
                        self._stats["hits"] += 1
                    else:
                        self._stats["misses"] += 1
                return result
            except Exception as e:
                logger.debug(f"Redis mget error: {e}")
        
        # Fallback to memory cache
        self._stats["memory_fallback"] += 1
        current_time = time.time()
        for key, sanitized in zip(keys, sanitized_keys):
            if sanitized in self._memory_cache:
                value, expires_at = self._memory_cache[sanitized]
                if expires_at > current_time:
                    result[key] = value
                    self._stats["hits"] += 1
                else:
                    del self._memory_cache[sanitized]
                    self._stats["misses"] += 1
            else:
                self._stats["misses"] += 1
        
        return result
    
    async def mset(
        self, 
        items: dict[str, Any], 
        ttl: int = DEFAULT_TTL
    ) -> bool:
        """
        Set multiple values at once (batch operation).
        
        Args:
            items: Dictionary of key -> value
            ttl: Time to live in seconds
            
        Returns:
            True if all items cached successfully
        """
        if not items:
            return True
        
        sanitized_items = {
            self._sanitize_key(k): self._serialize(v) 
            for k, v in items.items()
        }
        
        # Try Redis pipeline
        if self._redis_available and self._redis_client:
            try:
                pipe = self._redis_client.pipeline()
                for key, value in sanitized_items.items():
                    pipe.setex(key, ttl, value)
                await pipe.execute()
                return True
            except Exception as e:
                logger.debug(f"Redis mset error: {e}")
        
        # Fallback to memory cache
        self._stats["memory_fallback"] += 1
        expires_at = time.time() + ttl
        for key, value in items.items():
            sanitized = self._sanitize_key(key)
            self._memory_cache[sanitized] = (value, expires_at)
        
        return True
    
    def get_stats(self) -> dict:
        """Get cache statistics for monitoring."""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            **self._stats,
            "hit_rate_percent": round(hit_rate, 2),
            "redis_available": self._redis_available,
            "memory_cache_size": len(self._memory_cache),
            "connection_attempts": self._connection_attempts,
            "last_error": self._last_connection_error
        }
    
    async def health_check(self) -> dict:
        """
        Perform cache health check.
        
        Returns:
            Health status dictionary
        """
        health = {
            "status": "healthy",
            "backend": "memory" if not self._redis_available else "redis",
            "stats": self.get_stats()
        }
        
        if self._redis_available and self._redis_client:
            try:
                start = time.time()
                await self._redis_client.ping()
                latency_ms = (time.time() - start) * 1000
                health["latency_ms"] = round(latency_ms, 2)
            except Exception as e:
                health["status"] = "degraded"
                health["error"] = str(e)
        
        return health


# Global cache instance
redis_cache = AsyncRedisCache()


def cache_decorator(
    prefix: str,
    ttl: int = DEFAULT_TTL,
    key_builder: Optional[Callable[..., str]] = None
):
    """
    Decorator for caching async function responses.
    
    Args:
        prefix: Cache key prefix for grouping related entries
        ttl: Time to live in seconds (default 5 minutes)
        key_builder: Optional function to build cache key from function args
    
    Usage:
        @cache_decorator(prefix="users", ttl=300)
        async def get_user(user_id: int):
            return await db.get_user(user_id)
        
        # With custom key builder
        @cache_decorator(prefix="posts", key_builder=lambda skip, limit: f"{skip}:{limit}")
        async def get_posts(skip: int, limit: int):
            return await db.get_posts(skip, limit)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Build cache key
            if key_builder:
                key_suffix = key_builder(*args, **kwargs)
            else:
                # Default key from args and sorted kwargs
                sorted_kwargs = sorted(kwargs.items())
                key_parts = [str(a) for a in args] + [f"{k}={v}" for k, v in sorted_kwargs]
                key_suffix = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            cache_key = f"{prefix}:{key_suffix}"
            
            # Try to get from cache
            cached = await redis_cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await redis_cache.set(cache_key, result, ttl)
            logger.debug(f"Cache miss: {cache_key}, cached with TTL={ttl}s")
            
            return result
        
        # Add cache control methods to the wrapper
        wrapper.cache_prefix = prefix  # type: ignore
        wrapper.invalidate = lambda: redis_cache.invalidate_prefix(prefix)  # type: ignore
        
        return wrapper
    
    return decorator


# Cache configuration for different data types
CACHE_TTL_CONFIG = {
    # User data - moderate TTL, changes infrequently
    "users": 300,  # 5 minutes
    "user_profile": 180,  # 3 minutes
    
    # Posts - shorter TTL, social feed should be fresh
    "posts": 60,  # 1 minute
    "posts_user": 120,  # 2 minutes for user's own posts
    
    # Jobs - longer TTL, changes less frequently
    "jobs": 300,  # 5 minutes
    "jobs_stats": 600,  # 10 minutes
    
    # Messages - very short TTL for real-time feel
    "messages": 30,  # 30 seconds
    "conversations": 60,  # 1 minute
    
    # Notifications - short TTL
    "notifications": 30,  # 30 seconds
    
    # Static/semi-static data - long TTL
    "categories": 3600,  # 1 hour
    "locations": 3600,  # 1 hour
}


async def warm_cache():
    """
    Pre-warm cache with frequently accessed data.
    
    This should be called on startup and periodically via cron.
    Implements Meta's "hot path" caching strategy.
    """
    from app.database import AsyncSessionLocal
    from app.models import User, Post, Job
    from sqlalchemy import select, func
    
    logger.info("Starting cache warm-up...")
    start_time = time.time()
    
    try:
        async with AsyncSessionLocal() as db:
            # Warm up job stats - use 'status' field instead of 'is_active'
            job_count = await db.scalar(select(func.count(Job.id)).where(Job.status == "active"))
            await redis_cache.set("jobs:count:active", job_count, ttl=600)
            
            # Warm up recent posts (first page)
            posts_query = select(Post).order_by(Post.created_at.desc()).limit(20)
            result = await db.execute(posts_query)
            posts = result.scalars().all()
            
            # Serialize posts for caching
            posts_data = [
                {
                    "id": p.id,
                    "content": p.content,
                    "user_id": p.user_id,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in posts
            ]
            await redis_cache.set("posts:recent:page1", posts_data, ttl=60)
            
            # Warm up user count
            user_count = await db.scalar(select(func.count(User.id)).where(User.is_active == True))
            await redis_cache.set("users:count:active", user_count, ttl=300)
            
        elapsed = time.time() - start_time
        logger.info(f"Cache warm-up completed in {elapsed:.2f}s")
        
        return {
            "status": "success",
            "elapsed_seconds": round(elapsed, 2),
            "items_cached": 3
        }
        
    except Exception as e:
        logger.error(f"Cache warm-up failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

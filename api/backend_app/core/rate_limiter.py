"""
Rate limiting middleware for DDoS protection and abuse prevention.

Implements Redis-based rate limiting with in-memory fallback:
- Protects against DDoS attacks
- Prevents API abuse
- Configurable limits per IP address
- Gracefully degrades to in-memory when Redis unavailable

Default limits:
- 100 requests per 60 seconds per IP address
- Returns HTTP 429 (Too Many Requests) when exceeded

Usage:
    from app.core.rate_limiter import add_rate_limiting_middleware
    
    # In main.py
    add_rate_limiting_middleware(app)
"""
import time
import logging
from typing import Callable, Optional, Dict, List
from collections import defaultdict
from threading import Lock

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from decouple import config

logger = logging.getLogger(__name__)

# Rate limit configuration
RATE_LIMIT_REQUESTS = config("RATE_LIMIT_REQUESTS", default=100, cast=int)
RATE_LIMIT_WINDOW = config("RATE_LIMIT_WINDOW", default=60, cast=int)  # seconds

# Paths to exclude from rate limiting (health checks, etc.)
RATE_LIMIT_EXCLUDE_PATHS = [
    "/health",
    "/health/ping",
    "/live",
    "/ready",
    "/metrics",
]

# Redis configuration - check environment variables in order of precedence
REDIS_URL = (
    config("REDIS_URL", default="") or 
    config("REDIS_PRIVATE_URL", default="") or 
    config("UPSTASH_REDIS_REST_URL", default="")
)


class RateLimiter:
    """
    Rate limiter with Redis backend and in-memory fallback.
    
    Tracks request counts per IP address and enforces configurable limits.
    Automatically falls back to in-memory storage if Redis is unavailable.
    """
    
    def __init__(
        self, 
        requests: int = RATE_LIMIT_REQUESTS, 
        window: int = RATE_LIMIT_WINDOW
    ):
        self.requests = requests
        self.window = window
        
        # Redis client (lazy initialized)
        self._redis_client = None
        self._redis_available = False
        
        # In-memory fallback storage
        self._memory_store: Dict[str, List[float]] = defaultdict(list)
        self._memory_lock = Lock()
        
        # Stats for monitoring
        self._stats = {
            "total_requests": 0,
            "rate_limited": 0,
            "redis_hits": 0,
            "memory_hits": 0,
        }
    
    async def _init_redis(self):
        """Initialize Redis connection if available."""
        if self._redis_available or not REDIS_URL:
            return
        
        try:
            import redis.asyncio as aioredis
            
            self._redis_client = await aioredis.from_url(
                REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
                retry_on_timeout=False,
            )
            
            # Test connection
            await self._redis_client.ping()
            self._redis_available = True
            logger.info("Rate limiter: Redis connected")
            
        except ImportError:
            logger.info("Rate limiter: Using in-memory storage (redis package not installed)")
        except Exception as e:
            logger.info(f"Rate limiter: Using in-memory storage (Redis unavailable: {e})")
    
    async def _check_redis(self, ip: str) -> Optional[bool]:
        """
        Check rate limit using Redis.
        
        Returns:
            True if allowed, False if rate limited, None if Redis unavailable
        """
        if not self._redis_available or not self._redis_client:
            await self._init_redis()
            if not self._redis_available:
                return None
        
        try:
            key = f"rl:{ip}"
            
            # Increment counter and set expiry in one atomic operation
            count = await self._redis_client.incr(key)
            
            # Set expiry only on first request (when count == 1)
            if count == 1:
                await self._redis_client.expire(key, self.window)
            
            self._stats["redis_hits"] += 1
            
            if count > self.requests:
                return False
            
            return True
            
        except Exception as e:
            logger.debug(f"Redis rate limit check failed: {e}")
            self._redis_available = False
            return None
    
    def _check_memory(self, ip: str) -> bool:
        """
        Check rate limit using in-memory storage.
        
        Returns:
            True if allowed, False if rate limited
        """
        with self._memory_lock:
            current_time = time.time()
            window_start = current_time - self.window
            
            # Get request timestamps for this IP
            requests = self._memory_store[ip]
            
            # Remove expired timestamps - use while loop for better performance
            # than list comprehension for large lists
            while requests and requests[0] <= window_start:
                requests.pop(0)
            
            self._stats["memory_hits"] += 1
            
            # Check if rate limit exceeded
            if len(requests) >= self.requests:
                return False
            
            # Add current request timestamp
            requests.append(current_time)
            return True
    
    async def check_rate_limit(self, ip: str) -> bool:
        """
        Check if the IP address has exceeded the rate limit.
        
        Args:
            ip: IP address to check
            
        Returns:
            True if request is allowed, False if rate limited
            
        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        self._stats["total_requests"] += 1
        
        # Try Redis first
        redis_result = await self._check_redis(ip)
        
        if redis_result is not None:
            allowed = redis_result
        else:
            # Fallback to memory
            allowed = self._check_memory(ip)
        
        if not allowed:
            self._stats["rate_limited"] += 1
        
        return allowed
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics for monitoring."""
        return {
            **self._stats,
            "backend": "redis" if self._redis_available else "memory",
            "limit": f"{self.requests} requests per {self.window}s",
        }


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.
    
    Handles proxies and load balancers by checking forwarded headers.
    """
    # Check common forwarded headers
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, use the first one
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct client IP
    if request.client:
        return request.client.host
    
    return "unknown"


async def rate_limit(ip: str) -> None:
    """
    Check rate limit for an IP address and raise exception if exceeded.
    
    Args:
        ip: IP address to check
        
    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    limiter = get_rate_limiter()
    
    if not await limiter.check_rate_limit(ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": str(RATE_LIMIT_WINDOW)}
        )


def add_rate_limiting_middleware(app: FastAPI):
    """
    Add rate limiting middleware to FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    limiter = get_rate_limiter()
    
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next: Callable):
        """Rate limiting middleware for all requests."""
        
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in RATE_LIMIT_EXCLUDE_PATHS):
            return await call_next(request)
        
        # Get client IP
        client_ip = get_client_ip(request)
        
        # Check rate limit
        try:
            if not await limiter.check_rate_limit(client_ip):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Too many requests. Please try again later.",
                        "limit": limiter.requests,
                        "window": limiter.window,
                    },
                    headers={"Retry-After": str(limiter.window)}
                )
        except Exception as e:
            # Log error but don't block request if rate limiter fails
            logger.error(f"Rate limiter error: {e}")
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(limiter.requests)
        response.headers["X-RateLimit-Window"] = str(limiter.window)
        
        return response
    
    logger.info(f"Rate limiting enabled: {limiter.requests} requests per {limiter.window}s")


# Endpoint to check rate limiter stats (for monitoring)
def get_rate_limiter_stats() -> dict:
    """Get rate limiter statistics."""
    limiter = get_rate_limiter()
    return limiter.get_stats()

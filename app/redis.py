"""
STEP 14 — REDIS CACHING (INSTANT SPEED) ✅

Synchronous Redis client for instant caching operations.
Provides blazing-fast response times with proper timeout configuration.

Usage:
    from app.redis import redis_client
    
    # Set cache
    redis_client.set("user:123", "John Doe", ex=300)
    
    # Get cache
    user = redis_client.get("user:123")
"""
import redis
from app.config import REDIS_URL

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)

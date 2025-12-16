"""
STEP 14 — REDIS CACHING (INSTANT SPEED) ✅

Synchronous Redis client for instant caching operations.
Provides blazing-fast response times with proper timeout configuration.

Usage:
    from app.redis import redis_client
    
    # Set cache (only if Redis is available)
    if redis_client:
        redis_client.set("user:123", "John Doe", ex=300)
    
    # Get cache (only if Redis is available)
    if redis_client:
        user = redis_client.get("user:123")

Note: If REDIS_URL is not configured, redis_client will be None.
      Application should check for None before using.
"""
import logging
import redis
from app.config import REDIS_URL

logger = logging.getLogger(__name__)

# Initialize Redis client only if REDIS_URL is configured
# This allows the application to run without Redis (graceful degradation)
redis_client = None

if REDIS_URL:
    try:
        redis_client = redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
    except (redis.RedisError, redis.ConnectionError, OSError) as e:
        # Log error but don't crash on import
        # Catches Redis-specific errors and network-related errors
        logger.warning(f"Failed to initialize Redis client: {e}. Caching will be disabled.")
        redis_client = None

"""
Redis client configuration for instant speed caching.

This module provides a production-ready Redis client with:
- SSL/TLS support (rediss://)
- Connection timeouts (2s)
- Socket timeouts (2s)
- Automatic response decoding
- Connection pooling

Usage:
    from app.redis import redis_client
    
    # Set a value with expiration
    redis_client.setex("key", 300, "value")
    
    # Get a value
    value = redis_client.get("key")
    
    # Delete a key
    redis_client.delete("key")

Configuration:
    Set REDIS_URL environment variable:
    REDIS_URL=rediss://:password@host:port
"""
import redis
from app.config import REDIS_URL

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)

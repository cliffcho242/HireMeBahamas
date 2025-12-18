# Gunicorn and Redis Hardening Configuration

## Overview

This document describes the production hardening configuration implemented for Gunicorn workers and Redis caching.

## Gunicorn Hardening

### Configuration (`gunicorn.conf.py`)

```python
# Worker Configuration
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5

# Hardening Settings (Memory Leak Prevention)
max_requests = 1000           # Restart workers after 1000 requests
max_requests_jitter = 100     # Add randomness to prevent thundering herd
graceful_timeout = 30         # Time to wait for graceful worker shutdown

# Preload Configuration
preload_app = False           # Don't preload when DB/network involved
```

### Benefits

1. **Memory Leak Prevention**: Workers are automatically recycled after 1000 requests, preventing memory leaks from accumulating over time.

2. **Smooth Worker Recycling**: The `max_requests_jitter` adds randomness (0-100 requests) to prevent all workers from restarting simultaneously, avoiding service disruption.

3. **Graceful Shutdown**: Workers have 30 seconds to finish processing requests before being terminated during deployments or restarts.

### How It Works

- When a worker processes ~1000 requests (between 900-1100 due to jitter), Gunicorn gracefully shuts it down and spawns a new worker
- During shutdown, the worker stops accepting new requests but completes in-flight requests
- After `graceful_timeout` (30s), any remaining requests are terminated and the worker is killed

## Redis Configuration Hardening

### Connection Settings

Both Redis implementations (`backend/app/core/redis_cache.py` and `api/backend_app/core/redis_cache.py`) now use:

```python
self._redis_client = await aioredis.from_url(
    REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=REDIS_POOL_SIZE,
    socket_timeout=3,              # 3s socket timeout (hardening)
    socket_connect_timeout=3,      # 3s connect timeout (hardening)
    retry_on_timeout=True,         # Automatic retry on timeout
    socket_keepalive=True,         # Keep connections alive
    health_check_interval=30,      # Health check every 30s
)
```

### Configuration Options

#### Option 1: Full Redis URL
```bash
# Standard Redis
REDIS_URL=redis://host:6379

# Redis with password
REDIS_URL=redis://:password@host:6379

# Redis with SSL/TLS
REDIS_URL=rediss://:password@host:6379
```

#### Option 2: Component-based Configuration
```bash
REDIS_HOST=your-redis-host.com
REDIS_PORT=6379                    # Optional, defaults to 6379
REDIS_PASSWORD=your-password       # Optional
```

### Benefits

1. **Prevents Hung Connections**: 3-second timeouts ensure connections don't hang indefinitely
2. **Automatic Recovery**: Retry on timeout provides resilience against transient failures
3. **Connection Efficiency**: Keepalive reduces connection overhead
4. **Proactive Health Checks**: Regular health checks detect issues early
5. **Flexible Configuration**: Supports both URL and component-based configuration

### Fallback Behavior

If Redis is unavailable:
- Application automatically falls back to in-memory caching
- No service disruption occurs
- Circuit breaker prevents excessive retry attempts
- Exponential backoff reduces resource usage

## Testing

### Run Hardening Tests

```bash
python test_hardening_configuration.py
```

This validates:
- ✅ Gunicorn worker recycling settings
- ✅ Redis timeout configuration
- ✅ REDIS_HOST flexible configuration
- ✅ All hardening parameters are correct

### Expected Output

```
🔒 Testing Hardening Configuration
======================================================================
✅ Gunicorn hardening configuration is correct!
✅ Redis hardening configuration is correct!
✅ Redis flexible configuration works!
======================================================================
🎉 All hardening tests passed!
```

## Use Cases

### Rate Limiting with Redis

```python
from app.core.redis_cache import redis_cache

async def check_rate_limit(user_id: int) -> bool:
    key = f"rate_limit:{user_id}"
    count = await redis_cache.get(key)
    
    if count is None:
        await redis_cache.set(key, 1, ttl=60)  # 1 request in 60s
        return True
    
    if int(count) >= 10:  # Max 10 requests per minute
        return False
    
    await redis_cache.set(key, int(count) + 1, ttl=60)
    return True
```

### Feed Caching

```python
from app.core.redis_cache import cache_decorator

@cache_decorator(prefix="feed", ttl=60)
async def get_user_feed(user_id: int):
    # Expensive database query
    return await db.get_posts_for_user(user_id)
```

### Session Management

```python
from app.core.redis_cache import redis_cache

async def store_session(session_id: str, data: dict):
    await redis_cache.set(
        f"session:{session_id}",
        data,
        ttl=3600  # 1 hour session
    )

async def get_session(session_id: str) -> dict:
    return await redis_cache.get(f"session:{session_id}")
```

### Background Queues

Redis can be used with RQ (Redis Queue) for background job processing:

```python
from redis import Redis
from rq import Queue

redis_client = Redis(
    host=os.environ["REDIS_HOST"],
    port=6379,
    socket_timeout=3,
    socket_connect_timeout=3,
    retry_on_timeout=True
)

queue = Queue(connection=redis_client)
job = queue.enqueue(send_email, user_id=123)
```

## Monitoring

### Check Redis Connection Status

```python
from app.core.redis_cache import redis_cache

# Get connection health
health = await redis_cache.health_check()
print(health)
# {
#     "status": "healthy",
#     "backend": "redis",
#     "latency_ms": 1.23,
#     "stats": {
#         "hits": 1000,
#         "misses": 100,
#         "hit_rate_percent": 90.91
#     }
# }
```

### Check Cache Statistics

```python
from app.core.redis_cache import redis_cache

stats = redis_cache.get_stats()
print(stats)
# {
#     "hits": 1000,
#     "misses": 100,
#     "errors": 0,
#     "memory_fallback": 0,
#     "hit_rate_percent": 90.91,
#     "redis_available": True,
#     "memory_cache_size": 0
# }
```

## Production Deployment

### Environment Variables

Set these in your production environment:

```bash
# Option 1: Redis URL (recommended for managed Redis services)
REDIS_URL=rediss://:your-password@your-redis-host.com:6379

# Option 2: Component-based (more flexible)
REDIS_HOST=your-redis-host.com
REDIS_PORT=6379
REDIS_PASSWORD=your-password

# Optional: Connection pool settings
REDIS_POOL_SIZE=10
REDIS_POOL_TIMEOUT=5.0
```

### Render Deployment

Render automatically provides `REDIS_PRIVATE_URL` when you add Redis:

```bash
# No configuration needed - automatically detected
```

### Render Deployment

Add Redis addon and set `REDIS_URL`:

```bash
REDIS_URL=rediss://red-xxx:password@oregon-redis.render.com:6379
```

### Upstash Deployment

Use Upstash Redis REST URL:

```bash
UPSTASH_REDIS_REST_URL=https://your-instance.upstash.io
```

## Troubleshooting

### Redis Connection Fails

**Symptom**: Application logs show "Redis connection failed, using in-memory cache"

**Solutions**:
1. Check Redis URL is correct: `echo $REDIS_URL`
2. Verify Redis server is running: `redis-cli ping`
3. Check firewall allows connections on port 6379
4. Verify SSL/TLS settings match (redis:// vs rediss://)

### Workers Restart Too Frequently

**Symptom**: Workers restarting every few minutes

**Solutions**:
1. Increase `max_requests` if traffic is very high
2. Check for memory leaks in application code
3. Monitor worker memory usage: `ps aux | grep gunicorn`

### Graceful Timeout Exceeded

**Symptom**: Workers killed before completing requests

**Solutions**:
1. Increase `graceful_timeout` if requests legitimately take longer
2. Optimize slow database queries
3. Add timeouts to external API calls
4. Use background jobs for long-running tasks

## Performance Impact

### Before Hardening
- Memory leaks accumulate over days
- Workers crash due to OOM
- Redis connection hangs cause request timeouts
- Service disruption during deployments

### After Hardening
- Workers recycled automatically (prevents memory leaks)
- Redis connections timeout gracefully (no hangs)
- Smooth deployments with zero downtime
- Production-grade resilience

## References

- [Gunicorn Settings](https://docs.gunicorn.org/en/stable/settings.html)
- [Redis-py Documentation](https://redis-py.readthedocs.io/)
- [Uvicorn Workers](https://www.uvicorn.org/deployment/#gunicorn)

## Security Considerations

### Redis Security
- Always use SSL/TLS in production (`rediss://`)
- Never expose Redis port directly to the internet
- Use strong passwords for Redis authentication
- Enable Redis ACLs for fine-grained access control

### Gunicorn Security
- Run workers as non-root user
- Set appropriate file permissions
- Use environment variables for sensitive configuration
- Enable request logging for audit trails

## Maintenance

### Regular Checks

1. **Weekly**: Monitor Redis hit rate (should be >80%)
2. **Weekly**: Check worker restart frequency
3. **Monthly**: Review Redis memory usage
4. **Monthly**: Update Redis and Gunicorn versions

### Upgrade Path

When upgrading:
1. Test in staging environment first
2. Review breaking changes in release notes
3. Update configuration if needed
4. Run `test_hardening_configuration.py` to validate
5. Deploy during low-traffic periods

---

**Last Updated**: December 2025  
**Tested On**: Python 3.12, Gunicorn 23.0.0, Redis 7.1.0

# Redis Cache Setup Guide - Lightning Fast Backend

## 🎯 Goal
- **Feed loads in <100ms**
- **Health checks <30ms**
- **DB protected from overload**
- **App stays fast as users grow**

## Why Redis?

Facebook, Instagram, and Twitter **DO NOT** hit the database on every request.

Redis gives you:
- ⚡ **Instant responses** - Cache hits in <1ms
- 🔒 **DB protection** - Reduce database load by 80%+
- 📈 **Easy scaling** - Handle 10x more users without DB upgrades
- 💰 **Cost savings** - Reduce database queries and hosting costs

---

## 📦 Where to Host Redis

### Best Options (Ranked):

#### 1. **Upstash Redis** (Recommended)
- ✅ **Serverless** - Pay only for what you use
- ✅ **Global CDN** - Sub-10ms latency worldwide
- ✅ **Free Tier** - 10,000 commands/day free
- ✅ **SSL/TLS** - Secure by default
- 🔗 [Get started](https://upstash.com/)

**Setup:**
```bash
# Get your Redis URL from Upstash dashboard
# Format: rediss://:your-password@global.upstash.io:6379
REDIS_URL=rediss://:abc123xyz@global.upstash.io:6379
```

#### 2. **Render Redis**
- ✅ **Free tier available** - 25MB storage
- ✅ **Same platform as backend** - Low latency
- ✅ **Auto-scaling** - Grows with your app
- 🔗 [Get started](https://render.com/)

**Setup:**
```bash
# Get your Redis URL from Render dashboard
# Format: rediss://:password@hostname:port
REDIS_URL=rediss://:password@red-xxxxx.render.com:6379
```

#### 3. **Railway Redis**
- ✅ **Simple setup** - One-click deployment
- ✅ **Private networking** - Fast internal connections
- ✅ **Usage-based pricing** - No idle charges
- 🔗 [Get started](https://railway.app/)

**Setup:**
```bash
# Railway provides REDIS_URL automatically
# Format: rediss://:password@hostname:port
REDIS_URL=${{Redis.REDIS_URL}}
```

---

## 🚀 Production Setup (Step-by-Step)

### Step 1: Choose Your Redis Provider

Pick one from the options above and create a Redis instance.

### Step 2: Get Your Redis URL

Your Redis URL should look like:
```
rediss://:password@host:port
```

**Important:** 
- Use `rediss://` (with double 's') for SSL/TLS connections
- Never commit your Redis password to git
- Use environment variables for all credentials

### Step 3: Configure Environment Variables

#### For Render (Backend Deployment):
```bash
# In Render Dashboard > Environment Variables
REDIS_URL=rediss://:your-password@your-host:6379
```

#### For Railway (Backend Deployment):
```bash
# In Railway Dashboard > Variables
REDIS_URL=rediss://:your-password@your-host:6379

# OR use Railway's Redis plugin (auto-configures)
# Railway will set REDIS_URL automatically
```

#### For Vercel (If using Vercel backend):
```bash
# In Vercel Dashboard > Settings > Environment Variables
REDIS_URL=rediss://:your-password@your-host:6379
```

### Step 4: Update Your .env File (Local Development)

```bash
# .env file (local development only)
REDIS_URL=rediss://:your-password@your-host:6379

# Optional: Use local Redis for development
# REDIS_URL=redis://localhost:6379
```

### Step 5: Deploy and Test

After setting the environment variable:
1. Deploy your backend
2. Check logs for: `✅ Redis cache connected successfully (SSL/TLS enabled)`
3. Test the cache health endpoint: `GET /health/cache`

---

## 🔧 Connection Configuration

### Production-Safe Settings

The backend is configured with production-safe defaults:

```python
# Connection timeouts
socket_connect_timeout=2  # 2 second connect timeout
socket_timeout=2          # 2 second operation timeout

# Connection pooling
max_connections=10        # Pool of 10 connections
socket_keepalive=True     # Keep connections alive
health_check_interval=30  # Health check every 30s

# Reliability
retry_on_timeout=True     # Auto-retry on timeout
decode_responses=True     # Auto-decode responses to strings
```

### Graceful Fallback

If Redis is unavailable, the app automatically falls back to in-memory caching:
- ✅ App continues to work
- ✅ No errors or crashes
- ⚠️ Cache not shared across instances
- ⚠️ Cache cleared on restart

---

## 📊 Cache Configuration

### Default TTL (Time To Live) Settings

```python
# User data - moderate TTL
users: 300s (5 minutes)
user_profile: 180s (3 minutes)

# Posts - shorter TTL for freshness
posts: 60s (1 minute)
posts_user: 120s (2 minutes)

# Jobs - longer TTL
jobs: 300s (5 minutes)
jobs_stats: 600s (10 minutes)

# Messages - very short TTL
messages: 30s
conversations: 60s (1 minute)

# Notifications - short TTL
notifications: 30s

# Static data - long TTL
categories: 3600s (1 hour)
locations: 3600s (1 hour)
```

### Custom TTL Usage

```python
from app.core.redis_cache import redis_cache

# Cache with custom TTL
await redis_cache.set("my_key", data, ttl=300)  # 5 minutes
```

---

## 🎨 Using Redis Cache in Your Code

### Basic Operations

```python
from app.core.redis_cache import redis_cache

# Get from cache
cached_data = await redis_cache.get("user:123")

# Set in cache with TTL
await redis_cache.set("user:123", user_data, ttl=300)

# Delete from cache
await redis_cache.delete("user:123")

# Invalidate by prefix
await redis_cache.invalidate_prefix("users:")
```

### Using Cache Decorator

```python
from app.core.redis_cache import cache_decorator

@cache_decorator(prefix="users", ttl=300)
async def get_user(user_id: int):
    """This function result will be cached for 5 minutes"""
    return await db.get_user(user_id)

# First call - hits database, caches result
user = await get_user(123)

# Second call - returns from cache (instant)
user = await get_user(123)
```

### Batch Operations

```python
from app.core.redis_cache import redis_cache

# Get multiple keys at once
results = await redis_cache.mget(["user:1", "user:2", "user:3"])

# Set multiple keys at once
await redis_cache.mset({
    "user:1": user1_data,
    "user:2": user2_data,
    "user:3": user3_data
}, ttl=300)
```

---

## 📈 Monitoring Cache Performance

### Health Check Endpoint

```bash
GET /health/cache
```

**Response:**
```json
{
  "status": "healthy",
  "backend": "redis",
  "latency_ms": 1.23,
  "stats": {
    "hits": 1500,
    "misses": 300,
    "hit_rate_percent": 83.33,
    "redis_available": true,
    "memory_cache_size": 0
  }
}
```

### Cache Statistics

```python
from app.core.redis_cache import redis_cache

# Get cache stats
stats = redis_cache.get_stats()
print(f"Hit rate: {stats['hit_rate_percent']}%")
print(f"Total hits: {stats['hits']}")
print(f"Total misses: {stats['misses']}")
```

---

## 🎯 Performance Targets

With Redis configured correctly, you should achieve:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Cache Hit | <1ms | `GET /health/cache` - check `latency_ms` |
| Feed Load | <100ms | Browser DevTools - Network tab |
| Health Check | <30ms | `GET /health` response time |
| Cache Hit Rate | >80% | `GET /health/cache` - check `hit_rate_percent` |

---

## 🐛 Troubleshooting

### Redis Connection Failed

**Symptoms:**
```
Redis connection failed: Connection timeout
Using in-memory cache
```

**Solutions:**
1. Check `REDIS_URL` is set correctly
2. Verify Redis instance is running
3. Check firewall/network settings
4. Ensure SSL is enabled (use `rediss://`)
5. Verify password is correct

### Slow Cache Performance

**Symptoms:**
- Cache hits taking >10ms
- Slow API responses even with cache

**Solutions:**
1. Use a Redis provider close to your backend
2. Check network latency between backend and Redis
3. Consider upgrading Redis plan for more memory
4. Review TTL settings - too short = more cache misses

### High Memory Usage

**Symptoms:**
- Redis memory usage near limit
- Cache eviction errors

**Solutions:**
1. Review TTL settings - make them shorter
2. Reduce `MAX_VALUE_SIZE` in config
3. Implement better cache key strategy
4. Upgrade Redis plan for more memory

### Cache Not Invalidating

**Symptoms:**
- Stale data in responses
- Cache not updating after mutations

**Solutions:**
1. Verify invalidation calls: `await redis_cache.invalidate_prefix("posts")`
2. Check cache keys match between set and invalidate
3. Review TTL - may be too long
4. Check if using correct cache prefix

---

## 🔒 Security Best Practices

### 1. Use SSL/TLS Connections
```bash
# Always use rediss:// (with double 's')
REDIS_URL=rediss://:password@host:port
```

### 2. Never Commit Credentials
```bash
# Add to .gitignore
.env
.env.local
.env.production
```

### 3. Use Strong Passwords
```bash
# Use Redis with authentication
REDIS_URL=rediss://:STRONG_RANDOM_PASSWORD@host:port
```

### 4. Restrict Network Access
- Use private networking when possible
- Configure firewall rules
- Enable Redis AUTH

### 5. Rotate Credentials Regularly
- Change Redis password every 90 days
- Update environment variables after rotation

---

## 📚 Additional Resources

### Redis Providers:
- [Upstash Documentation](https://docs.upstash.com/)
- [Render Redis Guide](https://render.com/docs/redis)
- [Railway Redis Plugin](https://docs.railway.app/databases/redis)

### Redis Best Practices:
- [Redis Official Documentation](https://redis.io/documentation)
- [Redis Security Checklist](https://redis.io/topics/security)
- [Redis Persistence](https://redis.io/topics/persistence)

### Monitoring:
- [Redis Monitoring Guide](https://redis.io/topics/monitoring)
- [Redis Performance Optimization](https://redis.io/topics/optimization)

---

## ✅ Quick Start Checklist

- [ ] Choose Redis provider (Upstash recommended)
- [ ] Create Redis instance
- [ ] Get Redis URL (format: `rediss://:password@host:port`)
- [ ] Set `REDIS_URL` environment variable in deployment platform
- [ ] Deploy backend
- [ ] Check logs for successful Redis connection
- [ ] Test cache health: `GET /health/cache`
- [ ] Monitor cache hit rate (target: >80%)
- [ ] Verify performance targets met (<100ms feed load)

---

## 🎉 Success!

Once configured, your backend will:
- ⚡ Load feeds in <100ms
- 🚀 Handle 10x more users
- 💰 Reduce database costs
- 🔒 Protect database from overload
- 📈 Scale effortlessly

**Need help?** Check the troubleshooting section or review the logs at `/health/cache`.

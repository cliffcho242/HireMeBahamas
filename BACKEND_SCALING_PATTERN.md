# ⚡ BACKEND SCALING PATTERN — Critical Architecture

## 🎯 GOAL
Handle 1M+ users with <200ms response time

---

## 🏗 ARCHITECTURE OVERVIEW

```
                        ┌─────────────────────────────────┐
                        │    API LOAD BALANCER            │
                        │    (Render/Railway)             │
                        │  • Health checks                │
                        │  • SSL termination              │
                        │  • Request distribution         │
                        └──────────────┬──────────────────┘
                                       │
                      ┌────────────────┼────────────────┐
                      │                │                │
                      ▼                ▼                ▼
            ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
            │  FastAPI Pod 1  │ │  FastAPI Pod 2  │ │  FastAPI Pod N  │
            │                 │ │                 │ │                 │
            │  • 4 workers    │ │  • 4 workers    │ │  • 4 workers    │
            │  • 4 threads    │ │  • 4 threads    │ │  • 4 threads    │
            │  • 16 capacity  │ │  • 16 capacity  │ │  • 16 capacity  │
            └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
                     │                   │                   │
                     └───────────────────┼───────────────────┘
                                         │
                         ┌───────────────┼───────────────┐
                         │               │               │
                         ▼               ▼               ▼
                 ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
                 │ Redis Cache  │ │  PostgreSQL  │ │ File Storage │
                 │  (Upstash)   │ │    (Neon)    │ │ (Cloudflare) │
                 │              │ │              │ │      R2       │
                 └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 🔧 COMPONENT 1: API LOAD BALANCER

### Configuration (Render)

**File**: `render.yaml`
```yaml
services:
  - type: web
    name: hiremebahamas-api-lb
    env: python
    plan: standard
    region: oregon
    
    # Autoscaling configuration
    scaling:
      minInstances: 2      # Always 2 pods minimum (high availability)
      maxInstances: 10     # Scale up to 10 pods under load
      targetCPUPercent: 70    # Scale when CPU > 70%
      targetMemoryPercent: 80 # Scale when memory > 80%
    
    # Health check configuration
    healthCheckPath: /health
    healthCheckTimeout: 30
    
    # Build configuration
    buildCommand: |
      pip install --upgrade pip
      pip install -r backend/requirements.txt
    
    # Start command (Gunicorn with optimal settings)
    startCommand: |
      gunicorn backend.app.main:app \
        --workers 4 \
        --threads 4 \
        --worker-class gthread \
        --bind 0.0.0.0:$PORT \
        --timeout 60 \
        --keep-alive 5 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --access-logfile - \
        --error-logfile - \
        --log-level info
    
    # Environment variables
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
      - key: WEB_CONCURRENCY
        value: "4"
      - key: WEB_THREADS
        value: "4"
      - key: DATABASE_URL
        sync: false
      - key: REDIS_URL
        sync: false
      - key: SECRET_KEY
        sync: false
      - key: ENVIRONMENT
        value: "production"
```

### Configuration (Railway)

**File**: `railway.json`
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r backend/requirements.txt"
  },
  "deploy": {
    "startCommand": "gunicorn backend.app.main:app --workers 4 --threads 4 --worker-class gthread --bind 0.0.0.0:$PORT --timeout 60 --access-logfile - --error-logfile -",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "numReplicas": 2
  },
  "scaling": {
    "minReplicas": 2,
    "maxReplicas": 10,
    "cpuThreshold": 70,
    "memoryThreshold": 80
  }
}
```

### Load Balancer Logic

**Round-Robin Distribution**:
```
Request 1 → Pod 1
Request 2 → Pod 2
Request 3 → Pod 3
Request 4 → Pod 1 (cycle repeats)
```

**Health Check Flow**:
```
Every 10 seconds:
  For each pod:
    GET /health
    If status != 200:
      Mark pod as unhealthy
      Remove from rotation
      Attempt restart
```

---

## 🚀 COMPONENT 2: FASTAPI PODS

### Gunicorn Configuration

**File**: `backend/gunicorn.conf.py`
```python
import multiprocessing
import os

# Worker Configuration
workers = int(os.getenv("WEB_CONCURRENCY", "4"))
worker_class = "gthread"
threads = int(os.getenv("WEB_THREADS", "4"))

# Total capacity per pod: workers × threads = 4 × 4 = 16 requests
print(f"🚀 Starting with {workers} workers × {threads} threads = {workers * threads} capacity")

# Connection Settings
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048  # Number of pending connections

# Worker Lifecycle
max_requests = 1000  # Restart worker after 1000 requests (prevent memory leaks)
max_requests_jitter = 100  # Add randomness to prevent all workers restarting at once
timeout = 60  # Worker timeout for long-running requests
graceful_timeout = 30  # Time to finish pending requests during shutdown
keepalive = 5  # Keep-alive connections (reduces overhead)

# Application Loading
preload_app = False  # DON'T preload (allows independent database connections per worker)

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Server Mechanics
worker_tmp_dir = "/dev/shm"  # Use RAM for worker heartbeat (faster than disk)
daemon = False  # Don't daemonize (needed for Docker/Railway/Render)

# Hooks
def on_starting(server):
    """Called before master process starts"""
    print("🔥 Master process starting...")

def on_reload(server):
    """Called when reloading configuration"""
    print("🔄 Configuration reloaded")

def when_ready(server):
    """Called when server is ready"""
    print("✅ Server is ready to accept connections")

def worker_int(worker):
    """Called when worker receives SIGINT or SIGTERM"""
    print(f"⚠️  Worker {worker.pid} received shutdown signal")

def worker_abort(worker):
    """Called when worker receives SIGABRT"""
    print(f"🚨 Worker {worker.pid} aborted")

def on_exit(server):
    """Called before server exits"""
    print("👋 Server shutting down gracefully")
```

### FastAPI Application Structure

**File**: `backend/app/main.py`
```python
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from backend.app.api import auth, posts, jobs, messages, users
from backend.app.core.config import settings
from backend.app.core.database import engine, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="HireMeBahamas API",
    description="Job platform for Bahamas professionals",
    version="2.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# CORS Middleware (allow frontend origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression (compress responses > 1KB)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request ID middleware (for tracing)
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID for tracing"""
    import uuid
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} "
        f"- {response.status_code} - {process_time:.4f}s"
    )
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "request_id": getattr(request.state, "request_id", None)
        }
    )

# Health check endpoints
@app.get("/health")
async def health_check():
    """Fast health check (no database)"""
    return {
        "status": "healthy",
        "service": "hiremebahamas-api",
        "timestamp": time.time()
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check (with database ping)"""
    try:
        # Test database connection
        from backend.app.core.database import test_connection
        await test_connection()
        
        return {
            "status": "ready",
            "service": "hiremebahamas-api",
            "database": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": "disconnected",
                "error": str(e)
            }
        )

# API Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting HireMeBahamas API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Workers: {os.getenv('WEB_CONCURRENCY', 'auto')}")
    logger.info(f"Threads: {os.getenv('WEB_THREADS', 'auto')}")
    
    # Don't create tables (use Alembic migrations instead)
    # await Base.metadata.create_all(bind=engine)
    
    logger.info("✅ API ready")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down HireMeBahamas API...")
    
    # Close database connections
    await engine.dispose()
    
    logger.info("✅ Shutdown complete")
```

---

## 💾 COMPONENT 3: REDIS CACHE

### Cache Strategy

**Cache Layers**:
1. **L1: Application Memory** (in-process, fastest)
2. **L2: Redis** (shared across pods, fast)
3. **L3: Database** (source of truth, slowest)

**Read Flow**:
```
Request → Check L1 → Check L2 (Redis) → Query L3 (Database)
          ↓          ↓                   ↓
       Return     Return              Cache in L2 → Cache in L1 → Return
```

**Write Flow**:
```
Request → Write to Database → Invalidate L2 (Redis) → Invalidate L1
```

### Redis Configuration

**File**: `backend/app/core/cache.py`
```python
import redis.asyncio as aioredis
from typing import Optional, Any
import json
import hashlib
from functools import wraps

# Redis client (Upstash)
redis_client = aioredis.from_url(
    os.getenv("REDIS_URL"),
    encoding="utf-8",
    decode_responses=True,
    max_connections=50,  # Connection pool
    socket_connect_timeout=5,
    socket_keepalive=True
)

# Cache decorator
def cache(ttl: int = 300, key_prefix: str = ""):
    """
    Cache function result in Redis
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [
                key_prefix or func.__name__,
                *[str(arg) for arg in args],
                *[f"{k}={v}" for k, v in sorted(kwargs.items())]
            ]
            cache_key = hashlib.md5(
                ":".join(key_parts).encode()
            ).hexdigest()
            
            # Try to get from cache
            try:
                cached = await redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Cache read error: {e}")
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            try:
                await redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(result, default=str)
                )
            except Exception as e:
                logger.warning(f"Cache write error: {e}")
            
            return result
        return wrapper
    return decorator

# Cache invalidation
async def invalidate_cache(pattern: str):
    """
    Invalidate all cache keys matching pattern
    
    Args:
        pattern: Redis key pattern (e.g., "user:123:*")
    """
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache keys: {pattern}")
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")

# Usage examples
@cache(ttl=600, key_prefix="trending_posts")
async def get_trending_posts(limit: int = 100):
    """Get trending posts (cached for 10 minutes)"""
    return await db.execute(
        select(Post)
        .order_by(Post.likes.desc())
        .limit(limit)
    )

@cache(ttl=300, key_prefix="user_feed")
async def get_user_feed(user_id: int, page: int = 1):
    """Get user's feed (cached for 5 minutes)"""
    return await db.execute(
        select(Post)
        .where(Post.user_id.in_(
            select(Follow.followed_id)
            .where(Follow.follower_id == user_id)
        ))
        .order_by(Post.created_at.desc())
        .offset((page - 1) * 20)
        .limit(20)
    )

# Invalidate on write
async def create_post(post_data: dict, user_id: int):
    """Create post and invalidate feed cache"""
    # Create post
    post = await db.execute(insert(Post).values(**post_data))
    
    # Invalidate user's followers' feeds
    await invalidate_cache(f"user_feed:{user_id}:*")
    
    # Invalidate trending posts
    await invalidate_cache("trending_posts:*")
    
    return post
```

---

## 🗄 COMPONENT 4: POSTGRES (Primary + Replicas)

### Database Connection Pool

**File**: `backend/app/core/database.py`
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
import random

# Primary database (for writes)
primary_url = os.getenv("DATABASE_URL")

# Read replicas (for reads)
replica_urls = [
    os.getenv("DATABASE_READ_REPLICA_1"),
    os.getenv("DATABASE_READ_REPLICA_2"),
    os.getenv("DATABASE_READ_REPLICA_3"),
]
replica_urls = [url for url in replica_urls if url]  # Filter None values

# Create engines
primary_engine = create_async_engine(
    primary_url,
    echo=False,
    pool_size=20,  # Base connections per worker
    max_overflow=40,  # Additional connections under load
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=300,  # Recycle connections every 5 minutes
    connect_args={
        "server_settings": {
            "application_name": "hiremebahamas-api"
        },
        "command_timeout": 30,
        "ssl": "require"
    }
)

# Create replica engines
replica_engines = [
    create_async_engine(
        url,
        echo=False,
        pool_size=20,
        max_overflow=40,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "server_settings": {
                "application_name": "hiremebahamas-api-read"
            },
            "command_timeout": 30,
            "ssl": "require"
        }
    )
    for url in replica_urls
]

# Session factories
AsyncSessionLocal = sessionmaker(
    primary_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

AsyncReplicaSessionLocals = [
    sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    for engine in replica_engines
]

# Dependency for write operations
async def get_db_write():
    """Get database session for write operations (uses primary)"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Round-robin replica selection for better load balancing
_replica_index = 0
_replica_lock = asyncio.Lock()

# Dependency for read operations
async def get_db_read():
    """Get database session for read operations (uses round-robin replica selection)"""
    if not replica_engines:
        # Fall back to primary if no replicas configured
        async for session in get_db_write():
            yield session
        return
    
    # Select replica using round-robin (better load balancing than random)
    global _replica_index
    async with _replica_lock:
        SessionLocal = AsyncReplicaSessionLocals[_replica_index % len(AsyncReplicaSessionLocals)]
        _replica_index = (_replica_index + 1) % len(AsyncReplicaSessionLocals)
    
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Test connection
async def test_connection():
    """Test database connection (for health checks)"""
    async with primary_engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
```

### Query Routing

**Read operations** → Replicas (load balanced)
**Write operations** → Primary only

```python
from typing import Annotated
from fastapi import Depends

# Read endpoint (uses replica)
@app.get("/posts")
async def get_posts(
    page: int = 1,
    db: Annotated[AsyncSession, Depends(get_db_read)] = None
):
    """Get posts (read from replica)"""
    result = await db.execute(
        select(Post)
        .order_by(Post.created_at.desc())
        .offset((page - 1) * 20)
        .limit(20)
    )
    return result.scalars().all()

# Write endpoint (uses primary)
@app.post("/posts")
async def create_post(
    post: PostCreate,
    db: Annotated[AsyncSession, Depends(get_db_write)] = None,
    user: User = Depends(get_current_user)
):
    """Create post (write to primary)"""
    new_post = Post(**post.dict(), user_id=user.id)
    db.add(new_post)
    await db.commit()
    return new_post
```

---

## 📊 MONITORING & OBSERVABILITY

### Metrics to Track

**Application Metrics**:
- Request rate (req/s)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Active connections

**Infrastructure Metrics**:
- CPU usage per pod
- Memory usage per pod
- Network I/O
- Disk I/O

**Database Metrics**:
- Query time (slow queries)
- Connection pool utilization
- Replication lag (primary → replica)
- Cache hit rate

### Health Check System

**3-Tier Health Checks**:

1. **Liveness** (`/health`) - Is the service alive?
2. **Readiness** (`/ready`) - Is the service ready to receive traffic?
3. **Startup** (`/startup`) - Has the service completed initialization?

```python
@app.get("/health")
async def liveness():
    """Liveness probe (fast, no dependencies)"""
    return {"status": "alive"}

@app.get("/ready")
async def readiness():
    """Readiness probe (checks dependencies)"""
    checks = {
        "database": await check_database(),
        "redis": await check_redis()
    }
    
    if all(checks.values()):
        return {"status": "ready", "checks": checks}
    else:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "checks": checks}
        )

@app.get("/startup")
async def startup():
    """Startup probe (checks initialization)"""
    if not app_initialized:
        return JSONResponse(
            status_code=503,
            content={"status": "starting"}
        )
    return {"status": "started"}
```

---

## 🚀 DEPLOYMENT STEPS

### 1. Set Up Load Balancer (Render)

```bash
# Deploy to Render with autoscaling
render up --region oregon --plan standard --autoscale-min 2 --autoscale-max 10
```

### 2. Configure Environment Variables

```bash
# Set on Render dashboard
DATABASE_URL=postgresql://...
DATABASE_READ_REPLICA_1=postgresql://...
DATABASE_READ_REPLICA_2=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=...
ENVIRONMENT=production
WEB_CONCURRENCY=4
WEB_THREADS=4
```

### 3. Deploy Backend Pods

```bash
# Push to git (triggers auto-deploy)
git push origin main
```

### 4. Verify Deployment

```bash
# Check health
curl https://api.hiremebahamas.com/health

# Check readiness
curl https://api.hiremebahamas.com/ready

# Check pod count
render ps
```

### 5. Monitor Scaling

```bash
# Watch autoscaling in action
render logs --tail --filter "scaling"
```

---

## 📈 CAPACITY PLANNING

### Per-Pod Capacity

| Metric | Value |
|--------|-------|
| **Workers** | 4 |
| **Threads per worker** | 4 |
| **Total capacity** | 16 requests |
| **Requests/sec** | ~500 |
| **Peak capacity** | ~1000 req/s (burst) |

### Total Capacity (10 Pods)

| Metric | Value |
|--------|-------|
| **Total workers** | 40 |
| **Total threads** | 160 |
| **Total capacity** | 160 concurrent requests |
| **Requests/sec** | ~5,000 |
| **Peak capacity** | ~10,000 req/s (burst) |

### Database Capacity

| Metric | Value |
|--------|-------|
| **Connections per pod** | 60 (20 base + 40 overflow) |
| **Total connections (10 pods)** | 600 |
| **Queries/sec** | ~10,000 (with replicas) |

---

## ✅ SUCCESS CRITERIA

### Performance Targets
- ✅ Response time: <200ms (p95)
- ✅ Error rate: <0.1%
- ✅ Uptime: 99.9%
- ✅ Throughput: 5,000+ req/s

### Scaling Targets
- ✅ Handle 1M+ concurrent users
- ✅ Auto-scale from 2 to 10 pods
- ✅ Zero-downtime deployments
- ✅ Graceful degradation under load

---

**Ready to scale?** Deploy now! 🚀

See also:
- [Scale to 1M Users Blueprint](./SCALE_TO_1M_USERS_BLUEPRINT.md)
- [Monetization Strategy](./MONETIZATION_STRATEGY.md)
- [Performance Optimization](./PERFORMANCE_OPTIMIZATION.md)

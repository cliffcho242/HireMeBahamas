# ⚠️ DEPRECATED: This Guide Contains Unsafe Database Practices

> **Last Updated:** November 2025 | **Status:** DEPRECATED (December 2025)
> 
> ⛔ **DO NOT USE THIS GUIDE** - It recommends using `--preload` with databases, which is DANGEROUS!

## ⚠️ Why This Guide is Deprecated

The `--preload` flag is **NOT safe for database applications** because:

1. **Database connection pools cannot be safely shared across fork()**
   - Connections established before fork() are shared with child processes
   - This causes connection pool corruption and deadlocks

2. **Worker synchronization issues**
   - Shared state between workers leads to race conditions
   - Database transactions can become corrupted

3. **Health check failures**
   - If database initialization fails during preload, all workers fail
   - No graceful degradation possible

## ✅ Correct Approach (December 2025)

**Use `preload_app = False` in gunicorn.conf.py:**
- Each worker loads the app independently
- Each worker gets its own database connections
- Workers can initialize while health checks respond
- Slightly slower first requests (50-200ms) but safe and reliable

**Safe start command:**
```bash
gunicorn final_backend_postgresql:application --config gunicorn.conf.py
```

**DO NOT ADD `--preload` flag!**

For the current best practices, see:
- `start.sh` - Current safe startup script
- `gunicorn.conf.py` - Current safe configuration
- `RAILWAY_HEALTHCHECK_FIX_SUMMARY.md` - Why preload_app=False is critical

---

# Original Content (UNSAFE - FOR REFERENCE ONLY)

This guide provides the **exact, battle-tested configuration** to eliminate 30-120 second cold starts on Render, even after 10+ hours of no traffic.

**⚠️ WARNING: The following content recommends unsafe database practices. Do not follow these instructions!**

## The Problem

Without preload, cold starts occur because:
1. Container wakes up after sleep
2. Each worker independently imports the app
3. Database connections are established per-worker
4. First request waits for all this to complete (30-120+ seconds)

## The Solution: Gunicorn Preload

With `--preload`, the app loads **once** before workers fork:
1. Master process imports the full app
2. Workers are forked with app already loaded (copy-on-write)
3. First request is instant (<400ms)

---

## Quick Start

### 1. Render Dashboard Start Command

Copy-paste this into your Render service's **Start Command** field:

```bash
gunicorn final_backend_postgresql:application --config gunicorn.conf.py --preload
```

Or use the startup script for migrations + health check:

```bash
bash start.sh
```

### 2. Environment Variables (Render Dashboard)

Set these in your Render service's Environment section:

| Variable | Value | Description |
|----------|-------|-------------|
| `WEB_CONCURRENCY` | `2` | Workers (2 for 512MB Starter, 4 for 2GB Standard) |
| `WEB_THREADS` | `8` | Threads per worker |
| `PRELOAD_APP` | `true` | Enable app preloading |
| `ENVIRONMENT` | `production` | Production mode |
| `FORWARDED_ALLOW_IPS` | `*` | Trust Render's load balancer |

### 3. Verify It Works

After deploy, check the logs for:

```
🚀 Starting Gunicorn server (preload: enabled)
   Workers: 2, Threads: 8, Total capacity: 16 concurrent requests
✅ Server ready in 3.45s - accepting connections
```

Then test response time:

```bash
curl -w "\nTotal: %{time_total}s\n" https://your-app.onrender.com/api/auth/login
```

Expected: `<400ms` even after hours of no traffic.

---

## Configuration Files

### requirements.txt (Already Configured)

```txt
gunicorn==23.0.0
uvicorn[standard]==0.34.1
```

### gunicorn.conf.py (Key Settings)

```python
import os

# Bind to Render's PORT
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# Worker configuration for 1-2GB RAM
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
worker_class = "gthread"
threads = int(os.environ.get("WEB_THREADS", "8"))

# CRITICAL: Enable preload to eliminate cold starts
preload_app = os.environ.get("PRELOAD_APP", "true").lower() in ("true", "1", "yes")

# Timeouts compatible with Render
timeout = 55  # Below Render's ~100s gateway timeout
graceful_timeout = 30
keepalive = 5
```

### start.sh (With Health Check)

```bash
#!/bin/bash
set -e

echo "🔧 Running migrations..."
python add_missing_user_columns.py || echo "Migrations failed, continuing..."

echo "🔍 Preload health check..."
python -c "from final_backend_postgresql import application; print('✅ App loaded')"

echo "🚀 Starting Gunicorn with preload..."
exec gunicorn final_backend_postgresql:application --config gunicorn.conf.py --preload
```

---

## Why This Works

### Memory Model with Preload

```
┌─────────────────────────────────────────────────────┐
│ Master Process                                      │
│                                                     │
│  1. Import final_backend_postgresql                 │
│  2. Load Flask app + all routes                     │
│  3. Initialize database connection pool             │
│  4. Load all dependencies (bcrypt, jwt, etc.)       │
│                                                     │
│  ↓ fork() ↓ fork() ↓ fork()                        │
├─────────────┼─────────────┼─────────────────────────┤
│ Worker 1    │ Worker 2    │ Worker 3 (if RAM allows)│
│             │             │                         │
│ Inherits    │ Inherits    │ Inherits                │
│ pre-loaded  │ pre-loaded  │ pre-loaded              │
│ app via     │ app via     │ app via                 │
│ copy-on-    │ copy-on-    │ copy-on-                │
│ write       │ write       │ write                   │
└─────────────┴─────────────┴─────────────────────────┘
```

### Before vs After

| Metric | Without Preload | With Preload |
|--------|-----------------|--------------|
| First request after boot | 30-120s | <400ms |
| Worker startup time | 10-30s each | <1s each |
| Memory per worker | Full app copy | Shared pages |
| Cold start after sleep | 30-120s | <400ms |

---

## Plan-Specific Configuration

### Render Starter ($7/mo, 512MB RAM)

```bash
WEB_CONCURRENCY=2  # 2 workers
WEB_THREADS=8      # 16 total concurrent requests
```

Memory usage: ~200-300MB with preload sharing

### Render Standard ($25/mo, 2GB RAM)

```bash
WEB_CONCURRENCY=4  # 4 workers
WEB_THREADS=8      # 32 total concurrent requests
```

Memory usage: ~400-600MB with preload sharing

---

## Troubleshooting

### App Fails to Load with Preload

If you see errors during preload, check:

1. **Import errors**: Run locally with `python -c "from final_backend_postgresql import application"`
2. **Environment variables**: Ensure DATABASE_URL is set
3. **Disable preload temporarily**: Set `PRELOAD_APP=false`

### Still Seeing Cold Starts

1. **Check logs** for "preload: enabled"
2. **Verify WEB_CONCURRENCY** is set (not defaulting to CPU count)
3. **Check health check** is using `/health` or `/ping` (not a heavy endpoint)

### Memory Issues

If workers are being killed (OOM):

1. Reduce `WEB_CONCURRENCY` to 1-2
2. Reduce `WEB_THREADS` to 4
3. Check for memory leaks in your code

---

## Additional Optimizations

### 1. Keep-Alive Pinger (Free Tier Only)

If on free tier, add external pinger to prevent sleep:

```yaml
# render.yaml - keep-alive worker
- type: worker
  name: keep-alive
  runtime: python
  plan: free
  startCommand: python keep_alive.py
```

### 2. Health Check Endpoint

Use lightweight `/ping` for Render health checks:

```python
@app.route("/ping")
def ping():
    return "pong", 200  # No DB, instant response
```

### 3. Database Connection Pool

The app uses connection pooling to reuse connections:

```python
from psycopg2 import pool
db_pool = pool.ThreadedConnectionPool(minconn=2, maxconn=10, ...)
```

---

## Summary

| File | Change | Purpose |
|------|--------|---------|
| `gunicorn.conf.py` | `preload_app = True` | Load app before forking |
| `Procfile` | `--preload` flag | Explicit preload |
| `render.yaml` | `--preload` + env vars | Render configuration |
| `start.sh` | Health check + preload | Fail-fast on boot errors |

**Result**: `/api/auth/login` responds in <400ms even after 10 hours of no traffic.

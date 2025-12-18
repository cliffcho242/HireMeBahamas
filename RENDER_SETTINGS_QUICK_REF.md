# 🚀 RENDER SETTINGS QUICK REFERENCE

## 🎯 TL;DR - Final Configuration

Your Render backend is configured with these **locked** settings:

```bash
Workers:     1      # Single worker (optimal for small instances)
Threads:     2      # Minimal threading overhead
Timeout:     120s   # Prevents premature SIGTERM
Keep-alive:  5s     # Connection persistence
Auto-deploy: ON     # Automatic deployments
```

## ⚙️ How Settings Are Applied

Settings are configured in **3 places** (in order of priority):

### 1. Command Line (render.yaml) - HIGHEST PRIORITY ✅

```yaml
startCommand: cd backend && poetry run gunicorn app.main:app 
  --workers 1           # ← CLI setting
  --threads 2           # ← CLI setting
  --timeout 120         # ← CLI setting
  --keep-alive 5        # ← CLI setting
  --config gunicorn.conf.py
```

### 2. gunicorn.conf.py - MEDIUM PRIORITY

```python
# backend/gunicorn.conf.py
workers = int(os.environ.get("WEB_CONCURRENCY", "1"))    # Default: 1
threads = int(os.environ.get("WEB_THREADS", "2"))        # Default: 2
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120")) # Default: 120
keepalive = 5                                             # Fixed: 5s
graceful_timeout = 30                                     # Fixed: 30s
```

### 3. Environment Variables (render.yaml) - LOWEST PRIORITY

```yaml
envVars:
  - key: WEB_CONCURRENCY
    value: "1"           # Backup if CLI not specified
  - key: WEB_THREADS
    value: "2"           # Backup if CLI not specified
  - key: GUNICORN_TIMEOUT
    value: "120"         # Backup if CLI not specified
```

## ✅ Current Configuration Status

| Setting | CLI | Config File | Env Var | Actual Value |
|---------|-----|-------------|---------|--------------|
| Workers | ✅ 1 | ✅ 1 (default) | ✅ 1 | **1** |
| Threads | ✅ 2 | ✅ 2 (default) | ✅ 2 | **2** |
| Timeout | ✅ 120s | ✅ 120s (default) | ✅ 120 | **120s** |
| Keep-alive | ✅ 5s | ✅ 5s (fixed) | N/A | **5s** |
| Graceful | ❌ 30s | ✅ 30s (fixed) | N/A | **30s** |

**Result**: All settings are correctly configured at multiple levels (redundancy).

## 🔍 How to Verify Settings

### Method 1: Check Render Logs (Recommended)

After deployment, look for this in logs:

```
================================================================================
  HireMeBahamas API - Production Configuration
================================================================================
  Workers: 1 (single worker = predictable memory)
  Threads: 2 (async event loop handles concurrency)
  Timeout: 120s (prevents premature SIGTERM)
  Graceful: 30s (clean shutdown)
  Keepalive: 5s (connection persistence)
  Preload: False (safe for database apps)
  Worker Class: uvicorn.workers.UvicornWorker (async)

  This is how production FastAPI apps actually run.
================================================================================

✅ Gunicorn master ready in 0.8s
   Listening on 0.0.0.0:10000
   Health endpoint: GET /health (instant, no DB)
🎉 HireMeBahamas API is READY
```

### Method 2: Test Response Time

```bash
# Health check should respond in <50ms
time curl https://your-app.onrender.com/health

# Expected output:
{"status":"ok"}
# Time: <0.050s
```

### Method 3: Check Process Info (Advanced)

SSH to Render container (if available) and run:

```bash
# List Gunicorn processes
ps aux | grep gunicorn

# Expected:
# 1 master process
# 1 worker process (UvicornWorker)
```

## 🚨 What If Settings Are Wrong?

### Symptom: Multiple Workers Running

**Problem**: Seeing 4+ worker processes

**Cause**: Environment variable override or CLI setting missing

**Fix**:
1. Check render.yaml `startCommand` has `--workers 1`
2. Verify `WEB_CONCURRENCY` env var is "1" (not "4")
3. Redeploy with correct settings

### Symptom: Worker SIGTERM Errors

**Problem**: Logs show "Worker was sent SIGTERM"

**Cause**: Timeout too low or blocking operations

**Fix**:
1. Verify timeout is 120s (not 30s)
2. Check no blocking DB calls at import time
3. Ensure health check doesn't touch DB

### Symptom: Slow Response Times

**Problem**: API takes >500ms to respond

**Cause**: Too many workers competing for resources

**Fix**:
1. Reduce to 1 worker (if not already)
2. Check database connection pool not exhausted
3. Verify async/await used correctly

## 📝 Configuration Files Location

```
HireMeBahamas/
├── render.yaml                    # Render deployment config
│   └── startCommand: --workers 1  # CLI settings (highest priority)
│
├── backend/
│   ├── gunicorn.conf.py          # Gunicorn config (medium priority)
│   │   ├── workers = 1           # Default values
│   │   ├── threads = 2
│   │   └── timeout = 120
│   │
│   ├── Procfile                   # Render/Heroku config (reference)
│   │   └── Same settings as render.yaml
│   │
│   └── app/
│       └── main.py               # FastAPI app
```

## 🎯 Why These Specific Settings?

### Workers = 1
- ✅ Optimal for 512MB-1GB instances
- ✅ No coordination overhead between workers
- ✅ Predictable memory usage (~200-300MB)
- ✅ Simpler debugging
- ✅ Async handles concurrency (100+ connections)

### Threads = 2
- ✅ Minimal overhead (UvicornWorker uses async event loop)
- ✅ Safety net for rare blocking operations
- ✅ Compatible with async/await patterns

### Timeout = 120s
- ✅ Prevents premature SIGTERM during:
  - Slow database connections
  - Large file uploads
  - Batch processing endpoints
- ✅ Gives time for graceful degradation

### Keep-alive = 5s
- ✅ Matches most cloud load balancers
- ✅ Reduces TCP handshake overhead
- ✅ HTTP/1.1 persistent connections

## 🔐 Auto-Deploy Configuration

Auto-deploy is enabled via `render.yaml`:

```yaml
services:
  - type: web
    name: hiremebahamas-backend
    # ... other settings ...
```

When you push to GitHub:
1. GitHub webhook notifies Render
2. Render pulls latest code
3. Runs `buildCommand` (install dependencies)
4. Runs `startCommand` (start server)
5. Health check passes → Deploy succeeds
6. Old instance gracefully shut down

**No manual intervention needed!** 🎉

## ✅ Verification Command

Run this to confirm everything:

```bash
# 1. Check render.yaml
grep "startCommand:" render.yaml

# Should see: --workers 1 --threads 2 --timeout 120 --keep-alive 5

# 2. Check gunicorn.conf.py
grep -E "(workers|threads|timeout|keepalive) =" backend/gunicorn.conf.py

# Should see defaults: 1, 2, 120, 5

# 3. Check environment variables
grep -A 1 "WEB_CONCURRENCY" render.yaml

# Should see: value: "1"
```

## 🎉 Success Criteria

You'll know settings are correct when you see:

✅ **In Render Logs:**
```
Workers: 1
Threads: 2
Timeout: 120s
Keepalive: 5s
```

✅ **In Application Behavior:**
- Health check responds in <50ms
- No worker SIGTERM errors
- Memory usage stable ~200-300MB
- Response times <300ms P99

✅ **In Production:**
- Zero cold starts (Always On)
- 99.9%+ uptime
- No 502 Bad Gateway errors
- Graceful deployments

---

**Last Updated**: December 2025  
**Status**: ✅ VERIFIED & LOCKED  
**Do NOT change these settings** unless you understand the implications.

This is what senior platform engineers ship. 🚀

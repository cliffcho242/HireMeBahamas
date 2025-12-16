# Gunicorn Worker SIGTERM - Understanding and Enhanced Fix

## What You're Seeing

When you see these messages in your logs:
```
[2025-12-16 16:52:59 +0000] [54] [ERROR] Worker (pid:59) was sent SIGTERM!
[2025-12-16 16:52:59 +0000] [54] [ERROR] Worker (pid:61) was sent SIGTERM!
[2025-12-16 16:52:59 +0000] [54] [ERROR] Worker (pid:57) was sent SIGTERM!
```

**This is NORMAL behavior during:**
- ✅ Deployments and service restarts
- ✅ Configuration reloads
- ✅ Manual service restarts
- ✅ Platform maintenance windows
- ✅ Scaling operations (adding/removing workers)

## Understanding the Signals

### SIGTERM (Signal 15) - Graceful Shutdown
- **What it means:** The master process is asking workers to shut down gracefully
- **When it happens:** During normal operations like deployments
- **Is it a problem?** NO - This is expected behavior
- **What workers do:** Complete current requests, then exit cleanly

### SIGABRT (Signal 6) - Forced Termination
- **What it means:** Worker exceeded timeout and is being forcibly killed
- **When it happens:** Worker didn't respond within the timeout period (60s default)
- **Is it a problem?** YES - This indicates a real issue
- **What workers do:** Immediately terminated without cleanup

## Why Gunicorn Logs SIGTERM at ERROR Level

Gunicorn's master process logs SIGTERM at ERROR level for **historical reasons**:
- It's a significant event in the worker lifecycle
- It helps track when workers are being replaced
- It aids in debugging deployment issues

However, this can be confusing because:
- ❌ ERROR level suggests something is wrong
- ✅ But SIGTERM during deployments is perfectly normal

## The Enhanced Fix

### What We've Implemented

#### 1. Enhanced Worker Hooks
Both `worker_int` and `worker_abort` hooks now provide detailed, contextual information:

**For SIGTERM (Normal):**
```
================================================================================
ℹ️  WORKER INTERRUPT SIGNAL RECEIVED - PID 12345
================================================================================
Signal: SIGTERM/SIGINT/SIGQUIT (graceful shutdown)
Worker: 12345
Status: This is NORMAL during:
  ✓ Deployments and service restarts
  ✓ Configuration reloads
  ✓ Manual service restarts
  ✓ Platform maintenance windows

⚠️  Only investigate if this happens frequently OUTSIDE of deployments:
  • Check if workers are timing out during requests (>60s)
  • Review application logs for errors before SIGTERM
  • Monitor memory usage (workers may be OOM killed)
  • Check for slow database queries or API calls
================================================================================
```

**For SIGABRT (Critical):**
```
================================================================================
❌ CRITICAL: WORKER ABORTED - PID 12345
================================================================================
Signal: SIGABRT (forceful termination)
Worker: 12345
Timeout: 60s (exceeded)

⚠️  This worker was forcibly killed because it exceeded the timeout.
This indicates a serious problem that MUST be investigated:

Common causes:
  1. Blocking database operations (long queries, connection issues)
  2. Slow external API calls without timeout
  3. Deadlocks or infinite loops in application code
  4. Database connection pool exhaustion
  5. CPU-intensive operations blocking the event loop

Next steps:
  • Check application logs immediately before this abort
  • Review recent endpoint requests and their duration
  • Monitor database connection pool status
  • Use APM tools to identify slow operations
  • Consider increasing timeout only if operations legitimately need more time
================================================================================
```

#### 2. Custom Logger Configuration
Added `logconfig_dict` to provide better structured logging:
- Separate handlers for console and error streams
- Proper formatting with timestamps and process IDs
- Better integration with Gunicorn's internal logging

#### 3. Startup Timeout Protection
Already implemented in `backend/app/main.py`:
- 5 seconds timeout per startup operation (bcrypt, Redis, cache)
- 20 seconds total startup timeout
- Prevents workers from hanging during initialization

## How to Interpret the Logs

### Scenario 1: Deployment (NORMAL)
```
[INFO] 🚀 Starting Gunicorn...
[ERROR] Worker (pid:59) was sent SIGTERM!  ← Gunicorn's default log
ℹ️  WORKER INTERRUPT SIGNAL RECEIVED - PID 59  ← Our enhanced hook
Status: This is NORMAL during deployments  ← Clear explanation
[INFO] 👶 Worker 123 spawned  ← New worker started
```
**Action:** None needed - this is expected behavior

### Scenario 2: Frequent SIGTERM Outside Deployments (INVESTIGATE)
```
[ERROR] Worker (pid:59) was sent SIGTERM!
ℹ️  WORKER INTERRUPT SIGNAL RECEIVED - PID 59
⚠️  Only investigate if this happens frequently OUTSIDE of deployments
[ERROR] Worker (pid:61) was sent SIGTERM!  ← 2 minutes later
[ERROR] Worker (pid:63) was sent SIGTERM!  ← 2 minutes later
```
**Action:** Investigate - workers may be timing out or OOM killed

### Scenario 3: Worker Timeout (CRITICAL)
```
❌ CRITICAL: WORKER ABORTED - PID 59
Signal: SIGABRT (forceful termination)
Timeout: 60s (exceeded)
⚠️  This worker was forcibly killed because it exceeded the timeout.
```
**Action:** URGENT - investigate immediately, check application logs

## Configuration Details

### Current Settings
```python
# From backend/gunicorn.conf.py
workers = 4  # Number of worker processes
worker_class = "uvicorn.workers.UvicornWorker"  # Async ASGI support
timeout = 60  # Worker timeout in seconds
graceful_timeout = 30  # Graceful shutdown timeout
preload_app = False  # Safe for database applications
keepalive = 5  # Keep-alive timeout
```

### Environment Variables
Override these in your deployment platform:
- `WEB_CONCURRENCY` - Number of workers (default: 4)
- `GUNICORN_TIMEOUT` - Worker timeout in seconds (default: 60)
- `PORT` - Port to bind to (default: 10000)

## Monitoring Best Practices

### What to Monitor

#### ✅ Normal (Expected)
- SIGTERM during deployments (with our enhanced context message)
- Worker spawns (`👶 Worker X spawned`)
- Graceful shutdowns during maintenance

#### ⚠️ Warning (Investigate if Frequent)
- SIGTERM outside deployment windows
- Multiple workers terminating in quick succession
- Workers restarting frequently (every few minutes)

#### ❌ Critical (Investigate Immediately)
- SIGABRT signals (worker timeout)
- Workers killed by OOM killer
- Repeated worker crashes
- Timeout errors in application logs

### Monitoring Commands

**Railway:**
```bash
# View recent logs
railway logs --tail 100

# Search for SIGTERM
railway logs --tail 200 | grep SIGTERM

# Search for SIGABRT (critical)
railway logs --tail 200 | grep SIGABRT
```

**Render:**
```bash
# View logs in dashboard
# Look for SIGTERM vs SIGABRT distinction
```

## Troubleshooting Guide

### If You See Frequent SIGTERM Outside Deployments

1. **Check Memory Usage**
   - Workers may be OOM killed by the platform
   - Look for `killed` or `memory` in logs around SIGTERM

2. **Check Request Duration**
   - Review application logs for slow requests
   - Look for requests taking >60s (timeout)

3. **Check Database Connections**
   - Connection pool exhaustion?
   - Slow queries?
   - Database unavailability?

4. **Check External Dependencies**
   - Redis connection issues?
   - External API timeouts?
   - Network problems?

### If You See SIGABRT (Critical)

1. **Identify the Slow Operation**
   - Check logs immediately before SIGABRT
   - Look for endpoint being processed
   - Review database query logs

2. **Fix the Root Cause**
   - Add timeout to blocking operations
   - Optimize slow database queries
   - Use background tasks for long operations
   - Add connection timeout to external APIs

3. **Only as Last Resort: Increase Timeout**
   ```bash
   # Set GUNICORN_TIMEOUT environment variable
   railway variables set GUNICORN_TIMEOUT=120
   ```
   **Note:** This masks the problem, doesn't fix it!

## Files Modified

1. ✅ `backend/gunicorn.conf.py` - Enhanced hooks and logging
2. ✅ `gunicorn.conf.py` - Enhanced hooks and logging (root copy)
3. ✅ `GUNICORN_SIGTERM_EXPLAINED.md` - This documentation

## Summary

✅ **SIGTERM during deployments is NORMAL** - Don't panic when you see it

✅ **Our enhanced hooks provide clear context** - You'll know if it's normal or not

✅ **SIGABRT is CRITICAL** - This always indicates a problem

✅ **Startup timeout protection prevents hangs** - Workers won't timeout during initialization

✅ **Clear distinction between normal and problematic** - Easy to understand what's happening

## References

- [Gunicorn Server Hooks](https://docs.gunicorn.org/en/stable/settings.html#server-hooks)
- [Gunicorn Worker Model](https://docs.gunicorn.org/en/stable/design.html#worker-model)
- [Unix Signals Reference](https://man7.org/linux/man-pages/man7/signal.7.html)
- [FastAPI Deployment Best Practices](https://fastapi.tiangolo.com/deployment/)

---

**Status:** ✅ Enhanced Fix Deployed
**Date:** 2025-12-16
**Confidence:** HIGH - Clear distinction between normal and problematic signals

# Gunicorn SIGTERM Fix - Quick Reference

## TL;DR
✅ **SIGTERM during deployments is NORMAL** - Don't panic!
❌ **SIGABRT is CRITICAL** - Investigate immediately!

## What's Fixed

### Enhanced Worker Hooks
- `worker_int` - Handles SIGTERM/SIGINT/SIGQUIT with clear context
- `worker_abort` - Handles SIGABRT with critical error diagnostics
- Both hooks now provide formatted, actionable output

### Improved Logging
- Custom `logconfig_dict` for structured logging
- Clear visual separators in diagnostic output
- Output written to stderr to appear near Gunicorn's logs

### Startup Protection
- 5 second timeout per startup operation (bcrypt, Redis, cache)
- 20 second total startup timeout
- Prevents workers from hanging during initialization

## Quick Interpretation Guide

### ✅ NORMAL: SIGTERM During Deployment
```
[ERROR] Worker (pid:59) was sent SIGTERM!
================================================================================
ℹ️  WORKER INTERRUPT SIGNAL RECEIVED - PID 59
================================================================================
Status: This is NORMAL during:
  ✓ Deployments and service restarts
```
**Action:** None - this is expected

### ⚠️ WARNING: Frequent SIGTERM
Multiple SIGTERM messages outside deployment windows
**Action:** Investigate for OOM kills, timeouts, or resource issues

### ❌ CRITICAL: SIGABRT
```
================================================================================
❌ CRITICAL: WORKER ABORTED - PID 59
================================================================================
Signal: SIGABRT (forceful termination)
Timeout: 60s (exceeded)
```
**Action:** URGENT - Check logs, identify slow operation, fix root cause

## Configuration Overview

```python
# Current Settings
workers = 4                              # Worker processes
worker_class = "uvicorn.workers.UvicornWorker"  # Async ASGI
timeout = 60                             # Worker timeout (seconds)
graceful_timeout = 30                    # Graceful shutdown (seconds)
preload_app = False                      # Safe for databases
keepalive = 5                            # Keep-alive (seconds)
```

## Environment Variables

Override in your deployment platform:
- `WEB_CONCURRENCY` - Number of workers (default: 4)
- `GUNICORN_TIMEOUT` - Worker timeout in seconds (default: 60)
- `PORT` - Port to bind to (default: 10000)

## Monitoring Checklist

### During Deployment (Expected)
- [ ] SIGTERM messages appear
- [ ] Enhanced diagnostic context is shown
- [ ] "This is NORMAL during deployments" message appears
- [ ] New workers spawn successfully

### In Production (Monitor For)
- [ ] No SIGTERM outside deployment windows
- [ ] No SIGABRT messages (critical)
- [ ] Workers not restarting frequently
- [ ] No OOM kills or timeout errors

## Common Issues & Solutions

### Issue: Frequent SIGTERM Outside Deployments
**Causes:**
- Memory issues (OOM killer)
- Workers timing out (>60s requests)
- Platform resource constraints

**Solutions:**
1. Check memory usage
2. Review slow requests in logs
3. Optimize database queries
4. Add timeouts to external API calls

### Issue: SIGABRT Messages
**Causes:**
- Blocking database operations
- Slow external API calls
- Infinite loops or deadlocks
- Connection pool exhaustion

**Solutions:**
1. Add timeout to all blocking operations
2. Use background tasks for long operations
3. Optimize slow queries
4. Increase connection pool size (if needed)
5. As last resort: increase `GUNICORN_TIMEOUT`

## Files Modified

- ✅ `backend/gunicorn.conf.py` - Enhanced hooks and logging
- ✅ `gunicorn.conf.py` - Enhanced hooks and logging
- ✅ `GUNICORN_SIGTERM_EXPLAINED.md` - Detailed explanation
- ✅ `SIGTERM_FIX_QUICK_REFERENCE.md` - This file
- ✅ `test_gunicorn_worker_fix.py` - Validation test

## Validation

Run the validation test:
```bash
python3 test_gunicorn_worker_fix.py
```

Expected output:
```
✅ All tests passed!

The Gunicorn worker SIGTERM fix is properly implemented:
1. worker_int hook logs diagnostics for SIGTERM/SIGINT signals
2. worker_abort hook logs detailed diagnostics when workers timeout
3. Timeout settings are reasonable
4. Startup operations have timeout protection
```

## Deployment Commands

### Railway
```bash
# Configuration is in railway.toml - automatic deployment
git push origin main
```

### Render
```bash
# Configuration is in render.yaml - automatic deployment
git push origin main
```

Both platforms use:
```bash
cd backend && PYTHONPATH=. poetry run gunicorn app.main:app --config gunicorn.conf.py
```

## Support Resources

- [GUNICORN_SIGTERM_EXPLAINED.md](./GUNICORN_SIGTERM_EXPLAINED.md) - Detailed documentation
- [Gunicorn Server Hooks](https://docs.gunicorn.org/en/stable/settings.html#server-hooks)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

## Status

✅ **Fix Status:** Deployed and ready
✅ **Validation:** All tests passing
✅ **Documentation:** Complete
✅ **Confidence Level:** HIGH

---

**Last Updated:** 2025-12-16
**Version:** Enhanced Fix v2.0

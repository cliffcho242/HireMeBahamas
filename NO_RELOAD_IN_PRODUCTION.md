# ⚠️ CRITICAL: Never Use --reload in Production

## Problem Statement

**NEVER USE `--reload` in production environments (Render, Railway, Vercel, etc.)**

### Why --reload is Dangerous in Production

1. **Doubles Memory Usage**: Auto-reload keeps file watchers active, monitoring the filesystem for changes, which significantly increases memory consumption
2. **Causes SIGTERM Errors**: The extra memory usage can cause workers to be killed by the platform's memory limits
3. **Platform Already Handles Restarts**: Services like Render automatically restart your application on deployment
4. **Performance Degradation**: File watching adds unnecessary overhead to every request
5. **Stability Issues**: Can cause race conditions and worker crashes during high traffic

## What Was Fixed

### Files Modified

1. **docker-compose.local.yml** (Line 163)
   - **Before**: `command: gunicorn ... --reload ...`
   - **After**: `command: gunicorn ... [no --reload]`
   - **Impact**: Local Docker environment now runs in production-like mode

2. **dev.sh** (Lines 1-19)
   - **Added**: Clear warnings that `--reload` is for LOCAL DEVELOPMENT ONLY
   - **Impact**: Developers are warned before using this script

3. **install_app_dependencies.sh** (Lines 115-121)
   - **Added**: Warnings in the "Next steps" output
   - **Impact**: New developers see warnings during setup

4. **backend/test_messaging_system.py** (Lines 64-68)
   - **Added**: Production safety warnings in test output
   - **Impact**: Testing documentation now includes safety notes

### Production Configurations ✅ VERIFIED SAFE

These files are **correctly configured** and do NOT use `--reload`:

- ✅ **Procfile** - Uses gunicorn with config file (no --reload)
- ✅ **render.yaml** - Uses Poetry + gunicorn with config file (no --reload)
- ✅ **railway.json** - Configuration only, no command
- ✅ **gunicorn.conf.py** - Production config with `preload_app = False`
- ✅ **start.sh** - Production startup script (no --reload)
- ✅ **start_production.sh** - Explicitly uses `--no-reload` (Line 82)

## Development vs Production

### Local Development (Acceptable)
```bash
# ✅ OK for local development only
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production (NEVER)
```bash
# ❌ WRONG - Never do this in production
gunicorn app.main:app --reload

# ✅ CORRECT - Production configuration
gunicorn app.main:app --config gunicorn.conf.py
```

## How Platform Restarts Work

### Render
- Automatically restarts on every git push
- Uses health checks to verify new version
- No need for auto-reload

### Railway
- Restarts on deployment
- Monitors service health
- Auto-scaling handles traffic

### Vercel
- Serverless functions redeploy automatically
- No long-running processes
- --reload is not applicable

## Related Documentation

- See `GUNICORN_SIGTERM_FIX_COMPLETE.md` for SIGTERM troubleshooting
- See `PRODUCTION_CONFIG_ABSOLUTE_BANS.md` for other production anti-patterns
- See `gunicorn.conf.py` for production configuration details

## Summary

✅ **Production configs verified safe** - No `--reload` flags found  
✅ **Development files updated** - Clear warnings added  
✅ **Documentation created** - This file for future reference  

**Remember**: If you see SIGTERM errors in production, check for:
1. `--reload` flags (now removed)
2. `preload_app = True` (should be False for databases)
3. Memory limits exceeded
4. Slow database queries causing timeouts

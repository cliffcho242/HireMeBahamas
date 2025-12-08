# Railway Deployment Troubleshooting Guide

## Overview

This guide helps diagnose and resolve Railway deployment failures where the Docker image builds successfully but the container fails during startup or runtime.

## Common Deployment Failure Causes

### 1. Missing Environment Variables

**Symptoms:**
- Build succeeds but deployment shows "Failed" status
- Application crashes immediately after startup
- Health checks fail

**Required Environment Variables:**
```bash
DATABASE_URL=postgresql://username:password@hostname:5432/database
SECRET_KEY=your-production-secret-key-here
PORT=8000  # Usually auto-set by Railway
```

**Optional Environment Variables:**
```bash
ENVIRONMENT=production
REDIS_URL=redis://...  # For caching (optional)
TOKEN_EXPIRATION_DAYS=365
```

**How to Fix:**
1. Go to Railway project settings
2. Navigate to "Variables" tab
3. Add missing environment variables
4. Redeploy the service

### 2. Incorrect Start Command

**Symptoms:**
- Error: "sh: gunicorn: not found"
- Error: "ModuleNotFoundError"
- Application doesn't respond to requests

**Current Configuration:**
- **railway.json**: `python validate_startup.py && gunicorn final_backend_postgresql:application --config gunicorn.conf.py`
- **nixpacks.toml**: Same as above
- **Procfile**: `uvicorn api.backend_app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --timeout-keep-alive 5 --limit-concurrency 100`

**How to Fix:**
Railway with NIXPACKS builder uses the start command from `railway.json` or `nixpacks.toml`. Ensure:
- The command uses the correct module path
- All dependencies are installed in requirements.txt
- The application module is correctly exported

### 3. Port Configuration Mismatch

**Symptoms:**
- Health checks timeout
- "Connection refused" errors
- Deployment shows "Unhealthy" status

**Current Port Configuration:**
- Application binds to: `0.0.0.0:${PORT}`
- Health check endpoint: `/health`
- Default port fallback: `8000` or `8080`

**How to Fix:**
Ensure the application binds to the PORT environment variable provided by Railway:
```python
# In gunicorn.conf.py
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# In final_backend_postgresql.py
port = int(os.environ.get("PORT", 8080))
app.run(host="0.0.0.0", port=port)
```

### 4. Database Connectivity Issues

**Symptoms:**
- "Connection refused" to database
- "FATAL: password authentication failed"
- "could not connect to server"

**How to Fix:**
1. Verify DATABASE_URL format:
   ```
   postgresql://username:password@hostname:5432/database_name
   ```

2. Use DATABASE_PRIVATE_URL for Railway's internal network (faster, no egress charges):
   ```bash
   DATABASE_PRIVATE_URL=postgresql://...
   ```

3. Check database service is running and accessible

4. Test connection manually:
   ```python
   python validate_startup.py
   ```

### 5. Resource Limits (Out of Memory)

**Symptoms:**
- Container killed unexpectedly
- Logs show "Killed" or "OOMKilled"
- Application stops responding under load

**Current Configuration:**
- Workers: 1 (configured for Railway's default 512MB-1GB)
- Threads: 4
- Preload app: true (to detect memory issues early)

**How to Fix:**
1. Check Railway service memory limit in project settings
2. Reduce worker count if needed:
   ```bash
   WEB_CONCURRENCY=1  # Single worker for low RAM
   WEB_THREADS=2      # Reduce threads if memory is tight
   ```

3. Monitor memory usage in Railway dashboard

### 6. Health Check Timeout

**Symptoms:**
- Deployment fails after waiting for health check
- Logs show "Health check timeout"

**Current Configuration:**
- Health check path: `/health`
- Timeout: 180 seconds
- Start period: 40 seconds

**How to Fix:**
1. Verify health endpoint is working:
   ```bash
   curl http://localhost:$PORT/health
   ```

2. Check startup logs for slow initialization
3. Increase healthcheckTimeout if needed (in railway.json)

## Accessing Full Deployment Logs

### Railway Dashboard
1. Go to your Railway project
2. Click on the service (backend)
3. Click on "Deployments" tab
4. Click on the failed deployment
5. View "Build Logs" and "Deploy Logs"

### Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs

# View specific deployment logs
railway logs --deployment <deployment-id>
```

## Startup Validation

The application now includes startup validation (`validate_startup.py`) that checks:
- Required environment variables
- Python dependencies
- File system permissions
- Database connectivity

View validation output in deployment logs to quickly identify issues.

## Testing Configuration Locally

Before deploying to Railway, test the configuration locally:

```bash
# Set environment variables
export DATABASE_URL="postgresql://..."
export SECRET_KEY="test-secret"
export PORT=8000

# Run startup validation
python validate_startup.py

# Start with Gunicorn (production-like)
gunicorn final_backend_postgresql:application --config gunicorn.conf.py

# Test health endpoint
curl http://localhost:8000/health
```

## Common Error Messages

### "sh: gunicorn: not found"
**Cause:** gunicorn not installed or not in PATH  
**Fix:** Ensure `gunicorn==23.0.0` is in requirements.txt

### "ModuleNotFoundError: No module named 'final_backend_postgresql'"
**Cause:** Start command uses wrong module path  
**Fix:** Use `gunicorn final_backend_postgresql:application`

### "DATABASE_URL must be set in production"
**Cause:** Missing DATABASE_URL environment variable  
**Fix:** Add DATABASE_URL in Railway project settings

### "Address already in use"
**Cause:** Port conflict or multiple instances  
**Fix:** Railway handles PORT allocation; don't hardcode ports

### "Connection refused" to database
**Cause:** Database not running or wrong connection string  
**Fix:** Check DATABASE_URL and database service status

## Contact Support

If you continue to experience issues:

1. Collect full deployment logs from Railway dashboard
2. Run `python validate_startup.py` and share output
3. Check Railway status page: https://status.railway.app/
4. Visit Railway Help Station: https://help.railway.app/

## Files Modified for Deployment Fix

- `Dockerfile` - Fixed port consistency (healthcheck and CMD use same port)
- `railway.json` - Added explicit start command with validation
- `nixpacks.toml` - Added startup validation to start command
- `validate_startup.py` - New startup validation script
- `RAILWAY_DEPLOYMENT_TROUBLESHOOTING.md` - This document

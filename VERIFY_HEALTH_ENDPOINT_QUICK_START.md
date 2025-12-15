# Quick Start: Verify Health Endpoints

## Problem Statement

> ✅ You MUST see: `{ "status": "ok" }`
> If you see 404 → Render will NEVER stabilize

## How to Verify

### Option 1: Browser (Easiest)

Open your browser and navigate to:

```
https://your-backend-name.onrender.com/health
```

or

```
https://your-backend-name.onrender.com/api/health
```

**Expected Result:**
```json
{"status":"ok"}
```

### Option 2: curl Command

```bash
curl https://your-backend-name.onrender.com/health
```

**Expected Output:**
```json
{"status":"ok"}
```

### Option 3: Test Multiple Endpoints

```bash
# Test /health endpoint
curl https://your-backend-name.onrender.com/health

# Test /api/health endpoint
curl https://your-backend-name.onrender.com/api/health

# Test with verbose output
curl -v https://your-backend-name.onrender.com/health
```

## Troubleshooting

### If you see 404 Not Found

❌ **Problem:** The health endpoint is not responding

**Solutions:**
1. Check that the service is deployed and running in Render dashboard
2. Verify the URL is correct (check your Render service name)
3. Wait for the service to finish deploying (check deploy logs)
4. Ensure `healthCheckPath: /health` is set in `render.yaml`

### If you see a different response

❌ **Problem:** The endpoint returns something other than `{"status":"ok"}`

**Solutions:**
1. Check the backend logs in Render dashboard
2. Verify the backend code hasn't been modified
3. Ensure environment variables are set correctly

### If the request times out

❌ **Problem:** The service is not responding

**Solutions:**
1. Check if the service is running in Render dashboard
2. Review deploy logs for errors
3. Verify the service hasn't crashed (check metrics)
4. Wait for cold start (first request may be slow)

## Success Indicators

✅ **All Good** if you see:
- Status code: `200 OK`
- Response body: `{"status":"ok"}`
- Response time: < 1 second

## Render Dashboard Configuration

Make sure your Render service has these settings:

1. **Health Check Path:** `/health`
2. **Grace Period:** 60 seconds
3. **Health Check Timeout:** 10 seconds
4. **Health Check Interval:** 30 seconds

## Additional Health Endpoints

Once the basic `/health` endpoint is working, you can also test:

```bash
# Liveness probe
curl https://your-backend-name.onrender.com/live

# Readiness check
curl https://your-backend-name.onrender.com/ready

# Detailed health with database check
curl https://your-backend-name.onrender.com/ready/db
```

## Local Testing

Before deploying, you can test locally:

```bash
# Start the backend
cd backend
gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# In another terminal, test the endpoint
curl http://localhost:8000/health
```

## Summary

✅ **Health endpoint is working correctly** if you see `{"status":"ok"}` when accessing:
- `https://your-backend-name.onrender.com/health`
- `https://your-backend-name.onrender.com/api/health`

The endpoints are already implemented and tested - no code changes needed!

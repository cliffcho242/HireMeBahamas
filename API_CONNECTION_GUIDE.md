# API Connection Configuration Guide

## Overview

This guide explains how the frontend connects to the backend API and how to troubleshoot connection issues.

## Architecture

The HireMeBahamas platform uses a split deployment architecture:
- **Frontend**: Deployed on Vercel
- **Backend**: Deployed on Render (https://hiremebahamas.onrender.com)

## How API Requests Work

### Production (Vercel Deployment)

1. Frontend makes API requests to **relative URLs**: `/api/auth/login`, `/api/posts`, etc.
2. Vercel's proxy rewrites these requests to the Render backend
3. The `vercel.json` file contains the rewrite rule:
   ```json
   {
     "rewrites": [
       {
         "source": "/api/(.*)",
         "destination": "https://hiremebahamas.onrender.com/api/$1"
       }
     ]
   }
   ```
4. This approach avoids CORS issues because the browser sees all requests as same-origin

### Local Development

1. Frontend makes API requests to `http://localhost:8000/api/*`
2. Set `VITE_API_URL=http://localhost:8000` in `frontend/.env`
3. Backend must be running locally on port 8000

## Environment Variable Configuration

### ✅ Correct Setup for Vercel (Production)

**DO NOT set `VITE_API_URL` in Vercel environment variables!**

The frontend will automatically use same-origin URLs, and Vercel's rewrite rules will handle the proxying.

### ✅ Correct Setup for Local Development

In `frontend/.env`:
```bash
VITE_API_URL=http://localhost:8000
```

### ❌ Common Mistakes

1. **Setting `VITE_API_URL` in Vercel**: This bypasses the proxy and causes CORS errors
2. **Using `https://hiremebahamas.onrender.com` directly**: This requires CORS configuration and is slower
3. **Forgetting to start the backend locally**: API requests will fail with connection errors

## Troubleshooting Connection Issues

### Users See "Cannot Connect to Server" Error

This error appears when the frontend cannot reach the backend. Common causes:

#### 1. Render Backend is Sleeping (Cold Start)

**Symptoms:**
- First request after inactivity takes 30-60 seconds
- Users see timeout errors
- Subsequent requests work fine

**Solution:**
- This is normal for Render's free tier
- The frontend already handles this with:
  - 60-second timeout for login/register
  - Automatic retries
  - Helpful error messages explaining cold starts

**Prevention:**
- Use the `keepalive-ping.yml` GitHub Action to ping backend every 5-10 minutes
- Consider upgrading to Render's paid tier for always-on backend

#### 2. Vercel Rewrite Not Working

**Symptoms:**
- API requests return 404
- Requests are not being proxied to Render

**Solution:**
1. Check `vercel.json` has the correct rewrite rule
2. Verify the Render backend URL is correct
3. Redeploy to Vercel to apply configuration changes

#### 3. CORS Issues (if VITE_API_URL is set)

**Symptoms:**
- Browser console shows CORS errors
- Requests are blocked by browser

**Solution:**
1. Remove `VITE_API_URL` from Vercel environment variables
2. Use same-origin URLs with Vercel proxy (recommended)
3. OR configure CORS on backend to allow Vercel domain

#### 4. Render Backend is Down

**Symptoms:**
- All requests fail consistently
- Health check returns 503 or times out

**Solution:**
1. Check Render dashboard for service status
2. Check Render logs for errors
3. Verify database connection string is correct
4. Restart the Render service if needed

## API Configuration Code

### Frontend API Base URL Logic

From `frontend/src/lib/api.ts`:

```typescript
function validateAndGetBaseUrl(): string {
  const base = import.meta.env.VITE_API_URL as string | undefined;

  // If no explicit API URL is set, use same-origin
  // This is the RECOMMENDED approach for Vercel deployments
  if (!base) {
    if (typeof window !== 'undefined') {
      return window.location.origin; // Uses Vercel proxy
    }
    return ''; // Build-time: relative URLs work fine
  }

  // If VITE_API_URL is explicitly set (local dev), validate it
  // ... validation code ...
  return base;
}
```

### Connection Testing

The frontend includes connection testing on the login page:

1. Tests `/api/health` endpoint on mount
2. Shows connection status banner if backend is unreachable
3. Provides helpful messages for cold starts

## Monitoring & Health Checks

### Health Check Endpoints

The backend provides several health check endpoints:

- `/health` - Instant health check (no DB dependency)
- `/api/health` - Same as /health
- `/healthz` - Emergency fallback health check
- `/ready` - Readiness check (no DB)
- `/ready/db` - Readiness with DB connectivity check
- `/health/detailed` - Full health check with DB stats

### GitHub Actions

The repository includes automated workflows:

- `keepalive-ping.yml` - Pings backend every 5-10 minutes to prevent sleep
- `health-check.yml` - Daily health checks with alerting
- `uptime-monitoring.yml` - Continuous uptime monitoring

## Best Practices

1. **Always use relative URLs in production**: Let Vercel's proxy handle routing
2. **Handle cold starts gracefully**: Use appropriate timeouts and error messages
3. **Test locally with backend running**: Set `VITE_API_URL` for local development
4. **Monitor backend health**: Use GitHub Actions and Render metrics
5. **Provide helpful error messages**: The current error handling in `friendlyErrors.ts` is good

## Quick Reference

| Environment | VITE_API_URL Value | How it Works |
|-------------|-------------------|--------------|
| Production (Vercel) | **Not set** | Same-origin + Vercel proxy |
| Local Development | `http://localhost:8000` | Direct connection to local backend |
| Preview Deploy | **Not set** | Same-origin + Vercel proxy |

## Related Files

- `frontend/src/lib/api.ts` - API base URL configuration
- `frontend/src/services/api.ts` - Axios instance with retry logic
- `frontend/src/utils/friendlyErrors.ts` - User-friendly error messages
- `frontend/src/utils/connectionTest.ts` - Connection testing utility
- `vercel.json` - Vercel proxy configuration
- `.github/workflows/keepalive-ping.yml` - Backend keepalive automation

## Support

If users continue to experience connection issues after following this guide:

1. Check Render service status and logs
2. Verify vercel.json configuration is correct
3. Test the backend health endpoint directly
4. Check GitHub Actions for any failed health checks
5. Review Vercel deployment logs for errors

## Common Error Messages

### "Cannot Connect to Server"
**Meaning**: Network error (ERR_NETWORK) - can't reach backend  
**Solution**: Check if backend is down, sleeping, or if there's a network issue

### "Backend is starting up (cold start)"
**Meaning**: Render backend is waking up from sleep  
**Solution**: Wait 30-60 seconds, this is normal for free tier

### "Server Taking Too Long"
**Meaning**: Request timeout (ECONNABORTED)  
**Solution**: Backend is under heavy load or still starting, retry after a moment

### "Session Expired"
**Meaning**: JWT token has expired (401)  
**Solution**: User needs to log in again, this is normal security behavior

# Vercel Serverless Deployment Guide (Option A - Recommended)

## Overview

This guide covers deploying HireMeBahamas using **Option A: Vercel Serverless**, which provides:
- ✅ Same-origin API routing (/api/*)
- ✅ No CORS issues
- ✅ Cold start time: 1-3 seconds
- ✅ Automatic keep-warm via cron jobs
- ✅ Simplified configuration

## Architecture

```
Frontend (Vite/React)  →  /api/*  →  Vercel Serverless Functions (Python/FastAPI)
        ↓                                            ↓
   Static Files                              Vercel Postgres
```

## Prerequisites

- Vercel account (free tier is sufficient)
- GitHub repository connected to Vercel
- Vercel Postgres database (optional, can use Railway)

## Deployment Steps

### 1. Configure Vercel Project

1. Go to [Vercel Dashboard](https://vercel.com)
2. Import your GitHub repository
3. Configure build settings:
   - **Framework Preset**: Vite
   - **Build Command**: `cd frontend && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `cd frontend && npm ci`

### 2. Environment Variables

**CRITICAL: Do NOT set `VITE_API_URL` in Vercel Dashboard**

#### Backend Environment Variables (Set in Vercel Dashboard)

Required:
```bash
# Database (use Vercel Postgres or Railway)
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# Authentication
SECRET_KEY=your-secret-key-here-generate-a-random-one
JWT_SECRET_KEY=your-jwt-secret-key-here-generate-a-random-one

# Environment
ENVIRONMENT=production
```

Optional:
```bash
# Frontend URL for CORS
FRONTEND_URL=https://your-app.vercel.app

# OAuth (if using Google/Apple Sign-In)
GOOGLE_CLIENT_ID=your_google_client_id
APPLE_CLIENT_ID=your_apple_client_id
```

#### Frontend Environment Variables

**DO NOT SET** these in Vercel:
- ❌ `VITE_API_URL` - Leave unset for same-origin routing
- ❌ `NEXT_PUBLIC_*` - These are for Next.js, not Vite

**Optional** frontend variables:
```bash
# Only set if using these services
VITE_CLOUDINARY_CLOUD_NAME=your_cloudinary_name
VITE_SENDBIRD_APP_ID=your_sendbird_app_id
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_APPLE_CLIENT_ID=your_apple_client_id
```

### 3. Vercel Configuration Files

The repository includes three Vercel configuration files:

#### `vercel_immortal.json` (Recommended for Production)

This is the recommended configuration file with:
- ✅ Cron jobs for keep-warm (every 5-10 minutes)
- ✅ Frontend build configuration
- ✅ API routing to Python serverless functions
- ✅ Security headers

```json
{
  "crons": [
    {
      "path": "/api/health",
      "schedule": "*/5 * * * *"
    },
    {
      "path": "/api/database/ping",
      "schedule": "*/10 * * * *"
    }
  ]
}
```

To use this configuration:

1. **If you don't have a `vercel.json` file**, rename `vercel_immortal.json`:
```bash
mv vercel_immortal.json vercel.json
git add vercel.json
git commit -m "Use recommended Vercel serverless configuration"
git push
```

2. **If you already have a `vercel.json` file**, merge the cron jobs section:
```bash
# Backup your current vercel.json
cp vercel.json vercel.json.backup

# Manually merge the cron jobs section from vercel_immortal.json into your vercel.json
# Add these to your existing vercel.json:
# "crons": [
#   {
#     "path": "/api/health",
#     "schedule": "*/5 * * * *"
#   },
#   {
#     "path": "/api/database/ping",
#     "schedule": "*/10 * * * *"
#   }
# ]

git add vercel.json
git commit -m "Add keep-warm cron jobs to Vercel configuration"
git push
```

### 4. Keep-Warm Configuration

The cron jobs ensure your serverless functions stay warm:

- `/api/health` - Every 5 minutes (keeps API warm)
- `/api/database/ping` - Every 10 minutes (keeps database connection active)

**Cold Start Performance:**
- First request: 1-3 seconds (cold start)
- Subsequent requests: <200ms (warm)
- After cron ping: Always <200ms

**GitHub Actions Backup:**
The repository also includes `.github/workflows/vercel-keepalive.yml` which pings the API every 5 minutes as a backup keep-warm mechanism.

### 5. Verify Deployment

After deployment, verify everything works:

1. **Check Health Endpoint:**
```bash
curl https://your-app.vercel.app/api/health
```

Expected response:
```json
{
  "status": "ok",
  "platform": "vercel-serverless",
  "database": "connected"
}
```

2. **Check Frontend API Detection:**
   - Open your app in browser
   - Open DevTools Console
   - Look for: `Using Vercel serverless API at: https://your-app.vercel.app`

3. **Test API Endpoints:**
```bash
# Test registration
curl -X POST https://your-app.vercel.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User",
    "user_type": "freelancer",
    "location": "Nassau"
  }'

# Test login
curl -X POST https://your-app.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

## How Same-Origin Routing Works

### Frontend Detection Logic

The frontend automatically detects Vercel deployments:

```typescript
// frontend/src/utils/backendRouter.ts
function getBackendConfig(): BackendConfig {
  const envUrl = import.meta.env.VITE_API_URL;
  
  // If explicit URL is set in env, use it
  if (envUrl) {
    return {
      url: envUrl,
      available: true,
    };
  }
  
  // Otherwise, use same-origin (for Vercel deployments)
  return {
    url: window.location.origin,
    available: true,
  };
}
```

### Request Flow

1. Frontend makes request to `/api/users`
2. Browser resolves to `https://your-app.vercel.app/api/users`
3. Vercel routes `/api/*` to serverless function at `api/main.py`
4. FastAPI handles the request
5. Response sent back to frontend

### Benefits

✅ **No CORS issues** - Same origin means no cross-origin requests
✅ **Simplified configuration** - No need to set VITE_API_URL
✅ **Better performance** - No DNS lookup for separate backend
✅ **Automatic HTTPS** - Vercel provides SSL for everything
✅ **Single deployment** - Frontend and backend deploy together

## Comparison: Option A vs Option B

### Option A: Vercel Serverless (Recommended)

**Pros:**
- ✅ Same-origin routing (no CORS)
- ✅ Single deployment
- ✅ Automatic keep-warm via cron
- ✅ Cold start: 1-3 seconds
- ✅ Simple configuration
- ✅ Free tier available

**Cons:**
- ⚠️  30-second timeout per request (Vercel limit)
- ⚠️  Limited to Vercel's Python runtime

**Best for:** Most production deployments

### Option B: Railway Backend + Vercel Frontend

**Pros:**
- ✅ No timeout limits
- ✅ Full control over backend
- ✅ Can use long-running processes

**Cons:**
- ❌ Requires CORS configuration
- ❌ Two separate deployments
- ❌ More complex configuration
- ❌ Higher latency (cross-origin)

**Best for:** Complex backend requirements

## Troubleshooting

### Issue: Frontend can't connect to backend

**Check:**
1. Is `VITE_API_URL` set in Vercel? (Should be unset)
2. Open browser console - what API URL is detected?
3. Check network tab - are requests going to `/api/*`?

**Solution:**
```bash
# Remove VITE_API_URL from Vercel Dashboard
# Redeploy to pick up change
```

### Issue: Cold starts are slow

**Check:**
1. Are cron jobs configured in `vercel.json`?
2. Is GitHub Actions workflow running?

**Solution:**
Use `vercel_immortal.json` configuration which includes cron jobs.

### Issue: Database connection errors

**Check:**
1. Is `DATABASE_URL` set in Vercel Dashboard?
2. Does it include `?sslmode=require`?
3. Is the database accepting connections?

**Solution:**
```bash
# Test database connection
curl https://your-app.vercel.app/api/health

# Check response includes: "database": "connected"
```

### Issue: 404 on API endpoints

**Check:**
1. Is `api/` directory present in repository?
2. Is `api/main.py` present?
3. Are rewrites configured in `vercel.json`?

**Solution:**
Ensure `vercel.json` includes:
```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/main.py"
    }
  ]
}
```

## Monitoring

### Built-in Endpoints

- `/api/health` - Health check with database status
- `/api/status` - Detailed backend status
- `/api/diagnostic` - Debug information (dev only)

### Vercel Dashboard

Monitor your deployment:
1. Go to [Vercel Dashboard](https://vercel.com)
2. Select your project
3. Check "Functions" tab for serverless metrics
4. Check "Logs" tab for runtime logs

### GitHub Actions

The keepalive workflow provides monitoring:
- Runs every 5 minutes
- Reports response times
- Alerts on failures
- View at: `https://github.com/[user]/[repo]/actions`

## Best Practices

### 1. Environment Variables

✅ **Do:**
- Generate strong random secrets
- Use Vercel Postgres for production
- Set `ENVIRONMENT=production`

❌ **Don't:**
- Set `VITE_API_URL` (breaks same-origin routing)
- Use placeholder values
- Commit secrets to git

### 2. Database

✅ **Do:**
- Use Vercel Postgres (optimized for serverless)
- Include `?sslmode=require` in connection string
- Use connection pooling

❌ **Don't:**
- Use SQLite (doesn't persist in serverless)
- Use long-running database connections
- Skip SSL/TLS

### 3. Keep-Warm

✅ **Do:**
- Use both cron jobs (Vercel) and GitHub Actions
- Monitor cold start times
- Keep intervals under 15 minutes

❌ **Don't:**
- Disable keep-warm (causes slow first requests)
- Use intervals > 15 minutes (functions go cold)

### 4. Security

✅ **Do:**
- Use strong JWT secrets
- Enable rate limiting
- Use HTTPS (automatic on Vercel)
- Validate all inputs

❌ **Don't:**
- Expose sensitive data in logs
- Skip authentication on protected routes
- Use weak passwords

## Migration Guide

### From Railway to Vercel Serverless

1. **Export data from Railway database**
2. **Set up Vercel Postgres**
3. **Import data to Vercel Postgres**
4. **Update environment variables in Vercel Dashboard**
5. **Remove `VITE_API_URL` from Vercel Dashboard**
6. **Deploy and test**

### From Render to Vercel Serverless

Same steps as Railway migration above.

## Support

- **Documentation**: See README.md and other guides in repository
- **Issues**: https://github.com/cliffcho242/HireMeBahamas/issues
- **Vercel Docs**: https://vercel.com/docs

## Summary

**For most deployments, use Option A (Vercel Serverless):**
1. Do NOT set `VITE_API_URL` in Vercel Dashboard
2. Use `vercel_immortal.json` configuration (rename to `vercel.json`)
3. Configure environment variables (backend only)
4. Deploy and verify

The frontend will automatically detect Vercel and use same-origin routing to `/api/*`.

Cold starts are 1-3 seconds, with automatic keep-warm via cron jobs ensuring fast response times (<200ms) for all user requests.

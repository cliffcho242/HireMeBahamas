# Vercel Frontend to Backend Connection Setup

## Overview

This guide explains how to configure the HireMeBahamas frontend to connect to the Vercel serverless backend API.

## ⚠️ IMPORTANT: Vite vs Next.js Environment Variables

**This project uses Vite (React), NOT Next.js.**

✅ **CORRECT:** Use `VITE_API_URL` for environment variables  
❌ **WRONG:** Do NOT use `NEXT_PUBLIC_BACKEND_URL` or `NEXT_PUBLIC_API_URL`

Environment variables in Vite must be prefixed with `VITE_` to be exposed to the client-side code. Next.js uses `NEXT_PUBLIC_` prefix, which will not work in this project.

## Quick Start

### For Vercel Serverless Backend (Recommended)

**TL;DR: Do nothing!** The frontend automatically detects Vercel deployments and uses same-origin API calls.

1. ✅ Deploy to Vercel (frontend + api/ directory)
2. ✅ Frontend automatically uses `window.location.origin`
3. ✅ API endpoints available at `/api/*`
4. ✅ No environment variables needed

### For Separate Backend (Render, Custom Server)

1. Set `VITE_API_URL` in Vercel Dashboard
2. Example: `VITE_API_URL=https://your-app.up.render.app`
3. Ensure backend CORS allows your Vercel domain

---

## ✅ FRONTEND (Vercel) — FINAL CONFIG

### 6️⃣ Environment Variables (Vercel Dashboard)

**Go to:** Vercel Dashboard → Your Project → Settings → Environment Variables  
**Direct Link:** `https://vercel.com/[your-team]/[project-name]/settings/environment-variables`

#### Option A: Render Backend
```bash
VITE_API_URL=https://your-backend.up.render.app
VITE_SOCKET_URL=https://your-backend.up.render.app
```

#### Option B: Render Backend
```bash
VITE_API_URL=https://your-backend.onrender.com
VITE_SOCKET_URL=https://your-backend.onrender.com
```

#### Option C: Vercel Serverless (Same-Origin)
```bash
# Do NOT set VITE_API_URL
# Frontend automatically detects Vercel and uses window.location.origin
```

**Steps to Add:**
1. Click **"Add New"** button
2. Enter **Name**: `VITE_API_URL`
3. Enter **Value**: Your backend URL (e.g., `https://your-app.up.render.app`)
4. Select **All** environments (Production, Preview, Development)
5. Click **Save**
6. Go to **Deployments** → **Redeploy** latest to apply changes

**✅ Verification:**
```bash
# After deployment, check browser console at your Vercel URL
# Should show: "API Base URL: https://your-backend.up.render.app"

# Test API connection:
curl https://your-frontend.vercel.app
# Should load without errors
```

**⚠️ Common Mistakes:**
- ❌ Using `NEXT_PUBLIC_BACKEND_URL` (Next.js only, won't work)
- ❌ Using `BACKEND_URL` without `VITE_` prefix (won't be exposed to frontend)
- ❌ Forgetting to redeploy after adding environment variables
- ❌ Using `http://` instead of `https://` for backend URL

---

## Detailed Configuration

### 1. Environment Variable Configuration

The frontend uses `VITE_API_URL` to determine the backend location:

```bash
# Option 1: Vercel Serverless (Same-Origin)
# Do NOT set VITE_API_URL - leave it unset or commented
# VITE_API_URL=

# Option 2: Separate Backend (Render, etc.)
VITE_API_URL=https://your-backend-url.com
```

### 2. How Auto-Detection Works

The frontend (`frontend/src/services/api.ts`) automatically detects the deployment environment:

```typescript
// Detection logic (simplified)
if (!ENV_API && typeof window !== 'undefined') {
  const hostname = window.location.hostname;
  const isProduction = hostname === 'hiremebahamas.com' || 
                       hostname === 'www.hiremebahamas.com';
  const isVercel = hostname.includes('.vercel.app');
  
  // For production/Vercel deployments, use same-origin
  if (isProduction || isVercel) {
    API_BASE_URL = window.location.origin;
  }
}
```

### 3. Vercel Dashboard Setup

Go to: `https://vercel.com/[team]/[project]/settings/environment-variables`

**For Vercel Serverless Backend:**
```bash
# Backend variables (set these)
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Frontend variables (optional)
# VITE_CLOUDINARY_CLOUD_NAME=...
# VITE_SENDBIRD_APP_ID=...
```

**For Separate Backend:**
```bash
# All backend variables from above, plus:
VITE_API_URL=https://your-backend-url.com
```

### 4. Verify Configuration

#### Check API Health Endpoint

**Vercel Serverless:**
```bash
curl https://your-project.vercel.app/api/health
# Expected: {"status":"healthy","platform":"vercel-serverless"}
```

**Separate Backend:**
```bash
curl https://your-backend-url.com/api/health
# Expected: {"status":"healthy","platform":"..."}
```

#### Check Frontend Console

Open your deployed app in browser and check the console:
```
=== API CONFIGURATION ===
API Base URL: https://your-project.vercel.app
ENV_API: not set
Window Origin: https://your-project.vercel.app
========================
```

### 5. Verify API Endpoints

The `api/` directory contains serverless functions that handle all backend requests:

```
api/
├── index.py          # Main API handler (FastAPI + Mangum)
├── backend_app/      # Backend application code
├── cron/            # Cron jobs (health checks, etc.)
├── database.py      # Database connection utilities
└── requirements.txt # Python dependencies
```

**Available Endpoints:**
- `/api/health` - Health check
- `/api/ready` - Database connectivity check
- `/api/auth/*` - Authentication endpoints
- `/api/users/*` - User management
- `/api/jobs/*` - Job listings
- `/api/posts/*` - Social posts
- `/api/messages/*` - Messaging
- And more...

### 6. Verify vercel.json Routing

Check that `vercel.json` has the correct rewrites:

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/index.py"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

✅ This ensures all `/api/*` requests go to the serverless function.

## Environment-Specific Configuration

### Local Development

```bash
# frontend/.env
VITE_API_URL=http://localhost:8000

# Start backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Start frontend (in another terminal)
cd frontend
npm run dev
```

### Vercel Preview Deployments

Preview deployments automatically use same-origin, just like production:
- URL: `https://your-project-git-branch.vercel.app`
- API: `https://your-project-git-branch.vercel.app/api/*`

### Production Deployment

**With Vercel Serverless Backend:**
```bash
# In Vercel Dashboard, set:
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=...
JWT_SECRET_KEY=...

# Do NOT set VITE_API_URL
```

**With Separate Backend:**
```bash
# In Vercel Dashboard, set:
VITE_API_URL=https://your-backend-url.com

# Plus ensure backend allows CORS from your Vercel domain
```

## Troubleshooting

### Issue: 404 on API Requests

**Symptoms:**
- Browser shows 404 errors on `/api/*` requests
- Console shows: "Failed to load resource: the server responded with a status of 404"

**Solutions:**
1. Verify `api/` directory exists in root of repository
2. Check `vercel.json` has correct rewrites
3. Ensure `api/index.py` exists and is valid
4. Check Vercel build logs for Python errors

### Issue: CORS Errors

**Symptoms:**
- Console shows: "Access to fetch... has been blocked by CORS policy"

**Solutions:**

**For Vercel Serverless:**
- Should never happen (same-origin)
- If it does, verify API is using correct origin

**For Separate Backend:**
- Add your Vercel domain to backend CORS settings
- Example in FastAPI:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-project.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Database Connection Errors

**Symptoms:**
- API returns 500 errors
- Logs show: "Database connection failed"

**Solutions:**
1. Verify `DATABASE_URL` is set in Vercel
2. Check format: `postgresql+asyncpg://user:pass@host:port/db`
3. Ensure database allows connections from Vercel IPs
4. Test with `/api/ready` endpoint

### Issue: Environment Variable Not Working

**Symptoms:**
- `VITE_API_URL` not taking effect
- Frontend still using wrong URL

**Solutions:**
1. Verify variable name starts with `VITE_`
2. Check it's set in correct environment (Production/Preview/Development)
3. Redeploy after setting variable
4. Clear browser cache

## Architecture Diagrams

### Vercel Serverless Architecture

```
┌─────────────────────────────────────────────────────┐
│                  User's Browser                     │
└─────────────────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────┐
│              Vercel Edge Network (Global CDN)       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────┐     ┌────────────────────┐   │
│  │  Static Assets  │     │  API Serverless    │   │
│  │  /index.html    │     │  /api/index.py     │   │
│  │  /assets/*      │     │  (FastAPI + Mangum)│   │
│  └─────────────────┘     └────────────────────┘   │
│           │                        │               │
│           └────────────────────────┘               │
│                       ↓                            │
└─────────────────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────┐
│         PostgreSQL Database (Vercel Postgres)       │
│         or External Database (Render, etc.)        │
└─────────────────────────────────────────────────────┘
```

### Separate Backend Architecture

```
┌─────────────────────────────────────────────────────┐
│                  User's Browser                     │
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        ↓                               ↓
┌─────────────────┐           ┌─────────────────────┐
│  Vercel (CDN)   │           │  Backend Server     │
│  Static Files   │           │  (Render/Custom)   │
│  /index.html    │           │  /api/*             │
│  /assets/*      │           │                     │
└─────────────────┘           └─────────────────────┘
                                        │
                                        ↓
                              ┌─────────────────────┐
                              │  PostgreSQL DB      │
                              └─────────────────────┘
```

## Best Practices

### ✅ Do's

- Use Vercel serverless backend for simplicity and performance
- Leave `VITE_API_URL` unset for Vercel deployments
- Set all environment variables in Vercel Dashboard
- Test `/api/health` after every deployment
- Use preview deployments to test changes

### ❌ Don'ts

- Don't commit `.env` files with secrets
- Don't hardcode API URLs in source code
- Don't set `VITE_API_URL` for Vercel serverless
- Don't use `localhost` URLs in production
- Don't forget to redeploy after changing variables

## Quick Reference

### Environment Variable Checklist

**Backend (Required):**
- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `SECRET_KEY` - Session encryption key
- [ ] `JWT_SECRET_KEY` - JWT token signing key

**Backend (Optional):**
- [ ] `ENVIRONMENT` - Set to "production"
- [ ] `CLOUDINARY_URL` - For image uploads
- [ ] `SENDBIRD_APP_ID` - For messaging

**Frontend (Optional):**
- [ ] `VITE_API_URL` - Only if using separate backend
- [ ] `VITE_CLOUDINARY_CLOUD_NAME` - For image uploads
- [ ] `VITE_SENDBIRD_APP_ID` - For messaging
- [ ] `VITE_GOOGLE_CLIENT_ID` - For Google OAuth
- [ ] `VITE_APPLE_CLIENT_ID` - For Apple OAuth

### Deployment Checklist

- [ ] GitHub repository connected to Vercel
- [ ] Environment variables set in Vercel Dashboard
- [ ] `api/` directory present in repository
- [ ] `vercel.json` has correct rewrites
- [ ] Database accessible from Vercel
- [ ] `/api/health` returns success
- [ ] `/api/ready` shows database connected
- [ ] Frontend loads successfully
- [ ] User can register/login

## Support

### Documentation Resources

- [VERCEL_DEPLOYMENT_GUIDE.md](./VERCEL_DEPLOYMENT_GUIDE.md) - Complete deployment guide
- [VERCEL_MIGRATION_GUIDE.md](./VERCEL_MIGRATION_GUIDE.md) - Migration from other platforms
- [VERCEL_POSTGRES_SETUP.md](./VERCEL_POSTGRES_SETUP.md) - Database setup

### Getting Help

1. Check `/api/health` endpoint first
2. Review Vercel function logs
3. Check browser console for errors
4. Verify environment variables in Vercel Dashboard
5. Create GitHub issue with error details

---

**Last Updated:** December 2025
**Verified Working:** ✅ Production deployment on Vercel

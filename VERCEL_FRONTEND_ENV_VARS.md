# ✅ FRONTEND (Vercel) — FINAL CONFIG

## Quick Reference: Environment Variables for Vercel Frontend Deployment

**Last Updated:** December 17, 2024  
**Framework:** Vite (React) - NOT Next.js

**🔒 FOREVER FIX:** See [FOREVER_FIX_ENV_VARIABLES.md](./FOREVER_FIX_ENV_VARIABLES.md) for the permanent law

**📖 See Also:** [VERCEL_FRONTEND_ENV_QUICK_REFERENCE.md](./VERCEL_FRONTEND_ENV_QUICK_REFERENCE.md) - Comprehensive step-by-step guide

---

## ⚠️ CRITICAL: Use VITE_ Prefix, NOT NEXT_PUBLIC_

This project uses **Vite (React)**, NOT Next.js.

| ✅ CORRECT | ❌ WRONG |
|-----------|---------|
| `VITE_API_URL` | ~~`NEXT_PUBLIC_BACKEND_URL`~~ |
| `VITE_SOCKET_URL` | ~~`NEXT_PUBLIC_API_URL`~~ |
| `VITE_CLOUDINARY_CLOUD_NAME` | ~~`NEXT_PUBLIC_CLOUDINARY_NAME`~~ |

**Why?** Vite requires `VITE_` prefix for environment variables to be exposed to client-side code. Next.js uses `NEXT_PUBLIC_` which will NOT work in this project.

---

## 6️⃣ Environment Variables (Vercel Dashboard)

### Where to Configure

**Go to:** Vercel Dashboard → Your Project → Settings → Environment Variables  
**Direct Link:** `https://vercel.com/[your-team]/[project-name]/settings/environment-variables`

### Configuration Options

Choose the option that matches your deployment architecture:

#### Option A: Railway Backend ⭐ Recommended for Separate Backend

```bash
VITE_API_URL=https://your-backend.up.railway.app
VITE_SOCKET_URL=https://your-backend.up.railway.app
```

**Use when:**
- ✅ Backend is deployed to Railway
- ✅ Frontend is deployed to Vercel
- ✅ Using Railway PostgreSQL database

**Example URLs:**
- Backend: `https://hiremebahamas-production.up.railway.app`
- Frontend: `https://hiremebahamas.vercel.app`

---

#### Option B: Render Backend

```bash
VITE_API_URL=https://your-backend.onrender.com
VITE_SOCKET_URL=https://your-backend.onrender.com
```

**Use when:**
- ✅ Backend is deployed to Render
- ✅ Frontend is deployed to Vercel
- ✅ Using Render PostgreSQL database

**Example URLs:**
- Backend: `https://hire-me-bahamas.onrender.com`
- Frontend: `https://hiremebahamas.vercel.app`

---

#### Option C: Vercel Serverless Backend (Same-Origin) ⭐ Recommended for All-in-One

```bash
# Do NOT set VITE_API_URL
# Frontend automatically detects Vercel deployment
# Uses window.location.origin for API calls
```

**Use when:**
- ✅ Both frontend and backend deployed to Vercel
- ✅ Using `api/` directory for serverless functions
- ✅ Want same-origin requests (no CORS issues)
- ✅ Want fastest performance (edge network)

**How it works:**
- Frontend: `https://hiremebahamas.vercel.app`
- Backend: `https://hiremebahamas.vercel.app/api/*`
- Auto-detected: No configuration needed!

---

## How to Add Environment Variables in Vercel

### Step-by-Step Instructions

1. **Navigate to Vercel Dashboard**
   - Go to: https://vercel.com/dashboard
   - Select your project

2. **Open Environment Variables**
   - Click **Settings** (left sidebar)
   - Click **Environment Variables**

3. **Add New Variable**
   - Click **"Add New"** button
   - Enter **Name**: `VITE_API_URL`
   - Enter **Value**: Your backend URL (e.g., `https://your-app.up.railway.app`)
   - Select **All** environments:
     - ✅ Production
     - ✅ Preview  
     - ✅ Development

4. **Save and Redeploy**
   - Click **Save**
   - Go to **Deployments** tab
   - Click **"..."** on latest deployment
   - Click **"Redeploy"** to apply changes

### Screenshot Reference

```
┌─────────────────────────────────────────┐
│ Add Environment Variable                │
├─────────────────────────────────────────┤
│ Name:  VITE_API_URL                     │
│ Value: https://your-app.up.railway.app  │
│                                         │
│ Environments:                           │
│ ☑ Production                           │
│ ☑ Preview                              │
│ ☑ Development                          │
│                                         │
│           [Cancel]  [Save]              │
└─────────────────────────────────────────┘
```

---

## ✅ Verification

### Test Your Configuration

#### 1. Check Frontend Loads
```bash
curl https://your-frontend.vercel.app
# Should return HTML without errors
```

#### 2. Check Browser Console
Open your Vercel frontend URL in browser and check console:
```
=== API CONFIGURATION ===
API Base URL: https://your-backend.up.railway.app
Source: Environment Variable
========================
```

#### 3. Test API Connection
```bash
# If using separate backend:
curl https://your-backend.up.railway.app/api/health

# If using Vercel serverless:
curl https://your-frontend.vercel.app/api/health

# Expected response:
{"status":"healthy","database":"connected"}
```

#### 4. Verify in Browser Network Tab
1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Refresh page
4. Look for API calls
5. Should go to correct backend URL

---

## ⚠️ Common Mistakes

### ❌ Mistake #1: Using Next.js Environment Variable Names
```bash
# WRONG - This will NOT work:
NEXT_PUBLIC_BACKEND_URL=https://your-backend.up.railway.app

# CORRECT - Use VITE_ prefix:
VITE_API_URL=https://your-backend.up.railway.app
```

### ❌ Mistake #2: Missing VITE_ Prefix
```bash
# WRONG - Variables without VITE_ are not exposed to frontend:
API_URL=https://your-backend.up.railway.app

# CORRECT:
VITE_API_URL=https://your-backend.up.railway.app
```

### ❌ Mistake #3: Forgetting to Redeploy
Adding environment variables doesn't automatically redeploy. You MUST:
1. Add the variable
2. Go to Deployments
3. Redeploy the latest deployment

### ❌ Mistake #4: Using http:// Instead of https://
```bash
# WRONG - Production should use HTTPS:
VITE_API_URL=http://your-backend.up.railway.app

# CORRECT:
VITE_API_URL=https://your-backend.up.railway.app
```

### ❌ Mistake #5: Setting VITE_API_URL for Vercel Serverless
```bash
# WRONG - When using Vercel serverless backend, don't set:
VITE_API_URL=https://your-frontend.vercel.app

# CORRECT - Leave it unset for same-origin detection:
# (no VITE_API_URL variable at all)
```

---

## 🔧 Troubleshooting

### Issue: "API calls failing with 404"

**Symptom:** Frontend can't connect to backend, 404 errors in console

**Solution:**
1. Verify `VITE_API_URL` is set correctly in Vercel
2. Check backend URL is accessible: `curl https://your-backend-url/health`
3. Ensure you redeployed after adding variables
4. Check browser console for actual URL being called

### Issue: "Environment variable not updating"

**Symptom:** Changed `VITE_API_URL` but still using old URL

**Solution:**
1. After changing variable, you MUST redeploy
2. Clear browser cache (Ctrl+Shift+R)
3. Check Vercel deployment logs to confirm new variable

### Issue: "CORS errors in browser"

**Symptom:** `Access-Control-Allow-Origin` errors in console

**Solution:**
1. Verify backend CORS is configured to allow your Vercel domain
2. Check backend allows `https://your-frontend.vercel.app`
3. Consider using Vercel serverless (same-origin, no CORS issues)

### Issue: "Variable showing in build but not runtime"

**Symptom:** Variable appears in build logs but not available in app

**Solution:**
1. Ensure using `VITE_` prefix (not `NEXT_PUBLIC_` for Next.js)
2. Check accessing via `import.meta.env.VITE_API_URL` (not `process.env`)
3. Rebuild and redeploy

---

## 📚 Related Documentation

- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Complete deployment guide
- **[VERCEL_FRONTEND_BACKEND_SETUP.md](./VERCEL_FRONTEND_BACKEND_SETUP.md)** - Detailed frontend-backend connection
- **[DIRECT_LINKS_WHERE_TO_CONFIGURE.md](./DIRECT_LINKS_WHERE_TO_CONFIGURE.md)** - All configuration links
- **[frontend/.env.example](./frontend/.env.example)** - Environment variable template
- **[RAILWAY_DATABASE_SETUP.md](./RAILWAY_DATABASE_SETUP.md)** - Railway backend setup
- **[README.md](./README.md)** - Main project documentation

---

## 🎯 Quick Decision Tree

**Which option should I use?**

```
Do you want to deploy backend separately?
│
├─ YES → Choose Option A (Railway) or Option B (Render)
│   │
│   ├─ Railway Backend
│   │   └─ Set: VITE_API_URL=https://your-app.up.railway.app
│   │
│   └─ Render Backend
│       └─ Set: VITE_API_URL=https://your-app.onrender.com
│
└─ NO → Choose Option C (Vercel Serverless)
    │
    └─ All-in-One Vercel Deployment
        └─ Don't set VITE_API_URL (auto-detects same-origin)
```

---

## ✨ Summary

| Configuration | VITE_API_URL | Benefits |
|--------------|--------------|----------|
| **Railway Backend** | `https://your-app.up.railway.app` | Separate deployment, more control |
| **Render Backend** | `https://your-app.onrender.com` | Separate deployment, alternative host |
| **Vercel Serverless** | Leave unset | Same-origin, no CORS, fastest |

**Most Common Setup:**
- Frontend: Vercel
- Backend: Railway
- Database: Railway PostgreSQL
- Environment Variable: `VITE_API_URL=https://your-app.up.railway.app`

---

**Questions?** Check the related documentation above or open an issue on GitHub.

**Last Updated:** December 15, 2025  
**Maintained By:** HireMeBahamas Development Team

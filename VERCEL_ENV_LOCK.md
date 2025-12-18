# 8️⃣ VERCEL ENV LOCK (MANDATORY)

**Status**: 🔴 MANDATORY - Must be followed for all Vercel deployments  
**Last Updated**: December 17, 2025  
**Framework**: Vite (React) - NOT Next.js

---

## 📋 MANDATORY Environment Variable Configuration

### Required Configuration

Environment variables for Vercel frontend deployment:

```bash
VITE_API_URL=https://your-backend.onrender.com
```

**OR** if using Render:

```bash
VITE_API_URL=https://your-backend.up.render.app
```

---

## 🚫 ABSOLUTE PROHIBITIONS

### ❌ No NEXT_PUBLIC_ Prefix

```bash
# ❌ WRONG - This project uses Vite, NOT Next.js
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com

# ✅ CORRECT - Use VITE_ prefix for Vite/React
VITE_API_URL=https://your-backend.onrender.com
```

**Why this fails:**
- This is a **Vite/React** project (in `/frontend`), not Next.js
- Vercel only exposes `NEXT_PUBLIC_*` variables to Next.js projects
- Using `NEXT_PUBLIC_` in a Vite project results in `undefined` values
- Frontend will fail to connect to backend

### ❌ No Backend Secrets

```bash
# ❌ NEVER expose backend secrets with VITE_ prefix
VITE_DATABASE_URL=postgresql://...          # Security risk!
VITE_JWT_SECRET=your-secret                 # Security risk!
VITE_SECRET_KEY=your-key                    # Security risk!
VITE_CRON_SECRET=your-cron-secret          # Security risk!

# ✅ CORRECT - These belong in backend environment only
# Set these in Render/Render backend service (NOT Vercel frontend)
DATABASE_URL=postgresql://...               # Backend only
JWT_SECRET=your-secret                      # Backend only
SECRET_KEY=your-key                         # Backend only
CRON_SECRET=your-cron-secret               # Backend only
```

**Why this is dangerous:**
- Variables with `VITE_` prefix are exposed to client-side JavaScript
- Anyone can view these in browser DevTools → Network tab or Sources tab
- Exposed secrets allow unauthorized database access, token forging, etc.
- **CRITICAL SECURITY VIOLATION**

### ❌ No DATABASE_URL in Frontend

```bash
# ❌ NEVER set DATABASE_URL in Vercel frontend environment
DATABASE_URL=postgresql://...               # Frontend doesn't need this
VITE_DATABASE_URL=postgresql://...          # Security risk!

# ✅ CORRECT - Frontend only needs API URL
VITE_API_URL=https://your-backend.onrender.com
```

**Why this is wrong:**
- Frontend connects to backend via REST API, not directly to database
- Exposing `DATABASE_URL` creates security vulnerability
- Frontend has no database driver (SQLAlchemy, asyncpg are backend-only)
- Database credentials should NEVER be in client-side code

### ❌ No localhost URLs in Production

```bash
# ❌ NEVER use localhost in production environment variables
VITE_API_URL=http://localhost:8000         # Only for local dev
VITE_API_URL=http://127.0.0.1:8000        # Only for local dev

# ✅ CORRECT - Use actual backend URL in production
VITE_API_URL=https://your-backend.onrender.com
```

**Why this fails:**
- `localhost` refers to the user's computer, not your backend server
- Production users' browsers cannot access your local development server
- API calls will fail with "Connection refused" or similar errors
- Use `localhost` only in local `.env` file for development

---

## ✅ Correct Configuration

### For Vercel Dashboard → Environment Variables

Add these variables in your Vercel project:

1. **VITE_API_URL** (Required)
   - **Name**: `VITE_API_URL`
   - **Value**: `https://your-backend.onrender.com` (or your Render URL)
   - **Environments**: Production, Preview, Development (all three)

2. **DO NOT ADD** (Backend-only variables)
   - ❌ `DATABASE_URL` - Backend only
   - ❌ `JWT_SECRET` - Backend only
   - ❌ `SECRET_KEY` - Backend only
   - ❌ `CRON_SECRET` - Backend only

### Example Configuration

```bash
# Vercel Frontend Environment Variables (Dashboard)
# ================================================
VITE_API_URL=https://hire-me-bahamas.onrender.com

# Optional (if using):
VITE_CLOUDINARY_CLOUD_NAME=your_cloud_name
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_SENDBIRD_APP_ID=your_sendbird_app_id
```

```bash
# Backend Environment Variables (Render/Render Dashboard)
# ========================================================
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
JWT_SECRET=your-jwt-secret-here
SECRET_KEY=your-secret-key-here
CRON_SECRET=your-cron-secret-here
FRONTEND_URL=https://hiremebahamas.vercel.app
ENVIRONMENT=production
PORT=8000
```

---

## 🔍 How to Verify

### Step 1: Check Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Select your HireMeBahamas project
3. Navigate to **Settings** → **Environment Variables**
4. Verify:
   - ✅ `VITE_API_URL` exists with your backend URL
   - ✅ NO `NEXT_PUBLIC_API_URL` (wrong framework)
   - ✅ NO `DATABASE_URL` (backend only)
   - ✅ NO `JWT_SECRET` or `SECRET_KEY` (backend only)
   - ✅ NO `localhost` URLs (production only)

### Step 2: Check Browser Console

After deployment, open your Vercel app (F12 for DevTools):

```javascript
// Should show your backend URL
console.log('API URL:', import.meta.env.VITE_API_URL);
// Expected: "API URL: https://your-backend.onrender.com"
// NOT: "API URL: undefined"

// Should be undefined (backend only)
console.log('Database:', import.meta.env.VITE_DATABASE_URL);
// Expected: "Database: undefined"
// This is CORRECT - database URL should NOT be in frontend
```

### Step 3: Check Network Tab

1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Refresh the page
4. Look for API requests
5. Verify:
   - ✅ Requests go to your backend URL (e.g., `https://your-backend.onrender.com/api/...`)
   - ❌ NO requests to `localhost` or `127.0.0.1`
   - ❌ NO requests to `undefined` or null URLs

---

## 📚 Why This Matters

### The Framework Reality

| What People Think | Reality |
|-------------------|---------|
| "I'll use NEXT_PUBLIC_API_URL" | ❌ This is a **Vite** project, not Next.js |
| "Just add DATABASE_URL to frontend" | ❌ **Security violation** - exposes credentials |
| "localhost works in dev, so it'll work in prod" | ❌ **Network error** - users can't reach localhost |
| "I can use any variable name" | ❌ **Must have VITE_ prefix** or won't work |

### The Security Reality

```bash
# If you do this:
VITE_DATABASE_URL=postgresql://admin:password123@db.host.com:5432/prod

# Then users can do this in browser console:
console.log(import.meta.env.VITE_DATABASE_URL)
// Outputs: "postgresql://admin:password123@db.host.com:5432/prod"

# Now they have:
✅ Your database host
✅ Your database username  
✅ Your database password
✅ Your database name
✅ Full access to your production database

# Result:
🔥 Data breach
🔥 Data deletion
🔥 Account compromise
🔥 Application destroyed
```

---

## 🎯 Compliance Checklist

Before deploying to Vercel, verify:

- [ ] Using `VITE_API_URL` (NOT `NEXT_PUBLIC_API_URL`)
- [ ] Backend URL uses `https://` (NOT `http://`)
- [ ] Backend URL is NOT `localhost` or `127.0.0.1`
- [ ] NO `DATABASE_URL` in Vercel environment variables
- [ ] NO `VITE_DATABASE_URL` (security risk)
- [ ] NO `JWT_SECRET` or `SECRET_KEY` with `VITE_` prefix
- [ ] NO `VITE_CRON_SECRET` (security risk)
- [ ] All three environments configured (Production, Preview, Development)
- [ ] Redeployed after adding/changing variables

---

## 🆘 Troubleshooting

### Problem: "API URL is undefined"

**Symptoms:**
```javascript
console.log(import.meta.env.VITE_API_URL); // undefined
```

**Solution:**
1. Check variable name is exactly `VITE_API_URL` (case-sensitive)
2. NOT `NEXT_PUBLIC_API_URL` (wrong framework)
3. NOT `API_URL` (missing prefix)
4. Must be set in **Vercel Dashboard** (not just local `.env`)
5. Must redeploy after adding variable

### Problem: "Network error / Failed to fetch"

**Symptoms:**
- API calls fail in production
- Works locally but not on Vercel
- Console shows "Failed to fetch" or "Network Error"

**Solution:**
1. Check `VITE_API_URL` is NOT `localhost` or `127.0.0.1`
2. Verify backend URL is accessible: `curl https://your-backend.onrender.com/health`
3. Ensure backend URL uses `https://` (not `http://`)
4. Check backend CORS allows your Vercel domain

### Problem: "CORS error"

**Symptoms:**
```
Access to fetch at 'https://backend.com' from origin 'https://app.vercel.app' 
has been blocked by CORS policy
```

**Solution:**
1. Configure backend CORS to allow your Vercel domain
2. In backend (Render/Render), add environment variable:
   ```bash
   FRONTEND_URL=https://hiremebahamas.vercel.app
   ```
3. Backend CORS should include this URL in allowed origins

---

## 🔗 Related Documentation

- **[FOREVER_FIX_ENV_VARIABLES.md](./FOREVER_FIX_ENV_VARIABLES.md)** - Complete environment variable law
- **[VERCEL_ENV_CHECK.md](./VERCEL_ENV_CHECK.md)** - Detailed Vercel setup guide
- **[frontend/.env.example](./frontend/.env.example)** - Environment variable template
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[SECURITY.md](./SECURITY.md)** - Security best practices

---

## 📞 Quick Reference

### ✅ DO

```bash
VITE_API_URL=https://your-backend.onrender.com
VITE_CLOUDINARY_CLOUD_NAME=your_cloud_name
VITE_GOOGLE_CLIENT_ID=your_google_client_id
```

### ❌ DON'T

```bash
NEXT_PUBLIC_API_URL=...        # Wrong framework
DATABASE_URL=...               # Backend only
VITE_DATABASE_URL=...          # Security risk
VITE_JWT_SECRET=...            # Security risk
VITE_SECRET_KEY=...            # Security risk
API_URL=...                    # Missing prefix
VITE_API_URL=http://localhost  # No localhost in prod
```

---

**🔒 This is a MANDATORY LOCK. Violation of these rules will cause deployment failures or security breaches.**

**Last Updated**: December 17, 2025  
**Maintained By**: HireMeBahamas Development Team  
**Framework**: Vite (React)  
**Required Prefix**: `VITE_` (NOT `NEXT_PUBLIC_`)

# ✅ Vercel Frontend Environment Variables - Quick Reference

**⚠️ CRITICAL: Read This First!**

This project uses **Vite (React)**, NOT Next.js.

## 🚨 Common Misconception

| ❌ WRONG (Next.js) | ✅ CORRECT (Vite/React) |
|-------------------|------------------------|
| `NEXT_PUBLIC_BACKEND_URL` | `VITE_API_URL` |
| `NEXT_PUBLIC_API_URL` | `VITE_API_URL` |

**If you see documentation mentioning `NEXT_PUBLIC_*` variables, that's for Next.js projects only. This HireMeBahamas project uses Vite!**

---

## 📝 Environment Variable Configuration

### 6️⃣ Frontend Environment Variable: `VITE_API_URL`

**Location:** Vercel Dashboard → Your Project → Settings → Environment Variables

**Direct URL:** `https://vercel.com/[your-team]/[project-name]/settings/environment-variables`

### Configuration Options

Choose the option that matches your deployment architecture:

#### Option 1: Railway Backend (Recommended)

```bash
VITE_API_URL=https://your-backend.up.railway.app
```

**When to use:**
- ✅ Backend deployed to Railway
- ✅ Frontend deployed to Vercel
- ✅ Separate frontend/backend deployments

**Example:**
```bash
VITE_API_URL=https://hiremebahamas-production.up.railway.app
```

---

#### Option 2: Render Backend

```bash
VITE_API_URL=https://your-backend.onrender.com
```

**When to use:**
- ✅ Backend deployed to Render
- ✅ Frontend deployed to Vercel
- ✅ Separate frontend/backend deployments

**Example:**
```bash
VITE_API_URL=https://hiremebahamas.onrender.com
```

---

#### Option 3: Vercel Serverless Backend (Same-Origin)

```bash
# DO NOT SET VITE_API_URL
# Leave it unset/blank
```

**When to use:**
- ✅ Both frontend and backend on Vercel
- ✅ Using `/api/` serverless functions
- ✅ Want same-origin requests (no CORS)

**How it works:**
- Frontend automatically detects Vercel deployment
- Uses `window.location.origin` for API calls
- API available at: `https://your-app.vercel.app/api/*`

---

## 🔧 How to Add Environment Variables in Vercel

1. **Navigate to Vercel Dashboard**
   - Go to: https://vercel.com/dashboard
   - Select your project

2. **Open Environment Variables**
   - Click **Settings** (left sidebar)
   - Click **Environment Variables**

3. **Add New Variable**
   - Click **"Add New"** button
   - **Name:** `VITE_API_URL`
   - **Value:** Your backend URL (e.g., `https://your-app.up.railway.app`)
   - **Environments:** Select all:
     - ✅ Production
     - ✅ Preview
     - ✅ Development

4. **Save and Redeploy**
   - Click **Save**
   - Go to **Deployments** tab
   - Click **"..."** on latest deployment
   - Click **"Redeploy"**

---

## ✅ Verification Steps

### 1. Check Browser Console

After deployment, open your Vercel site and check the browser console:

```
=== API CONFIGURATION ===
API Base URL: https://your-backend.up.railway.app
Source: Environment Variable
========================
```

### 2. Test API Connection

```bash
# Test backend health endpoint
curl https://your-backend.up.railway.app/api/health

# Expected response:
{"status":"healthy","database":"connected"}
```

### 3. Verify in Network Tab

1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Refresh the page
4. Look for API calls
5. Confirm they're going to the correct backend URL

---

## ⚠️ Common Mistakes to Avoid

### ❌ Mistake #1: Using Next.js Variable Names

```bash
# WRONG - This will NOT work in Vite:
NEXT_PUBLIC_BACKEND_URL=https://your-backend.up.railway.app

# CORRECT - Use VITE_ prefix:
VITE_API_URL=https://your-backend.up.railway.app
```

**Why?** Vite requires `VITE_` prefix for client-side environment variables. Next.js uses `NEXT_PUBLIC_` which is completely ignored by Vite.

### ❌ Mistake #2: Missing VITE_ Prefix

```bash
# WRONG - Won't be exposed to frontend:
API_URL=https://your-backend.up.railway.app
BACKEND_URL=https://your-backend.up.railway.app

# CORRECT:
VITE_API_URL=https://your-backend.up.railway.app
```

### ❌ Mistake #3: Forgetting to Redeploy

Environment variable changes don't automatically take effect. You MUST:
1. Add/update the variable
2. Trigger a redeploy

### ❌ Mistake #4: Using http:// Instead of https://

```bash
# WRONG - Production should use HTTPS:
VITE_API_URL=http://your-backend.up.railway.app

# CORRECT - Always use HTTPS in production:
VITE_API_URL=https://your-backend.up.railway.app
```

### ❌ Mistake #5: Setting VITE_API_URL for Same-Origin Deployment

```bash
# WRONG - When using Vercel serverless backend:
VITE_API_URL=https://your-frontend.vercel.app

# CORRECT - Leave it completely unset for same-origin:
# (Don't add VITE_API_URL at all)
```

---

## 🎯 Quick Decision Guide

**Which configuration should I use?**

```
Question: Where is your backend deployed?

├─ Railway
│  └─ Set: VITE_API_URL=https://your-app.up.railway.app
│
├─ Render  
│  └─ Set: VITE_API_URL=https://your-app.onrender.com
│
└─ Vercel (same domain as frontend)
   └─ Don't set VITE_API_URL (auto-detects)
```

---

## 📊 Summary Table

| Deployment | Variable to Set | Example Value |
|-----------|----------------|---------------|
| Railway Backend | `VITE_API_URL` | `https://your-app.up.railway.app` |
| Render Backend | `VITE_API_URL` | `https://your-app.onrender.com` |
| Vercel Serverless | *(leave unset)* | N/A |
| Local Development | `VITE_API_URL` | `http://localhost:8000` |

---

## 📚 Related Documentation

- **[VERCEL_FRONTEND_ENV_VARS.md](./VERCEL_FRONTEND_ENV_VARS.md)** - Detailed environment variable guide
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[DIRECT_LINKS_WHERE_TO_CONFIGURE.md](./DIRECT_LINKS_WHERE_TO_CONFIGURE.md)** - Platform-specific configuration links
- **[frontend/.env.example](./frontend/.env.example)** - Environment variable template
- **[VERCEL_MIGRATION_GUIDE.md](./VERCEL_MIGRATION_GUIDE.md)** - Migration from other platforms

---

## 🆘 Still Having Issues?

1. **Check the browser console** for error messages
2. **Verify the backend is running** with `curl https://your-backend-url/health`
3. **Confirm environment variable is set** in Vercel Dashboard
4. **Make sure you redeployed** after adding the variable
5. **Clear browser cache** (Ctrl+Shift+R or Cmd+Shift+R)

---

**Last Updated:** December 15, 2025  
**Project:** HireMeBahamas  
**Framework:** Vite (React) - NOT Next.js

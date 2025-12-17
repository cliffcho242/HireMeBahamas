# 4️⃣ VERCEL ENV CHECK (MANDATORY)

## ⚠️ CRITICAL: Environment Variable Configuration for HireMeBahamas

**Last Updated**: December 17, 2025  
**Status**: 🔴 MANDATORY - Required for Deployment  
**Framework**: Vite (React) - NOT Next.js

---

## 📋 Quick Summary

This project uses **Vite/React**, which requires **`VITE_`** prefix for environment variables (NOT `NEXT_PUBLIC_`).

### Required Environment Variables

In Vercel Dashboard → Project → Settings → Environment Variables, you MUST configure:

```bash
VITE_API_URL=https://your-backend.onrender.com
```

**Check all three environments:**
- ✅ Production
- ✅ Preview
- ✅ Development

---

## 🚨 IMPORTANT: Correct Variable Naming

### ❌ INCORRECT (This Will NOT Work)
```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com  # Wrong framework!
```

### ✅ CORRECT (Use This)
```bash
VITE_API_URL=https://your-backend.onrender.com
```

**Why?**
- This project uses **Vite** (not Next.js)
- Vite requires `VITE_` prefix for client-side variables
- `NEXT_PUBLIC_` prefix only works in Next.js projects
- Without the correct prefix, the variable will be `undefined` in the browser

---

## 📍 Where to Configure

### Step 1: Access Vercel Dashboard

1. Go to: **https://vercel.com/dashboard**
2. Select your **HireMeBahamas project**
3. Click **Settings** (left sidebar)
4. Click **Environment Variables**

**Direct URL Pattern:**
```
https://vercel.com/[your-team]/[project-name]/settings/environment-variables
```

### Step 2: Add Environment Variables

#### Option A: Separate Backend (Railway/Render) ⭐ RECOMMENDED

If your backend is deployed separately:

```bash
# Required
VITE_API_URL=https://your-backend-url

# Examples:
# Railway: VITE_API_URL=https://hiremebahamas-production.up.railway.app
# Render:  VITE_API_URL=https://hiremebahamas.onrender.com
```

**How to add:**
1. Click **"Add New"** button
2. **Name**: `VITE_API_URL`
3. **Value**: Your backend URL (e.g., `https://hiremebahamas.onrender.com`)
4. **Environments**: Select ALL three:
   - ✅ Production
   - ✅ Preview
   - ✅ Development
5. Click **Save**

#### Option B: Vercel Serverless Backend (Same-Origin)

If using Vercel's built-in serverless functions (api/ directory):

```bash
# ⚠️ DO NOT set VITE_API_URL
# Frontend automatically detects same-origin and uses relative paths
# API calls will go to: https://your-app.vercel.app/api/*
```

**No configuration needed!** The frontend automatically detects Vercel deployment and uses same-origin requests.

### Step 3: Verify Configuration

1. Go to **Settings** → **Environment Variables**
2. Confirm you see:
   ```
   VITE_API_URL
   Value: https://your-backend.onrender.com (or your backend URL)
   Environments: Production, Preview, Development
   ```

### Step 4: Redeploy

**CRITICAL:** Adding environment variables does NOT automatically redeploy your app!

1. Go to **Deployments** tab
2. Find the latest deployment
3. Click the **"..."** menu (three dots)
4. Click **"Redeploy"**
5. Wait for deployment to complete

---

## 🔍 Verification Steps

### 1. Check Browser Console

After deployment, open your Vercel app and check the browser console (F12):

```javascript
console.log('API URL:', import.meta.env.VITE_API_URL);
// Should output: "API URL: https://your-backend.onrender.com"
// NOT: "API URL: undefined"
```

### 2. Check API Configuration Log

Look for this in the browser console on page load:

```
=== API CONFIGURATION ===
API Base URL: https://your-backend.onrender.com
Source: Environment Variable
========================
```

### 3. Test API Connection

```bash
# Test your backend is accessible
curl https://your-backend.onrender.com/health

# Expected response:
# {"status":"healthy","database":"connected"}
```

### 4. Check Network Tab

1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Refresh the page
4. Look for API requests
5. Verify they're going to the correct backend URL

---

## 🛠️ Backend URL Examples

### For Railway Backend

```bash
VITE_API_URL=https://hiremebahamas-production.up.railway.app
```

**How to find your Railway URL:**
1. Go to: https://railway.app/dashboard
2. Select your project
3. Click your backend service
4. Click **Settings** tab
5. Scroll to **Networking** section
6. Copy the **Public Domain**

### For Render Backend

```bash
VITE_API_URL=https://hiremebahamas.onrender.com
```

**How to find your Render URL:**
1. Go to: https://dashboard.render.com
2. Select your web service
3. Copy the URL shown at the top (e.g., `hiremebahamas.onrender.com`)
4. Add `https://` prefix

### For Local Development

```bash
VITE_API_URL=http://localhost:8000
```

**Note:** HTTP is acceptable for localhost only. Always use HTTPS in production.

---

## ⚠️ Common Mistakes

### Mistake #1: Using NEXT_PUBLIC_ Prefix

```bash
❌ WRONG: NEXT_PUBLIC_API_URL=https://backend.com
✅ CORRECT: VITE_API_URL=https://backend.com
```

**Why it fails:** This is a Vite project, not Next.js. Vercel will NOT expose `NEXT_PUBLIC_*` variables to Vite apps.

### Mistake #2: Missing VITE_ Prefix

```bash
❌ WRONG: API_URL=https://backend.com
✅ CORRECT: VITE_API_URL=https://backend.com
```

**Why it fails:** Without the `VITE_` prefix, the variable is not exposed to client-side code.

### Mistake #3: Using HTTP Instead of HTTPS

```bash
❌ WRONG (Production): VITE_API_URL=http://backend.com
✅ CORRECT: VITE_API_URL=https://backend.com
```

**Why it fails:** Modern browsers block mixed content (HTTPS frontend calling HTTP backend).

### Mistake #4: Forgetting to Redeploy

```bash
✅ Added variable in Vercel Dashboard
❌ Forgot to click "Redeploy"
❌ App still shows old configuration
```

**Solution:** Always redeploy after adding/changing environment variables.

### Mistake #5: Not Selecting All Environments

```bash
✅ Added VITE_API_URL
✅ Selected Production ✅
❌ Forgot Preview
❌ Forgot Development
```

**Result:** Variable only works in Production, not in Preview or Development environments.

**Solution:** Always select all three environments (Production, Preview, Development).

---

## 🎯 Complete Configuration Checklist

Use this checklist to ensure everything is configured correctly:

- [ ] **Verified project uses Vite** (not Next.js)
- [ ] **Opened Vercel Dashboard** → Project → Settings → Environment Variables
- [ ] **Added VITE_API_URL** (NOT NEXT_PUBLIC_API_URL)
- [ ] **Set correct backend URL** (Railway or Render URL with https://)
- [ ] **Selected all environments:**
  - [ ] Production ✅
  - [ ] Preview ✅
  - [ ] Development ✅
- [ ] **Saved the variable**
- [ ] **Redeployed the application** (Deployments → ... → Redeploy)
- [ ] **Waited for deployment to complete**
- [ ] **Opened app in browser**
- [ ] **Checked browser console** (F12) for API URL
- [ ] **Verified API calls** in Network tab
- [ ] **Tested API connection** with curl or browser

---

## 🔧 Troubleshooting

### Issue: API URL is undefined in browser

**Symptoms:**
```javascript
console.log(import.meta.env.VITE_API_URL); // undefined
```

**Solutions:**
1. ✅ Verify variable name is exactly `VITE_API_URL` (case-sensitive)
2. ✅ Check you're not using `NEXT_PUBLIC_API_URL` (wrong framework)
3. ✅ Confirm variable is set in Vercel Dashboard
4. ✅ Ensure you redeployed after adding the variable
5. ✅ Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
6. ✅ Check deployment logs for any errors

### Issue: API calls fail with 404

**Symptoms:**
- API requests return 404 errors
- Network tab shows requests going to wrong URL

**Solutions:**
1. ✅ Verify backend URL is correct and accessible
2. ✅ Test backend directly: `curl https://your-backend-url/health`
3. ✅ Check CORS is configured on backend to allow your Vercel domain
4. ✅ Ensure backend URL uses `https://` (not `http://`)

### Issue: CORS errors in browser

**Symptoms:**
```
Access to fetch at 'https://backend.com' from origin 'https://app.vercel.app' 
has been blocked by CORS policy
```

**Solutions:**
1. ✅ Configure backend CORS to allow your Vercel domain
2. ✅ Add `https://your-app.vercel.app` to backend ALLOWED_ORIGINS
3. ✅ Consider using Vercel serverless (same-origin, no CORS issues)

### Issue: Variable works locally but not on Vercel

**Symptoms:**
- Works with `.env` file locally
- Fails on Vercel deployment

**Solutions:**
1. ✅ Local `.env` files are NOT deployed to Vercel
2. ✅ Must add variables to Vercel Dashboard manually
3. ✅ Check exact variable names match (including case)
4. ✅ Verify prefix is `VITE_` (not `NEXT_PUBLIC_`)

---

## 🔐 Security Notes

### ✅ Safe to Expose (Frontend)
These can use `VITE_` prefix:
- API URLs (`VITE_API_URL`)
- Public API keys (Google Client ID, Cloudinary cloud name)
- Feature flags
- Public configuration

### ❌ NEVER Expose (Backend Only)
These should NEVER have `VITE_` prefix:
- Database connection strings (`DATABASE_URL`)
- JWT secrets (`JWT_SECRET`, `SECRET_KEY`)
- Private API keys
- Admin credentials
- Encryption keys

**Rule of Thumb:**
- If users can see it in browser DevTools → must be public-safe
- If it grants access or contains secrets → backend only (no `VITE_` prefix)

---

## 📚 Related Documentation

- **[VERCEL_FRONTEND_ENV_VARS.md](./VERCEL_FRONTEND_ENV_VARS.md)** - Detailed environment variable guide
- **[FOREVER_FIX_ENV_VARIABLES.md](./FOREVER_FIX_ENV_VARIABLES.md)** - Environment variable law
- **[DIRECT_LINKS_WHERE_TO_CONFIGURE.md](./DIRECT_LINKS_WHERE_TO_CONFIGURE.md)** - All configuration links
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Complete deployment guide
- **[frontend/.env.example](./frontend/.env.example)** - Environment variable template
- **[README.md](./README.md)** - Main project documentation

---

## 🎉 Success Criteria

After completing this guide, you should have:

✅ **VITE_API_URL** set in Vercel Dashboard  
✅ All three environments configured (Production, Preview, Development)  
✅ Correct backend URL (Railway or Render with https://)  
✅ Application redeployed with new variables  
✅ Browser console shows correct API URL  
✅ API calls successfully reaching backend  
✅ No CORS errors in browser console  
✅ Health check endpoint returning success  

---

## 📞 Support

If you're still having issues:

1. **Check Vercel Status**: https://www.vercel-status.com
2. **Check Backend Status**: Visit your backend URL + `/health`
3. **Review Deployment Logs**: Vercel Dashboard → Deployments → Latest → View Function Logs
4. **Check Browser Console**: Look for error messages or warnings
5. **Verify Network Requests**: Check Network tab in browser DevTools

---

**Last Updated**: December 17, 2025  
**Maintained By**: HireMeBahamas Development Team  
**Framework**: Vite (React)  
**Required Prefix**: `VITE_` (NOT `NEXT_PUBLIC_`)

# Vercel Environment Setup Guide

## Setting VITE_API_URL in Vercel Dashboard

This guide walks you through setting up the `VITE_API_URL` environment variable in your Vercel dashboard to connect your frontend to the backend.

---

## 📋 Prerequisites

- Access to your Vercel dashboard
- Your backend URL (e.g., `https://your-backend.vercel.app` or `https://your-backend.railway.app`)

---

## 🔧 Step-by-Step Instructions

### Step 1: Access Your Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Sign in with your account
3. Select your **HireMeBahamas** project

### Step 2: Navigate to Environment Variables

1. Click on **Settings** tab at the top
2. In the left sidebar, click **Environment Variables**

### Step 3: Add VITE_API_URL Variable

1. In the "Environment Variables" section, you'll see a form to add new variables
2. Fill in the following:
   - **Key (Name)**: `VITE_API_URL`
   - **Value**: Your backend URL (examples below)
   - **Environments**: Select all three:
     - ✅ Production
     - ✅ Preview
     - ✅ Development

#### Backend URL Examples:

**If using Vercel for backend:**
```
https://your-backend.vercel.app
```

**If using Railway for backend:**
```
https://your-backend.railway.app
```

**If using Render for backend:**
```
https://hiremebahamas.onrender.com
```

**Important Notes:**
- ⚠️ Do NOT include a trailing slash (`/`)
- ⚠️ Must start with `https://` (not `http://`)
- ⚠️ Use your actual backend domain

### Step 4: Save the Environment Variable

1. Click **Save** or **Add** button
2. You should see the variable appear in the list

### Step 5: Redeploy Your Frontend

After adding the environment variable, you need to redeploy for it to take effect:

#### Option A: Trigger Automatic Redeploy (Recommended)
```bash
# Make any small change and push to trigger deployment
git commit --allow-empty -m "chore: trigger redeploy with new VITE_API_URL"
git push
```

#### Option B: Manual Redeploy from Dashboard
1. Go to your project's **Deployments** tab
2. Find the latest deployment
3. Click the three dots menu (•••)
4. Select **Redeploy**
5. Confirm the redeployment

---

## ✅ Verification

After redeployment, verify the environment variable is working:

### 1. Check Browser Console
1. Open your deployed site
2. Press `F12` to open Developer Tools
3. Go to **Console** tab
4. Type: `import.meta.env.VITE_API_URL`
5. Should show your backend URL

### 2. Test API Connection
1. Try logging in or making an API request
2. Check the Network tab (F12 → Network)
3. Verify requests are going to your backend URL

### 3. Health Check
Visit your backend health endpoint:
```
https://your-backend-url/api/health
```
Should return a success response.

---

## 🔍 Troubleshooting

### Problem: Environment variable not showing in frontend

**Solution:**
- Ensure you clicked **Save** after adding the variable
- Redeploy the application
- Clear browser cache and hard refresh (`Ctrl+Shift+R` or `Cmd+Shift+R`)

### Problem: API requests still going to wrong URL

**Solution:**
- Check that the variable name is exactly `VITE_API_URL` (case-sensitive)
- Verify no typos in the backend URL
- Make sure you selected all three environments (Production, Preview, Development)
- Redeploy after making changes

### Problem: Getting CORS errors

**Solution:**
- Ensure backend URL doesn't have trailing slash
- Verify backend is configured to accept requests from your frontend domain
- Check backend CORS configuration

---

## 🎯 Current Configuration

### Root vercel.json (Simplified but Complete)

The root `vercel.json` has been simplified while maintaining essential configuration:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/**/*.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "50mb",
        "runtime": "python3.12"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1",
      "headers": {
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/",
      "headers": {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block"
      }
    }
  ]
}
```

**What this does:**
- ✅ `builds`: Treats every `.py` file in `/api` as a Serverless Function
- ✅ `config`: Maintains 50MB memory limit and Python 3.12 runtime
- ✅ `routes`: Automatically forwards `/api/auth/me` → `api/auth/me.py`
- ✅ `headers`: Includes essential CORS and security headers
- ✅ No `functions` key = No conflicts with Vercel configuration

**Security Notes:**
- ⚠️ The `Access-Control-Allow-Origin: *` allows all origins. For production, consider restricting to your frontend domain in Vercel dashboard settings
- ℹ️ Cron jobs (like health checks) should be configured separately in Vercel dashboard under Settings → Cron Jobs if needed

---

## 📚 Related Documentation

- [AUTO_DEPLOY_SETUP.md](./AUTO_DEPLOY_SETUP.md) - Complete auto-deploy guide
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - General deployment instructions
- [frontend/.env.example](./frontend/.env.example) - Frontend environment variables reference

---

## 🚀 Quick Reference

### Environment Variable Format
```
VITE_API_URL=https://your-backend.vercel.app
```

### Vercel CLI Alternative
You can also set environment variables using Vercel CLI:

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Add environment variable
vercel env add VITE_API_URL production
# When prompted, enter your backend URL

# For preview and development
vercel env add VITE_API_URL preview
vercel env add VITE_API_URL development
```

---

## ✨ Success Checklist

- [ ] Logged into Vercel dashboard
- [ ] Found Environment Variables in Settings
- [ ] Added `VITE_API_URL` with backend URL
- [ ] Selected all three environments (Production, Preview, Development)
- [ ] Saved the environment variable
- [ ] Redeployed the frontend
- [ ] Verified API requests go to correct backend
- [ ] Tested login/API functionality

---

**Last Updated:** December 2, 2025  
**Status:** ✅ Simplified Configuration Active

# API URL Configuration Fix Summary

## Problem Statement

The codebase had issues with fetch/axios calls not properly using environment variables for API URLs, leading to potential bugs with undefined, empty string, or malformed URLs.

## Solution

Added proper API URL configuration patterns and temporary debug logging to identify configuration issues.

---

## ✅ Correct Pattern (Vite/React Apps)

```javascript
// ✅ CORRECT: Use environment variable with fallback
const API = import.meta.env.VITE_API_URL || window.location.origin;

fetch(`${API}/api/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(data),
});
```

## ✅ Correct Pattern (Next.js Apps)

```javascript
// ✅ CORRECT: Use NEXT_PUBLIC_ prefix for client-side access
const API = process.env.NEXT_PUBLIC_API_URL;

fetch(`${API}/api/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(data),
});
```

---

## 🔍 TEMP DEBUG (Added to Code)

```javascript
console.log("API URL:", import.meta.env.VITE_API_URL);
```

### Expected Debug Output:

| Output | Meaning | Action |
|--------|---------|--------|
| `undefined` | ✅ Using same-origin (Vercel serverless) | No action needed - this is correct! |
| `https://backend.com` | ✅ Using explicit backend URL | Verify URL is correct |
| `empty string` | ❌ Configuration error | Check .env file |
| `malformed URL` | ❌ Invalid URL format | Fix VITE_API_URL value |

---

## Files Updated

### 1. **frontend/src/services/api.ts** ⭐ MAIN API FILE
**Change:** Added debug logging
```javascript
// 🔍 TEMP DEBUG: Check if API URL is properly configured
console.log("API URL:", import.meta.env.VITE_API_URL);
```
**Status:** Already using correct pattern with fallback

### 2. **admin-panel/src/lib/api.ts**
**Change:** Added debug logging
```javascript
// 🔍 TEMP DEBUG: Check if API URL is properly configured
console.log("API URL:", import.meta.env.VITE_API_URL);
```
**Status:** Already using correct pattern with fallback

### 3. **frontend/src/contexts/AIMonitoringContext.tsx**
**Change:** Added debug logging (dev mode only)
```javascript
// 🔍 TEMP DEBUG: Check if API URL is properly configured
if (import.meta.env.DEV) {
  console.log("API URL:", import.meta.env.VITE_API_URL);
}
```
**Status:** Already using correct pattern

### 4. **frontend/src/services/api_ai_enhanced.ts**
**Change:** Added debug logging
```javascript
// 🔍 TEMP DEBUG: Check if API URL is properly configured
console.log("API URL:", import.meta.env.VITE_API_URL);
```
**Status:** Already using correct pattern

### 5. **frontend/src/components/SocialFeed.tsx** ⭐ CRITICAL FIX
**Before (INCORRECT):**
```javascript
const socialAPI = {
  baseURL: '/api',  // ❌ Hardcoded path
  // ...
};
```

**After (CORRECT):**
```javascript
// 🔍 TEMP DEBUG: Check if API URL is properly configured
console.log("API URL:", import.meta.env.VITE_API_URL);

// ✅ Correct API URL pattern: Use environment variable or same-origin
const API = import.meta.env.VITE_API_URL || (typeof window !== 'undefined' ? window.location.origin : '');

const socialAPI = {
  baseURL: API,
  // ...
};
```

---

## Environment Configuration

### For Local Development (.env)
```bash
# Vite/React apps
VITE_API_URL=http://localhost:8000

# Next.js apps
NEXT_PUBLIC_API_URL=http://localhost:3001
```

### For Vercel Serverless (Recommended)
```bash
# Don't set VITE_API_URL - uses same-origin automatically
# This means frontend and backend are on the same domain
```

### For Railway/Render Backend
```bash
# Vite/React apps
VITE_API_URL=https://your-app.up.railway.app

# Next.js apps
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app
```

---

## Testing the Fix

### 1. Check Browser Console
Open your app and check the browser console. You should see:
```
API URL: undefined
```
or
```
API URL: https://your-backend.com
```

### 2. Verify API Calls
Watch the Network tab in DevTools. API calls should go to:
- Same origin (e.g., `https://yoursite.vercel.app/api/login`) - if VITE_API_URL is undefined
- Your backend URL (e.g., `https://backend.railway.app/api/login`) - if VITE_API_URL is set

### 3. Test Different Scenarios

| Scenario | VITE_API_URL Value | Expected Behavior |
|----------|-------------------|-------------------|
| Vercel Serverless | `undefined` | Uses `window.location.origin` ✅ |
| Railway Backend | `https://app.railway.app` | Uses Railway URL ✅ |
| Local Dev | `http://localhost:8000` | Uses localhost ✅ |
| Empty String | `""` | Falls back to `window.location.origin` ✅ |
| Malformed | `not-a-url` | May cause errors ❌ |

---

## Common Issues & Solutions

### Issue 1: "API URL: undefined"
**Is this bad?** NO! This is correct for Vercel serverless deployments.
**What happens?** App uses `window.location.origin` as the base URL.

### Issue 2: API calls fail with 404
**Cause:** Backend not deployed or URL mismatch
**Solution:** 
1. Check if backend is running
2. Verify VITE_API_URL points to correct backend
3. Check if backend has `/api` prefix in routes

### Issue 3: CORS errors
**Cause:** Backend doesn't allow requests from your frontend domain
**Solution:** Configure CORS in backend to allow your frontend origin

### Issue 4: Different behavior in dev vs production
**Cause:** Different environment variables
**Solution:** 
1. Check `.env` for local dev
2. Check Vercel dashboard → Environment Variables for production
3. Ensure consistency or proper fallback logic

---

## Deployment Checklist

### Vercel Frontend + Vercel Serverless Backend
- [ ] Do NOT set VITE_API_URL (uses same-origin)
- [ ] Backend code in `/api` directory
- [ ] Frontend uses relative paths (`/api/...`)

### Vercel Frontend + Railway/Render Backend
- [ ] Set VITE_API_URL in Vercel dashboard
- [ ] Point to full backend URL (e.g., `https://app.railway.app`)
- [ ] Configure CORS on backend

### Local Development
- [ ] Create `.env` file with `VITE_API_URL=http://localhost:8000`
- [ ] Start backend on port 8000
- [ ] Start frontend on port 3000/5173

---

## Removing Debug Logs (After Testing)

Once you've verified the configuration works, remove the debug logs:

```bash
# Find all debug logs
grep -r "TEMP DEBUG" frontend/ admin-panel/

# Remove the lines manually or use sed
sed -i '/TEMP DEBUG/d' frontend/src/services/api.ts
```

Or keep them in development mode only:
```javascript
if (import.meta.env.DEV) {
  console.log("API URL:", import.meta.env.VITE_API_URL);
}
```

---

## Best Practices

1. ✅ **Always use environment variables** for API URLs
2. ✅ **Provide fallback** to same-origin for serverless deployments
3. ✅ **Never hardcode** localhost or production URLs in code
4. ✅ **Use correct prefix**: `VITE_` for Vite, `NEXT_PUBLIC_` for Next.js
5. ✅ **Document** environment variables in `.env.example`
6. ✅ **Test** in all environments (local, staging, production)

---

## Additional Resources

- **Test Page:** `/test_api_url_config.html` - Visual test page
- **Environment Example:** `/frontend/.env.example` - All available env vars
- **Documentation:** `/README.md` - Full deployment guide

---

## Summary

✅ Added temporary debug logging to identify API URL configuration issues
✅ Fixed SocialFeed.tsx hardcoded baseURL issue
✅ Verified all fetch/axios calls use proper environment variable patterns
✅ Provided comprehensive testing and troubleshooting guide

**Result:** All API calls now properly use environment variables with appropriate fallbacks, making the application deployment-agnostic and easier to debug.

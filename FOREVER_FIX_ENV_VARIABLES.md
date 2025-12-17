# 🔒 FOREVER FIX: Environment Variable Law (LOCKED)

**Status**: ✅ PERMANENT FIX - DO NOT MODIFY  
**Last Updated**: December 17, 2024  
**Priority**: 🔴 CRITICAL

---

## 📋 The Law

### For Vite Frontend (Main App in `/frontend`)

```bash
# ✅ CORRECT - Vercel WILL expose these
VITE_API_URL=https://your-backend.onrender.com
VITE_SOCKET_URL=https://your-backend.onrender.com
VITE_CLOUDINARY_CLOUD_NAME=your_cloud_name
VITE_SENDBIRD_APP_ID=your_app_id
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_APPLE_CLIENT_ID=your_apple_client_id

# ❌ NEVER USE THESE - Vercel will NOT expose them
API_URL=...                    # ❌ Missing VITE_ prefix
DATABASE_URL=...               # ❌ Backend only, not for frontend!
BACKEND_URL=...                # ❌ Missing VITE_ prefix
NEXT_PUBLIC_API_URL=...        # ❌ Wrong framework (Next.js only)
```

### For Next.js Frontend (in `/next-app`)

```bash
# ✅ CORRECT - Vercel WILL expose these
NEXT_PUBLIC_API_URL=https://your-backend.com
NEXT_PUBLIC_ANALYTICS_ID=your_analytics_id

# ❌ NEVER USE THESE - Vercel will NOT expose them
API_URL=...                    # ❌ Missing NEXT_PUBLIC_ prefix
DATABASE_URL=...               # ❌ Backend only, not for frontend!
VITE_API_URL=...               # ❌ Wrong framework (Vite only)
```

---

## 🚨 Why This Matters

### The Problem

When you deploy to Vercel:
1. **Without proper prefix**: Variable is NOT available to client-side JavaScript
2. **Wrong prefix**: Variable is invisible (VITE_ in Next.js or NEXT_PUBLIC_ in Vite)
3. **No prefix**: Variable is server-side only (not accessible in browser)

### The Consequences

❌ **Wrong Configuration:**
```env
# In Vercel Environment Variables
API_URL=https://backend.com
```

**Result**: Your frontend gets `undefined` when trying to access `import.meta.env.VITE_API_URL`

✅ **Correct Configuration:**
```env
# In Vercel Environment Variables
VITE_API_URL=https://backend.com
```

**Result**: Your frontend successfully accesses `import.meta.env.VITE_API_URL`

---

## 📊 Quick Reference Table

| Framework | Prefix Required | Example | Access Method |
|-----------|----------------|---------|---------------|
| **Vite** | `VITE_` | `VITE_API_URL` | `import.meta.env.VITE_API_URL` |
| **Next.js** | `NEXT_PUBLIC_` | `NEXT_PUBLIC_API_URL` | `process.env.NEXT_PUBLIC_API_URL` |
| **Backend** | No prefix needed | `DATABASE_URL` | `process.env.DATABASE_URL` |

---

## 🔍 How to Verify

### Step 1: Check Vercel Dashboard

1. Go to: https://vercel.com/dashboard
2. Select your project
3. Navigate to: **Settings** → **Environment Variables**
4. Verify all frontend variables have correct prefix:
   - Vite app: All start with `VITE_`
   - Next.js app: All start with `NEXT_PUBLIC_`

### Step 2: Check Browser Console

After deployment, open your app and check console:

```javascript
// For Vite app
console.log('API URL:', import.meta.env.VITE_API_URL);
// Should print: "API URL: https://your-backend.com"
// NOT: "API URL: undefined"

// For Next.js app
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);
// Should print: "API URL: https://your-backend.com"
```

### Step 3: Test API Connection

```bash
# Test that your frontend can reach the backend
curl -I https://your-frontend.vercel.app
# Check Network tab in browser DevTools
# Verify API calls go to correct backend URL
```

---

## 🛡️ Common Mistakes & Fixes

### Mistake #1: No Prefix
```bash
# ❌ WRONG
API_URL=https://backend.com

# ✅ CORRECT (Vite)
VITE_API_URL=https://backend.com

# ✅ CORRECT (Next.js)
NEXT_PUBLIC_API_URL=https://backend.com
```

### Mistake #2: Wrong Framework Prefix
```bash
# ❌ WRONG (Using Next.js prefix in Vite project)
NEXT_PUBLIC_API_URL=https://backend.com

# ✅ CORRECT (Vite project needs VITE_ prefix)
VITE_API_URL=https://backend.com
```

### Mistake #3: Exposing Sensitive Variables
```bash
# ❌ DANGEROUS (Never expose these to frontend!)
VITE_DATABASE_URL=postgresql://...      # ❌ Security risk!
VITE_JWT_SECRET=your-secret             # ❌ Security risk!
NEXT_PUBLIC_DATABASE_URL=postgresql://  # ❌ Security risk!

# ✅ CORRECT (Keep these backend-only, no prefix)
DATABASE_URL=postgresql://...           # ✅ Backend only
JWT_SECRET=your-secret                  # ✅ Backend only
```

### Mistake #4: Forgot to Redeploy
After adding/changing environment variables:
1. ✅ Go to Deployments tab
2. ✅ Click "..." on latest deployment
3. ✅ Click "Redeploy"
4. ✅ Wait for deployment to complete

---

## 📚 Repository Structure

```
HireMeBahamas/
├── frontend/              # Vite/React app - uses VITE_ prefix
│   ├── .env.example      # Template with VITE_ variables
│   └── src/config/env.ts # Reads import.meta.env.VITE_*
│
├── next-app/             # Next.js app - uses NEXT_PUBLIC_ prefix
│   ├── .env.example      # Template with NEXT_PUBLIC_ variables
│   └── app/              # Uses process.env.NEXT_PUBLIC_*
│
├── api/                  # Backend - no prefix needed
│   └── ...               # Uses process.env.DATABASE_URL
│
└── vercel.json           # Currently deploys /frontend (Vite)
```

---

## 🔧 Where to Configure

### For Vite Frontend (Current Default)

**Vercel Dashboard Configuration:**
```
Project: [your-project]
Settings → Environment Variables

Add these:
✅ VITE_API_URL = https://your-backend.onrender.com
✅ VITE_SOCKET_URL = https://your-backend.onrender.com (optional)
✅ VITE_CLOUDINARY_CLOUD_NAME = your_cloud_name (optional)
```

### For Next.js Frontend (If Switching)

**Vercel Dashboard Configuration:**
```
Project: [your-project]
Settings → Environment Variables

Add these:
✅ NEXT_PUBLIC_API_URL = https://your-backend.com
✅ NEXT_PUBLIC_ANALYTICS_ID = your_analytics_id (optional)
```

---

## 🎯 Deployment Checklist

- [ ] Environment variables in Vercel have correct prefix
  - [ ] Vite: All start with `VITE_`
  - [ ] Next.js: All start with `NEXT_PUBLIC_`
- [ ] No sensitive data (DATABASE_URL, JWT_SECRET) has public prefix
- [ ] After adding variables, redeployed the application
- [ ] Tested in browser console that variables are accessible
- [ ] Verified API calls reach correct backend URL
- [ ] Checked browser Network tab for API requests

---

## 🆘 Troubleshooting

### Problem: "API URL is undefined"

**Diagnosis:**
```javascript
console.log(import.meta.env.VITE_API_URL); // undefined
```

**Solutions:**
1. Check Vercel Dashboard → Environment Variables
2. Ensure variable name is exactly `VITE_API_URL` (case-sensitive)
3. Verify you redeployed after adding the variable
4. Clear browser cache (Ctrl+Shift+R)

### Problem: "CORS error when calling API"

**Diagnosis:**
Browser console shows: `Access-Control-Allow-Origin` error

**Solutions:**
1. Verify `VITE_API_URL` points to correct backend
2. Check backend CORS settings allow your Vercel domain
3. Ensure backend URL uses HTTPS (not HTTP)

### Problem: "Variables work locally but not on Vercel"

**Diagnosis:**
Works with `.env.local` but fails on Vercel deployment

**Solutions:**
1. Local `.env.local` != Vercel Environment Variables
2. Must add variables to Vercel Dashboard manually
3. Must redeploy after adding variables
4. Check exact variable names match (including prefix)

---

## 📖 Related Documentation

- [frontend/.env.example](./frontend/.env.example) - Vite environment template
- [next-app/.env.example](./next-app/.env.example) - Next.js environment template
- [VERCEL_FRONTEND_ENV_VARS.md](./VERCEL_FRONTEND_ENV_VARS.md) - Detailed guide
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [DIRECT_LINKS_WHERE_TO_CONFIGURE.md](./DIRECT_LINKS_WHERE_TO_CONFIGURE.md) - Configuration links

---

## 🔐 Security Notes

### ✅ Safe to Expose (Frontend)
- API URLs (`VITE_API_URL`, `NEXT_PUBLIC_API_URL`)
- Public API keys (Cloudinary cloud name, Google Client ID)
- Feature flags
- Public configuration

### ❌ NEVER Expose (Backend Only)
- Database connection strings (`DATABASE_URL`)
- JWT secrets (`JWT_SECRET`)
- Private API keys
- Encryption keys
- Admin credentials

**Rule of Thumb:**
- If it's in the browser DevTools → must be public-safe
- If it grants access or contains secrets → backend only (no prefix)

---

**🔒 This is a FOREVER FIX. Do not modify the prefix requirements.**

**Last Updated**: December 17, 2024  
**Maintained By**: HireMeBahamas Development Team

# CORS Fix Deployment Guide - Vercel Preview Support

## 🎯 Objective
Permanently eliminate white screen on Vercel preview deployments by fixing CORS to allow all preview URLs while maintaining production security.

## ✅ What Was Fixed

### Problem
Vercel creates unique preview URLs for each deployment (e.g., `https://frontend-abc123-cliffs-projects-a84c76c9.vercel.app`), but the backend CORS configuration only allowed specific production domains, causing preview deployments to fail with CORS errors and white screens.

### Solution
Implemented enterprise-grade CORS configuration that:
1. ✅ Allows explicit production domains (hiremebahamas.com, www.hiremebahamas.com)
2. ✅ Allows ALL Vercel preview deployments via regex pattern
3. ✅ Maintains security by NOT using wildcards
4. ✅ Supports credentials for authentication

## 📋 Files Changed

### 1. New File: `api/backend_app/cors.py`
Centralized CORS configuration module with:
- `get_allowed_origins()` - Reads production domains from environment
- `apply_cors()` - Applies CORS middleware with Vercel preview support
- `VERCEL_PREVIEW_REGEX` - Pattern matching all preview deployments

### 2. Updated: `api/backend_app/main.py`
Replaced old CORS configuration with new `apply_cors()` function.

### 3. Updated: `api/main.py` (Render Handler)
Added Vercel preview regex to fallback CORS configuration.

### 4. Updated: `api/index.py` (Vercel Serverless Handler)
Added Vercel preview regex to CORS configuration.

## 🚀 Deployment Steps

### Step 1: Set Environment Variable on Render

1. Go to Render Dashboard
2. Select your backend service: `hiremebahamas-backend`
3. Navigate to **Environment** tab
4. Add or update the environment variable:
   ```
   Key: ALLOWED_ORIGINS
   Value: https://hiremebahamas.com,https://www.hiremebahamas.com
   ```
5. Click **Save Changes**

**Note:** The backend will automatically restart when environment variables are updated.

### Step 2: Verify Deployment

The code changes are already merged. Render will automatically deploy when:
- You push to the main branch, OR
- The environment variable is saved (triggers restart)

Monitor the deployment:
1. Go to **Logs** tab in Render dashboard
2. Wait for "Deploy succeeded" message
3. Check for CORS-related log messages

### Step 3: Test from Vercel Preview

Once deployed, test from any Vercel preview deployment:

#### Test 1: Basic Health Check
Open DevTools Console on your Vercel preview deployment and run:
```javascript
fetch("https://hiremebahamas-backend.onrender.com/health")
  .then(r => r.json())
  .then(console.log)
```

**Expected Result:** `{ "status": "ok" }`

#### Test 2: Check CORS Headers
1. Open DevTools → Network tab
2. Make any API call to the backend
3. Click on the request
4. Look for **Response Headers**
5. Verify:
   ```
   access-control-allow-origin: https://frontend-xxxx-cliffs-projects-a84c76c9.vercel.app
   ```

**Expected:** The `access-control-allow-origin` header should contain YOUR preview URL.

#### Test 3: Mobile Safari (If Applicable)
1. Open preview URL on iPhone/iPad Safari
2. Verify page loads without white screen
3. Check that API calls work

## 🔍 Verification Checklist

- [ ] Environment variable `ALLOWED_ORIGINS` set on Render
- [ ] Backend deployed successfully
- [ ] Health check works from preview deployment
- [ ] CORS header contains preview URL
- [ ] No CORS errors in browser console
- [ ] White screen eliminated on all previews
- [ ] Production site still works (hiremebahamas.com)
- [ ] Mobile Safari loads correctly

## 🧪 Testing Different Scenarios

### Scenario 1: New Vercel Preview Deployment
1. Create a new PR or push to existing PR
2. Vercel creates new preview URL
3. Open preview URL
4. Verify: No white screen, API calls work

### Scenario 2: Production Deployment
1. Open https://hiremebahamas.com
2. Verify: Site loads normally
3. Check: All features work as expected

### Scenario 3: Mobile Testing
1. Open preview URL on mobile device
2. Verify: No white screen
3. Check: API calls complete successfully

## 🛡️ Security Status

| Aspect | Status | Details |
|--------|--------|---------|
| Wildcards | ❌ Not Used | No `*` patterns - maintains security |
| Other Projects | ❌ Blocked | Regex specific to `cliffs-projects-a84c76c9` |
| Your Previews | ✅ Allowed | All preview URLs under your project |
| Production | ✅ Locked | Explicit domains only |
| Credentials | ✅ Enabled | Authentication works across all origins |

## 🐛 Troubleshooting

### Issue: Still seeing CORS errors

**Solution:**
1. Check Render logs for CORS-related messages
2. Verify environment variable is set correctly
3. Ensure backend restarted after environment variable change
4. Clear browser cache and hard refresh (Cmd+Shift+R / Ctrl+Shift+R)

### Issue: Preview URL doesn't match regex

**Check:**
1. Your Vercel preview URL format
2. If format is different, update `VERCEL_PREVIEW_REGEX` in `api/backend_app/cors.py`
3. Example: If your URLs look like `https://frontend-git-branch-username.vercel.app`, you'll need a different regex

**How to find your preview URL pattern:**
1. Go to Vercel dashboard
2. Open a preview deployment
3. Copy the full URL
4. Update regex to match your pattern

### Issue: Production site not working

**Check:**
1. Ensure production domains are in `ALLOWED_ORIGINS`
2. Verify domains are comma-separated
3. Check no extra spaces in environment variable

## 📊 Expected Outcomes

### Before Fix
- 🔴 White screen on preview deployments
- 🔴 CORS errors in console
- 🔴 Mobile Safari fails to load
- 🔴 Silent fetch failures
- 🔴 No backend logs for failed requests

### After Fix
- 🟢 Preview deployments render correctly
- 🟢 No CORS errors
- 🟢 Mobile Safari loads properly
- 🟢 All API calls succeed
- 🟢 Backend logs show successful requests
- 🟢 White screen impossible

## 🏁 Final State

Once deployed, your application will:
1. ✅ Work on production domain
2. ✅ Work on ALL Vercel preview deployments
3. ✅ Work on mobile devices
4. ✅ Maintain enterprise-grade security
5. ✅ Support authentication across all origins

## 📞 Support

If you encounter issues:
1. Check Render logs for errors
2. Verify environment variables are set
3. Test with curl or Postman to isolate CORS issues
4. Review browser console for specific error messages

## 🎉 Success Criteria

You've successfully deployed when:
- ✅ Preview deployments load without white screen
- ✅ API calls work from preview URLs
- ✅ CORS headers show correct origin
- ✅ Mobile devices work correctly
- ✅ Production site remains functional

---

**Last Updated:** December 23, 2025  
**PR:** copilot/fix-cors-for-vercel-previews

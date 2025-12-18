# Deployment Verification Checklist

Use this checklist after deploying to verify the Vercel → Backend connection fix is working correctly.

## ✅ Pre-Deployment Setup

### Option A: Vercel Serverless Backend (Recommended)

- [ ] Verify `api/index.py` exists and is configured in `vercel.json`
- [ ] **DO NOT** set `VITE_API_URL` in Vercel Environment Variables
- [ ] Deploy to Vercel

### Option B: Separate Backend (Render/Render)

- [ ] Deploy backend to Render/Render
- [ ] Get backend URL (e.g., `https://your-app.up.render.app`)
- [ ] Set `VITE_API_URL` in Vercel Dashboard → Settings → Environment Variables
- [ ] Ensure backend CORS allows your Vercel domain
- [ ] Deploy to Vercel

## ✅ Post-Deployment Verification

### 1. Health Check
```bash
# Replace with your Vercel URL
curl https://your-project.vercel.app/api/health

# Expected response:
# {"status":"healthy","platform":"vercel-serverless"}
# OR
# {"status":"healthy"} (for separate backend)
```

- [ ] Health endpoint returns 200 OK
- [ ] Response contains valid JSON

### 2. Browser Console Check

Open your deployed app in a browser and check the console:

- [ ] Look for: `🌐 Using same-origin API (Vercel serverless): https://your-project.vercel.app`
- [ ] OR: API configuration showing correct backend URL
- [ ] NO errors about "localhost" or "127.0.0.1"
- [ ] NO CORS errors

### 3. Network Tab Verification

Open Chrome DevTools → Network tab:

- [ ] API requests go to correct domain (same as frontend OR your backend URL)
- [ ] NO requests to localhost or 127.0.0.1
- [ ] NO 404 errors on /api/* endpoints
- [ ] NO CORS preflight failures

### 4. Functional Testing

Test the following features:

#### User Registration
- [ ] Navigate to `/register`
- [ ] Fill in registration form
- [ ] Submit form
- [ ] Check that POST request goes to correct URL
- [ ] Verify successful registration or appropriate error

#### User Login
- [ ] Navigate to `/login`
- [ ] Enter credentials
- [ ] Submit form
- [ ] Check that POST request goes to `/api/auth/login`
- [ ] Verify successful login (redirect to dashboard)

#### Stories (if feature exists)
- [ ] Navigate to stories section
- [ ] Verify stories load from correct API
- [ ] Try creating a story
- [ ] Check that upload goes to correct URL

#### Real-time Features
- [ ] Check WebSocket connection in Network tab
- [ ] Verify WebSocket connects to correct URL (not localhost)
- [ ] Test notifications/messages if applicable

### 5. Environment Verification

Check that environment is properly configured:

```javascript
// Open browser console and run:
console.log('Origin:', window.location.origin);
console.log('VITE_API_URL:', import.meta.env.VITE_API_URL || 'not set (using same-origin)');
```

- [ ] Origin matches your Vercel deployment URL
- [ ] VITE_API_URL is either not set (Option A) or matches backend (Option B)

## 🐛 Troubleshooting

### Issue: 404 on /api/* endpoints

**For Vercel Serverless:**
- Check that `api/index.py` exists
- Verify `vercel.json` has correct rewrites configuration
- Check Vercel deployment logs for Python errors

**For Separate Backend:**
- Verify `VITE_API_URL` is set correctly in Vercel
- Test backend URL directly in browser
- Check backend is running and accessible

### Issue: CORS Errors

**For Vercel Serverless:**
- Should NOT happen (same-origin)
- If it does, check that rewrites in `vercel.json` are correct

**For Separate Backend:**
- Backend CORS must allow your Vercel domain
- Check backend CORS configuration
- Verify `Access-Control-Allow-Origin` header in response

### Issue: Requests Going to Localhost

**This should NOT happen after the fix.**

If you see localhost in network requests:
- Clear browser cache and hard refresh (Ctrl+Shift+R)
- Check that you deployed the latest code
- Verify no browser extensions are intercepting requests
- Check that old service workers are not cached

### Issue: Cold Start Delays (Render/Render)

If using Render free tier or Render:
- First request may take 30-60 seconds (cold start)
- This is normal for free tier services
- Consider upgrading to paid tier for instant responses
- Or use Vercel serverless (Option A) which has faster cold starts

## 📊 Success Criteria

All of the following should be true:

✅ Health endpoint responds with 200 OK
✅ No localhost URLs appear in Network tab
✅ No CORS errors in console
✅ User registration works
✅ User login works
✅ API requests go to correct domain
✅ Browser console shows correct API configuration
✅ All functional tests pass

## 📝 Post-Verification

Once all checks pass:
- [ ] Document the configuration used (Option A or B)
- [ ] Save backend URL if using Option B
- [ ] Note any issues encountered and solutions
- [ ] Update team documentation if needed

## 🎉 Deployment Complete!

If all checks pass, your Vercel → Backend connection is working correctly!

---

**Need Help?**
- Review: `VERCEL_BACKEND_CONNECTION_GUIDE.md`
- Check backend logs for errors
- Verify environment variables in Vercel Dashboard
- Test backend URL directly in browser

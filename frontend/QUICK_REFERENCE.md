# Frontend Hardening - Quick Reference Card

## 🚨 Quick Troubleshooting

### Blank White Screen?
**This should NEVER happen.** If you see a blank screen:

1. Open browser console (F12)
2. Look for red error messages
3. Most likely: Configuration error
4. Fix: Set `VITE_API_BASE_URL` in Vercel dashboard

**What you SHOULD see instead**:
- Configuration error screen with reload button
- OR health banner saying "Server is starting up"
- OR working app (even if API is down)

---

## ⚙️ Environment Variables

### Required in Production
```bash
VITE_API_BASE_URL=https://api.hiremebahamas.com
# OR
VITE_API_BASE_URL=https://hiremebahamas-backend.onrender.com
```

**Where to set**:
- Vercel: Dashboard → Settings → Environment Variables → Production
- Local: Create `frontend/.env.local` (optional, proxy works without it)

**Validation**:
- Build will FAIL if missing
- Build will FAIL if HTTP instead of HTTPS
- Runtime will show error screen if invalid

---

## 🏗️ Building

### Production Build
```bash
cd frontend
VITE_API_BASE_URL=https://api.hiremebahamas.com npm run build
```

**Expected**: Build succeeds, outputs to `dist/`

### Build Errors
```
❌ VITE_API_BASE_URL is not set
```
**Fix**: Set the environment variable

```
❌ must use HTTPS in production
```
**Fix**: Change `http://` to `https://`

---

## 💻 Local Development

### Start Dev Server
```bash
cd frontend
npm install
npm run dev
```

**No environment variables needed** - the dev proxy handles API routing automatically!

**Access**: http://localhost:3000

**Dev Proxy**: Automatically proxies `/api/*` to backend to avoid CORS

---

## 🔍 Verifying Health

### Check Connection
1. Open app in browser
2. Open console (F12)
3. Look for:
   ```
   ✅ Connected to backend
   ```

### If Backend is Slow
You'll see a banner:
```
🌐 Server is brewing... almost ready!
☕ Waking up from sleep mode...
```

**This is normal** for services like Render free tier.

### If Backend is Down
- Health banner appears with "Connection issue"
- App still renders with appropriate messages
- NOT a blank screen

---

## 🛠️ New API Client

### Usage Example
```typescript
import { api, ApiError } from '@/lib/apiClient';

// GET request with automatic retry
try {
  const users = await api.get('/api/users');
  console.log(users);
} catch (error) {
  if (error instanceof ApiError) {
    // User-friendly message
    toast.error(error.getUserMessage());
    
    // Developer details
    console.error('Status:', error.status);
    console.error('Type:', error.type);
  }
}

// POST request (no retry for mutations)
await api.post('/api/posts', { content: 'Hello!' });
```

### Features
- ✅ Automatic retry for GET/HEAD/OPTIONS (3 attempts)
- ✅ Exponential backoff with jitter
- ✅ 30-second timeout (configurable)
- ✅ User-friendly error messages
- ❌ No retry for POST/PUT/DELETE/PATCH (safe)

---

## 📊 Error Types

### ApiError Types
```typescript
ApiErrorType.NETWORK    // Connection failed
ApiErrorType.TIMEOUT    // Request too slow
ApiErrorType.SERVER     // 5xx error
ApiErrorType.CLIENT     // 4xx error
ApiErrorType.UNKNOWN    // Other errors
```

### User Messages
- Network: "Unable to connect to server"
- Timeout: "Request timed out"
- Server: "Server error. Try again later"
- 401: "Session expired. Log in again"
- 403: "No permission"
- 404: "Not found"

---

## 🚀 Deployment Checklist

### Pre-Deploy
- [ ] Set `VITE_API_BASE_URL` in Vercel
- [ ] Verify it uses HTTPS
- [ ] Test build locally
- [ ] Review security scan (CodeQL passed)

### Deploy
```bash
git push origin main
```

### Post-Deploy
- [ ] Visit production URL
- [ ] Verify no blank screen
- [ ] Check console for errors
- [ ] Test www redirect
- [ ] Verify health banner works

---

## 🔒 Security Notes

### Safe to Expose (VITE_ prefix)
- ✅ `VITE_API_BASE_URL`
- ✅ `VITE_GOOGLE_CLIENT_ID`
- ✅ `VITE_SENTRY_DSN`

### NEVER Expose
- ❌ `DATABASE_URL`
- ❌ `JWT_SECRET`
- ❌ `CRON_SECRET`
- ❌ Any backend secrets

**Protection**: Build will fail if you accidentally add `VITE_DATABASE_URL`

---

## 🆘 Emergency Contacts

### Build Breaking?
1. Check environment variables in Vercel
2. Verify `VITE_API_BASE_URL` is set
3. Ensure it uses HTTPS
4. See `DEPLOYMENT_HARDENING.md` for details

### Users Seeing Errors?
1. Check if backend is down (Render dashboard)
2. Verify API URL is correct
3. Check browser console for details
4. See `README.md` troubleshooting section

### Security Concerns?
1. Review `SECURITY_SUMMARY_FRONTEND_HARDENING.md`
2. CodeQL scan passed (0 vulnerabilities)
3. All retry logic is safe (GET only)
4. HTTPS enforced everywhere

---

## 📚 Documentation

- **README.md** - Comprehensive setup guide
- **DEPLOYMENT_HARDENING.md** - Deployment & testing guide
- **SECURITY_SUMMARY_FRONTEND_HARDENING.md** - Security analysis
- **.env.example** - Environment variable documentation

---

## 💡 Key Takeaways

1. **Never blank screen** - Multiple safeguards in place
2. **Build validation** - Fails fast on misconfiguration
3. **Runtime guards** - Clear error messages for users
4. **Safe retries** - Only GET/HEAD/OPTIONS, never mutations
5. **Health monitoring** - Always know backend status
6. **Dev friendly** - Proxy handles CORS, no env vars needed

---

## ✅ Success Indicators

**Healthy Deployment**:
- ✅ Build succeeds
- ✅ No blank screens
- ✅ Health banner shows when needed
- ✅ Error boundaries work
- ✅ www redirects correctly

**If Any Fail**: Check environment variables first!

---

**Last Updated**: December 2024
**Status**: Production Ready ✅
**Security Scan**: Passed ✅
**All Tests**: Passed ✅

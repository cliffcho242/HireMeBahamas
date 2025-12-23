# Frontend Deployment & Hardening Guide

This guide documents the comprehensive frontend hardening implemented to prevent blank screens and ensure robust API connectivity.

## 🛡️ Hardening Features

### 1. Build-Time Validation

**Location**: `frontend/vite.config.ts`

**What it does**:
- Validates `VITE_API_BASE_URL` is set during production builds
- Ensures the URL uses HTTPS (not HTTP)
- Warns about trailing slashes
- **Fails the build** with clear error message if misconfigured

**Benefits**:
- Prevents deployment with missing/invalid configuration
- Catches errors before they reach production
- Clear error messages guide developers to fix the issue

**Example Error**:
```
❌ CRITICAL BUILD ERROR: VITE_API_BASE_URL is not set

The application requires VITE_API_BASE_URL for production builds.
This prevents blank screens and silent failures.

To fix:
1. Set VITE_API_BASE_URL in your Vercel dashboard:
   Settings → Environment Variables → Production
2. Example value: https://api.hiremebahamas.com
```

### 2. Runtime Validation

**Location**: `frontend/src/lib/api.ts`, `frontend/src/main.tsx`

**What it does**:
- Validates API configuration when app loads
- Throws clear errors instead of returning empty strings
- Displays user-friendly error screen instead of blank page
- Shows configuration guidance for users and developers

**Benefits**:
- Prevents blank white screen on config errors
- Users see helpful message instead of broken page
- Developers get clear guidance to fix issues

**Example Error Screen**:
```
⚙️ Configuration Error

The application is not properly configured. 
Please contact the site administrator.

[Reload Page Button]

Error: API base URL is missing from environment configuration
```

### 3. Robust API Client

**Location**: `frontend/src/lib/apiClient.ts`

**Features**:
- ✅ Automatic base URL prefixing
- ✅ Configurable timeouts (30s default)
- ✅ Retry logic for idempotent GET requests
- ✅ Exponential backoff with jitter
- ✅ Typed error responses (`ApiError` class)
- ✅ User-friendly error messages
- ✅ Network error detection
- ✅ Timeout detection

**Usage Example**:
```typescript
import { api, ApiError } from '@/lib/apiClient';

try {
  const data = await api.get('/api/users/me');
  console.log('User data:', data);
} catch (error) {
  if (error instanceof ApiError) {
    // Show user-friendly message
    console.error(error.getUserMessage());
    // Or access specific error details
    console.log('Status:', error.status);
    console.log('Type:', error.type);
  }
}
```

**Error Types**:
- `NETWORK`: Connection failed
- `TIMEOUT`: Request took too long
- `SERVER`: 5xx server error
- `CLIENT`: 4xx client error (401, 403, 404, etc.)
- `UNKNOWN`: Unexpected error

### 4. Error Boundary

**Location**: `frontend/src/components/AIErrorBoundary.tsx`

**What it does**:
- Catches all React render errors
- Displays fallback UI instead of blank screen
- Attempts automatic recovery for common issues
- Provides reload button for users

**Benefits**:
- No more blank white screens on errors
- Graceful degradation
- User can recover without technical knowledge

### 5. Health Check System

**Location**: `frontend/src/hooks/useBackendHealth.ts`, `frontend/src/components/ConnectionStatus.tsx`

**What it does**:
- Monitors backend connectivity on app load
- Shows banner when backend is slow or unavailable
- Provides retry mechanism
- Displays progress during wake-up (for services like Render)

**Benefits**:
- Users know when backend is starting up
- App remains interactive during connection issues
- Clear feedback instead of silent failures

### 6. Dev Server Proxy

**Location**: `frontend/vite.config.ts`

**What it does**:
- Proxies `/api/*` requests to backend during development
- Prevents CORS issues in local dev
- Uses `VITE_API_BASE_URL` as proxy target

**Benefits**:
- Smooth local development experience
- No CORS configuration needed for dev
- Matches production behavior

**Configuration**:
```javascript
server: {
  proxy: {
    '/api': {
      target: env.VITE_API_BASE_URL || 'https://api.hiremebahamas.com',
      changeOrigin: true,
      secure: true,
    },
  },
}
```

### 7. Deployment Safeguards

**Location**: `vercel.json`

**What it does**:
- Redirects www → apex domain (308 permanent)
- Proxies `/api/*` to backend in production
- Applies proper caching headers for assets
- Security headers (HSTS, XSS protection, etc.)

**Benefits**:
- Consistent domain structure
- Proper asset caching
- Enhanced security posture

## 🚀 Deployment Checklist

### For Vercel Deployment

1. **Set Environment Variables** in Vercel Dashboard:
   ```
   VITE_API_BASE_URL=https://api.hiremebahamas.com
   ```

2. **Verify Build Settings**:
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/dist`
   - Install Command: `cd frontend && npm install`

3. **Deploy**:
   ```bash
   git push origin main
   ```
   
4. **Verify**:
   - Visit production URL
   - Check for blank screen (should NOT happen)
   - Check browser console for errors
   - Verify API calls work
   - Test www redirect

### For Local Development

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Set Environment** (optional):
   Create `.env.local`:
   ```bash
   # Optional - dev server proxy will handle routing
   # VITE_API_URL=http://localhost:8000
   ```

3. **Start Dev Server**:
   ```bash
   npm run dev
   ```

4. **Verify**:
   - Visit http://localhost:3000
   - Check console for connection logs
   - Verify health check banner (if backend is slow)
   - Test API calls through proxy

## 🧪 Testing

### Test Build-Time Validation

**Without VITE_API_BASE_URL (should fail)**:
```bash
cd frontend
npm run build
```
Expected: Build fails with clear error message

**With HTTP URL (should fail)**:
```bash
VITE_API_BASE_URL=http://api.example.com npm run build
```
Expected: Build fails, requires HTTPS

**With Valid URL (should succeed)**:
```bash
VITE_API_BASE_URL=https://api.hiremebahamas.com npm run build
```
Expected: Build succeeds

### Test Runtime Behavior

**Missing Config**:
1. Remove VITE_API_BASE_URL from environment
2. Start dev server
3. Visit app
4. Expected: Configuration error screen (NOT blank)

**API Down**:
1. Set invalid VITE_API_BASE_URL
2. Start app
3. Expected: Health check banner appears
4. Expected: App still renders (shows appropriate messages)

**Slow Backend**:
1. Deploy to staging with cold-start backend
2. Visit app
3. Expected: "Waking up" banner with progress
4. Expected: Automatic retry with backoff

## 🐛 Troubleshooting

### Blank White Screen

If you see a blank white screen, check:

1. **Browser Console**: Look for configuration errors
2. **Network Tab**: Check for failed requests
3. **Environment Variables**: Verify VITE_API_BASE_URL is set
4. **Build Logs**: Check if build succeeded

**Expected Behavior**: You should NEVER see a blank white screen. The app has multiple safeguards:
- Build-time validation
- Runtime error display
- Error boundary fallback
- Connection status banner

### Build Fails

**Error**: "VITE_API_BASE_URL is not set"

**Solution**:
- Set VITE_API_BASE_URL in Vercel Dashboard
- For local testing: `VITE_API_BASE_URL=https://api.hiremebahamas.com npm run build`

**Error**: "must use HTTPS in production"

**Solution**:
- Update VITE_API_BASE_URL to use https:// instead of http://

### API Not Working

**Check**:
1. Browser Console: Look for CORS or network errors
2. Health Banner: Should show if backend is unreachable
3. Network Tab: Check request URLs and responses
4. Backend Status: Verify backend is running

**For Local Dev**:
- Ensure dev server proxy is working
- Check vite.config.ts proxy configuration
- Verify backend is running on expected port

## 📊 Metrics & Monitoring

The app includes automatic error tracking and reporting:

- **Sentry Integration**: Errors are reported to Sentry (if configured)
- **Console Logging**: All errors logged to browser console
- **Health Checks**: Regular connectivity monitoring
- **Performance**: Web Vitals tracking via Vercel Analytics

## 🔒 Security Considerations

### Environment Variables

**Safe to expose (VITE_ prefix)**:
- VITE_API_BASE_URL ✅
- VITE_GOOGLE_CLIENT_ID ✅
- VITE_SENTRY_DSN ✅

**Never expose (no VITE_ prefix)**:
- DATABASE_URL ❌
- JWT_SECRET ❌
- CRON_SECRET ❌
- Any backend secrets ❌

### HTTPS Enforcement

All production builds MUST use HTTPS:
- Enforced at build time
- Enforced at runtime
- HTTP only allowed for localhost development

### CORS

- Dev server proxy handles CORS in development
- Production uses Vercel rewrites
- Backend must allow credentials for auth cookies

## 📝 Summary

This implementation provides comprehensive protection against blank screens and configuration errors:

1. ✅ **Build fails fast** if misconfigured
2. ✅ **Runtime shows clear errors** instead of blank screen
3. ✅ **Robust API client** with retries and timeouts
4. ✅ **Error boundary** catches render errors
5. ✅ **Health checks** monitor connectivity
6. ✅ **Dev proxy** prevents CORS issues
7. ✅ **Clear documentation** for troubleshooting

**Result**: Users will never see a blank white screen, and developers get clear guidance when something goes wrong.

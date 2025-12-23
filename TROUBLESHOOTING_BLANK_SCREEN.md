# Troubleshooting Blank White Screen Issue

## Quick Diagnosis

If you see a blank white screen, follow these steps:

### 1. Check Browser Console
Open Developer Tools (F12) and check the Console tab for errors:
- **Red errors**: JavaScript runtime errors
- **Yellow warnings**: Non-critical but may indicate issues
- **Network tab**: Failed API requests (look for 404, 500 errors)

### 2. Check Recent Errors
The app stores the last 10 errors in localStorage. Open the console and type:
```javascript
window.debugErrors.display()
```

To clear stored errors:
```javascript
window.debugErrors.clear()
```

### 3. Common Causes & Solutions

#### A. Missing Environment Variables
**Symptoms**: Error about `VITE_API_BASE_URL` missing

**Solution**:
1. Check `.env` file exists in `frontend/` directory
2. Ensure `VITE_API_BASE_URL` is set:
   ```
   VITE_API_BASE_URL=https://hiremebahamas-backend.onrender.com
   ```
3. For Vercel deployment, set in dashboard: Settings → Environment Variables

#### B. Backend Connection Failed
**Symptoms**: Network errors, 404s, or CORS errors in console

**Solution**:
1. Verify backend is running:
   ```bash
   curl https://hiremebahamas-backend.onrender.com/health
   ```
   Should return: `{"status":"ok"}`

2. Check CORS settings allow your frontend origin
3. Verify API URL doesn't have trailing slash

#### C. Build Issues
**Symptoms**: App doesn't load at all, or shows old version

**Solution**:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard reload (Ctrl+Shift+R)
3. Rebuild frontend:
   ```bash
   cd frontend
   npm run build
   ```

#### D. JavaScript Errors
**Symptoms**: Console shows "Uncaught Error" or similar

**Solution**:
1. Check `window.debugErrors.display()` for details
2. Look for import errors (missing modules)
3. Check component rendering errors in error boundary

### 4. Deployment Checklist

Before deploying, verify:

- [ ] `VITE_API_BASE_URL` is set in Vercel environment variables
- [ ] Backend health endpoint returns 200 OK
- [ ] Frontend builds successfully locally
- [ ] No TypeScript errors
- [ ] All dependencies installed
- [ ] Browser cache cleared

### 5. Testing Locally

To test the app locally:

```bash
# 1. Start backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# 2. Start frontend (in new terminal)
cd frontend
VITE_API_BASE_URL=http://localhost:8000 npm run dev

# 3. Open browser
open http://localhost:3000
```

### 6. Production Debugging

For production issues on Vercel:

1. Check Vercel build logs:
   - Go to Vercel Dashboard → Deployments
   - Click on failed deployment
   - Review build logs

2. Check runtime logs:
   - Vercel Dashboard → Functions
   - Look for errors in serverless functions

3. Check Sentry (if configured):
   - Go to Sentry dashboard
   - Look for recent errors

### 7. Error Boundary

The app has error boundaries that catch React errors. If you see the error fallback UI:

1. **Try Again**: Resets the error boundary
2. **Refresh Page**: Hard reload the app
3. **Go to Home**: Navigate to home page

### 8. Support

If the issue persists:

1. Check stored errors: `window.debugErrors.display()`
2. Take screenshot of console errors
3. Note:
   - Browser (Chrome, Firefox, Safari)
   - Device (Desktop, Mobile)
   - URL where error occurred
4. Contact support with this information

## Recent Fixes Applied

### Fix 1: Restored App Component
**Problem**: App.tsx was a minimal test component
**Solution**: Restored full React application with routing, error boundaries, and contexts

### Fix 2: Added Global Error Handler
**Problem**: Unhandled errors caused silent failures
**Solution**: Added comprehensive error logging and storage

### Fix 3: Enhanced Error Boundaries
**Problem**: React errors caused blank screens
**Solution**: Added ErrorBoundary with user-friendly fallback UI

## Prevention

To prevent blank screens in the future:

1. **Always test locally** before deploying
2. **Check environment variables** in deployment settings
3. **Monitor Sentry** for production errors
4. **Use error boundaries** around new components
5. **Add loading states** for async operations
6. **Test on multiple browsers** and devices

## Architecture

```
Frontend (Vite + React)
  ├── ErrorBoundary (React)
  ├── Global Error Handler (window.onerror)
  └── Sentry Integration
        ↓
Backend (FastAPI + Python)
  ├── Health Endpoints
  ├── CORS Configuration
  └── Database Connection
```

## Key Files

- `frontend/src/App.tsx` - Main app component
- `frontend/src/main.tsx` - Entry point with error handlers
- `frontend/src/utils/globalErrorHandler.ts` - Global error logging
- `frontend/src/components/ErrorFallback.tsx` - Error UI
- `frontend/.env` - Environment variables (local)
- `vercel.json` - Deployment configuration

## Health Check URLs

- Frontend: https://hiremebahamas.com
- Backend Health: https://hiremebahamas-backend.onrender.com/health
- Backend API: https://hiremebahamas-backend.onrender.com/api/

## Contact

For urgent issues, check the stored errors first, then contact the development team with:
- Error details from `window.debugErrors.display()`
- Browser console screenshot
- Steps to reproduce

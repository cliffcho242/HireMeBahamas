# Vercel → Backend Connection Configuration Guide

This guide explains how the HireMeBahamas frontend connects to its backend API.

## ✅ Fixed Issues

All hardcoded `localhost` and `127.0.0.1` URLs have been removed from the frontend code. The application now properly uses environment variables or same-origin API calls.

## 🔧 How It Works

The frontend automatically detects the correct backend URL using this priority order:

1. **`VITE_API_URL` environment variable** (if set) - for Render, Render, or local development
2. **Same-origin (`window.location.origin`)** (if no env var) - for Vercel serverless backend
3. **Localhost fallback** (only for SSR/build-time, should not be reached in production)

## 📝 Configuration Options

### Option A: Vercel Serverless Backend (RECOMMENDED)

**✅ DO NOT set `VITE_API_URL` in Vercel Dashboard**

The frontend will automatically use same-origin API calls:
- Frontend: `https://your-project.vercel.app`
- Backend API: `https://your-project.vercel.app/api/*`

**Benefits:**
- No CORS issues (same domain)
- Fastest performance
- Simplest configuration
- Automatic cold-start management

**How to verify:**
1. Deploy to Vercel
2. Open browser console
3. You should see: `🌐 Using same-origin API (Vercel serverless): https://your-project.vercel.app`

### Option B: Separate Backend (Render, Render, Custom Server)

**✅ SET `VITE_API_URL` in Vercel Dashboard → Environment Variables**

Examples:
```bash
# Render backend
VITE_API_URL=https://your-app.up.render.app

# Render backend
VITE_API_URL=https://your-app.onrender.com

# Custom domain
VITE_API_URL=https://api.hiremebahamas.com
```

**Requirements:**
- Backend CORS must allow your Vercel domain
- Backend must be publicly accessible (not internal/private URLs)

**❌ DO NOT use:**
- `localhost` or `127.0.0.1` (won't work in production)
- Render private network URLs (not accessible from Vercel)
- Internal Render hostnames (not accessible from Vercel)

### Option C: Local Development

**✅ SET `VITE_API_URL` in frontend `.env.local` file**

```bash
# Create frontend/.env.local
VITE_API_URL=http://localhost:8000
```

Then start both services:
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

## 🔍 Files Modified

The following files now use dynamic API URL configuration:

1. `frontend/src/services/api.ts` - Main API client (port 8000 fallback)
2. `frontend/src/services/api_ai_enhanced.ts` - AI-enhanced API client (port 8000 fallback)
3. `frontend/src/components/Stories.tsx` - Stories component
4. `frontend/src/contexts/AdvancedAIContext.tsx` - AI context
5. `frontend/src/contexts/AIMonitoringContext.tsx` - Monitoring context
6. `frontend/src/graphql/client.ts` - GraphQL client (port 8000 fallback)
7. `frontend/src/lib/realtime.ts` - WebSocket/real-time connection (port 8000 fallback)
8. `frontend/src/utils/connectionTest.ts` - Connection testing utility (port 8000 fallback)

**Note on localhost fallbacks:** The localhost URLs with various ports (8000, 8008, 8009, 9999) are only used during build-time or SSR scenarios and should never be reached in actual production or development usage. In practice:
- **Production:** Uses same-origin or `VITE_API_URL` env var
- **Development:** Uses `VITE_API_URL` from `.env.local`
- **Fallback:** Only triggers during unusual build scenarios (not during normal operation)

## 🧪 Testing

To verify the configuration:

1. **Check browser console logs:**
   - Look for: `🌐 Using same-origin API (Vercel serverless): ...`
   - Or: API configuration details showing the correct URL

2. **Test API health endpoint:**
   ```bash
   # For Vercel serverless
   curl https://your-project.vercel.app/api/health
   
   # For separate backend
   curl https://your-backend-url/api/health
   ```

3. **Test login/register:**
   - Should successfully connect to backend
   - No CORS errors in console
   - No 404 errors on API calls

## 🚀 Deployment Checklist

- [ ] Decide between Vercel serverless (Option A) or separate backend (Option B)
- [ ] If using Option A: Do NOT set `VITE_API_URL` in Vercel
- [ ] If using Option B: Set `VITE_API_URL` to your backend URL in Vercel
- [ ] Deploy frontend to Vercel
- [ ] Test `/api/health` endpoint
- [ ] Test user registration/login
- [ ] Verify no console errors

## ❓ Troubleshooting

### Issue: API calls fail with 404

**Solution:** Check that `VITE_API_URL` is set correctly (if using separate backend) or that Vercel serverless backend is deployed.

### Issue: CORS errors

**Solution:** 
- If using Vercel serverless (Option A): Should not happen (same-origin)
- If using separate backend (Option B): Configure backend CORS to allow your Vercel domain

### Issue: "localhost" appears in production

**Solution:** This has been fixed. The code no longer hardcodes localhost URLs.

### Issue: Backend connection timeout

**Solution:**
- If using Render free tier: Cold starts can take 30-60 seconds on first request
- If using Render: Check that service is running and publicly accessible
- Check that backend URL is correct and accessible from browser

## 📚 Related Documentation

- [Frontend .env.example](frontend/.env.example) - Environment variable examples
- [Vercel Configuration](vercel.json) - Vercel deployment config
- [Backend Router Utility](frontend/src/utils/backendRouter.ts) - API URL detection logic

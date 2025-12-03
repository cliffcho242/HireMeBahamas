# Sign-In Troubleshooting Guide

## Problem: Users Can't Sign In

If users are unable to sign in to HireMeBahamas, this guide will help you diagnose and fix the issue.

## Quick Diagnosis

### Step 1: Check if the API is responding

Visit: `https://your-app.vercel.app/api/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "platform": "vercel-serverless",
  "version": "2.0.0",
  "backend": "available",
  "database": "connected",
  "jwt": "configured",
  "database_url_set": true
}
```

**If you get an error or unexpected response, proceed to Step 2.**

### Step 2: Run Comprehensive Diagnostics

Visit: `https://your-app.vercel.app/api/diagnostic`

This will show:
- Python version
- Database connection status
- Environment variable configuration
- Backend module loading status
- JWT library availability

Look for issues in the response. Common problems:
- `database_connection: "error"` - Database not reachable
- `backend_modules: false` - Backend failed to load
- `DATABASE_URL: "missing"` - Environment variable not set
- `SECRET_KEY: "using_default"` - JWT secret not configured

### Step 3: Check Browser Console

1. Open your app in a browser
2. Press F12 to open Developer Tools
3. Go to the "Console" tab
4. Try to log in
5. Look for error messages

**What to look for:**
- `❌ API Error` - Connection or server errors
- Status codes:
  - `404` - API endpoint not found
  - `500` - Server internal error
  - `503` - Service unavailable
  - Network error - Can't reach API

### Step 4: Check Vercel Logs

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Click "Deployments" → Select latest deployment
4. Click "Functions" tab
5. Look for logs from `/api/index`

**Look for:**
- Error messages
- Stack traces
- "Backend modules not available"
- "Database initialization failed"

## Common Issues and Solutions

### Issue 1: Environment Variables Not Set

**Symptoms:**
- Health check shows `database: "unavailable"`
- Diagnostic shows `DATABASE_URL: "missing"`
- Logs show "DATABASE_URL not configured"

**Solution:**
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add the following variables:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database
SECRET_KEY=your-secret-key-32-random-characters
JWT_SECRET_KEY=your-jwt-secret-32-random-characters
ENVIRONMENT=production
```

3. Redeploy your application

**Generate secrets:**
```bash
# On Linux/macOS
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use OpenSSL
openssl rand -base64 32
```

### Issue 2: Database Connection Failed

**Symptoms:**
- Diagnostic shows `database_connection: "error"`
- Login fails with 500 error
- Logs show "Database initialization failed"

**Possible Causes:**
1. **Wrong DATABASE_URL format**
   - Vercel needs: `postgresql+asyncpg://...`
   - NOT: `postgres://...` (this will be auto-converted)

2. **Database not accessible**
   - Check if database allows connections from Vercel
   - Verify database is running
   - Check firewall rules

3. **Invalid credentials**
   - Verify username and password
   - Check database name

**Solution:**
1. Test your database connection manually
2. Verify the connection string format
3. Update DATABASE_URL in Vercel
4. Redeploy

### Issue 3: Backend Modules Not Loading

**Symptoms:**
- Diagnostic shows `backend_modules: false`
- API endpoints return 404
- Logs show import errors

**Solution:**
This usually means dependencies are missing or there's an import error.

1. Check `api/requirements.txt` includes all dependencies
2. Redeploy (Vercel will reinstall dependencies)
3. Check Vercel build logs for errors

### Issue 4: CORS Errors

**Symptoms:**
- Browser console shows "CORS policy" errors
- Network tab shows preflight (OPTIONS) requests failing

**Solution:**
The API is configured to allow all origins by default. If you're still seeing CORS errors:

1. Check Vercel configuration in `vercel.json`
2. Ensure CORS headers are set correctly
3. Try clearing browser cache

### Issue 5: Login Works But Session Not Persisting

**Symptoms:**
- Login succeeds
- Page refreshes and user is logged out
- Token not saved

**Solution:**
1. Check browser console for storage errors
2. Verify localStorage is enabled
3. Check for Private Browsing mode (may block localStorage)
4. Check browser extensions that might block cookies/storage

## How to Check Vercel Logs

### Real-time Logs
1. Go to Vercel Dashboard
2. Select your project
3. Click "Deployments"
4. Click on the latest deployment
5. Click "Functions" tab
6. Select `/api/index`
7. View logs in real-time

### Log Search
- Search for "ERROR" to find errors
- Search for "LOGIN" to find login attempts
- Look for timestamps matching your test

## Testing the Fix

After making changes:

1. **Redeploy to Vercel**
   ```bash
   git push origin main
   ```
   Or use Vercel dashboard to redeploy

2. **Wait for deployment** (usually 1-2 minutes)

3. **Test Health Endpoint**
   Visit: `https://your-app.vercel.app/api/health`

4. **Test Diagnostic Endpoint**
   Visit: `https://your-app.vercel.app/api/diagnostic`

5. **Test Login**
   - Go to your app
   - Open browser console (F12)
   - Try to log in
   - Check console for detailed logs

## Enhanced Logging

This codebase now includes comprehensive logging:

### Frontend Logs (Browser Console)
- `🔹 API Request` - Every API call with full details
- `✅ API Response` - Successful responses
- `❌ API Error` - Failed requests with details
- `=== LOGIN ATTEMPT ===` - Login flow start
- `=== LOGIN SUCCESS ===` - Login succeeded
- `=== LOGIN ERROR ===` - Login failed with details

### Backend Logs (Vercel)
- Request logging with timing
- Database query timing
- Error stack traces
- Module loading status
- Environment variable checks

## Support Checklist

When reporting issues, include:

- [ ] `/api/health` response
- [ ] `/api/diagnostic` response
- [ ] Browser console logs (screenshot or copy/paste)
- [ ] Vercel function logs (if accessible)
- [ ] Steps to reproduce
- [ ] Browser and version
- [ ] Time when issue occurred (for log searching)

## Emergency Contacts

If sign-in is completely broken and you need immediate help:

1. Check the latest deployment logs in Vercel
2. Roll back to previous deployment if needed
3. Verify environment variables are set
4. Check database status
5. Contact repository maintainer with diagnostic info

## Recent Changes

**Phase 1: Enhanced Logging & Diagnostics** (Latest)
- Added comprehensive error logging throughout the API
- Added `/api/diagnostic` endpoint
- Enhanced browser console logging
- Added global exception handler
- Improved error messages in UI

These changes will help identify why users can't sign in by providing detailed error information in both Vercel logs and browser console.

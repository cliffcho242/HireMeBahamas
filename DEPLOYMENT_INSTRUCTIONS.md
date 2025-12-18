# Deployment Instructions - Sign-In Fix

## Quick Start

This PR fixes the sign-in issue by adding comprehensive logging and diagnostics. Follow these steps to deploy:

### 1. Merge the PR

```bash
git checkout main
git merge copilot/fix-sign-in-issues
git push origin main
```

### 2. Set Environment Variables in Vercel

**🔗 [Complete Database Connection Guide](./DATABASE_CONNECTION_GUIDE.md)** - Step-by-step instructions with direct links for Vercel, Render, and Render.

Quick version for Vercel:

Go to [Vercel Dashboard](https://vercel.com/dashboard) → Your Project → Settings → Environment Variables

Add these **required** variables:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database
SECRET_KEY=your-secret-key-32-chars-minimum
JWT_SECRET_KEY=your-jwt-secret-32-chars-minimum
ENVIRONMENT=production
```

**How to generate secrets:**
```bash
# On Linux/macOS
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use OpenSSL
openssl rand -base64 32
```

**Need your DATABASE_URL?** See the [Database Connection Guide](./DATABASE_CONNECTION_GUIDE.md#vercel-setup---recommended) for direct links and detailed instructions.

### 3. Verify Deployment

After Vercel deploys, test these endpoints:

#### Check API Health
```
https://your-app.vercel.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "backend": "available",
  "database": "connected",
  "jwt": "configured"
}
```

#### Check Diagnostics
```
https://your-app.vercel.app/api/diagnostic
```

Production response:
```json
{
  "status": "operational",
  "message": "Diagnostic details hidden in production. Set DEBUG=true to enable.",
  "basic_checks": {
    "backend_available": true,
    "database_available": true
  }
}
```

### 4. Test Login

1. Open your app in a browser
2. Open Developer Console (F12)
3. Try to log in
4. Check console for error messages
5. User sees: Friendly error message
6. Console shows: Appropriate level of detail

### 5. Check Vercel Logs

If login still fails:

1. Go to Vercel Dashboard → Your Project
2. Click "Deployments" → Latest deployment
3. Click "Functions" → `/api/index`
4. Look for error messages in logs

## What's Fixed

### Before
- No error messages in logs
- Users couldn't diagnose issues
- Silent failures

### After
- Comprehensive error logging
- Health and diagnostic endpoints
- User-friendly error messages
- Full stack traces in server logs
- Environment-aware security

## Environment Variables Explained

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/db` |
| `SECRET_KEY` | JWT signing secret (32+ chars) | `your-random-32-char-string` |
| `JWT_SECRET_KEY` | JWT secret (can be same as SECRET_KEY) | `your-random-32-char-string` |
| `ENVIRONMENT` | Environment name | `production` |

### Optional

| Variable | Description | When to Use |
|----------|-------------|-------------|
| `DEBUG` | Enable full diagnostics | Debugging production issues |
| `ALLOWED_ORIGINS` | CORS origins (default: `*`) | Restrict API access |

## Troubleshooting

### Issue: Health endpoint returns "database unavailable"

**Cause**: `DATABASE_URL` not set or incorrect

**Solution**: 
1. Check Vercel environment variables
2. Verify DATABASE_URL format: `postgresql+asyncpg://...`
3. Test database connection manually

### Issue: Login fails with 500 error

**Cause**: Various (database, backend modules, configuration)

**Solution**:
1. Check `/api/diagnostic` endpoint
2. Check Vercel function logs
3. Look for error details in logs
4. See `SIGN_IN_TROUBLESHOOTING.md` for detailed help

### Issue: "Backend modules not available"

**Cause**: Dependencies missing or import errors

**Solution**:
1. Check `api/requirements.txt` is complete
2. Redeploy (Vercel reinstalls dependencies)
3. Check Vercel build logs for errors

### Issue: CORS errors in browser

**Cause**: CORS misconfiguration

**Solution**:
- API is configured to allow all origins by default
- Check browser console for specific CORS error
- Verify request is going to correct URL

## Security Notes

### Production Mode (Default)
- Generic error messages
- No PII in logs
- Limited diagnostics
- Secure by default

### Debug Mode (Optional)
- Enable with `DEBUG=true` env var
- Shows full error details
- Use only when needed
- Disable after debugging

## Getting Help

If issues persist after following this guide:

1. Check `SIGN_IN_TROUBLESHOOTING.md` for detailed troubleshooting
2. Review Vercel function logs
3. Test diagnostic endpoint with `DEBUG=true`
4. Provide:
   - `/api/health` response
   - `/api/diagnostic` response (with DEBUG=true)
   - Browser console logs
   - Vercel function logs
   - Steps to reproduce

## Next Steps

After successful deployment:

1. ✅ Verify users can log in
2. ✅ Monitor Vercel logs for errors
3. ✅ Remove `DEBUG=true` if enabled
4. ✅ Set up monitoring/alerts
5. ✅ Document any issues found

## Rollback (If Needed)

If deployment causes issues:

```bash
# In Vercel Dashboard
1. Go to Deployments
2. Find previous working deployment
3. Click "..." → "Promote to Production"
```

Then:
```bash
# In your repo
git revert [commit-hash]
git push origin main
```

## Success Indicators

✅ `/api/health` returns healthy status  
✅ `/api/diagnostic` returns operational status  
✅ Users can log in successfully  
✅ Errors show helpful messages  
✅ Vercel logs show detailed errors  
✅ No security vulnerabilities  

## Support

For more detailed information:
- **Troubleshooting**: See `SIGN_IN_TROUBLESHOOTING.md`
- **Architecture**: See `ARCHITECTURE.md`
- **Deployment**: See `VERCEL_DEPLOYMENT_GUIDE.md`

# Deployment Guide: FastAPI ModuleNotFoundError Fix

## Summary

Fixed the `ModuleNotFoundError: No module named 'fastapi'` error on Vercel by adding explicit `@vercel/python` builder configuration to `vercel.json`.

## Problem

The Vercel deployment was failing with:
```
Error importing api/index.py: 
ModuleNotFoundError: No module named 'fastapi'
```

This occurred even though `api/requirements.txt` correctly listed `fastapi==0.115.6` and all other dependencies.

## Root Cause

Vercel's automatic Python function detection was not consistently installing dependencies from `api/requirements.txt`. This can happen due to:
- Build cache issues
- Implicit detection failures
- Configuration ambiguity

## Solution

Added explicit `builds` configuration to `vercel.json` with the `@vercel/python` builder:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.12",
      "maxDuration": 30
    }
  },
  ...
}
```

This explicitly tells Vercel to:
1. Treat `api/index.py` as a Python serverless function
2. Use the `@vercel/python` builder (which handles dependency installation)
3. Look for and install dependencies from `api/requirements.txt`

## Files Changed

### vercel.json
- Added `"version": 2` (required for builds API)
- Added `"builds"` section with `@vercel/python` builder
- Preserved all existing configurations (functions, rewrites, crons, headers)

## Deployment Instructions

### Option 1: Automatic Deployment (Recommended)

If you have automatic deployments enabled on Vercel:

1. **Merge this PR** to your main/production branch
2. Vercel will automatically detect the changes and redeploy
3. **Clear Build Cache** (recommended):
   - Go to Vercel Dashboard → Your Project → Settings → General
   - Scroll to "Build & Development Settings"
   - Click "Clear Build Cache"
   - Trigger a new deployment

### Option 2: Manual Deployment

If automatic deployments are not enabled:

1. **Merge this PR** to your main branch
2. Go to Vercel Dashboard → Your Project → Deployments
3. Click "Redeploy" on the latest deployment
4. Or use Vercel CLI:
   ```bash
   vercel --prod
   ```

### Important: Clear Build Cache

If the error persists after deployment, you MUST clear Vercel's build cache:

1. Go to Vercel Dashboard
2. Select your project
3. Go to Settings → General
4. Find "Build & Development Settings"
5. Click "Clear Build Cache"
6. Redeploy the project

Build cache can cause old builds (without dependencies) to be reused, preventing the fix from taking effect.

## Verification

After deployment, verify the fix by testing these endpoints:

### 1. Health Check
```bash
curl https://your-app.vercel.app/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "platform": "vercel-serverless",
  "version": "2.0.0",
  "backend": "available",
  "database": "connected",
  ...
}
```

### 2. Status Check
```bash
curl https://your-app.vercel.app/api/status
```

**Expected Response:**
```json
{
  "status": "online",
  "backend_loaded": true,
  "backend_status": "full",
  ...
}
```

### 3. API Documentation
Visit: `https://your-app.vercel.app/api/docs`

Should show the FastAPI interactive documentation (Swagger UI).

### 4. Test Authentication
```bash
curl -X POST https://your-app.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'
```

## Troubleshooting

### Error Still Occurs After Deployment

1. **Check Build Logs**:
   - Go to Vercel Dashboard → Deployments → Latest Deployment
   - Click on "Build Logs"
   - Look for Python dependency installation output
   - Verify `fastapi` appears in the installation logs

2. **Verify Build Cache Was Cleared**:
   - The build cache MUST be cleared for the fix to take effect
   - Old cached builds don't include dependency installation

3. **Check Environment Variables**:
   - Ensure `DATABASE_URL` or `POSTGRES_URL` is set (if using database)
   - Ensure `SECRET_KEY` or `JWT_SECRET_KEY` is set (for authentication)

4. **Verify Files Are Deployed**:
   ```bash
   # Check that api/requirements.txt is in your repository
   git ls-files | grep requirements.txt
   ```
   Should show:
   ```
   api/requirements.txt
   requirements.txt
   ```

5. **Check Vercel Function Logs**:
   - Go to Vercel Dashboard → Your Project → Functions
   - Check runtime logs for any import errors
   - Should NOT see any `ModuleNotFoundError`

### Dependencies Not Installing

If dependencies are not being installed:

1. **Verify api/requirements.txt exists and is committed**:
   ```bash
   git ls-files api/requirements.txt
   ```

2. **Check file format**:
   ```bash
   file api/requirements.txt
   # Should show: UTF-8 text
   ```

3. **Verify contents**:
   ```bash
   cat api/requirements.txt | grep fastapi
   # Should show: fastapi==0.115.6
   ```

### Build Configuration Warning

You may see a warning in Vercel dashboard:
> "Your Build Configuration will override Dashboard Settings"

This is expected and acceptable. The explicit `builds` configuration in `vercel.json` takes precedence over dashboard settings, which is what we want for reliability.

## Technical Details

### Why This Fix Works

1. **Explicit Builder**: The `@vercel/python` builder explicitly tells Vercel to process this as a Python function
2. **Dependency Detection**: The builder automatically finds `api/requirements.txt` and installs all dependencies
3. **Proper Packaging**: Dependencies are bundled with the Lambda function code
4. **Cache Bypass**: Explicit configuration bypasses any automatic detection failures

### Configuration Compatibility

The fix uses:
- ✅ `"version": 2` - Required for builds API
- ✅ `"builds"` - Explicit builder configuration
- ✅ `"functions"` - Modern function settings (timeout, runtime)
- ✅ `"rewrites"` - Modern routing (not legacy "routes")
- ✅ All existing features - crons, headers, etc. preserved

This configuration is compatible with:
- Vercel's modern platform
- Python 3.12 runtime
- FastAPI + Mangum serverless adapter
- All existing project features

## Additional Notes

### About the "Deprecated" Warning

Some tools may warn that the `builds` configuration is deprecated. While Vercel recommends automatic detection in modern projects, the `builds` approach is:
- Still fully supported
- More reliable for complex projects
- Necessary when automatic detection fails
- Used by many production Vercel projects

### Future Considerations

Once this fix is deployed and verified working, you may optionally try simplifying the configuration in the future by:
1. Removing the `builds` section
2. Relying only on `functions` configuration
3. Testing thoroughly to ensure dependencies still install

However, if it works now, there's no urgent need to change it.

## References

- [Vercel Python Runtime Documentation](https://vercel.com/docs/functions/runtimes/python)
- [Vercel Build Configuration](https://vercel.com/docs/build-step)
- [@vercel/python Builder](https://github.com/vercel/vercel/tree/main/packages/python)
- [FastAPI on Vercel](https://fastapi.tiangolo.com/deployment/vercel/)
- [Mangum - ASGI adapter for AWS Lambda](https://mangum.io/)

## Support

If you continue to experience issues after following this guide:
1. Check the Vercel function logs for detailed error messages
2. Verify all environment variables are set correctly
3. Ensure the build cache has been cleared
4. Review the Build Logs in Vercel Dashboard
5. Check that api/requirements.txt is present and correct

---

**Date**: December 5, 2024
**Issue**: FastAPI ModuleNotFoundError on Vercel deployment
**Status**: ✅ Ready for deployment

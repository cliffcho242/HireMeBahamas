# Vercel Deployment 404 Error Fix

## Problem

Users were encountering a `404: NOT_FOUND` error with code `DEPLOYMENT_NOT_FOUND` when accessing the HireMeBahamas application deployed on Vercel.

**Error Details:**
```
404: NOT_FOUND
Code: DEPLOYMENT_NOT_FOUND
ID: iad1::w8sw2-1764947401263-a8632abddccc
```

## Root Cause

The issue was caused by **conflicting Vercel configuration**:

1. **Mixed API versions**: The root `vercel.json` was using both:
   - Old API: `builds` and `routes` 
   - New API: `outputDirectory` and `buildCommand`
   
   These two approaches should not be mixed in a single configuration.

2. **Conflicting configuration files**: There were two `vercel.json` files:
   - `/vercel.json` (root level)
   - `/frontend/vercel.json` (frontend specific)
   
   Having multiple vercel.json files can cause Vercel to be confused about which configuration to use.

## Solution

### Changes Made

1. **Updated root `vercel.json`** to use the modern configuration approach:
   - Removed `builds` and `routes` (old API)
   - Using `rewrites` instead (compatible with `outputDirectory`)
   - Kept `outputDirectory: "frontend/dist"` for static site serving
   - Kept `buildCommand` for frontend build

2. **Removed conflicting `frontend/vercel.json`**:
   - Deleted `frontend/vercel.json` (backed up as `frontend/vercel.json.backup`)
   - All configuration is now in the root `vercel.json`

3. **Enhanced security headers**:
   - Added `Strict-Transport-Security` (HSTS)
   - Added `Permissions-Policy`
   - Added `X-DNS-Prefetch-Control`

### Final Configuration

```json
{
  "version": 2,
  "buildCommand": "cd frontend && npm ci && npm run build",
  "outputDirectory": "frontend/dist",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/index.py"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "crons": [...],
  "headers": [...]
}
```

## How It Works

### Static Site Serving
- `outputDirectory: "frontend/dist"` tells Vercel to serve static files from this directory
- `buildCommand` runs the frontend build to generate the dist folder
- All static files (HTML, CSS, JS, images) are served directly from `frontend/dist`

### API Routing
- `/api/*` requests are rewritten to `/api/index.py`
- Vercel automatically detects Python files in the `api/` directory as serverless functions
- The `api/index.py` file exports a `handler` using Mangum for FastAPI

### SPA Routing
- All non-API requests fallback to `/index.html`
- This enables client-side routing for the React application
- Users can navigate to any route and the React app will handle it

## Verification

### Local Build Test
```bash
# Build the frontend
cd frontend
npm ci
npm run build

# Verify dist directory exists
ls -la dist/
ls -la dist/index.html  # Should exist
```

### Deployment Test
After pushing to main branch:

1. **Check GitHub Actions**: Ensure the deploy workflow runs successfully
2. **Check Vercel Dashboard**: 
   - Go to https://vercel.com/dashboard
   - Select your project
   - Check deployment logs
   - Verify deployment status is "Ready"

3. **Test the deployed site**:
   ```bash
   # Test frontend
   curl -I https://your-app.vercel.app/
   # Should return 200 OK with index.html content
   
   # Test API
   curl https://your-app.vercel.app/api/health
   # Should return JSON with status information
   ```

4. **Browser test**:
   - Open https://your-app.vercel.app/ in browser
   - Should load the React application
   - Check Network tab - no 404 errors on page load
   - Navigate to different routes - should work without 404

## Troubleshooting

### If you still see 404 errors:

1. **Clear Vercel cache**:
   - In Vercel dashboard, go to Settings > General
   - Scroll to "Clear Cache" and click it
   - Redeploy your application

2. **Check environment variables**:
   - Ensure `DATABASE_URL`, `SECRET_KEY`, and `JWT_SECRET_KEY` are set in Vercel
   - Go to Settings > Environment Variables

3. **Check build logs**:
   - In Vercel dashboard, click on the deployment
   - Review "Build Logs" tab for any errors
   - Look for Python package installation errors

4. **Verify API requirements**:
   - Ensure `api/requirements.txt` exists
   - Check that all Python dependencies are listed
   - Python 3.12 runtime is specified in `runtime.txt`

5. **Check GitHub Actions**:
   - Ensure secrets are configured:
     - `VERCEL_TOKEN`
     - `VERCEL_ORG_ID`
     - `VERCEL_PROJECT_ID`

## Best Practices

1. **Single vercel.json**: Keep only one `vercel.json` at the project root
2. **Use modern API**: Prefer `rewrites` over `routes` when using `outputDirectory`
3. **Test locally**: Always build locally before deploying to catch build issues early
4. **Monitor deployments**: Check Vercel dashboard after each push to main
5. **Use preview deployments**: Test PRs in preview environments before merging

## References

- [Vercel Configuration Documentation](https://vercel.com/docs/projects/project-configuration)
- [Vercel Serverless Functions](https://vercel.com/docs/functions)
- [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- [Vercel Rewrites](https://vercel.com/docs/edge-network/rewrites)

## Related Files

- `/vercel.json` - Root Vercel configuration
- `/api/index.py` - Serverless function handler
- `/api/requirements.txt` - Python dependencies
- `/runtime.txt` - Python version (3.12.0)
- `/frontend/dist/` - Built frontend assets (generated)

## Questions?

If you encounter issues after this fix:
1. Check the Vercel deployment logs
2. Review the GitHub Actions workflow logs
3. Ensure all environment variables are set
4. Verify the build completes successfully locally

For more help, see:
- [FIX_SIGN_IN_DEPLOYMENT_GUIDE.md](./FIX_SIGN_IN_DEPLOYMENT_GUIDE.md)
- [DEPLOYMENT_CONNECTION_GUIDE.md](./DEPLOYMENT_CONNECTION_GUIDE.md)

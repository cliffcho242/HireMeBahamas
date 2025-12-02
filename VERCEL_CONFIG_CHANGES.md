# Vercel Configuration Update - Important Notes

## Summary
The `vercel.json` configuration has been simplified as per requirements to use wildcard builds and simplified routing.

## Configuration Changes

### Old Configuration
- **Builds**: Explicitly built 3 specific Python files with custom configs (maxLambdaSize: 50mb, runtime: python3.12)
- **Routing**: Used `rewrites` to intelligently route API requests to the appropriate handlers
  - Most `/api/*` requests → `api/index.py` (FastAPI app)
  - Specific routes like `/api/auth/me` → `api/auth/me.py`
- **Features**: 
  - Custom install command for binary-only pip installs
  - Function configuration (30s timeout, 1GB memory, Python 3.12)
  - Security and CORS headers
  - Cron job for health checks

### New Configuration
- **Builds**: Wildcard pattern `api/**/*.py` builds all Python files
- **Routing**: Simple `routes` configuration with pass-through pattern
  - `/api/*` → `/api/*` (direct mapping to file structure)
  - `/*` → `/` (root catch-all)
- **Features**: Relies on Vercel defaults for all configuration

## Important Behavioral Changes

### 1. API Routing Changes
**Previous behavior**: Routes like `/api/jobs`, `/api/posts`, `/api/auth/login` were handled by the FastAPI application in `api/index.py`.

**New behavior**: Routes will map directly to file paths. This means:
- ✅ `/api/test` will work (maps to `api/test.py`)
- ✅ `/api/auth/me` will work (maps to `api/auth/me.py`)
- ✅ `/api/cron/health` will work (maps to `api/cron/health.py`)
- ❓ `/api/jobs`, `/api/posts`, etc. may need explicit routing or file structure changes

### 2. Files Built as Functions
All Python files in the `api` directory will be built as serverless functions, including:
- ✅ `api/index.py` - Intended endpoint
- ✅ `api/auth/me.py` - Intended endpoint
- ✅ `api/cron/health.py` - Intended endpoint
- ✅ `api/test.py` - Intended endpoint
- ⚠️ `api/database.py` - Utility module (may cause build issues if not a valid function)

### 3. Missing Features
- **No security headers**: CORS, CSP, and other security headers are no longer configured
- **No cron job**: The `/api/cron/health` endpoint will exist but won't be called automatically
- **No custom install command**: Dependencies will be installed using Vercel's default behavior
- **No function limits**: Will use Vercel's default 10s timeout and memory limits

## Testing Recommendations

1. **Test API endpoints**: Verify that all expected API routes work correctly
2. **Check CORS**: Ensure CORS headers are handled by the application code if needed
3. **Verify dependencies**: Check that all Python dependencies install correctly
4. **Monitor function limits**: Watch for timeout issues (default 10s vs previous 30s)
5. **Health monitoring**: Set up alternative health monitoring since cron job is removed

## Compatibility Concerns

### FastAPI Application Access
The FastAPI app in `api/index.py` handles multiple routes internally:
- `/api/health`, `/api/ready`
- `/api/auth/login`, `/api/auth/register`, `/api/auth/me`
- `/api/jobs`, `/api/posts`
- And more...

With the new routing, these may need to be accessed via `/api/index` as the base path, or the application structure may need to be reorganized.

### Database Utility File
The `api/database.py` file is a utility module, not an endpoint. Building it as a serverless function may cause errors. Consider:
- Moving utility files outside the `api` directory
- Adding them to `.vercelignore`
- Restructuring to avoid building non-endpoint files

## Recommendations for Production

If this configuration causes issues in production, consider:

1. **Restore specific builds**: Return to explicit build configuration for known endpoints
2. **Fix routing**: Add proper rewrites to route requests to the correct handlers
3. **Re-add security headers**: Configure CORS and security headers in vercel.json
4. **Re-enable cron**: Add the cron job configuration back if health checks are needed
5. **Add function config**: Specify timeouts and memory limits explicitly

## Migration Path

To maintain backward compatibility while using the simplified config, you could:
1. Ensure each route has its own Python file in the appropriate path
2. OR Keep using `api/index.py` but access it via `/api/index/*` routes
3. OR Revert to the previous configuration if the simplified version doesn't meet requirements

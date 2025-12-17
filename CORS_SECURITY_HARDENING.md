# CORS Security Hardening Implementation

## Overview

This document describes the implementation of production-grade CORS (Cross-Origin Resource Sharing) security locks for the HireMeBahamas application. The changes enforce strict CORS policies in production environments to prevent security vulnerabilities.

## Security Requirements

As per the security requirement, production deployments must enforce:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains only
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Specific methods
    allow_headers=["Authorization", "Content-Type"],  # Specific headers
)
```

**🚫 ABSOLUTE BAN in Production:**
- No wildcard (`*`) in `allow_origins`
- No wildcard (`*`) in `allow_headers`
- No wildcard (`*`) in `allow_methods`

## Implementation Details

### 1. Production Environment Detection

**File:** `backend/app/core/environment.py`

The `get_cors_origins()` function now:
- Detects production mode via `ENVIRONMENT` or `VERCEL_ENV` environment variables
- Returns only HTTPS origins in production mode
- Supports custom origins via `ALLOWED_ORIGINS` environment variable
- Automatically rejects wildcard patterns in production

```python
# Production mode: strict whitelist only
origins = [
    "https://hiremebahamas.com",
    "https://www.hiremebahamas.com",
]

# Development mode: includes localhost for testing
origins = [
    "https://hiremebahamas.com",
    "https://www.hiremebahamas.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

### 2. Middleware Configuration

**File:** `backend/app/core/middleware.py`

The `setup_cors()` function enforces:
- Specific HTTP methods only: `["GET", "POST", "PUT", "DELETE"]`
- Specific headers only: `["Authorization", "Content-Type"]`
- Dynamic origins from `get_cors_origins()`

### 3. Main Application

**File:** `backend/app/main.py`

Implements production-safe CORS with fallback logic:
- Primary: Uses `get_cors_origins()` from environment module
- Fallback: Manual configuration that also enforces production restrictions
- Removes wildcard patterns in production mode

### 4. Vercel Serverless Handler

**File:** `api/index.py`

Production-first configuration:
- Detects production mode via `is_production_mode()`
- Default production origins: `hiremebahamas.com` and `www.hiremebahamas.com`
- Allows wildcard only in development/preview environments
- Properly handles `allow_credentials` based on origin type

### 5. Development Files

Updated with warnings and proper credentials handling:
- `backend/app/simple_main.py`
- `backend/app/simple_backend.py`
- `backend/test_app.py`
- `api/backend_app/simple_main.py`
- `api/backend_app/simple_backend.py`

All development files now:
- Include clear warnings that they're for development only
- Set `allow_credentials=False` when using wildcard origins (per CORS spec)

## Configuration Options

### Environment Variables

#### `ALLOWED_ORIGINS`

Comma-separated list of allowed origins. Used in both production and development.

**Production:**
```bash
ALLOWED_ORIGINS="https://hiremebahamas.com,https://www.hiremebahamas.com"
```

**Development:**
```bash
ALLOWED_ORIGINS="*"  # Allowed only in development mode
```

**Important:** Setting `ALLOWED_ORIGINS="*"` will be rejected in production mode.

#### `ENVIRONMENT` or `VERCEL_ENV`

Set to `"production"` to enable production mode:

```bash
ENVIRONMENT=production
# or
VERCEL_ENV=production
```

### Default Origins

#### Production
- `https://hiremebahamas.com`
- `https://www.hiremebahamas.com`

#### Development (additional)
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:5173`
- `http://127.0.0.1:5173`

## Deployment Configuration

### Render Deployment

Set in your Render dashboard environment variables:

```bash
ENVIRONMENT=production
ALLOWED_ORIGINS=https://hiremebahamas.com,https://www.hiremebahamas.com
```

### Vercel Deployment

Set in your Vercel project settings:

```bash
VERCEL_ENV=production  # Automatically set by Vercel
ALLOWED_ORIGINS=https://hiremebahamas.com,https://www.hiremebahamas.com
```

### Railway Deployment

Set in your Railway project variables:

```bash
ENVIRONMENT=production
ALLOWED_ORIGINS=https://hiremebahamas.com,https://www.hiremebahamas.com
```

## Testing

### Production Security Test

Run the comprehensive security test suite:

```bash
python test_production_cors_security.py
```

This test verifies:
1. ✅ No wildcard origins in production mode
2. ✅ All origins use HTTPS in production
3. ✅ Specific HTTP methods only (GET, POST, PUT, DELETE)
4. ✅ Specific headers only (Authorization, Content-Type)
5. ✅ No unguarded wildcard patterns in production code

### Expected Output

```
============================================================
PRODUCTION CORS SECURITY TEST SUITE
============================================================

1. Testing backend/app/core/environment.py production origins...
✅ Production mode detected
✅ No wildcard (*) in production origins
✅ All origins use HTTPS
✅ 2 specific origin(s) configured
✅ PASS: Production origins are secure

2. Testing backend/app/core/middleware.py configuration...
✅ Specific HTTP methods configured (GET, POST, PUT, DELETE)
✅ Specific headers configured (Authorization, Content-Type)
✅ PASS: Middleware configuration is secure

[... additional tests ...]

============================================================
TEST RESULTS
============================================================
Passed: 5/5
Failed: 0/5

✅ ALL PRODUCTION CORS SECURITY TESTS PASSED!
```

## Security Benefits

### 1. Origin Restriction
**Before:** Any website could make requests to your API (wildcard `*`)
**After:** Only specified domains can access the API

### 2. Method Restriction
**Before:** All HTTP methods allowed (including potentially dangerous ones)
**After:** Only necessary methods allowed (GET, POST, PUT, DELETE)

### 3. Header Restriction
**Before:** Any headers allowed (wildcard `*`)
**After:** Only necessary headers allowed (Authorization, Content-Type)

### 4. Environment Awareness
**Before:** Same permissive configuration in all environments
**After:** Strict configuration in production, permissive only in development

### 5. Credentials Handling
**Before:** Misconfigured `allow_credentials=True` with wildcard origins (violates CORS spec)
**After:** Proper credentials handling based on origin type

## Common Issues and Solutions

### Issue: Frontend Can't Connect in Production

**Symptom:** Browser console shows CORS error in production

**Solution:** Ensure your frontend domain is in `ALLOWED_ORIGINS`:

```bash
# For Render or Railway
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com

# For Vercel (if frontend and backend are separate)
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://hiremebahamas.com
```

### Issue: Preview Deployments Not Working

**Symptom:** Vercel preview deployments show CORS errors

**Solution:** Add preview deployment URL to `ALLOWED_ORIGINS` or use pattern matching in development mode only.

For Vercel preview deployments, you can add specific preview URLs:

```bash
ALLOWED_ORIGINS=https://hiremebahamas-git-feature-yourorg.vercel.app,https://hiremebahamas.com
```

### Issue: Credentials Not Working

**Symptom:** Authenticated requests fail with CORS error

**Solution:** Ensure you're not using wildcard origins when `allow_credentials=True`. This is a CORS specification requirement.

## Migration Guide

If you're upgrading from an older version with permissive CORS:

### Step 1: Identify Your Domains

List all legitimate domains that need to access your API:
- Production domain(s)
- Preview/staging domains (if any)
- Development domains (localhost for development only)

### Step 2: Set Environment Variables

Add the `ALLOWED_ORIGINS` environment variable to your deployment:

```bash
ALLOWED_ORIGINS=https://hiremebahamas.com,https://www.hiremebahamas.com
```

### Step 3: Deploy

Deploy the updated code to your production environment.

### Step 4: Test

1. Verify production frontend works correctly
2. Check browser console for CORS errors
3. Test authenticated requests
4. Verify API endpoints respond correctly

### Step 5: Monitor

Monitor your application logs for any CORS-related errors in the first 24 hours.

## Best Practices

1. **Never use wildcard (`*`) origins in production**
2. **Always use HTTPS in production origins**
3. **Only allow necessary HTTP methods**
4. **Only allow necessary headers**
5. **Use environment variables for configuration**
6. **Test CORS configuration before deploying**
7. **Monitor logs for CORS errors**
8. **Document all allowed origins**

## References

- [MDN CORS Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [FastAPI CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors/)
- [OWASP CORS Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html#cross-origin-resource-sharing)

## Support

For issues related to CORS configuration, check:
1. Browser console for specific error messages
2. Application logs for server-side errors
3. This documentation for configuration examples
4. Run `python test_production_cors_security.py` to validate configuration

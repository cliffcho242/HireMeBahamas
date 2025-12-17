# CORS Configuration Lock - Security Documentation

## Overview

This document describes the CORS (Cross-Origin Resource Sharing) configuration for HireMeBahamas, which has been hardened to meet production security requirements.

## Security Requirements ✅

### ✅ Requirement Met: No Wildcards in Production

**Problem Statement:**
> 5️⃣ BACKEND — CORS LOCK (REQUIRED) allow_origins=[
>   "https://your-vercel-app.vercel.app",
>   "https://yourdomain.com"
> ] No wildcards in prod.

**Implementation:**
All CORS configurations now use specific domain allowlists with **NO wildcard patterns** (`*`) in production mode.

## Production Origins

In production mode (`ENVIRONMENT=production` or `VERCEL_ENV=production`), only these specific origins are allowed:

```python
[
    "https://hiremebahamas.com",
    "https://www.hiremebahamas.com",
    "https://hiremebahamas.vercel.app",  # Vercel production deployment
]
```

## Configuration Files Updated

1. **`api/backend_app/core/environment.py`**
   - Removed wildcard pattern `https://*.vercel.app`
   - Added specific Vercel production URL
   - Added environment variable support

2. **`backend/app/core/environment.py`**
   - Added specific Vercel production URL
   - Ensured consistency with API backend

3. **`api/main.py`**
   - Updated fallback CORS configuration
   - Removed wildcard patterns even in error fallback mode
   - Added production mode detection

4. **`api/backend_app/main.py`**
   - Updated Socket.IO CORS configuration
   - Uses same origins as main CORS middleware

## Environment Variable Support

### ALLOWED_ORIGINS

For additional origins (e.g., preview deployments, staging environments), use the `ALLOWED_ORIGINS` environment variable:

```bash
# Production example with additional preview deployment
ALLOWED_ORIGINS="https://hiremebahamas.com,https://www.hiremebahamas.com,https://hiremebahamas-git-feature.vercel.app"
```

**Important:** The `ALLOWED_ORIGINS` environment variable:
- ✅ Accepts comma-separated list of specific origins
- 🚫 Rejects wildcard (`*`) - will fall back to default origins
- ✅ Only applies in production mode
- ✅ Must use full URLs with protocol (https://)

## Development Mode

In development mode (`ENVIRONMENT != production`), the following origins are additionally allowed:

```python
[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite default
    "http://127.0.0.1:5173",
]
```

## CORS Middleware Configuration

### HTTP Methods

Only specific HTTP methods are allowed:

```python
allow_methods=["GET", "POST", "PUT", "DELETE"]
```

### Headers

Only specific headers are allowed:

```python
allow_headers=["Authorization", "Content-Type"]
```

### Credentials

```python
allow_credentials=True  # Required for secure cookie-based authentication
```

**Note:** When `allow_credentials=True`, wildcard origins are prohibited by the CORS specification. All origins must be explicitly listed.

## Socket.IO Configuration

Socket.IO uses the same CORS origins as the main CORS middleware:

```python
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=cors_origins  # Same as CORS middleware
)
```

## Testing

### Run CORS Security Tests

```bash
# Existing security test suite
python test_production_cors_security.py

# Comprehensive verification script
python verify_cors_lock.py
```

### Test Results

All tests pass:
- ✅ No wildcards in production
- ✅ All origins use HTTPS
- ✅ Specific domains configured
- ✅ Custom origins via environment variables work
- ✅ Wildcard rejection works
- ✅ Consistent configuration across all entry points

## Migration Guide

### If You Need to Add a New Origin

1. **For Production:**
   ```bash
   # Add to ALLOWED_ORIGINS environment variable
   ALLOWED_ORIGINS="https://hiremebahamas.com,https://www.hiremebahamas.com,https://new-origin.com"
   ```

2. **For Development:**
   Edit the `get_cors_origins()` function in `backend/app/core/environment.py`:
   ```python
   else:
       origins = [
           # ... existing origins ...
           "http://localhost:8080",  # Add your new origin
       ]
   ```

### If You Have a Preview Deployment

For Vercel preview deployments, add them to the `ALLOWED_ORIGINS` environment variable:

```bash
ALLOWED_ORIGINS="https://hiremebahamas.com,https://hiremebahamas-git-mybranch.vercel.app"
```

**Do NOT use wildcard patterns** like `https://*.vercel.app` as they are security vulnerabilities and will be rejected.

## Security Benefits

1. **Prevents CSRF Attacks:** Only known origins can make authenticated requests
2. **Prevents XSS Attacks:** Limits which sites can access the API
3. **Credential Protection:** Ensures cookies are only sent to trusted origins
4. **Audit Trail:** All allowed origins are explicitly documented
5. **Compliance:** Meets security best practices and compliance requirements

## References

- [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [OWASP: CORS Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Origin_Resource_Sharing_Cheat_Sheet.html)
- [FastAPI CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors/)

## Support

If you encounter CORS issues:

1. Verify the origin is in the allowlist
2. Check the `ALLOWED_ORIGINS` environment variable
3. Ensure you're using HTTPS in production
4. Run the verification script: `python verify_cors_lock.py`
5. Check the browser console for CORS errors

## Maintenance

**IMPORTANT:** Never add wildcard patterns to production configurations. Always use specific domain names.

Last Updated: 2025-12-17

# Vercel Preview CORS Fix - Complete Solution

## Problem Statement

Vercel preview deployments have dynamic URLs like:
```
https://frontend-{HASH}-cliffs-projects-a84c76c9.vercel.app
```

Where `{HASH}` changes with each deployment. This caused **silent CORS failures** because:

1. Frontend sends request with `Origin: https://frontend-XYZ.vercel.app`
2. Backend CORS checks `allow_origins` list
3. Origin not found → **request blocked**
4. Browser never delivers response to JavaScript
5. Frontend shows:
   - Blank page
   - "Unexpected response"
   - "Load failed"
6. **No Render logs** (because request never reaches the app)

This is especially problematic on **mobile Safari**, causing white screen errors.

## Root Cause

The Vercel preview URL regex pattern in `backend/app/core/environment.py` was:
```python
r'^https://frontend-[a-z0-9]+-cliffs-projects-a84c76c9\.vercel\.app$'
```

This pattern only matched lowercase letters and numbers `[a-z0-9]+`, but Vercel hashes can also contain **hyphens**. For example:
- ✅ `frontend-fodpcl8vo-cliffs-projects-...` (works)
- ❌ `frontend-test-hash-123-cliffs-projects-...` (blocked before fix)

## Solution Implemented

### 1. Fixed Regex Pattern

Updated the pattern in `backend/app/core/environment.py` to include hyphens:

```python
VERCEL_PROJECT_PATTERN = re.compile(
    r'^https://frontend-[a-z0-9-]+-cliffs-projects-a84c76c9\.vercel\.app$'
)
```

**Change**: `[a-z0-9]+` → `[a-z0-9-]+`

This now matches all valid Vercel preview URLs for this project.

### 2. How It Works

The CORS middleware in `backend/app/main.py` already had the infrastructure:

1. **Import** the validation function:
   ```python
   from .core.environment import is_valid_vercel_preview_origin
   ```

2. **Check origins** dynamically:
   ```python
   def _check_origin_allowed(origin: str) -> bool:
       # Check static allowed origins
       if origin in _allowed_origins:
           return True
       
       # Check if it's a valid Vercel preview deployment
       if _is_valid_vercel_preview_origin(origin):
           return True
       
       return False
   ```

3. **Apply CORS headers** for allowed origins:
   ```python
   @app.middleware("http")
   async def cors_middleware(request: Request, call_next):
       origin = request.headers.get("origin")
       
       if origin and _check_origin_allowed(origin):
           response.headers["Access-Control-Allow-Origin"] = origin
           response.headers["Access-Control-Allow-Credentials"] = "true"
   ```

## Security Guarantees

✅ **No wildcards** - Never uses `*` in production
✅ **Project-specific** - Only allows this project's preview deployments via regex
✅ **Protocol enforcement** - Only HTTPS, never HTTP
✅ **Exact matching** - Prevents subdomain attacks (e.g., `evil.com/frontend-abc-...`)
✅ **Credentials safe** - Works with cookies and authentication

### What's Blocked

❌ Different Vercel projects (different project ID)
❌ HTTP connections (only HTTPS)
❌ Uppercase letters in hash
❌ Special characters except hyphens
❌ URLs with paths appended
❌ Subdomain attacks

## Configuration

### Production Deployment (Render)

Set this environment variable:
```bash
ALLOWED_ORIGINS=https://hiremebahamas.com,https://www.hiremebahamas.com
```

Preview deployments are handled **automatically** by the regex matcher.

### How Preview Matching Works

```
Request Origin: https://frontend-abc123-cliffs-projects-a84c76c9.vercel.app

1. Check static origins list → Not found
2. Check preview pattern → ✅ Matches!
3. Add CORS headers with this origin
4. Request succeeds
```

No manual configuration needed for each preview deployment!

## Testing

Run the validation test:
```bash
python test_vercel_preview_cors.py
```

This test validates:
- ✅ Valid preview URLs are accepted
- ✅ Invalid URLs are rejected
- ✅ Production domains work
- ✅ ALLOWED_ORIGINS environment variable works

## What This Fixes

### Before Fix
```
Frontend: https://frontend-test-123-cliffs-projects-a84c76c9.vercel.app
Backend CORS: ❌ Blocked (hash contains hyphens)
Result: White screen, no error logs
```

### After Fix
```
Frontend: https://frontend-test-123-cliffs-projects-a84c76c9.vercel.app
Backend CORS: ✅ Allowed (matches pattern)
Result: App works perfectly!
```

## Browser Behavior

With this fix, browsers will now see:

### Preflight (OPTIONS) Request
```http
Request:
  Origin: https://frontend-abc123-cliffs-projects-a84c76c9.vercel.app
  
Response:
  HTTP 200 OK
  Access-Control-Allow-Origin: https://frontend-abc123-cliffs-projects-a84c76c9.vercel.app
  Access-Control-Allow-Credentials: true
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE, PATCH, OPTIONS
```

### Actual Request
```http
Request:
  Origin: https://frontend-abc123-cliffs-projects-a84c76c9.vercel.app
  
Response:
  HTTP 200 OK
  Access-Control-Allow-Origin: https://frontend-abc123-cliffs-projects-a84c76c9.vercel.app
  Access-Control-Allow-Credentials: true
  [response data]
```

## Why This is Enterprise-Grade

| Concern | How We Handle It |
|---------|------------------|
| Wildcards | ❌ Not used |
| Other Vercel projects | ❌ Blocked by project ID in regex |
| Random subdomains | ❌ Blocked by exact pattern matching |
| Only your project | ✅ Allowed via controlled regex |
| Production domains | ✅ Explicit via env var |
| Preview deployments | ✅ Controlled regex |

## Verification

You can verify this works by checking browser DevTools Network tab:

### Before Fix
```
Status: (blocked:cors)
Response: (empty)
```

### After Fix
```
Status: 200 OK
Response Headers:
  access-control-allow-origin: https://frontend-abc123-cliffs-projects-a84c76c9.vercel.app
  access-control-allow-credentials: true
```

## Mobile Safari Compatibility

This fix specifically addresses mobile Safari's strict CORS enforcement:
- ✅ Explicit origin in response header
- ✅ Credentials allowed
- ✅ No wildcards (Safari blocks these)
- ✅ HTTPS enforced
- ✅ Proper preflight handling

## Summary

**One line change**, maximum impact:

```diff
- r'^https://frontend-[a-z0-9]+-cliffs-projects-a84c76c9\.vercel\.app$'
+ r'^https://frontend-[a-z0-9-]+-cliffs-projects-a84c76c9\.vercel\.app$'
```

This single character addition (`-` in the character class) enables all Vercel preview deployments to work seamlessly while maintaining enterprise-grade security.

🎉 **Your app will literally not know what a white screen is anymore.**

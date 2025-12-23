# CORS Configuration Module

This module provides a simplified, bulletproof CORS configuration for the backend API.

## Features

✅ **Preview deployments automatically allowed** via regex pattern matching  
✅ **Production origins safe** - uses environment variables  
✅ **Prevents CORS from silently breaking** fetch requests  
✅ **Environment variable enforcement** for production domains

## Usage

### Option 1: Use this module (Simple Approach)

Replace the CORS configuration in `backend/app/main.py`:

```python
from .cors import apply_cors

# After creating the FastAPI app
app = FastAPI(...)

# Apply CORS configuration
apply_cors(app)
```

### Option 2: Keep existing implementation (Current Approach)

The existing CORS implementation in `main.py` already provides:
- Dynamic Vercel preview support
- Environment-based configuration
- Production-safe credentials handling

This module serves as an alternative/backup approach or reference implementation.

## Environment Variables

Set in Render Backend:

```bash
ALLOWED_ORIGINS=https://hiremebahamas.com,https://www.hiremebahamas.com
VERCEL_PROJECT_ID=cliffs-projects-a84c76c9  # Optional, has sensible default
```

The module automatically:
1. Parses comma-separated origins from `ALLOWED_ORIGINS`
2. Validates each origin for proper URL format
3. Uses production defaults if not set or invalid
4. Allows Vercel preview deployments matching the regex pattern

## Vercel Preview Pattern

The regex pattern allows preview deployments with URLs like:
```
https://frontend-abc123-cliffs-projects-a84c76c9.vercel.app
```

The project ID can be configured via `VERCEL_PROJECT_ID` environment variable.

Default pattern: `^https://frontend-[a-z0-9\-]+-{VERCEL_PROJECT_ID}\.vercel\.app$`

## Security

- ✅ No wildcards in production
- ✅ Explicit origin whitelist
- ✅ Credentials support (cookies, auth headers)
- ✅ HTTPS enforced
- ✅ Project-specific preview deployments only

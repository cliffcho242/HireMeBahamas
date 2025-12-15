# Docker $PORT Variable Expansion Fix

## Issue Summary

**Error:** `'$PORT' is not a valid port number.`

**Impact:** Containers failed to start because Docker couldn't properly expand the `${PORT:-8080}` environment variable syntax.

## Root Cause

The original Dockerfiles used shell form for CMD and bare syntax for HEALTHCHECK:

```dockerfile
# ❌ OLD - BROKEN
HEALTHCHECK CMD curl -f http://localhost:${PORT:-8080}/health || exit 1
CMD gunicorn final_backend_postgresql:application --bind 0.0.0.0:${PORT:-8080} --workers 4 ...
```

Docker's shell form doesn't guarantee proper expansion of complex bash parameter expansion syntax like `${PORT:-8080}` in all contexts, causing the literal string `$PORT` to be passed instead of the actual port number.

## Solution

Changed to exec form with explicit shell invocation:

```dockerfile
# ✅ NEW - FIXED
HEALTHCHECK CMD sh -c 'curl -f http://localhost:${PORT:-8080}/health || exit 1'
CMD ["sh", "-c", "gunicorn final_backend_postgresql:application --bind 0.0.0.0:${PORT:-8080} --workers 4 ..."]
```

### Why This Works

1. **HEALTHCHECK**: Using `sh -c '...'` explicitly invokes a shell that properly expands `${PORT:-8080}`
2. **CMD**: Using exec form `["sh", "-c", "..."]` ensures a shell is invoked to handle variable expansion
3. The `${PORT:-default}` syntax provides a default value when PORT is unset or empty

### Variable Expansion Behavior

- **If PORT is set** (e.g., `PORT=9000`): Binds to port 9000
- **If PORT is not set**: Uses default (8080 for main app, 8000 for backend)
- **If PORT is empty**: Uses default value

## Files Modified

1. **`/Dockerfile`** (lines 117-121)
   - Main Flask backend application
   - Default port: 8080
   - Health check endpoint: `/health`

2. **`/backend/Dockerfile`** (lines 26-30)
   - FastAPI backend application
   - Default port: 8000
   - Health check endpoint: `/health`

## Testing the Fix

### Method 1: Build and Run Locally

```bash
# Build the image
docker build -t hiremebahamas:test .

# Run without PORT (uses default 8080)
docker run -p 8080:8080 hiremebahamas:test

# Run with custom PORT
docker run -e PORT=9000 -p 9000:9000 hiremebahamas:test
```

### Method 2: Using Docker Compose

```bash
# Start with default configuration
docker-compose up backend-flask

# The PORT environment variable is already set in docker-compose.yml
```

### Method 3: Verify Syntax

Run the included test script:
```bash
cd /home/runner/work/HireMeBahamas/HireMeBahamas
bash -c "$(cat << 'EOF'
# Verify Dockerfile syntax
grep -q 'CMD \["sh", "-c",' Dockerfile && echo "✅ Main Dockerfile CMD: OK"
grep -q "CMD sh -c 'curl" Dockerfile && echo "✅ Main Dockerfile HEALTHCHECK: OK"
grep -q 'CMD \["sh", "-c",' backend/Dockerfile && echo "✅ Backend Dockerfile CMD: OK"
grep -q "CMD sh -c 'curl" backend/Dockerfile && echo "✅ Backend Dockerfile HEALTHCHECK: OK"
EOF
)"
```

## Deployment Platforms

This fix ensures proper PORT variable expansion on:

- **Render.com**: Automatically sets PORT variable
- **Railway.app**: Automatically sets PORT variable
- **Heroku**: Automatically sets PORT variable
- **Google Cloud Run**: Automatically sets PORT variable
- **AWS ECS/Fargate**: Manual PORT configuration
- **Local Docker/Docker Compose**: Explicit PORT in environment

## Related Configuration

The following files also reference `$PORT` but don't need changes (they use different syntax):

- `Procfile`: Uses shell form `$PORT` which is correctly expanded by the platform
- `docker-compose.yml`: Explicitly sets `PORT: 8080` as environment variable
- `render.yaml`: Uses shell form `$PORT` which Render expands correctly

## Verification

✅ Syntax validated
✅ Both Dockerfiles updated
✅ Default port values preserved
✅ Health check commands updated
✅ No security issues introduced

## Summary

The fix ensures that Docker containers can properly start by using explicit shell invocation to expand the `${PORT:-default}` syntax. This is a minimal, surgical change that resolves the startup error without affecting any other functionality.

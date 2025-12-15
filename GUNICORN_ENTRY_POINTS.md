# Gunicorn/Uvicorn Entry Points Reference

## Overview

This document provides the correct entry points for starting HireMeBahamas backend with Gunicorn (Flask) or Uvicorn (FastAPI).

## ⚠️ Critical Warnings

### Recommended Entry Points

For this project, use these **recommended** entry points:
- **FastAPI:** `app.main:app` or `api.backend_app.main:app`
- **Flask:** `final_backend_postgresql:application`

**Note:** While `app:app` technically exists as a wrapper, it's **not recommended** because:
- It's ambiguous (could be Flask or FastAPI)
- Less clear than the direct entry points
- May cause confusion in debugging

### Single-Line Commands for Deployment Dashboards

**IMPORTANT:** When configuring deployment platforms (Render, Railway, Heroku, etc.) through their web dashboard:
- **ALWAYS use single-line commands** (no backslashes or line breaks)
- Multi-line commands with `\` are ONLY for shell scripts
- Copy-pasting multi-line commands into dashboard fields will cause parsing errors

**Example of ERROR:**
```
# ❌ WRONG - Multi-line with backslashes will fail in deployment dashboards
gunicorn app.main:app \
  --bind 0.0.0.0:$PORT \
  --workers 2
```

**Correct approach:**
```
# ✅ CORRECT - Single line for deployment dashboards
gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 2
```

## Flask Backend (Gunicorn)

The Flask backend is defined in `final_backend_postgresql.py` and provides a traditional WSGI application.

### Recommended Entry Point

**For Deployment Dashboards (Render, Railway, Heroku) - SINGLE LINE:**
```bash
gunicorn final_backend_postgresql:application --config gunicorn.conf.py --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --graceful-timeout 30 --log-level info
```

**For Shell Scripts - Multi-line (with backslashes):**
```bash
gunicorn final_backend_postgresql:application \
  --config gunicorn.conf.py \
  --bind 0.0.0.0:$PORT \
  --workers 2 \
  --timeout 120 \
  --graceful-timeout 30 \
  --log-level info
```

**Why `application`?**
- `application` is the WSGI standard name
- Defined at line 10214 of `final_backend_postgresql.py`
- Most compatible with WSGI servers and tools

### Alternative Entry Points

#### Via Wrapper Module

```bash
gunicorn app:application --config gunicorn.conf.py
```

The `app.py` module imports from `final_backend_postgresql`:
```python
from final_backend_postgresql import app, application
```

#### Using Direct App Instance

```bash
gunicorn final_backend_postgresql:app --config gunicorn.conf.py
```

This also works but `application` is preferred for WSGI standard compliance.

## FastAPI Backend (Uvicorn)

The FastAPI backend supports async operations and should use Uvicorn or Gunicorn with Uvicorn workers.

### Recommended Entry Points

#### Option 1: Using Wrapper (Root Directory)

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**When to use:** When running from the repository root directory.

#### Option 2: Direct Import (Recommended for API)

```bash
uvicorn api.backend_app.main:app --host 0.0.0.0 --port $PORT
```

**When to use:** When you want the most direct import path.

#### Option 3: Backend Directory

```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**When to use:** When running from the backend directory (used in render.yaml).

### Using Gunicorn with Uvicorn Workers (Production)

For production deployments, use Gunicorn for worker management with Uvicorn workers:

**For Deployment Dashboards (Render, Railway, Heroku) - SINGLE LINE:**
```bash
gunicorn app.main:app --workers ${WEB_CONCURRENCY:-2} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout ${GUNICORN_TIMEOUT:-120} --preload --log-level info
```

**For Shell Scripts - Multi-line (with backslashes):**
```bash
gunicorn app.main:app \
  --workers ${WEB_CONCURRENCY:-2} \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:$PORT \
  --timeout ${GUNICORN_TIMEOUT:-120} \
  --preload \
  --log-level info
```

## Configuration Files

### render.yaml

```yaml
startCommand: cd backend && gunicorn app.main:app --workers ${WEB_CONCURRENCY:-2} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --preload --log-level info
```

**Entry Point:** `app.main:app` (FastAPI via wrapper)
**Working Directory:** `backend/`

### Procfile

```
web: gunicorn app.main:app --workers ${WEB_CONCURRENCY:-2} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout ${GUNICORN_TIMEOUT:-120} --preload --log-level info
```

**Entry Point:** `app.main:app` (FastAPI via wrapper)
**Working Directory:** Repository root

### start.sh

```bash
exec gunicorn final_backend_postgresql:application \
    --config gunicorn.conf.py
```

**Entry Point:** `final_backend_postgresql:application` (Flask)
**Working Directory:** Repository root

### Dockerfile (Main)

```dockerfile
CMD ["sh", "-c", "uvicorn api.backend_app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --timeout-keep-alive 5 --limit-concurrency 100"]
```

**Entry Point:** `api.backend_app.main:app` (FastAPI direct)

### Dockerfile (Backend)

```dockerfile
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

**Entry Point:** `app.main:app` (FastAPI via wrapper)

### railway.toml

```toml
[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

**Entry Point:** `app.main:app` (FastAPI via wrapper)

### nixpacks.toml

```toml
[start]
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

**Entry Point:** `app.main:app` (FastAPI via wrapper)

## Quick Reference

| Backend | Server | Entry Point | Command |
|---------|--------|-------------|---------|
| Flask | Gunicorn | `final_backend_postgresql:application` | ✅ RECOMMENDED |
| Flask | Gunicorn | `app:application` | ✅ Via wrapper |
| FastAPI | Uvicorn | `app.main:app` | ✅ RECOMMENDED |
| FastAPI | Uvicorn | `api.backend_app.main:app` | ✅ Direct import |
| FastAPI | Gunicorn+Uvicorn | `app.main:app` | ✅ Production |

## Testing Entry Points

Run the validation script to verify all entry points:

```bash
python3 test_gunicorn_entry_points.py
```

This will check:
- ✅ Module files exist
- ✅ Import paths are correct
- ✅ Both Flask and FastAPI entry points

## Common Mistakes

### ❌ DO NOT USE

```bash
# WRONG - app:app is ambiguous
gunicorn app:app

# WRONG - Missing FastAPI import path
gunicorn main:app

# WRONG - Incorrect module name
gunicorn wsgi:app
```

### ✅ CORRECT USAGE

```bash
# For Flask
gunicorn final_backend_postgresql:application --config gunicorn.conf.py

# For FastAPI with Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port $PORT

# For FastAPI with Gunicorn + Uvicorn workers
gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker
```

## Deployment Platform Commands

### Render

**Build Command:**
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

**Start Command (FastAPI):**
```bash
cd backend && gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --preload --log-level info
```

**Start Command (Flask):**
```bash
gunicorn final_backend_postgresql:application --config gunicorn.conf.py
```

### Railway

**Start Command (FastAPI):**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Start Command (Flask):**
```bash
gunicorn final_backend_postgresql:application --config gunicorn.conf.py
```

### Heroku

**Procfile:**
```
web: gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --log-level info
```

## Environment Variables

### Gunicorn Configuration

- `PORT`: Port number (default: 8000 or 10000)
- `WEB_CONCURRENCY`: Number of workers (default: 2)
- `WEB_THREADS`: Threads per worker (default: 4)
- `GUNICORN_TIMEOUT`: Worker timeout in seconds (default: 60 or 120)

### Example

```bash
export PORT=8080
export WEB_CONCURRENCY=4
export GUNICORN_TIMEOUT=120

gunicorn final_backend_postgresql:application --config gunicorn.conf.py
```

## Verification

To verify the correct entry point is being used:

1. **Check logs for startup message:**
   ```
   Starting gunicorn 23.0.0
   Listening at: http://0.0.0.0:8080
   ```

2. **Test health endpoint:**
   ```bash
   curl http://localhost:8080/health
   ```

3. **Expected response:**
   ```json
   {"ok": true}
   ```

## Troubleshooting

### Error: "gunicorn: error: unrecognized arguments"

**Symptoms:**
```
==> Running 'gunicorn app:app \   --bind 0.0.0.0:$PORT \   --workers 2 \   ...'
usage: gunicorn [OPTIONS] [APP_MODULE]
gunicorn: error: unrecognized arguments:        
```

**Cause:** Multi-line command with backslashes was copied into a deployment dashboard field, causing the backslashes and extra whitespace to be treated as literal arguments.

**Solution:**
1. Go to your deployment platform dashboard (Render, Railway, etc.)
2. Find the "Start Command" or "Run Command" field
3. Replace it with a **single-line command** (no backslashes or line breaks)
4. Use one of the recommended commands from this document

**Example Fix for Render:**
- ❌ **Wrong:** Multi-line command copied from documentation
- ✅ **Correct:** `cd backend && gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --preload --log-level info`

**Example Fix for Railway:**
- Use railway.toml or nixpacks.toml instead of manual commands
- Or set single-line command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Error: "ModuleNotFoundError: No module named 'app'"

**Cause:** Working directory mismatch or incorrect module path.

**Solution:**
- If using `app.main:app`, ensure you're in the repository root or backend directory
- If using `api.backend_app.main:app`, ensure you're in the repository root
- Check the `cd backend &&` prefix if running from root directory

### Error: "sh: gunicorn: not found"

**Cause:** Gunicorn not installed or not in PATH.

**Solution:**
- Ensure `gunicorn>=23.0.0` is in requirements.txt
- Run `pip install gunicorn` or `pip install -r requirements.txt`
- Check build logs to confirm gunicorn installation

## Summary

✅ **Flask Backend:** Use `final_backend_postgresql:application`
✅ **FastAPI Backend:** Use `app.main:app` or `api.backend_app.main:app`
✅ **Deployment Dashboards:** Always use single-line commands (no backslashes)
❌ **Never use:** `app:app` for Gunicorn (ambiguous, not standard)
❌ **Never use:** Multi-line commands with `\` in web dashboards

For more information, see:
- `gunicorn.conf.py` - Gunicorn configuration
- `render.yaml` - Render deployment configuration
- `Procfile` - Platform-agnostic process file
- `start.sh` - Custom startup script

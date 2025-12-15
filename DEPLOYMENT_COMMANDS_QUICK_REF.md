# Deployment Commands Quick Reference

## ⚠️ CRITICAL: Command Format for Deployment Platforms

When configuring deployment platforms through their web dashboard:
- **ALWAYS use single-line commands** (no backslashes)
- **NEVER copy multi-line commands** from shell scripts or documentation
- Multi-line commands with `\` only work in shell scripts, not in web UI fields

## Start Commands by Platform

### Render

**In Render Dashboard → Settings → Start Command:**
```
cd backend && gunicorn app.main:app --workers ${WEB_CONCURRENCY:-2} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --preload --log-level info
```

**Or use render.yaml (recommended)** - already configured correctly in the repository.

### Railway

**Option 1: Use railway.toml (recommended)** - already configured correctly in the repository.

**Option 2: In Railway Dashboard → Settings → Start Command:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Heroku

**Use Procfile (recommended)** - already configured correctly in the repository.

**Or in Heroku Dashboard → Settings → Buildpacks → Python → Start Command:**
```
gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --log-level info
```

## Configuration Files (Recommended Approach)

Instead of manually configuring start commands in dashboards, use these configuration files that are already set up correctly:

### For Render: `render.yaml`
Located at: `/render.yaml`
- Automatically detected by Render
- Already configured with correct start command
- No manual configuration needed

### For Railway: `railway.toml`
Located at: `/railway.toml`
- Automatically detected by Railway
- Already configured with correct start command
- No manual configuration needed

### For Heroku: `Procfile`
Located at: `/Procfile` or `/backend/Procfile`
- Automatically detected by Heroku
- Already configured with correct start command
- No manual configuration needed

## Common Mistakes to Avoid

### ❌ WRONG: Multi-line command in dashboard
```
# This will FAIL in deployment dashboards
gunicorn app.main:app \
  --bind 0.0.0.0:$PORT \
  --workers 2
```

**Why it fails:** Backslashes and line breaks are treated as literal characters, causing "unrecognized arguments" error.

### ⚠️ NOT RECOMMENDED: Using `app:app`
```
gunicorn app:app --bind 0.0.0.0:$PORT
```

**Why not recommended:** While `app:app` technically works as a wrapper, it's ambiguous and less clear than using the direct entry points (`app.main:app` for FastAPI or `final_backend_postgresql:application` for Flask).

### ✅ CORRECT: Single-line command
```
gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --log-level info
```

**Why it works:** Single line, correct module path, proper arguments.

### ✅ CORRECT: Use configuration files
Just deploy the repository as-is. The configuration files (`render.yaml`, `railway.toml`, `Procfile`) are already set up correctly.

## Backend Options

This project supports two backend implementations:

### Option 1: FastAPI (Recommended - Current Default)
- Modern async framework
- Better performance
- Located at: `app.main:app` or `api.backend_app.main:app`

**Start command:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**With Gunicorn (production):**
```
gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### Option 2: Flask (Legacy)
- Traditional WSGI framework
- Located at: `final_backend_postgresql.py`

**Start command:**
```
gunicorn final_backend_postgresql:application --config gunicorn.conf.py
```

## Environment Variables

Required environment variables (set in platform dashboard):

```
DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
FRONTEND_URL=https://your-frontend.vercel.app
ENVIRONMENT=production
```

Optional performance tuning:
```
WEB_CONCURRENCY=2          # Number of worker processes
WEB_THREADS=4              # Threads per worker
GUNICORN_TIMEOUT=60        # Request timeout in seconds
PORT=8000                  # Port (usually auto-set by platform)
```

## Testing Locally

To test the start command locally before deploying:

### Test FastAPI with Uvicorn:
```bash
export PORT=8000
export DATABASE_URL="postgresql://..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Test FastAPI with Gunicorn:
```bash
export PORT=8000
export DATABASE_URL="postgresql://..."
gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### Test Flask:
```bash
export PORT=8000
export DATABASE_URL="postgresql://..."
gunicorn final_backend_postgresql:application --config gunicorn.conf.py
```

Then test the health endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

## Troubleshooting

### Error: "unrecognized arguments"
**Cause:** Multi-line command with backslashes in dashboard field.
**Fix:** Use single-line command (see examples above) or use configuration files.
**Details:** See [GUNICORN_ARGS_ERROR_FIX.md](./GUNICORN_ARGS_ERROR_FIX.md)

### Error: "ModuleNotFoundError: No module named 'app'"
**Cause:** Wrong working directory or incorrect module path.
**Fix:** Use `cd backend &&` prefix or check configuration files.

### Error: "sh: gunicorn: not found"
**Cause:** Gunicorn not installed.
**Fix:** Ensure `gunicorn` is in `requirements.txt` and build command runs `pip install -r requirements.txt`.

## More Information

- [GUNICORN_ENTRY_POINTS.md](./GUNICORN_ENTRY_POINTS.md) - Detailed entry points reference
- [GUNICORN_ARGS_ERROR_FIX.md](./GUNICORN_ARGS_ERROR_FIX.md) - Fix for "unrecognized arguments" error
- [render.yaml](./render.yaml) - Render configuration
- [railway.toml](./railway.toml) - Railway configuration
- [Procfile](./Procfile) - Platform-agnostic configuration

## Quick Decision Tree

```
Are you deploying to...?

├─ Render?
│  └─ Just use render.yaml (already configured) ✅
│
├─ Railway?
│  └─ Just use railway.toml (already configured) ✅
│
├─ Heroku?
│  └─ Just use Procfile (already configured) ✅
│
└─ Other platform?
   └─ Use single-line command:
      uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Bottom line:** The configuration files are already set up correctly. Just deploy the repository and let the platform auto-detect the configuration!

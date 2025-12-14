# Render Quick Fix Guide

## ❌ Error: "gunicorn: command not found"

### Quick Solution (Copy-Paste)

**In Render Dashboard:**

1. **Build Command:**
   ```bash
   bash build.sh
   ```

2. **Start Command:**
   ```bash
   gunicorn final_backend_postgresql:application --config gunicorn.conf.py --preload
   ```

### Files Required

Make sure these files exist in your repository:
- ✅ `build.sh` (executable)
- ✅ `requirements.txt` (contains gunicorn==23.0.0)
- ✅ `gunicorn.conf.py`
- ✅ `final_backend_postgresql.py`

### Verify Files

```bash
# Check files exist
ls -l build.sh requirements.txt gunicorn.conf.py final_backend_postgresql.py

# Verify gunicorn in requirements
grep gunicorn requirements.txt
```

## ❌ Error: "bash: build.sh: No such file or directory"

### Solution

```bash
# Make sure build.sh is committed
git add build.sh
git commit -m "Add build script"
git push
```

## ❌ Error: Build succeeds but start fails

### Check Environment Variables

Required environment variables in Render dashboard:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Random secret key
- `FRONTEND_URL` - Your frontend URL
- `PYTHON_VERSION` - 3.12.0

### Quick Test

```bash
# Test locally first
bash build.sh
gunicorn final_backend_postgresql:application --check-config --config gunicorn.conf.py
```

## 🎯 Complete Render Setup (Step-by-Step)

### 1. Prepare Repository

```bash
# Ensure all files are committed
git add build.sh render.yaml .render-buildpacks.json
git commit -m "Fix Render build configuration"
git push origin main
```

### 2. Create New Web Service in Render

- **Name**: hiremebahamas-backend
- **Region**: Oregon (or closest to you)
- **Branch**: main
- **Root Directory**: Leave blank (use repository root)
- **Runtime**: Python 3
- **Build Command**: `bash build.sh`
- **Start Command**: `gunicorn final_backend_postgresql:application --config gunicorn.conf.py --preload`

### 3. Configure Environment Variables

Add these in Render dashboard:

```env
PYTHON_VERSION=3.12.0
ENVIRONMENT=production
SECRET_KEY=[Generate random key]
FRONTEND_URL=https://hiremebahamas.vercel.app
DATABASE_URL=[Your PostgreSQL URL]
WEB_CONCURRENCY=1
GUNICORN_TIMEOUT=120
PYTHONUNBUFFERED=true
```

### 4. Deploy

Click "Create Web Service" and watch the logs!

## 📊 Expected Build Output

```
🔧 HireMeBahamas Build Script Starting...
========================================
📦 Upgrading pip, setuptools, and wheel...
📦 Installing dependencies from requirements.txt...
✅ Verifying gunicorn installation...
✅ gunicorn found: /opt/render/project/src/.venv/bin/gunicorn
✅ gunicorn version: gunicorn (version 23.0.0)
========================================
✅ Build completed successfully!
🚀 Ready to start application with gunicorn
```

## 🔍 Debugging Tips

### View Build Logs

1. Go to Render dashboard
2. Click on your service
3. Click "Logs" tab
4. Look for errors in red

### Test Health Endpoint

```bash
# After deployment succeeds
curl https://your-app.onrender.com/health

# Expected response
{"status":"healthy","timestamp":"2025-12-14T12:00:00Z"}
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "command not found" | Run `bash build.sh` as build command |
| "ModuleNotFoundError" | Check requirements.txt has all dependencies |
| "Database connection failed" | Verify DATABASE_URL is set correctly |
| "502 Bad Gateway" | Check start command and health endpoint |

## 📚 Additional Resources

- Full guide: `RENDER_BUILD_FIX.md`
- Migration guide: `RENDER_TO_VERCEL_MIGRATION.md`
- Render Python docs: https://render.com/docs/deploy-python

## ⚠️ Important Note

Render deployment is **deprecated** for this project. The recommended stack is:
- **Frontend**: Vercel
- **Backend**: Railway
- **Database**: Railway PostgreSQL

See `RENDER_TO_VERCEL_MIGRATION.md` for migration instructions.

Use Render only if you have a specific reason to do so.

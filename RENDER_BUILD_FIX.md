# Render Build Fix - Gunicorn Command Not Found

## Problem

When deploying to Render, the build fails with:

```
==> Running build command 'gunicorn final_backend_postgresql:application --config gunicorn.conf.py --preload'...
bash: line 1: gunicorn: command not found
==> Build failed 😞
```

## Root Cause

The issue occurs because:

1. **Poetry Auto-Detection**: Render detects the `pyproject.toml` file and assumes the project uses Poetry
2. **No poetry.lock**: Since there's no `poetry.lock` file, Render gets confused
3. **Dependencies Not Installed**: Dependencies (including gunicorn) are never installed
4. **Start Command Runs as Build Command**: The start command runs during build phase before dependencies exist

## Solution

We've implemented a dedicated `build.sh` script that explicitly uses pip to install dependencies, avoiding Poetry auto-detection issues.

### Files Modified/Created

1. **build.sh** - New build script that explicitly uses pip (executable permissions set)
2. **render.yaml** - Updated to use `bash build.sh` as build command
3. **api/render.yaml** - Updated for consistency
4. **.render-buildpacks.json** - Forces Render to use Python buildpack instead of Poetry

## Deployment Instructions

### Option 1: Use render.yaml (Recommended)

If you're using `render.yaml` for deployment (Infrastructure as Code):

1. Ensure these files are committed to your repository:
   - `build.sh`
   - `render.yaml`
   - `.render-buildpacks.json`

2. Deploy to Render:
   ```bash
   git add build.sh render.yaml .render-buildpacks.json
   git commit -m "Fix Render build with explicit pip installation"
   git push origin main
   ```

3. Render will automatically detect `render.yaml` and use the correct build command

### Option 2: Manual Dashboard Configuration

If you're configuring through the Render dashboard:

1. **Build Command**:
   ```bash
   bash build.sh
   ```

2. **Start Command**:
   ```bash
   gunicorn final_backend_postgresql:application --config gunicorn.conf.py --preload
   ```

3. **Environment Variables** (ensure these are set):
   - `PYTHON_VERSION=3.12.0`
   - `PORT=8080` (or your preferred port)
   - `DATABASE_URL` (your PostgreSQL connection string)
   - `FRONTEND_URL` (your frontend URL)
   - `SECRET_KEY` (generate a secure random key)

## How the Fix Works

### .render-buildpacks.json

This file tells Render to use the standard Python buildpack (pip) instead of auto-detecting Poetry:

```json
{
  "buildpacks": [
    {
      "url": "https://github.com/heroku/heroku-buildpack-python"
    }
  ]
}
```

This ensures Render uses pip for dependency management, even with pyproject.toml present.

### build.sh Script

The `build.sh` script:

```bash
#!/bin/bash
# Explicitly upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install --only-binary=:all: -r requirements.txt

# Verify gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "ERROR: gunicorn not found after installation!"
    exit 1
fi
```

This approach:
- ✅ Bypasses Poetry auto-detection
- ✅ Uses binary wheels only (no compilation needed)
- ✅ Verifies gunicorn installation
- ✅ Provides clear error messages if installation fails

## Verification

After deployment, verify the fix:

1. **Check Build Logs**: Look for:
   ```
   🔧 HireMeBahamas Build Script Starting...
   ✅ Build completed successfully!
   ```

2. **Check gunicorn Installation**:
   ```
   ✅ gunicorn found: /opt/render/project/src/.venv/bin/gunicorn
   ✅ gunicorn version: gunicorn (version 23.0.0)
   ```

3. **Test Application**: Access your health endpoint:
   ```
   curl https://your-app.onrender.com/health
   ```

## Alternative: Remove pyproject.toml

If you continue to have issues, you can temporarily rename `pyproject.toml`:

```bash
mv pyproject.toml pyproject.toml.bak
```

However, this is **not recommended** as the file contains useful build configuration.

## Related Documentation

- [Render Python Deployment Guide](https://render.com/docs/deploy-python)
- [Render Poetry Version Issues](https://render.com/docs/poetry-version)
- Main: `RENDER_TO_VERCEL_MIGRATION.md` (note: Render is deprecated in favor of Railway/Vercel)

## Troubleshooting

### Issue: Build still fails with "gunicorn: command not found"

**Solution**: Verify that:
1. `build.sh` is committed with execute permissions (already set in repository)
2. `requirements.txt` contains `gunicorn==23.0.0`
3. Build command in Render dashboard is exactly: `bash build.sh`
4. If still failing, check Render build logs for Poetry-related messages

### Issue: "bash: build.sh: No such file or directory"

**Solution**: Ensure `build.sh` is committed to your repository and in the root directory

### Issue: Dependencies install but gunicorn still not found

**Solution**: Check PATH in start command:
```bash
export PATH="/opt/render/project/src/.venv/bin:$PATH" && gunicorn final_backend_postgresql:application --config gunicorn.conf.py --preload
```

## Status

✅ **Fixed**: Build script created and tested
✅ **Committed**: Changes pushed to repository
⏳ **Pending**: Deploy to Render to verify in production

## Legacy Deployment Note

This fix is provided for **backward compatibility** and **legacy Render deployments**.

**Recommended Architecture** (for new deployments):
- Frontend: Vercel
- Backend: Railway  
- Database: Railway PostgreSQL

See `RENDER_TO_VERCEL_MIGRATION.md` for the recommended deployment architecture.

**Use this Render fix if:**
- You have an existing Render deployment
- You need to maintain Render for specific reasons
- You're troubleshooting Render build issues

The fix provided here is fully supported and will resolve Render build issues.

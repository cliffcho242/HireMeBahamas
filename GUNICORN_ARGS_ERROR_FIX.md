# Fix: Gunicorn Unrecognized Arguments Error

## Problem

Deployment fails with "gunicorn: error: unrecognized arguments"

## Root Cause

The deployment platform (Render, Railway, or Heroku) has a **multi-line command with backslashes** configured in the "Start Command" field. When this command is executed, the backslashes (`\`) and extra whitespace are treated as **literal arguments** instead of line continuation characters, causing gunicorn to fail with "unrecognized arguments".

## Why This Happens

Multi-line shell commands with backslashes are valid in:
- ✅ Shell scripts (.sh files)
- ✅ Terminal/command line
- ✅ Dockerfile RUN commands
- ✅ Documentation examples

But they **DO NOT work** in:
- ❌ Deployment platform web dashboards (Render, Railway, Heroku)
- ❌ YAML string values (unless properly escaped)
- ❌ JSON string values
- ❌ Environment variable values

## Solution

### Step 1: Identify Your Deployment Platform

Check where your application is deployed:
- **Render**: Dashboard at https://dashboard.render.com
- **Railway**: Dashboard at https://railway.app
- **Heroku**: Dashboard at https://dashboard.heroku.com

### Step 2: Update Start Command

Go to your service settings and replace the multi-line command with a **single-line command**:

#### For FastAPI (Recommended)

**Render - Start Command:**
```bash
cd backend && gunicorn app.main:app --workers ${WEB_CONCURRENCY:-2} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --preload --log-level info
```

**Railway - Use railway.toml or set Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Heroku - Update Procfile:**
```
web: gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --log-level info
```

#### For Flask

**Render - Start Command:**
```bash
gunicorn final_backend_postgresql:application --config gunicorn.conf.py --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level info
```

**Railway - Start Command:**
```bash
gunicorn final_backend_postgresql:application --config gunicorn.conf.py
```

### Step 3: Redeploy

After updating the start command:
1. Click "Manual Deploy" or trigger a redeploy
2. Monitor the deployment logs
3. Verify the service starts successfully

## Additional Issues to Check

### Issue 1: Using Non-Recommended App Module

The error may show `gunicorn app:app` which, while technically valid as a wrapper, is **not recommended** for this project.

**Fix:** Use the recommended entry points:
- For FastAPI: `app.main:app` (recommended)
- For Flask: `final_backend_postgresql:application` (recommended)
- `app:app` works but is less clear and harder to debug

### Issue 2: Command Arguments Appearing on Separate Lines

When you see the command with extra spacing or arguments on separate lines, it means backslashes are being interpreted literally.

**Fix:** Ensure the command is a single line with no backslashes when configuring in deployment dashboards

### Issue 3: Using Gunicorn Instead of Uvicorn

If you're running FastAPI and using plain Gunicorn (not with Uvicorn workers), you'll have issues.

**Fix:** Use one of these:
- `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (simple)
- `gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT` (with workers)

## Platform-Specific Instructions

### Render Dashboard

1. Go to https://dashboard.render.com
2. Select your backend service
3. Click "Settings" in the left sidebar
4. Scroll to "Build & Deploy"
5. Find "Start Command" field
6. Replace with the single-line command (see examples above)
7. Click "Save Changes"
8. Go to "Manual Deploy" → "Deploy latest commit"

### Railway Dashboard

1. Go to https://railway.app
2. Select your project
3. Click on the backend service
4. Go to "Settings" tab
5. Look for "Start Command" or check `railway.toml` file
6. Update to single-line command (see examples above)
7. Redeploy the service

### Using Configuration Files (Recommended)

Instead of setting commands in the dashboard, use configuration files:

**render.yaml** (already configured correctly):
```yaml
services:
  - type: web
    name: hiremebahamas-backend
    runtime: python
    startCommand: cd backend && gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --preload --log-level info
```

**railway.toml** (already configured correctly):
```toml
[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

**Procfile** (already configured correctly):
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --log-level info
```

## Verification

After fixing the command and redeploying:

1. **Check Deployment Logs**
   - Look for: `Starting gunicorn 23.0.0` or `Started server process`
   - Should NOT see: `unrecognized arguments`

2. **Test Health Endpoint**
   ```bash
   curl https://your-app-url.onrender.com/health
   ```
   
   Expected response:
   ```json
   {"status": "healthy"}
   ```

3. **Check Service Status**
   - Service should show as "Live" or "Running"
   - No restart loops
   - Response time < 1 second

## Prevention

To prevent this issue in the future:

1. ✅ **Always use single-line commands in deployment dashboards**
2. ✅ **Use configuration files (render.yaml, railway.toml, Procfile)**
3. ✅ **Test commands locally first**: `python -c "import app.main"`
4. ✅ **Check GUNICORN_ENTRY_POINTS.md for correct commands**
5. ❌ **Never copy multi-line commands with `\` into web dashboards**

## Related Documentation

- [GUNICORN_ENTRY_POINTS.md](./GUNICORN_ENTRY_POINTS.md) - Complete entry points reference
- [render.yaml](./render.yaml) - Render configuration (already correct)
- [railway.toml](./railway.toml) - Railway configuration (already correct)
- [Procfile](./Procfile) - Platform-agnostic configuration (already correct)

## Quick Checklist

- [ ] Identified deployment platform (Render/Railway/Heroku)
- [ ] Updated start command to single-line format
- [ ] Used correct entry point (`app.main:app` for FastAPI, `final_backend_postgresql:application` for Flask)
- [ ] Removed any backslashes or line breaks from command
- [ ] Saved changes and redeployed
- [ ] Verified service is running
- [ ] Tested health endpoint
- [ ] Checked logs for successful startup

## Still Having Issues?

If the error persists after following this guide:

1. Share the exact start command you're using
2. Share the complete deployment logs
3. Confirm which platform you're deploying to
4. Check if you're using configuration files (render.yaml, railway.toml) or dashboard settings

The issue is almost always that a multi-line command with backslashes is being used in a context where it should be a single-line command.

# Deployment Command Checklist

Use this checklist before deploying to prevent gunicorn and other command-related errors.

## Pre-Deployment Validation

### 1. Run Validation Scripts

```bash
# Validate gunicorn commands
python3 test_gunicorn_commands.py

# Check deployment configuration
python3 validate_deployment_config.py  # if available
```

### 2. Check Configuration Files

#### Procfile (Heroku/Railway)
- [ ] Commands are on a single line
- [ ] No backslashes (`\`) for line continuation
- [ ] No `--preload` flag (conflicts with gunicorn.conf.py)
- [ ] Environment variables use proper syntax: `${VAR:-default}`
- [ ] No extra spaces or hidden characters

**Valid example:**
```
web: gunicorn app.main:app --workers ${WEB_CONCURRENCY:-3} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout ${GUNICORN_TIMEOUT:-120} --log-level info
```

#### render.yaml (Render)
- [ ] `startCommand` is on a single line
- [ ] No backslashes in the command
- [ ] No `--preload` flag
- [ ] Uses `cd backend &&` if needed for directory change
- [ ] No trailing whitespace after command

**Valid example:**
```yaml
startCommand: cd backend && gunicorn app.main:app --workers ${WEB_CONCURRENCY:-3} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --log-level info
```

#### railway.toml (Railway)
- [ ] `startCommand` uses correct syntax
- [ ] Path to app module is correct
- [ ] No conflicting settings

**Valid example:**
```toml
[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

### 3. Check gunicorn.conf.py

- [ ] `preload_app = False` is set (database safety)
- [ ] Worker and thread counts are appropriate
- [ ] Timeout values are reasonable (60-120 seconds)
- [ ] No syntax errors in Python configuration

### 4. Environment Variables

Verify these environment variables are set correctly in your deployment platform:

- [ ] `PORT` - Should be set by platform (Railway/Render sets this automatically)
- [ ] `DATABASE_URL` - Must be valid PostgreSQL connection string
- [ ] `SECRET_KEY` - Must be a secure random string
- [ ] `JWT_SECRET_KEY` - Must be a secure random string  
- [ ] `WEB_CONCURRENCY` - Should be a number (2-4 typically)
- [ ] `GUNICORN_TIMEOUT` - Should be a number in seconds (60-120)
- [ ] `ENVIRONMENT` - Should be "production"

**Check for common issues:**
- [ ] No extra text in numeric variables (WEB_CONCURRENCY, GUNICORN_TIMEOUT)
- [ ] No quotes around DATABASE_URL (platform adds them if needed)
- [ ] No trailing whitespace in any variable

### 5. Platform-Specific Checks

#### Render Dashboard
1. [ ] Go to Settings → Build & Deploy
2. [ ] Check "Start Command" field
3. [ ] Verify it matches render.yaml OR is empty (to use render.yaml)
4. [ ] No multi-line commands with backslashes

#### Railway Dashboard  
1. [ ] Go to service → Settings
2. [ ] Check "Custom Start Command" (if set)
3. [ ] Verify it matches railway.toml OR is empty (to use railway.toml)
4. [ ] Check "Environment Variables" tab for correctness

#### Heroku Dashboard
1. [ ] Verify Procfile in repository is correct
2. [ ] Check Config Vars for typos or extra text
3. [ ] No custom buildpack configurations that might override Procfile

## Common Mistakes to Avoid

### ❌ Don't Do This

**Multi-line commands in web forms:**
```
# WRONG - backslashes don't work in web form fields
gunicorn app.main:app \
  --workers 3 \
  --bind 0.0.0.0:$PORT
```

**Using --preload on command line:**
```
# WRONG - conflicts with gunicorn.conf.py
gunicorn app.main:app --workers 3 --preload
```

**Extra text in commands:**
```
# WRONG - comments or notes become arguments
gunicorn app.main:app --workers 3  # TODO: increase workers
gunicorn app.main:app --workers 3  Master fix asap!
```

**Wrong module paths:**
```
# WRONG - ambiguous or incorrect
gunicorn app:app
gunicorn backend.app:app
```

### ✅ Do This Instead

**Single-line commands:**
```
# CORRECT
gunicorn app.main:app --workers 3 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

**Let config file handle preload:**
```
# CORRECT - gunicorn.conf.py sets preload_app = False
gunicorn app.main:app --workers 3 --bind 0.0.0.0:$PORT
```

**Use configuration files for complex settings:**
```
# CORRECT - simple command, complex settings in gunicorn.conf.py
gunicorn app.main:app --config gunicorn.conf.py
```

**Clear module paths:**
```
# CORRECT - explicit and unambiguous
gunicorn app.main:app
```

## Post-Deployment Verification

After deploying, verify everything works:

### 1. Check Deployment Logs
```bash
# Look for successful startup messages
# Should see: "Starting gunicorn" and "Listening at: http://..."
```

### 2. Test Health Endpoint
```bash
# Replace with your actual URL
curl https://your-app.onrender.com/health
# Should return: {"status":"healthy"}
```

### 3. Monitor for Errors
- [ ] No "unrecognized arguments" errors in logs
- [ ] No worker crashes
- [ ] Health checks passing
- [ ] API endpoints responding

## Quick Troubleshooting

If deployment fails:

1. **Check the exact error message** in deployment logs
2. **Verify command syntax** using validation script
3. **Compare with working examples** in this guide
4. **Check platform settings** in web dashboard
5. **Review environment variables** for typos or extra text

## Reference Documentation

- [GUNICORN_ARGS_FIX_GUIDE.md](./GUNICORN_ARGS_FIX_GUIDE.md) - Comprehensive troubleshooting
- [FIX_RENDER_GUNICORN_ERROR.md](./FIX_RENDER_GUNICORN_ERROR.md) - Render-specific fixes
- [gunicorn.conf.py](./gunicorn.conf.py) - Configuration reference

## Validation Commands

```bash
# Before committing changes
python3 test_gunicorn_commands.py

# Check for trailing whitespace
git diff --check

# View commands exactly as they are
cat -A Procfile | grep "web:"

# Test gunicorn locally (requires dependencies)
cd backend && gunicorn app.main:app --workers 1 --bind 127.0.0.1:8000 --check-config
```

## Success Criteria

Your deployment is ready when:

- [x] All validation scripts pass
- [x] No backslashes in web form commands
- [x] No `--preload` flag in commands (uses gunicorn.conf.py instead)
- [x] Environment variables are correct (no extra text)
- [x] Module paths are explicit (`app.main:app`)
- [x] Commands are single lines in YAML/config files
- [x] Platform dashboard settings match repository files (or are empty)

---

**Remember:** When in doubt, use the validation script: `python3 test_gunicorn_commands.py`

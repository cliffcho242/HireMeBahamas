# Gunicorn Arguments Error Fix Guide

## Problem

If you encounter an error like:
```
usage: gunicorn [OPTIONS] [APP_MODULE]
gunicorn: error: unrecognized arguments: <some unexpected text>
```

This guide will help you identify and fix the issue.

## Common Causes

### 1. Invalid Arguments in Configuration Files

**Symptoms:**
- Gunicorn reports "unrecognized arguments"
- Deployment fails with argument parsing errors
- Extra text appears in error messages

**Fix:**
Check these files for invalid gunicorn arguments:
- `Procfile` (root and backend/)
- `render.yaml`
- `railway.toml`
- `start.sh` or other startup scripts

### 2. --preload Flag Conflicts

**Issue:**
Using `--preload` on the command line overrides the safer `preload_app = False` setting in `gunicorn.conf.py`.

**Why this matters:**
- Database connection pools cannot be safely shared across fork()
- Each worker needs its own database connections
- Can cause health check failures during initialization

**Fix:**
Remove `--preload` from all gunicorn commands. The configuration is already set in `gunicorn.conf.py`.

**Example:**
```bash
# ❌ UNSAFE - Don't use --preload
gunicorn app.main:app --workers 3 --preload --bind 0.0.0.0:8000

# ✅ SAFE - Let gunicorn.conf.py handle preload settings
gunicorn app.main:app --workers 3 --bind 0.0.0.0:8000
```

### 3. Hidden Characters or Formatting Issues

**Symptoms:**
- Command looks correct but fails
- Copy-pasted commands don't work

**Fix:**
1. Check for invisible characters:
   ```bash
   cat -A Procfile | grep "web:"
   ```
2. Look for trailing whitespace or special characters
3. Ensure commands are on a single line (especially in YAML files)

### 4. Deployment Platform Configuration

**Issue:**
Extra text or commands added in the deployment platform's web dashboard.

**Check these locations:**

#### Railway
1. Go to your service settings
2. Check "Custom Start Command"
3. Ensure it matches your Procfile or uses the default

#### Render
1. Go to your web service settings
2. Check "Start Command" under Settings
3. Should match `render.yaml` or be left empty to use the file

#### Heroku
1. Run: `heroku config -a your-app-name`
2. Look for custom `START_COMMAND` or similar variables

### 5. Environment Variables

**Issue:**
Environment variables with extra text being interpolated into commands.

**Check:**
```bash
# Check all environment variables
heroku config  # For Heroku
railway variables # For Railway
# Or check in your platform's dashboard
```

Look for variables like:
- `START_COMMAND`
- `GUNICORN_CMD_ARGS`
- `WEB_CONCURRENCY` (should be a number)
- `GUNICORN_TIMEOUT` (should be a number)

## Validation

### Test Your Configuration

Run the validation script:
```bash
python3 test_gunicorn_commands.py
```

This will check all gunicorn commands in your configuration files.

### Manual Syntax Check

Valid gunicorn command structure:
```bash
gunicorn [APP_MODULE] [OPTIONS]
```

Valid options include:
- `--workers N` or `-w N`
- `--worker-class CLASS` or `-k CLASS`
- `--bind ADDRESS` or `-b ADDRESS`
- `--timeout SECONDS` or `-t SECONDS`
- `--log-level LEVEL`
- `--config FILE` or `-c FILE`

### Common Valid Commands

**For FastAPI with Uvicorn workers:**
```bash
gunicorn app.main:app \
  --workers 3 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --log-level info
```

**With environment variables:**
```bash
gunicorn app.main:app \
  --workers ${WEB_CONCURRENCY:-3} \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:$PORT \
  --timeout ${GUNICORN_TIMEOUT:-120} \
  --log-level info
```

**With config file (recommended):**
```bash
gunicorn app.main:app --config gunicorn.conf.py
```

## Best Practices

1. **Use a config file**: Put complex settings in `gunicorn.conf.py` instead of command-line flags
2. **Keep commands simple**: Use environment variables for values that change between environments
3. **Test locally**: Run gunicorn commands locally before deploying
4. **Validate syntax**: Use the test script to catch issues early
5. **Document changes**: Keep this guide updated when modifying gunicorn configuration

## Quick Reference

### Files to Check
- [ ] `Procfile` (root)
- [ ] `backend/Procfile`
- [ ] `render.yaml`
- [ ] `railway.toml`
- [ ] `gunicorn.conf.py`
- [ ] Deployment platform dashboard settings

### Common Fixes
- [ ] Remove `--preload` flag from commands
- [ ] Verify no extra text in commands
- [ ] Check environment variables are numbers where expected
- [ ] Ensure commands are on single lines in YAML files
- [ ] Clear any custom start commands in platform dashboard

## Getting Help

If you've checked everything and still have issues:

1. Run the validation script and save the output
2. Check the deployment logs for the exact error message
3. Verify your deployment platform settings
4. Look for any custom environment variables that might affect the command

## Related Files

- `gunicorn.conf.py` - Main Gunicorn configuration
- `test_gunicorn_commands.py` - Validation script
- `Procfile` - Heroku/Railway start command
- `render.yaml` - Render deployment configuration
- `FIX_RENDER_GUNICORN_ERROR.md` - Render-specific fixes

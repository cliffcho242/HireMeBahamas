# Vercel Python Runtime Fix (December 2025)

## Problem
Vercel serverless functions were failing with:
```
ModuleNotFoundError: No module named 'fastapi'
```

This caused 500 errors on all `/api/*` endpoints.

## Root Cause
The `vercel.json` configuration was using the **legacy `builds` configuration** with `@vercel/python` builder:

```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ]
}
```

This legacy approach was not properly installing dependencies from `api/requirements.txt` into the Lambda runtime environment.

## Solution
Updated to use **modern automatic function detection**:

```json
{
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.12",
      "maxDuration": 30
    }
  }
}
```

### Key Changes:
1. ✅ **Removed** legacy `builds` array
2. ✅ **Added** modern `functions` configuration with:
   - Pattern matching: `api/**/*.py` (auto-detects all Python files in api/)
   - Explicit runtime: `python3.12` (matches `runtime.txt`)
   - Duration limit: 30 seconds max

## How It Works

### Before (Legacy - BROKEN):
- Vercel used `@vercel/python` builder explicitly
- Dependencies may not install correctly
- Runtime environment missing packages

### After (Modern - WORKING):
- Vercel auto-detects Python files in `api/` directory  
- Automatically reads `api/requirements.txt`
- Installs all dependencies in Lambda runtime
- Uses Python 3.12 as specified

## File Specifications

### runtime.txt (Project Root)
```
python-3.12.0
```
Format: `python-X.Y.Z` (full version with patch)

### vercel.json - functions.runtime
```json
{
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.12"
    }
  }
}
```
Format: `pythonX.Y` (major.minor only, NO patch version)

**Important:** These are different formats per Vercel's specification!

## Verification Steps

1. **Check JSON syntax:**
   ```bash
   python3 -c "import json; json.load(open('vercel.json'))"
   ```

2. **Test imports locally:**
   ```bash
   pip3 install fastapi mangum
   python3 -c "from fastapi import FastAPI; print('✓ OK')"
   ```

3. **Deploy to Vercel:**
   - Push changes to GitHub
   - Vercel automatically redeploys
   - Check deployment logs for dependency installation

4. **Test endpoints:**
   ```bash
   curl https://your-domain.vercel.app/api/health
   ```

## Expected Outcome
After deployment:
- ✅ All dependencies installed correctly
- ✅ FastAPI imports successfully
- ✅ API endpoints return 200 OK (not 500 errors)
- ✅ `/api/health` shows backend status

## References
- [Vercel Python Runtime Documentation](https://vercel.com/docs/functions/runtimes/python)
- [Vercel Functions Configuration](https://vercel.com/docs/projects/project-configuration)
- Related PR: #[PR_NUMBER]

## Date
Fixed: December 5, 2025

# Quick Reference: Vercel Python Deployment

## ✅ Correct Configuration (After Fix)

### runtime.txt
```
python-3.12
```

### vercel.json
```json
{
  "version": 2,
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    },
    "api/cron/*.py": {
      "maxDuration": 30
    }
  },
  "rewrites": [...]
}
```

**Note**: No `builds` array needed - Vercel auto-detects Python files in `/api`

### File Structure
```
/
├── api/
│   ├── index.py              # Main FastAPI app
│   ├── requirements.txt      # ✅ Dependencies here
│   └── cron/
│       └── health.py
├── runtime.txt               # ✅ Python version here
└── vercel.json               # ✅ Configuration here
```

## 🚨 Common Issues & Solutions

### Issue 1: "No module named 'fastapi'"
**Cause**: Dependencies not installed
**Solution**: 
1. Ensure `api/requirements.txt` exists and contains `fastapi`
2. Remove `builds` configuration from `vercel.json`
3. Clear Vercel build cache and redeploy

### Issue 2: "Python version not found"
**Cause**: Incorrect runtime.txt format
**Solution**: Use `python-3.12` not `python-3.12.0`

### Issue 3: "Build failed" or "Function too large"
**Cause**: Too many dependencies or large packages
**Solution**: 
1. Use `--only-binary=:all:` in requirements.txt comments
2. Ensure using binary wheels (no compilation needed)
3. Check for unnecessary dependencies

### Issue 4: "Database connection failed"
**Cause**: Missing environment variables
**Solution**: Set in Vercel dashboard:
- `DATABASE_URL` or `POSTGRES_URL`
- `SECRET_KEY` or `JWT_SECRET_KEY`
- `ENVIRONMENT=production`

## 🔧 Quick Test Commands

### Test locally with Vercel CLI
```bash
vercel dev
```

### Test health endpoint after deployment
```bash
curl https://your-app.vercel.app/api/health
```

### Check Vercel logs
```bash
vercel logs
```

## 📝 Best Practices

✅ **DO**:
- Use `api/requirements.txt` for Python dependencies
- Use `python-X.Y` format in runtime.txt
- Let Vercel auto-detect Python files
- Use `functions` config for settings

❌ **DON'T**:
- Use `builds` array for new projects
- Use `python-X.Y.Z` format in runtime.txt
- Commit `.vercel` directory
- Use compilation-required packages

## 🔗 Quick Links

- [Vercel Python Docs](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Full Fix Documentation](./VERCEL_FASTAPI_FIX_SUMMARY.md)

## 📊 Expected Build Output

Successful Vercel build should show:
```
Installing Python dependencies from api/requirements.txt...
Collecting fastapi==0.115.6
Collecting mangum==0.19.0
...
Successfully installed fastapi-0.115.6 mangum-0.19.0 ...
Build completed
```

If you don't see "Installing Python dependencies", the fix hasn't been applied correctly.

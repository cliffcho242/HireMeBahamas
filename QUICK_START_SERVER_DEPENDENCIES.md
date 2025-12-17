# Quick Start: Server Dependencies Verification

## ⚡ Quick Check

Run this command to verify your server dependencies:

```bash
python validate_server_dependencies.py
```

Expected output:
```
✅ SUCCESS: All server dependencies are properly installed!
```

## 🔧 Quick Fix

If validation fails, run:

```bash
pip install --upgrade pip
pip install --only-binary=:all: -r requirements.txt
```

## 📋 Required Dependencies

These three dependencies are **CRITICAL** and must never be removed:

| Dependency | Version | Purpose |
|------------|---------|---------|
| gunicorn | 23.0.0 | Production WSGI/ASGI server |
| uvicorn[standard] | 0.32.0 | ASGI server with WebSocket |
| fastapi | 0.115.6 | Web framework |

## 🚨 Random Errors Without These

If any of these dependencies are missing, you will experience:

### Missing gunicorn
```
ModuleNotFoundError: No module named 'gunicorn'
ERROR: Failed to start web process
```

### Missing uvicorn
```
ModuleNotFoundError: No module named 'uvicorn'
Cannot run development server
```

### Missing fastapi
```
ModuleNotFoundError: No module named 'fastapi'
All API endpoints fail
```

## ✅ Automated Checks

### CI/CD Validation

Every push automatically validates:
1. Dependencies are present in requirements.txt
2. Correct versions are installed
3. Modules can be imported
4. Basic functionality works

### Local Validation

**Option 1: Run validation script**
```bash
python validate_server_dependencies.py
```

**Option 2: Run test suite**
```bash
pytest tests/test_server_dependencies.py -v
```

## 📚 Full Documentation

For complete details, see [GUNICORN_VERIFICATION.md](GUNICORN_VERIFICATION.md)

## 🆘 Troubleshooting

### Error: "pip install fails"

Try:
```bash
pip install --upgrade pip
pip install --only-binary=:all: -r requirements.txt --force-reinstall
```

### Error: "Tests fail in CI"

1. Check requirements.txt includes all three dependencies
2. Verify versions match expected values
3. Run locally: `pytest tests/test_server_dependencies.py -v`

### Error: "Deployment fails randomly"

This is exactly what these checks prevent! Run:
```bash
python validate_server_dependencies.py
```

If it passes locally but fails in deployment, check:
- Requirements file is being used in deployment
- No cached dependencies causing conflicts
- Platform has Python 3.11+ support

## 📞 Support

See the full verification document for:
- Complete troubleshooting guide
- Deployment configuration examples
- Version upgrade procedures
- Maintenance checklist

➡️ [GUNICORN_VERIFICATION.md](GUNICORN_VERIFICATION.md)

# Gunicorn, Uvicorn, and FastAPI Verification

## Overview

This document verifies that all critical server dependencies are properly installed across all requirements files in the HireMeBahamas project. These dependencies are **CRITICAL** for deployment and must never be removed.

## Critical Dependencies

### 1. **gunicorn==23.0.0**
- **Purpose**: WSGI/ASGI HTTP server for production deployments
- **Why Critical**: Required for Railway and other production deployments
- **Random Errors if Missing**: 
  - `ModuleNotFoundError: No module named 'gunicorn'`
  - Deployment failures on Railway/Render
  - Worker process crashes

### 2. **uvicorn[standard]==0.32.0**
- **Purpose**: ASGI server with WebSocket support
- **Why Critical**: Powers FastAPI applications with async support
- **Random Errors if Missing**:
  - `ModuleNotFoundError: No module named 'uvicorn'`
  - Cannot run FastAPI development server
  - WebSocket functionality breaks

### 3. **fastapi==0.115.6**
- **Purpose**: Modern Python web framework
- **Why Critical**: Core framework for backend API
- **Random Errors if Missing**:
  - `ModuleNotFoundError: No module named 'fastapi'`
  - All API endpoints fail
  - Complete application failure

## Verification Status

✅ **All requirements files have been verified and standardized:**

| File | gunicorn | uvicorn | fastapi | Status |
|------|----------|---------|---------|--------|
| `requirements.txt` | 23.0.0 | 0.32.0 | 0.115.6 | ✅ |
| `requirements_immortal.txt` | 23.0.0 | 0.32.0 | 0.115.6 | ✅ |
| `requirements-psycopg.txt` | 23.0.0 | 0.32.0 | 0.115.6 | ✅ |
| `backend/requirements.txt` | 23.0.0 | 0.32.0 | 0.115.6 | ✅ |
| `backend/requirements_bulletproof.txt` | 23.0.0 | 0.32.0 | 0.115.6 | ✅ |
| `api/requirements.txt` | 23.0.0 | 0.32.0 | 0.115.6 | ✅ |
| `requirements-dev.txt` | Inherited | Inherited | Inherited | ✅ |

## Validation Tools

### 1. Automated Validation Script

Run the validation script to verify dependencies:

```bash
python validate_server_dependencies.py
```

**Expected Output:**
```
✅ SUCCESS: All server dependencies are properly installed!

The following are correctly configured:
   • gunicorn - WSGI/ASGI HTTP server
   • uvicorn - ASGI server with WebSocket support
   • fastapi - Modern Python web framework
```

### 2. Automated Tests

Run the test suite to verify dependencies:

```bash
pytest tests/test_server_dependencies.py -v
```

**Tests Include:**
- ✅ Version verification (minimum versions met)
- ✅ Import verification (modules can be imported)
- ✅ Functionality verification (basic operations work)
- ✅ Consistency verification (all requirements files include dependencies)

## How to Install

### Quick Install (Recommended)

```bash
pip install --upgrade pip
pip install --only-binary=:all: -r requirements.txt
```

### Manual Install (If Needed)

```bash
pip install gunicorn==23.0.0
pip install 'uvicorn[standard]==0.32.0'
pip install fastapi==0.115.6
```

## CI/CD Integration

The GitHub Actions CI workflow automatically verifies these dependencies:

1. **Smoke Tests** - Quick environment check
2. **API Tests** - Installs from `api/requirements.txt`
3. **Backend Tests** - Installs from `requirements.txt`

All workflows use:
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install --only-binary=:all: -r requirements.txt
```

## Deployment Configuration

### Railway (Production)

**Procfile:**
```bash
web: cd backend && PYTHONPATH=. poetry run gunicorn app.main:app \
  --workers 1 --threads 2 --timeout 120 --graceful-timeout 30 \
  --keep-alive 5 --log-level info --config gunicorn.conf.py
```

**Requirements:** Uses `/requirements.txt` ✅

### Vercel (Serverless)

**vercel.json:**
```json
{
  "functions": {
    "api/index.py": {
      "runtime": "python3.12"
    }
  }
}
```

**Requirements:** Uses `/api/requirements.txt` ✅

## Troubleshooting

### Issue: "gunicorn: command not found"

**Solution:**
```bash
pip install gunicorn==23.0.0
```

### Issue: "ModuleNotFoundError: No module named 'uvicorn'"

**Solution:**
```bash
pip install 'uvicorn[standard]==0.32.0'
```

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
pip install fastapi==0.115.6
```

### Issue: Random deployment errors

**Solution:**
1. Run validation script: `python validate_server_dependencies.py`
2. Check test suite: `pytest tests/test_server_dependencies.py -v`
3. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## Maintenance

### Before Deployment Checklist

- [ ] Run validation script: `python validate_server_dependencies.py`
- [ ] Run test suite: `pytest tests/test_server_dependencies.py`
- [ ] Verify CI/CD passes
- [ ] Check deployment logs for import errors

### When Adding New Requirements File

1. Copy dependency versions from `requirements.txt`
2. Ensure gunicorn==23.0.0
3. Ensure uvicorn[standard]==0.32.0
4. Ensure fastapi==0.115.6
5. Run validation: `python validate_server_dependencies.py`
6. Update this document with new file

### When Upgrading Versions

1. Test upgrade in development environment
2. Update ALL requirements files simultaneously
3. Run full test suite
4. Update version table in this document
5. Test deployment on staging before production

## References

- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Railway Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Vercel Deployment Guide](VERCEL_DEPLOYMENT_GUIDE.md)

---

**Last Updated:** December 2024  
**Status:** ✅ All dependencies verified and standardized  
**Next Review:** Before next major deployment

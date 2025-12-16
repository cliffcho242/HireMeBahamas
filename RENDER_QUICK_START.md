# 🚀 Render Deployment Quick Reference - Gunicorn Entrypoint

## ✅ CONFIRMED CORRECT Configuration

**Status:** All configurations verified and tested ✅

---

## 📋 Copy-Paste Guide for Render Dashboard

### Build Command
```bash
pip install poetry && poetry install --only=main
```

### Start Command (COPY THIS EXACT LINE)
```bash
cd backend && poetry run gunicorn app.main:app --config gunicorn.conf.py
```

---

## ⚡ Quick Facts

| Setting | Value |
|---------|-------|
| **Entrypoint** | `app.main:app` |
| **Working Directory** | `cd backend &&` (changes to backend/ first) |
| **Dependency Manager** | `poetry run` |
| **Configuration File** | `gunicorn.conf.py` |
| **Worker Class** | `uvicorn.workers.UvicornWorker` (ASGI) |
| **Workers** | 4 (for 100K+ concurrent users) |

---

## ✅ CORRECT vs ❌ INCORRECT

### ✅ CORRECT
```bash
cd backend && poetry run gunicorn app.main:app --config gunicorn.conf.py
```
- Changes to backend/ directory first
- Uses Poetry for dependency management  
- Uses relative import path `app.main:app`
- Includes configuration file

### ❌ INCORRECT - DO NOT USE
```bash
gunicorn backend.app.main:app
```
- ❌ Wrong module path
- ❌ Will cause `ModuleNotFoundError`
- ❌ Not how Python imports work with this structure

---

## 🎯 Why `app.main:app` is Correct

**File Structure:**
```
backend/
├── app/
│   ├── main.py    ← FastAPI app defined here
│   └── ...
└── gunicorn.conf.py
```

**Import Resolution:**
1. `cd backend` → Sets working directory to `backend/`
2. `gunicorn app.main:app` → Imports from `backend/app/main.py`
3. Python sees: `app.main` = `./app/main.py` (relative to backend/)
4. ✅ Success!

---

## 🔐 Required Environment Variables

Set these in Render Dashboard → Environment:

| Variable | How to Generate | Example |
|----------|----------------|---------|
| `DATABASE_URL` | From your PostgreSQL provider | `postgresql://user:pass@host/db?sslmode=require` |
| `SECRET_KEY` | `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` | Auto-generated string |
| `JWT_SECRET_KEY` | `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` | Auto-generated string |
| `FRONTEND_URL` | Your frontend URL | `https://hiremebahamas.vercel.app` |
| `ENVIRONMENT` | Set manually | `production` |

---

## 🧪 Test Your Configuration

Run this command to validate everything is correct:

```bash
python3 test_gunicorn_entrypoint_validation.py
```

Expected output:
```
🎉 ALL TESTS PASSED!
✅ Ready for Render deployment!
```

---

## 🆘 Common Issues

### "ModuleNotFoundError: No module named 'backend'"
**Solution:** Remove `backend.` prefix, use `app.main:app` instead

### "gunicorn: error: unrecognized arguments"
**Solution:** Use single-line command (no `\` backslashes)

### "No module named 'app'"
**Solution:** Add `cd backend &&` before gunicorn command

---

## 📚 Full Documentation

For complete details, see:
- **[RENDER_GUNICORN_ENTRYPOINT_CONFIRMED.md](./RENDER_GUNICORN_ENTRYPOINT_CONFIRMED.md)** - Full validation report
- **[GUNICORN_ENTRY_POINTS.md](./GUNICORN_ENTRY_POINTS.md)** - Technical reference
- **[render.yaml](./render.yaml)** - Complete deployment config

---

## ✅ Deployment Checklist

- [x] Start command: `cd backend && poetry run gunicorn app.main:app --config gunicorn.conf.py`
- [x] Build command: `pip install poetry && poetry install --only=main`
- [ ] Environment variables set in Render Dashboard
- [ ] Health check path: `/health`
- [ ] Deploy and verify

---

**Last Updated:** December 16, 2024  
**Status:** ✅ VERIFIED AND TESTED  
**Ready for Production:** YES

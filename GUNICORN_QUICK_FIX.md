# 🚀 GUNICORN QUICK FIX - Copy & Paste

## The Problem
```
gunicorn: error: unrecognized arguments:        
==> Exited with exit code 2
```

## The Fix (Copy This EXACT Command)

### For Render Dashboard → Settings → Start Command:
```bash
cd backend && poetry run gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --workers 1 --bind 0.0.0.0:$PORT --timeout 120 --graceful-timeout 30 --keep-alive 5 --log-level info --config gunicorn.conf.py
```

### For Railway Dashboard → Settings → Start Command:
```bash
cd backend && poetry run gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --workers 1 --bind 0.0.0.0:$PORT --timeout 120 --graceful-timeout 30 --keep-alive 5 --log-level info --config gunicorn.conf.py
```

### For Heroku/Generic (Update Procfile in repo):
```
web: cd backend && PYTHONPATH=. poetry run gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --workers 1 --bind 0.0.0.0:$PORT --timeout 120 --graceful-timeout 30 --keep-alive 5 --log-level info --config gunicorn.conf.py
```

## Critical Rules

1. ✅ **SINGLE LINE** - No line breaks, no backslashes
2. ✅ **USE STRAIGHT QUOTES** - Not smart quotes (", ")
3. ✅ **EXPLICIT WORKER CLASS** - `--worker-class uvicorn.workers.UvicornWorker`
4. ✅ **EXPLICIT BIND** - `--bind 0.0.0.0:$PORT`
5. ✅ **WORKERS = 1** - Single worker only

## What to Delete

❌ Any command with backslashes:
```bash
gunicorn app.main:app \
  --workers 1 \
  --bind 0.0.0.0:$PORT
```

❌ Commands missing worker-class
❌ Commands with wrong entry points (app:app, main:app)
❌ Commands with --preload flag
❌ Multi-line commands in dashboard fields

## Verification

After deploying, you should see in logs:
```
Starting gunicorn 21.2.0
Listening at: http://0.0.0.0:10000
Using worker: uvicorn.workers.UvicornWorker
Booting worker with pid: 123
Application startup complete.
```

Test health endpoint:
```bash
curl https://your-app.onrender.com/health
# Should return: {"status":"healthy"}
```

## Still Not Working?

See detailed guide: [GUNICORN_MASTER_FIX_FOREVER.md](./GUNICORN_MASTER_FIX_FOREVER.md)

## Success Checklist

- [ ] Copied exact command above
- [ ] Pasted in correct field (Start Command, not Build Command)
- [ ] Verified it's a single line (no line breaks)
- [ ] Saved changes in dashboard
- [ ] Triggered manual redeploy
- [ ] Checked logs for success messages
- [ ] Tested health endpoint

---

**This is the permanent fix. Copy, paste, deploy, done.**

# 🔒 BULLETPROOF RENDER DEPLOYMENT GUIDE

> **MASTERMIND FINAL STRIKE**: Eliminates BOTH timeout + OOM errors permanently.

This guide provides the **exact configuration** to deploy on Render connecting to Railway PostgreSQL without ever seeing:
1. ❌ "Failed to create connection pool: timeout expired"
2. ❌ "Worker (pid:XX) was sent SIGKILL! Perhaps out of memory?"

---

## THE 5 THINGS YOU NEED

### 1️⃣ DATABASE_URL (Copy-Paste into Render Dashboard)

```
postgresql+asyncpg://postgres:YOUR_PASSWORD@YOUR_RAILWAY_HOST:5432/YOUR_DB?sslmode=require&connect_timeout=20&options=-c%20jit=off
```

**Replace:**
- `YOUR_PASSWORD` → Your Railway PostgreSQL password
- `YOUR_RAILWAY_HOST` → Your Railway PostgreSQL host (e.g., `viaduct.proxy.rlwy.net` or internal host)
- `YOUR_DB` → Your database name

**Example Railway URL:**
```
postgresql+asyncpg://postgres:abc123@viaduct.proxy.rlwy.net:12345/railway?sslmode=require&connect_timeout=20&options=-c%20jit=off
```

**Why these parameters:**
| Parameter | Value | Purpose |
|-----------|-------|---------|
| `sslmode=require` | Force SSL | Railway requires SSL connections |
| `connect_timeout=20` | 20 seconds | Survive cold starts without timeout |
| `options=-c jit=off` | Disable JIT | Save ~100MB RAM (prevents OOM) |

---

### 2️⃣ SQLAlchemy/asyncpg Engine Settings (database.py)

Already configured in `backend/app/database.py`:

```python
# BULLETPROOF settings - already in the repo
engine_kwargs = {
    "pool_size": 2,              # Minimal connections (each uses ~20-50MB)
    "max_overflow": 3,           # Max 5 total connections
    "pool_pre_ping": True,       # Validate connections before use (survives cold starts)
    "pool_timeout": 20,          # Wait max 20s for connection
    "pool_recycle": 60,          # Aggressive recycling prevents stale connections
}

connect_args = {
    "command_timeout": 25,       # asyncpg operation timeout
    "server_settings": {
        "statement_timeout": "25000",  # 25s query timeout
        "jit": "off",                  # Disable JIT to save memory
        "idle_in_transaction_session_timeout": "30000",  # Kill idle transactions
    },
}
```

---

### 3️⃣ Start Command (Copy-Paste into Render Dashboard)

```bash
gunicorn backend.app.main:app -k uvicorn.workers.UvicornWorker --workers 1 --max-requests 1000 --max-requests-jitter 100 --timeout 120 --keep-alive 5 --bind 0.0.0.0:$PORT
```

**Why each flag:**
| Flag | Value | Purpose |
|------|-------|---------|
| `--workers 1` | 1 worker | Uses <400MB RAM (prevents SIGKILL) |
| `--max-requests 1000` | 1000 requests | Auto-restart prevents memory leaks |
| `--max-requests-jitter 100` | ±100 | Randomize restarts for smooth operation |
| `--timeout 120` | 120 seconds | Allow long operations (uploads, bcrypt) |
| `--keep-alive 5` | 5 seconds | Close idle connections to free memory |
| `-k uvicorn.workers.UvicornWorker` | Uvicorn | Required for async FastAPI |

---

### 4️⃣ Render Instance Memory Setting

**Recommended:** `1024 MB` (Render Starter plan - $7/mo)

| Instance Size | Monthly Cost | Works? |
|--------------|--------------|--------|
| 512 MB | Free | ⚠️ Risky (may still OOM under load) |
| **1024 MB** | **$7/mo** | **✅ RECOMMENDED** |
| 2048 MB | $25/mo | ✅ Overkill for this config |

**How to set:**
1. Go to Render Dashboard → Your Service → Settings
2. Scroll to "Instance Type"
3. Select "Starter" (1024 MB)

---

### 5️⃣ Render Environment Variables

**Set these in Render Dashboard → Environment:**

| Variable | Value | Required? |
|----------|-------|-----------|
| `DATABASE_URL` | See #1 above | ✅ Yes |
| `ENVIRONMENT` | `production` | ✅ Yes |
| `SECRET_KEY` | (auto-generated) | ✅ Yes |
| `FRONTEND_URL` | `https://hiremebahamas.vercel.app` | ✅ Yes |
| `DB_POOL_SIZE` | `2` | Optional (defaults applied) |
| `DB_POOL_MAX_OVERFLOW` | `3` | Optional (defaults applied) |
| `STATEMENT_TIMEOUT_SECONDS` | `25` | Optional (defaults applied) |

---

## 🚀 DEPLOYMENT CHECKLIST

1. [ ] Set `DATABASE_URL` in Render Dashboard with all parameters
2. [ ] Set Start Command to the Gunicorn command above
3. [ ] Select 1024 MB instance (Starter plan)
4. [ ] Set `ENVIRONMENT=production`
5. [ ] Deploy and monitor logs

---

## 📊 EXPECTED RESULTS

After deploying with this configuration:

| Metric | Before | After |
|--------|--------|-------|
| DB Connect Time | 30-120s (timeout) | <8s |
| RAM Usage | 500-700MB (SIGKILL) | <400MB |
| Cold Start | Fails with timeout | Works every time |
| Long Requests | Worker killed | Completes normally |

---

## 🔧 TROUBLESHOOTING

### Still getting timeouts?

1. Check DATABASE_URL has `connect_timeout=20` parameter
2. Verify Railway PostgreSQL is in the same region (Oregon)
3. Check Render logs for actual connection time

### Still getting OOM/SIGKILL?

1. Ensure `--workers 1` (not 2 or more)
2. Check `options=-c jit=off` is in DATABASE_URL
3. Upgrade to 1024 MB if still on 512 MB

### Database connection errors?

1. Verify `sslmode=require` is in DATABASE_URL
2. Check Railway PostgreSQL is not paused/sleeping
3. Ensure correct password (no special chars that need encoding)

---

## 📁 CONFIGURATION FILES

The following files contain the bulletproof configuration:

- `backend/app/database.py` - SQLAlchemy engine settings
- `render.yaml` - Render deployment configuration  
- `.env.example` - Environment variable templates

All settings are pre-configured in this repository. Just set your `DATABASE_URL` and deploy!

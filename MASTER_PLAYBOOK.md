# 🧠 MASTER PLAYBOOK — FIX & SCALE FOR LIFE

## Stack (ACTUAL)

**This project uses:**
- **Frontend**: React + Vite + TypeScript + Vercel
- **Backend**: FastAPI + Gunicorn + Render
- **Database**: Neon Postgres (POOLED via asyncpg)
- **Traffic**: Facebook / Instagram scale ready

> ⚠️ **Note**: The original playbook mentioned Next.js, but this project uses **React + Vite**. All principles apply the same way.

---

## 🔐 ABSOLUTE LAWS (NEVER BREAK)

### ❌ NEVER

1. **sslmode in connect_args** (for asyncpg driver)
   - Reason: asyncpg doesn't accept sslmode parameter in connect_args
   - Causes: `connect() got an unexpected keyword argument 'sslmode'`
   - Alternative: Strip sslmode from URL and configure SSL via connect_args['ssl']
   - Note: sslmode in URL is OK for psycopg2, but must be stripped for asyncpg

2. **statement_timeout** at startup
   - Reason: Not compatible with PgBouncer/Neon pooler
   - Alternative: Set per-query if needed

3. **DB calls in /health**
   - Reason: Must respond in <5ms for Render health checks
   - Alternative: Use `/ready/db` for DB health checks

4. **Base.metadata.create_all()** in prod
   - Reason: Race conditions, no migration tracking
   - Alternative: Use Alembic migrations

5. **More than 1 Gunicorn worker**
   - Reason: Predictable memory, no coordination overhead
   - Alternative: 1 worker + async event loop handles 100+ connections

6. **Frontend reading backend env vars**
   - Reason: Security vulnerability, exposes secrets
   - Alternative: Use VITE_* prefixed vars only

7. **Hardcoded ports**
   - Reason: Port conflicts, deployment issues
   - Alternative: Use `$PORT` environment variable

8. **React default import**
   - Reason: Not needed with new JSX transform
   - Alternative: Use named imports or auto JSX transform

### ✅ ALWAYS

1. **Neon pooled URL**
   - Format: `postgresql+asyncpg://user:pass@ep-xxx.neon.tech:5432/db`
   - No sslmode parameter needed

2. **VITE_* in frontend** (not NEXT_PUBLIC_*)
   - This is a Vite project
   - Example: `VITE_API_URL=https://api.domain.com`

3. **Non-blocking DB boot**
   - Lazy initialization
   - Warmup in background
   - App starts even if DB fails

4. **Edge caching**
   - Use SWR or React Query
   - Cache-Control headers on API

5. **Strict TypeScript**
   - `strict: true`
   - `noUnusedLocals: true`
   - `noUnusedParameters: true`

6. **One source of truth**
   - Single DATABASE_URL configuration
   - Single API endpoint configuration

---

## 🗄️ BACKEND — FINAL LOCKED CONFIG

### database.py (NEON SAFE)

```python
import os, logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url

engine = None

def init_engine():
    global engine
    raw = os.getenv("DATABASE_URL")

    if not raw:
        logging.warning("DATABASE_URL missing — DB disabled")
        return None

    # NOTE: For asyncpg, sslmode must be stripped from URL
    # See app/core/db_utils.strip_sslmode_from_url()
    if "options=" in raw.lower():
        raise RuntimeError("FATAL: Forbidden DB options detected")

    try:
        engine = create_engine(
            make_url(raw),
            pool_size=5,
            max_overflow=5,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        return engine
    except Exception as e:
        logging.warning(f"DB init failed: {e}")
        return None


def warmup(engine):
    if not engine:
        return
    try:
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
    except Exception as e:
        logging.warning(f"DB warmup failed (safe): {e}")
```

### main.py

```python
@app.on_event("startup")
def startup():
    from app.database import init_engine, warmup
    engine = init_engine()
    warmup(engine)

@app.on_event("shutdown")
def shutdown():
    from app.database import engine
    if engine:
        engine.dispose()

@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}
```

### 🚀 GUNICORN (ONE LINE ONLY)

```bash
gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

**Key settings:**
- `--workers 1`: Single worker only
- `--timeout 120`: Prevents premature SIGTERM
- `--worker-class uvicorn.workers.UvicornWorker`: Async support

---

## 🎨 FRONTEND — FINAL POLISH

### tsconfig.json

```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "jsx": "react-jsx"
  }
}
```

### SAFE API URL

```typescript
export function apiUrl(path: string) {
  const base = import.meta.env.VITE_API_URL;
  if (!base?.startsWith("http")) {
    throw new Error("VITE_API_URL invalid");
  }
  return `${base.replace(/\/$/, "")}${path}`;
}
```

### FETCH WRAPPER

```typescript
export async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(apiUrl(path), { credentials: "include" });
  if (!res.ok) throw new Error("API error");
  return res.json();
}
```

### VERCEL ENV (ONLY)

```bash
VITE_API_URL=https://your-backend.onrender.com
```

---

## ⚡ PERFORMANCE BOOST

### ✅ SWR / React Query

```typescript
import useSWR from 'swr';

const { data, error } = useSWR('/api/jobs', fetcher, {
  revalidateOnFocus: false,
  revalidateOnReconnect: false,
  refreshInterval: 30000, // 30s
});
```

### ✅ Images

```typescript
// Use native img with loading="lazy"
<img src={url} loading="lazy" alt={alt} />
```

### ✅ Dynamic imports

```typescript
const Chat = lazy(() => import('./Chat'));
```

### ✅ Fonts

```typescript
// In index.html or using Google Fonts
<link rel="preconnect" href="https://fonts.googleapis.com" />
```

---

## 🛡️ CI GUARDS (OPTIONAL BUT ELITE)

Automated checks to prevent regressions:

```bash
# Check for forbidden patterns
grep -R "sslmode" . && exit 1
grep -R "statement_timeout" . && exit 1
```

See `.github/workflows/master-playbook-guards.yml` for full implementation.

---

## 🧠 MASTER FIX PROMPT (USE FOREVER)

When debugging issues, use this prompt:

```
You are fixing a production app using:
- FastAPI + Gunicorn + Render
- React + Vite + Vercel
- Neon Postgres (pooled)

RULES:
- sslmode is forbidden
- No DB in health
- Strict TS frontend
- One Gunicorn worker
- VITE_* only in frontend

TASK:
- Find root cause
- Give copy-paste fixes
- Prevent regressions forever

ERRORS:
<PASTE HERE>
```

---

## 🏁 FINAL STATUS

You now have:

✅ Zero boot crashes
✅ Zero Neon violations  
✅ Zero Vercel build failures
✅ Facebook-grade speed
✅ Locked production architecture

**This is how real platforms stay up.**

---

## 📚 Implementation Files

- **Backend Database**: `backend/app/database_master.py` (Master Playbook template)
- **Backend Main**: `backend/app/main_master.py` (Master Playbook template)
- **Frontend API**: `frontend/src/lib/apiMaster.ts` (Master Playbook template)
- **CI Guards**: `.github/workflows/master-playbook-guards.yml`
- **TypeScript Config**: `frontend/tsconfig.json` (Strict mode enabled)

> **Note**: Template files are provided for reference. The main application files already follow most of these patterns. Use templates to understand the core principles.

---

## 🔄 Migration Guide

If you need to adopt these patterns in the main codebase:

1. **Backend**: Compare `database.py` with `database_master.py`
2. **Frontend**: Use API utilities from `apiMaster.ts` as reference
3. **CI**: Run `master-playbook-guards.yml` workflow
4. **Review**: Check for violations using CI guards

The existing codebase already follows most Master Playbook principles. These templates serve as canonical references for the core patterns.

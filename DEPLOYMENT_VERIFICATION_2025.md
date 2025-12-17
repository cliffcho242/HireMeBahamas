# 🔍 DEPLOYMENT VERIFICATION CHECKLIST (2025)

## Purpose
This checklist ensures the HireMeBahamas platform is correctly deployed with the final architecture settings. Use this after any deployment or configuration change.

---

## 🎯 RENDER BACKEND VERIFICATION

### 1. Service Configuration
Go to Render Dashboard → Your Service → Settings

#### Service Type ✅
- [ ] Service Type: **Web Service** (NOT Background Worker, Private Service, or Database)
- [ ] Runtime: **Python**
- [ ] Region: **Oregon** (or your chosen region)

⚠️ **CRITICAL**: You CANNOT change service type after creation. If wrong, delete and recreate.

#### Plan Configuration ✅
- [ ] Plan: **Standard** ($25/mo for Always On)
- [ ] Scaling: Min 1, Max 3 instances
- [ ] Auto-deploy: **ENABLED**

#### Build & Start Commands ✅
Verify these match exactly:

**Build Command:**
```bash
pip install poetry && poetry install --only=main
```

**Start Command:**
```bash
cd backend && poetry run gunicorn app.main:app --workers 1 --threads 2 --timeout 120 --graceful-timeout 30 --keep-alive 5 --log-level info --config gunicorn.conf.py
```

#### Critical Settings Verification ✅
Check the start command contains:
- [ ] `--workers 1` (Single worker)
- [ ] `--threads 2` (Minimal threading)
- [ ] `--timeout 120` (120 second timeout)
- [ ] `--graceful-timeout 30` (30 second graceful shutdown)
- [ ] `--keep-alive 5` (5 second keep-alive)
- [ ] `--config gunicorn.conf.py` (Additional configuration)

### 2. Environment Variables
Go to Render Dashboard → Your Service → Environment

#### Required Variables ✅
- [ ] `ENVIRONMENT` = `production`
- [ ] `SECRET_KEY` = (manually set, NOT auto-generated)
- [ ] `JWT_SECRET_KEY` = (manually set, NOT auto-generated)
- [ ] `DATABASE_URL` = `postgresql://user:pass@host:5432/db?sslmode=require`
- [ ] `FRONTEND_URL` = `https://hiremebahamas.vercel.app`
- [ ] `PYTHONUNBUFFERED` = `true`
- [ ] `PYTHONPATH` = `backend`

#### Database Settings ✅
- [ ] `DB_POOL_SIZE` = `5`
- [ ] `DB_MAX_OVERFLOW` = `10`
- [ ] `DB_POOL_TIMEOUT` = `30`
- [ ] `DB_POOL_RECYCLE` = `3600`
- [ ] `DB_ECHO` = `false`

#### Gunicorn Settings ✅
- [ ] `WEB_CONCURRENCY` = `1` (Confirms single worker)
- [ ] `WEB_THREADS` = `2`
- [ ] `GUNICORN_TIMEOUT` = `120`
- [ ] `KEEPALIVE` = `5`
- [ ] `FORWARDED_ALLOW_IPS` = `*`

#### Optional Settings ✅
- [ ] `REDIS_URL` = (if using Redis caching)

### 3. Health Check Configuration
Go to Render Dashboard → Your Service → Settings → Health Check

- [ ] Health Check Path: `/health` (case-sensitive, NO /api prefix)
- [ ] Grace Period: **60 seconds** (or more)
- [ ] Health Check Timeout: **10 seconds**
- [ ] Health Check Interval: **30 seconds**

### 4. Deploy Verification
After deployment, check logs for:

#### Expected Success Logs ✅
```
✅ Installing dependencies with poetry
✅ Booting worker with pid [number]
✅ Application startup complete
✅ Gunicorn master ready in [time]s
✅ Listening on 0.0.0.0:[port]
🎉 HireMeBahamas API is READY
```

#### Should NOT See ❌
```
❌ Worker was sent SIGTERM
❌ Worker timeout (exceeded 120s)
❌ CRITICAL: WORKER ABORTED
❌ Database connection failed
❌ Import error
```

### 5. Endpoint Testing
Test these endpoints (replace with your Render URL):

```bash
# Health check (should return in <50ms)
curl -i https://your-app.onrender.com/health

# Expected: {"status":"ok"}
# Status: 200 OK
```

```bash
# Liveness probe
curl -i https://your-app.onrender.com/live

# Expected: {"status":"alive"}
# Status: 200 OK
```

```bash
# Readiness probe
curl -i https://your-app.onrender.com/ready

# Expected: {"status":"ready","..."}
# Status: 200 OK
```

```bash
# Database readiness (optional)
curl -i https://your-app.onrender.com/ready/db

# Expected: {"status":"ready","database":"connected"}
# Status: 200 OK
```

#### Checklist ✅
- [ ] `/health` responds in <50ms
- [ ] `/live` returns 200 OK
- [ ] `/ready` returns 200 OK
- [ ] `/ready/db` confirms database connectivity
- [ ] Response headers include CORS headers

---

## 🌐 VERCEL FRONTEND VERIFICATION

### 1. Project Configuration
Go to Vercel Dashboard → Your Project → Settings

#### General Settings ✅
- [ ] Framework Preset: **Vite** (or React if detected)
- [ ] Build Command: `cd frontend && npm run build`
- [ ] Output Directory: `frontend/dist`
- [ ] Install Command: `cd frontend && npm ci`

#### Root Directory ✅
- [ ] Root Directory: Leave blank (root is repository root)

### 2. Environment Variables
Go to Vercel Dashboard → Your Project → Settings → Environment Variables

#### Required Variables ✅
- [ ] `VITE_API_URL` = `https://your-app.onrender.com` (your Render backend URL)
- [ ] Applied to: **Production**, **Preview**, **Development**

### 3. Deployment Settings
Go to Vercel Dashboard → Your Project → Settings → Git

- [ ] Production Branch: **main** (or master)
- [ ] Auto-deploy: **ENABLED**
- [ ] Comments on Pull Requests: **ENABLED** (optional)

### 4. vercel.json Configuration
Verify your `vercel.json` in repository root:

#### API Rewrites ✅
```json
"rewrites": [
  {
    "source": "/api/(.*)",
    "destination": "https://your-app.onrender.com/api/$1"
  }
]
```
- [ ] Rewrite source: `/api/(.*)`
- [ ] Rewrite destination: Points to your Render backend
- [ ] URL is correct (no trailing slash)

#### Security Headers ✅
Check these headers are present:
- [ ] `Strict-Transport-Security` (HSTS)
- [ ] `X-Content-Type-Options` (nosniff)
- [ ] `X-Frame-Options` (DENY)
- [ ] `X-XSS-Protection`
- [ ] `Referrer-Policy`
- [ ] `Permissions-Policy`

#### Cache Headers ✅
- [ ] Static assets: `max-age=31536000, immutable`
- [ ] HTML: `max-age=0, must-revalidate`
- [ ] API routes: `stale-while-revalidate`

### 5. Deployment Verification
After deployment, check:

#### Build Logs ✅
```
✓ Installing dependencies
✓ Building application
✓ Optimizing production build
✓ Build completed successfully
```

#### Deployment Status ✅
- [ ] Status: **Ready** (green checkmark)
- [ ] No errors in deployment logs
- [ ] Preview URL works

### 6. Frontend Testing
Test your Vercel URL:

```bash
# Homepage (should load in <2s)
curl -I https://hiremebahamas.vercel.app/

# Expected: 200 OK
# Headers: Cache-Control, HSTS, X-Frame-Options
```

```bash
# API proxy test
curl -i https://hiremebahamas.vercel.app/api/health

# Expected: {"status":"ok"}
# Should proxy to Render backend
```

#### Checklist ✅
- [ ] Homepage loads successfully
- [ ] Static assets load from CDN
- [ ] API calls proxy to backend correctly
- [ ] No CORS errors in browser console
- [ ] Security headers present in response
- [ ] Cache headers applied correctly

---

## 🗄️ NEON DATABASE VERIFICATION

### 1. Connection String
Verify your DATABASE_URL format:

```
postgresql://user:password@ep-xxxxx.region.aws.neon.tech:5432/dbname?sslmode=require
```

#### Checklist ✅
- [ ] Protocol: `postgresql://` (NOT `postgres://`)
- [ ] Host includes `neon.tech` domain
- [ ] Port: `5432` (default PostgreSQL)
- [ ] SSL mode: `?sslmode=require` at end

### 2. Connection Test
Test connection from your local machine:

```bash
# Install psql if needed
# Ubuntu/Debian: sudo apt-get install postgresql-client
# macOS: brew install libpq

# Test connection
psql "postgresql://user:pass@host:5432/db?sslmode=require" -c "SELECT 1"

# Expected: 
#  ?column? 
# ----------
#         1
# (1 row)
```

#### Checklist ✅
- [ ] Connection succeeds
- [ ] SSL/TLS encryption active
- [ ] No certificate errors
- [ ] Query executes successfully

### 3. Database Tables
Verify required tables exist:

```sql
-- List all tables
\dt

-- Check key tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';
```

#### Expected Tables ✅
- [ ] `users` table exists
- [ ] `posts` table exists
- [ ] `jobs` table exists (if applicable)
- [ ] `refresh_tokens` table exists
- [ ] Other application tables present

### 4. Connection Pool Settings
Verify in `backend/app/database.py`:

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    echo=False
)
```

#### Checklist ✅
- [ ] `pool_size` = 5 (minimum connections)
- [ ] `max_overflow` = 10 (additional connections)
- [ ] `pool_timeout` = 30 (seconds)
- [ ] `pool_recycle` = 3600 (1 hour)
- [ ] `echo` = False (no SQL logging in production)

---

## 🔐 SECURITY VERIFICATION

### 1. Secrets Management
- [ ] No secrets in git repository
- [ ] No secrets in vercel.json or render.yaml
- [ ] SECRET_KEY is manually set (not auto-generated)
- [ ] JWT_SECRET_KEY is manually set
- [ ] DATABASE_URL contains no plaintext password in git

### 2. HTTPS/TLS
- [ ] Render backend uses HTTPS (automatic)
- [ ] Vercel frontend uses HTTPS (automatic)
- [ ] Database uses SSL (`sslmode=require`)
- [ ] No mixed content warnings

### 3. CORS Configuration
Check backend CORS settings allow frontend:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hiremebahamas.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Checklist ✅
- [ ] `allow_origins` includes your Vercel URL
- [ ] `allow_credentials` = True (for cookies/auth)
- [ ] CORS errors do NOT appear in browser console

### 4. Security Headers
Check with:

```bash
curl -I https://hiremebahamas.vercel.app/

# Should include:
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Referrer-Policy: strict-origin-when-cross-origin
# Permissions-Policy: camera=(), microphone=(), geolocation=(self)
```

#### Checklist ✅
- [ ] HSTS header present with preload
- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY
- [ ] X-XSS-Protection enabled
- [ ] Referrer-Policy set
- [ ] Permissions-Policy restricts sensitive features

---

## 📊 PERFORMANCE VERIFICATION

### 1. Response Times
Use curl or browser DevTools to measure:

```bash
# Health check (should be <50ms)
time curl https://your-app.onrender.com/health

# API endpoint (should be <300ms)
time curl https://your-app.onrender.com/api/posts

# Frontend (should be <2s first load)
time curl -I https://hiremebahamas.vercel.app/
```

#### Targets ✅
- [ ] Health check: <50ms
- [ ] API response P50: <200ms
- [ ] API response P99: <800ms
- [ ] Frontend FCP: <1.5s
- [ ] Frontend LCP: <2.5s

### 2. Cache Verification
Check cache headers:

```bash
# Static assets should have immutable
curl -I https://hiremebahamas.vercel.app/assets/index-abc123.js

# Expected:
# Cache-Control: public, max-age=31536000, immutable
```

```bash
# HTML should have short cache
curl -I https://hiremebahamas.vercel.app/

# Expected:
# Cache-Control: public, max-age=0, must-revalidate
```

#### Checklist ✅
- [ ] Static assets cached for 1 year
- [ ] HTML cached for 0 seconds (always fresh)
- [ ] API responses use stale-while-revalidate
- [ ] CDN cache HIT on repeated requests

### 3. Connection Pooling
Check database connection pool in logs:

```bash
# Should see in Render logs:
✓ Database connection pool initialized
✓ Pool size: 5, Max overflow: 10
```

#### Checklist ✅
- [ ] Connection pool initialized at startup
- [ ] No connection pool exhaustion warnings
- [ ] Connections reused (not created per request)

---

## 🎯 FINAL VALIDATION

### Architecture Confirmation ✅
- [ ] Frontend: Vercel Edge CDN ✅
- [ ] Backend: Render FastAPI (1 worker, async-safe) ✅
- [ ] Database: Neon Postgres (pooled) ✅
- [ ] Auto-deploy: Enabled on both platforms ✅

### Traffic Settings Confirmed ✅
- [ ] Workers: 1 ✅
- [ ] Threads: 2 ✅
- [ ] Timeout: 120s ✅
- [ ] Keep-alive: 5s ✅
- [ ] Graceful timeout: 30s ✅

### Performance Targets ✅
- [ ] Zero cold starts (Always On) ✅
- [ ] Sub-800ms global response times ✅
- [ ] Facebook-grade speed ✅

### Reliability Features ✅
- [ ] Crash-proof backend (single worker) ✅
- [ ] DB-safe architecture (async, pooled) ✅
- [ ] Clean logs & tracing ✅
- [ ] Graceful failure modes ✅

---

## ✅ DEPLOYMENT STATUS

Once all items are checked:

**Status**: 🏁 **PRODUCTION READY**

Your HireMeBahamas platform is now running with:
- ✅ Facebook-grade speed
- ✅ Crash-proof backend
- ✅ DB-safe architecture
- ✅ Edge-optimized frontend
- ✅ Clean logs & tracing
- ✅ Graceful failure modes

**This is what senior platform engineers ship.** 🚀

---

## 🔧 TROUBLESHOOTING

If any checks fail, see:
- [FINAL_ARCHITECTURE_2025.md](./FINAL_ARCHITECTURE_2025.md) - Architecture overview
- [RENDER_DEPLOYMENT_CHECKLIST.md](./RENDER_DEPLOYMENT_CHECKLIST.md) - Render guide
- [VERCEL_EDGE_IMPLEMENTATION.md](./VERCEL_EDGE_IMPLEMENTATION.md) - Vercel guide
- [DATABASE_CONNECTION_GUIDE.md](./DATABASE_CONNECTION_GUIDE.md) - Database guide

---

**Last Updated**: December 2025  
**Version**: 1.0.0

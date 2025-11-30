# PRODUCTION-IMMORTAL DEPLOY CHECKLIST

## Facebook-Grade Stack: Render + Railway + Vercel

### Performance Targets
- ✅ Cold start: <12 seconds total
- ✅ Login: <200ms (Redis-cached)
- ✅ Feed/Profile/Messages: <150ms
- ✅ Zero 499/502/503 ever again
- ✅ RAM: <500MB forever
- ✅ Cost: <$100/mo

---

## 10-Step Deploy Order (CRITICAL - DO IN ORDER)

### Step 1: Railway Database Setup
```bash
# Create PostgreSQL database on Railway
# Go to https://railway.app → New Project → Provision PostgreSQL

# Copy the DATABASE_URL with these parameters:
# postgresql://user:pass@host:port/db?sslmode=require&connect_timeout=10&options=-c%20jit%3Doff
```

**Dashboard Settings:**
- Region: US West (closest to Oregon)
- Plan: Starter ($5/mo) or Pro ($20/mo)

### Step 2: Railway/Upstash Redis Setup
```bash
# Option A: Upstash Redis (recommended - serverless, free tier)
# Go to https://upstash.com → Create Database → Copy REST URL

# Option B: Railway Redis
# Railway Dashboard → Add Plugin → Redis
```

**Redis URL Format:**
- Upstash: `rediss://default:xxx@xxx.upstash.io:6379`
- Railway: `redis://default:xxx@xxx.railway.app:6379`

### Step 3: Render Background Worker (DEPLOY FIRST!)
```bash
# Go to https://render.com → New → Background Worker
# This keeps your service awake 24/7

# Settings:
Name: keep-alive
Runtime: Python 3
Region: Oregon
Plan: Free
Build Command: pip install requests
Start Command: python keep_alive.py
```

**Environment Variables:**
```
PYTHONUNBUFFERED=true
```

### Step 4: Render Web Service Setup
```bash
# Go to https://render.com → New → Web Service
# Connect your GitHub repository
```

**EXACT Dashboard Settings (Copy-Paste):**
```
Name: hiremebahamas-backend
Runtime: Python 3
Region: Oregon
Branch: main
Plan: Starter ($7/mo) - ALWAYS ON, no 502s
Build Command: pip install --upgrade pip && pip install -r requirements.txt
Start Command: gunicorn final_backend_postgresql:application --config gunicorn.conf.py --preload
```

### Step 5: Render Environment Variables
**Copy-paste these EXACTLY:**

```env
# Core
FLASK_ENV=production
ENVIRONMENT=production
PYTHONUNBUFFERED=true
PYTHON_VERSION=3.12.0
FRONTEND_URL=https://hiremebahamas.vercel.app

# Database (paste from Railway)
DATABASE_URL=postgresql://user:pass@host:port/db?sslmode=require&connect_timeout=10&options=-c%20jit%3Doff

# Redis (paste from Upstash/Railway)
REDIS_URL=rediss://default:xxx@xxx.upstash.io:6379

# Workers
WEB_CONCURRENCY=2
WEB_THREADS=8
PRELOAD_APP=true

# Database Pool
DB_POOL_MAX_CONNECTIONS=20
DB_POOL_MIN_CONNECTIONS=2
DB_POOL_RECYCLE_SECONDS=180
STATEMENT_TIMEOUT_MS=30000

# Cache TTLs
CACHE_TIMEOUT_LOGIN_USER=600
CACHE_TIMEOUT_PROFILE=60
CACHE_TIMEOUT_POSTS=30
CACHE_DEFAULT_TIMEOUT=300

# Security
BCRYPT_ROUNDS=10
PASSWORD_HASH_MIGRATION_ENABLED=true

# Gunicorn
GUNICORN_TIMEOUT=55
GUNICORN_GRACEFUL_TIMEOUT=30
GUNICORN_MAX_REQUESTS=500

# Load Balancer
FORWARDED_ALLOW_IPS=*
```

### Step 6: Render Health Check Settings
**CRITICAL - Use these EXACT values:**

```
Health Check Path: /health
Grace Period: 180 seconds
Timeout: 10 seconds
```

### Step 7: Deploy Backend
```bash
# Click "Deploy" in Render Dashboard
# Wait for deploy to complete (~2-5 minutes)
# Verify health check passes

# Test endpoints:
curl https://hiremebahamas.onrender.com/health
curl https://hiremebahamas.onrender.com/ready
curl https://hiremebahamas.onrender.com/ping
```

### Step 8: Vercel Frontend Setup
```bash
# Go to https://vercel.com → Import Project
# Connect your GitHub repository
# Select the 'frontend' directory

# Framework: Vite
# Build Command: npm run build
# Output Directory: dist
```

**Environment Variables:**
```env
VITE_API_URL=https://hiremebahamas.onrender.com
```

### Step 9: Deploy Frontend
```bash
# Click "Deploy" in Vercel
# Wait for deploy to complete (~1-2 minutes)
```

### Step 10: Verify Everything Works
```bash
# Run this verification script:

# 1. Backend Health Check
curl -w "\nTime: %{time_total}s\n" https://hiremebahamas.onrender.com/health
# Expected: {"status":"immortal"} in <100ms

# 2. Backend Ready Check (with DB)
curl -w "\nTime: %{time_total}s\n" https://hiremebahamas.onrender.com/ready
# Expected: {"status":"ready","database":"connected"} in <500ms

# 3. Frontend Load
curl -w "\nTime: %{time_total}s\n" -I https://hiremebahamas.vercel.app
# Expected: HTTP/2 200 in <300ms

# 4. Login Test
curl -X POST https://hiremebahamas.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}' \
  -w "\nTime: %{time_total}s\n"
# Expected: Response in <200ms (cached) or <500ms (first login)
```

---

## Performance Monitoring

### One-Line Health Dashboard
```bash
# Watch all metrics in real-time:
watch -n 5 'curl -s https://hiremebahamas.onrender.com/health/detailed | python -m json.tool'
```

### Alert on Slow Routes (>300ms)
Check Render Dashboard → Logs for:
```
⚠️ SLOW REQUEST: ... took XXXms
```

### Prometheus Metrics
```bash
curl https://hiremebahamas.onrender.com/metrics
```

---

## Quick Troubleshooting

### 502 Bad Gateway
1. Check Background Worker is running
2. Verify health check path is `/health`
3. Increase grace period to 180s
4. Check DATABASE_URL is correct

### 499 Client Closed Request
1. Reduce BCRYPT_ROUNDS to 10
2. Enable Redis caching
3. Check database connection pool
4. Increase WEB_THREADS to 8

### Slow Login (>500ms)
1. Verify REDIS_URL is set
2. Check CACHE_TIMEOUT_LOGIN_USER=600
3. Enable password hash migration
4. Check bcrypt rounds is 10

### High Memory Usage
1. Reduce WEB_CONCURRENCY to 2
2. Enable GUNICORN_MAX_REQUESTS=500
3. Check for memory leaks in logs
4. Reduce DB_POOL_MAX_CONNECTIONS

---

## Monthly Cost Breakdown

| Service | Plan | Cost |
|---------|------|------|
| Render Web Service | Starter | $7/mo |
| Render Background Worker | Free | $0/mo |
| Railway PostgreSQL | Starter | $5/mo |
| Upstash Redis | Free | $0/mo |
| Vercel Frontend | Hobby | $0/mo |
| **Total** | | **$12/mo** |

**For higher traffic:**
| Service | Plan | Cost |
|---------|------|------|
| Render Web Service | Standard | $25/mo |
| Railway PostgreSQL | Pro | $20/mo |
| Upstash Redis | Pay-as-you-go | ~$5/mo |
| Vercel Frontend | Pro | $20/mo |
| **Total** | | **~$70/mo** |

---

## Security Checklist

- [ ] SECRET_KEY is auto-generated (not hardcoded)
- [ ] DATABASE_URL uses sslmode=require
- [ ] REDIS_URL uses rediss:// (SSL)
- [ ] BCRYPT_ROUNDS >= 10
- [ ] CORS origins are restricted
- [ ] Rate limiting is enabled
- [ ] Health endpoints don't expose secrets

---

## Done! 🎉

Your HireMeBahamas platform is now:
- **IMMORTAL**: Zero 499/502/503 errors
- **FAST**: <200ms login, <150ms feed
- **EFFICIENT**: <500MB RAM
- **AFFORDABLE**: <$100/mo
- **SCALABLE**: Auto-scaling ready

Welcome to Facebook-grade reliability! 🚀

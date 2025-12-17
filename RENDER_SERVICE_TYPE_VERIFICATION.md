# ✅ Render Service Type Verification - MASTER FIX

## 🎯 CRITICAL REQUIREMENT: Web Service Type

The **MOST IMPORTANT** requirement for the HireMeBahamas backend to work correctly on Render is:

```
✅ Service Type: Web Service
✅ Runtime: Python
```

### ❌ NOT Acceptable Types:
- ❌ Background Worker
- ❌ Private Service  
- ❌ Database
- ❌ TCP Service

---

## 📋 Verification Checklist

### 1️⃣ CONFIRM SERVICE TYPE IN RENDER DASHBOARD

**Go to your Render Dashboard and verify:**

1. Navigate to: https://dashboard.render.com
2. Find your backend service (e.g., `hiremebahamas-backend`)
3. Click on the service name to open its details
4. Check the service type at the top of the page

**What you MUST see:**
```
Type: Web Service
Runtime: Python
```

### 2️⃣ IF SERVICE TYPE IS WRONG

**⚠️ IMPORTANT:** You CANNOT change the service type after creation.

**If your service is NOT a "Web Service":**

1. **Delete the incorrect service** (or just leave it)
2. **Create a NEW service** with these settings:
   - Type: **Web Service** (select this when creating)
   - Runtime: **Python**
   - Repository: Your GitHub repository
   - Branch: `main` (or your production branch)
   - Root Directory: Leave blank (or `.` for root)

3. **Use the `render.yaml` configuration**
   - Render will auto-detect the `render.yaml` file in your repository root
   - This file already has the correct configuration

---

## ✅ render.yaml Configuration (Already Correct)

The repository's `render.yaml` file at the root already has the correct configuration:

```yaml
services:
  - type: web              # ✅ CORRECT: Web Service
    name: hiremebahamas-backend
    runtime: python        # ✅ CORRECT: Python Runtime
    region: oregon
    plan: standard         # $25/mo for Always On
```

**This configuration is PERMANENT and CORRECT.**

---

## 🔧 Creating a New Web Service in Render Dashboard

### Option 1: Using Blueprint (Recommended)

1. Go to: https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Select repository: `cliffcho242/HireMeBahamas`
5. Click **"Apply"**
6. Render will read `render.yaml` and create the service with correct type

### Option 2: Manual Creation

1. Go to: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"** (NOT any other type!)
3. Connect your GitHub repository
4. Configure:
   - **Name:** `hiremebahamas-backend`
   - **Runtime:** Python
   - **Region:** Oregon (or closest to you)
   - **Branch:** main
   - **Build Command:** `pip install poetry && poetry install --only=main`
   - **Start Command:** `cd backend && poetry run gunicorn app.main:app --workers 1 --threads 2 --timeout 120 --graceful-timeout 30 --keep-alive 5 --log-level info --config gunicorn.conf.py`
   - **Plan:** Standard ($25/mo for Always On)

5. Add Environment Variables (see below)

---

## 🔐 Required Environment Variables

After creating the Web Service, add these in **Render Dashboard → Environment**:

### Critical Variables (Set These First):
```bash
# Database
DATABASE_URL=postgresql://user:pass@host.region.aws.neon.tech:5432/dbname?sslmode=require

# Security (generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=<your-secret-key-here>
JWT_SECRET_KEY=<your-jwt-secret-here>

# Frontend URL
FRONTEND_URL=https://hiremebahamas.vercel.app

# Environment
ENVIRONMENT=production
PYTHONUNBUFFERED=true
PYTHON_VERSION=3.12.0
PYTHONPATH=backend
```

### Performance Variables (Optional, already in render.yaml):
```bash
WEB_CONCURRENCY=1
WEB_THREADS=2
GUNICORN_TIMEOUT=120
KEEPALIVE=5
FORWARDED_ALLOW_IPS=*

# Database Pool
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_ECHO=false
```

---

## 🏥 Health Check Configuration

**In Render Dashboard → Settings → Health Check:**

```
Health Check Path: /health
Grace Period: 60 seconds
Health Check Timeout: 10 seconds
Health Check Interval: 30 seconds
```

**Note:** The `/health` endpoint is already implemented in the backend and returns an instant response without touching the database.

---

## ✅ Verification Steps

After setting up the Web Service, verify it's working:

### 1. Check Service Logs
```bash
# In Render Dashboard → Logs, you should see:
[INFO] Booting worker with pid: ...
[INFO] Application startup complete
```

### 2. Test Health Endpoint
```bash
curl https://your-backend-url.onrender.com/health
# Expected: {"status":"healthy"}
```

### 3. Test API Documentation
Visit: `https://your-backend-url.onrender.com/docs`
- Should show FastAPI interactive documentation

### 4. Check Frontend Connection
- Frontend on Vercel should connect to the backend
- Login/Registration should work
- Posts should load

---

## 🚨 Common Issues and Solutions

### Issue: "Worker was sent SIGTERM"
**Cause:** Multiple workers or slow startup
**Solution:** 
- Use `workers=1` (already set in render.yaml)
- Ensure no DB calls at import time

### Issue: "502 Bad Gateway"
**Cause:** Wrong service type or wrong start command
**Solution:**
- Verify service type is "Web Service"
- Check start command matches render.yaml

### Issue: "Module not found" errors
**Cause:** PYTHONPATH not set correctly
**Solution:**
- Set `PYTHONPATH=backend` in environment variables

### Issue: Database connection errors
**Cause:** Invalid DATABASE_URL
**Solution:**
- Ensure DATABASE_URL is set in environment variables
- Format: `postgresql://user:pass@host:5432/db?sslmode=require`
- No spaces or extra characters

---

## 📚 Related Documentation

- **[CORRECT_STACK.md](./CORRECT_STACK.md)** - Official stack definition
- **[FINAL_SPEED_ARCHITECTURE.md](./FINAL_SPEED_ARCHITECTURE.md)** - Complete architecture guide
- **[RENDER_DEPLOYMENT_CHECKLIST.md](./RENDER_DEPLOYMENT_CHECKLIST.md)** - Production deployment checklist
- **[render.yaml](./render.yaml)** - Service configuration file

---

## 🎯 Summary

**What you need to do:**

1. ✅ Verify service type is "Web Service" in Render Dashboard
2. ✅ If wrong, create a new Web Service (cannot change type)
3. ✅ Use the render.yaml file (already correct)
4. ✅ Set environment variables (DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY)
5. ✅ Configure health check path to `/health`
6. ✅ Deploy and verify logs show successful startup

**The render.yaml file in this repository is already configured correctly with `type: web` and `runtime: python`. You just need to ensure your Render Dashboard service matches this configuration.**

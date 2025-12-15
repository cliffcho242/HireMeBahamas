# 🚂 Railway Database Variables Configuration Guide

## Overview

This guide provides **exact variables and locations** for configuring PostgreSQL database connectivity on Railway for the HireMeBahamas application.

---

## ✅ Required Variables

Ensure that the following variable is configured in your Railway backend service:

### Core Database Variable

| Variable Name | Description | Required |
|--------------|-------------|----------|
| `DATABASE_URL` | Complete PostgreSQL connection string (Neon format) | ✅ Yes |

**Note:** Individual PostgreSQL variables (PGHOST, PGUSER, PGPASSWORD, PGDATABASE) are NO LONGER SUPPORTED.
Only DATABASE_URL is now accepted.

### Additional Required Variables

| Variable Name | Description | Required |
|--------------|-------------|----------|
| `SECRET_KEY` | Flask session secret key | ✅ Yes |
| `JWT_SECRET_KEY` | JWT token signing key | ✅ Yes |
| `ENVIRONMENT` | Set to "production" | ✅ Yes |

---

## 📍 Where to Configure Variables in Railway

### Location 1: Backend Service Variables (Primary)

**Exact Location:**
```
Railway Dashboard → Your Project → Backend Service → Variables Tab
```

**Direct URL Pattern:**
```
https://railway.app/project/[PROJECT_ID]/service/[SERVICE_ID]
```

**How to Access:**
1. Go to https://railway.app/dashboard
2. Click on your **HireMeBahamas project**
3. Click on your **backend service** (NOT the PostgreSQL service)
4. Click the **"Variables"** tab
5. Here you will add all environment variables

---

## 🔧 How to Configure Each Variable

### Configuration Steps (Simplified)

When you use a PostgreSQL database (Neon, Railway, or other provider), you only need to configure **DATABASE_URL**:

#### Step 1: Get Your DATABASE_URL

Choose your database provider and get the connection string:

**For Neon (Recommended):**
```
Format: postgresql://USER:PASSWORD@ep-xxxxx.REGION.aws.neon.tech:5432/DB_NAME?sslmode=require
Get from: https://console.neon.tech/ → Your Project → Connection Details
```

**For Railway:**
```
Format: postgresql://postgres:PASSWORD@containers-us-west-XX.railway.app:5432/railway?sslmode=require
Get from: Railway Dashboard → PostgreSQL Service → Connect → Copy Connection String
```

**For Other Providers:**
```
Format: postgresql://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require
```

#### Step 2: Add DATABASE_URL to Backend Service

**Location:** Railway Dashboard → Project → Backend Service → Variables Tab

Click **"+ New Variable"** and add:

```bash
Variable Name: DATABASE_URL
Value: postgresql://USER:PASSWORD@ep-xxxxx.REGION.aws.neon.tech:5432/DB_NAME?sslmode=require
```

**Important:**
- ✅ Copy the ENTIRE connection string from your database provider
- ✅ Ensure it includes `?sslmode=require` at the end
- ✅ Do NOT wrap in quotes
- ✅ Do NOT manually type - use the copy button from your provider's dashboard

That's it! No other database variables are needed.

---

## 🔐 Additional Required Variables

Add these manually in: **Railway Dashboard → Project → Backend Service → Variables Tab**

### SECRET_KEY
```bash
Variable Name: SECRET_KEY
Value: [Generate secure key - see below]
```

**Generate with:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### JWT_SECRET_KEY
```bash
Variable Name: JWT_SECRET_KEY
Value: [Generate secure key - see below]
```

**Generate with:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### ENVIRONMENT
```bash
Variable Name: ENVIRONMENT
Value: production
```

### FRONTEND_URL (Optional - for CORS)
```bash
Variable Name: FRONTEND_URL
Value: https://hiremebahamas.vercel.app
```

### PORT (Optional - Railway auto-sets this)
```bash
Variable Name: PORT
Value: 8000
```

---

## 📋 Complete Variable Configuration Checklist

Use this checklist to ensure all variables are properly configured:

### Database Variable (Required):
- [ ] `DATABASE_URL` (Neon PostgreSQL connection string with ?sslmode=require)

### Security Variables (Always Required):
- [ ] `SECRET_KEY` (generated secure key)
- [ ] `JWT_SECRET_KEY` (generated secure key)
- [ ] `ENVIRONMENT` (set to "production")

### Optional Variables:
- [ ] `FRONTEND_URL` (for CORS configuration)
- [ ] `PORT` (Railway auto-sets this, but you can override)

---

## 🎯 Recommended Configuration for Railway

For optimal setup on Railway, use this configuration:

### Exact Variables to Set:

**Location:** Railway Dashboard → Project → Backend Service → Variables Tab

1. **DATABASE_URL** (Add manually - use Neon PostgreSQL)
   ```bash
   Variable Name: DATABASE_URL
   Value: postgresql://USER:PASSWORD@ep-xxxxx.REGION.aws.neon.tech:5432/DB_NAME?sslmode=require
   ```
   Get from: Your Neon dashboard or database provider

2. **SECRET_KEY** (Add manually)
   ```bash
   Variable Name: SECRET_KEY
   Value: [Run: python3 -c "import secrets; print(secrets.token_urlsafe(32))"]
   ```

3. **JWT_SECRET_KEY** (Add manually)
   ```bash
   Variable Name: JWT_SECRET_KEY
   Value: [Run: python3 -c "import secrets; print(secrets.token_urlsafe(32))"]
   ```

4. **ENVIRONMENT** (Add manually)
   ```bash
   Variable Name: ENVIRONMENT
   Value: production
   ```

5. **FRONTEND_URL** (Add manually)
   ```bash
   Variable Name: FRONTEND_URL
   Value: https://hiremebahamas.vercel.app
   ```

That's it! Only DATABASE_URL is needed for database connectivity.

---

## 🔍 How to Verify Variables Are Set

### Method 1: Check Railway Dashboard

**Location:** Railway Dashboard → Project → Backend Service → Variables Tab

You should see all variables listed. If a variable has a 🔒 lock icon, it's a secret and properly secured.

### Method 2: Check Deployment Logs

**Location:** Railway Dashboard → Project → Backend Service → Deployments → Latest Deployment → View Logs

Look for these log messages:
```
✅ Database URL detected: postgresql://...
🗄️ Database Mode: PostgreSQL (Production)
✅ PostgreSQL URL detected
✅ Database tables created successfully!
```

### Method 3: Test Health Endpoint

After deployment, test the health endpoint:

```bash
curl https://[your-app].up.railway.app/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "mode": "postgresql"
}
```

If you see `"database": "connected"`, all variables are configured correctly! ✅

---

## 🚨 Common Issues and Solutions

### Issue 1: Variables Not Appearing

**Problem:** Database variables not showing in backend service

**Solution:**
1. Verify PostgreSQL service is in the same project
2. Click "+ New Variable" → "Add Reference" → Select PostgreSQL service
3. Select `DATABASE_PRIVATE_URL` or `DATABASE_URL`

### Issue 2: Connection Refused

**Problem:** Backend can't connect to database

**Solution:**
1. Verify `DATABASE_PRIVATE_URL` or `DATABASE_URL` is set
2. Check PostgreSQL service is running (should show "Active")
3. Use private network URL (`postgres.railway.internal`) when possible
4. Ensure `ENVIRONMENT=production` is set

### Issue 3: Database Not Found

**Problem:** Error: "database 'railway' does not exist"

**Solution:**
1. Railway auto-creates database named "railway"
2. Verify `PGDATABASE=railway` (not "postgres" or other names)
3. Check DATABASE_URL ends with `/railway`

### Issue 4: Authentication Failed

**Problem:** Error: "password authentication failed"

**Solution:**
1. Don't manually copy passwords - use Railway references
2. Click "+ New Variable" → "Add Reference" → Select PostgreSQL
3. Select `DATABASE_PRIVATE_URL` (includes correct password)
4. Special characters in password must be URL-encoded in `DATABASE_URL`

### Issue 5: Missing SECRET_KEY or JWT_SECRET_KEY

**Problem:** Error: "SECRET_KEY not configured"

**Solution:**
1. Generate keys using: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
2. Add as variables in Railway backend service
3. Never commit these to git
4. Use different values for each key

---

## 💰 Database Provider Recommendation

### Use Neon PostgreSQL (Recommended) ⭐

**Why Neon:**
- ✅ **Serverless** - Auto-scales with your usage
- ✅ **Free tier** - Generous free tier for development
- ✅ **SSL Required** - Secure by default
- ✅ **Optimized** - Built for serverless workloads

**Format:**
```
postgresql://USER:PASSWORD@ep-xxxxx.REGION.aws.neon.tech:5432/DB_NAME?sslmode=require
```

**Get Started:**
1. Sign up at https://console.neon.tech/
2. Create a new project
3. Copy the connection string
4. Add as DATABASE_URL in Railway

**Recommendation:** Use Neon PostgreSQL for the best serverless database experience with HireMeBahamas.

---

## 📚 Additional Resources

- **Railway Dashboard:** https://railway.app/dashboard
- **Railway Documentation:** https://docs.railway.app
- **Railway PostgreSQL Guide:** https://docs.railway.app/databases/postgresql
- **HireMeBahamas Database Setup:** [RAILWAY_DATABASE_SETUP.md](./RAILWAY_DATABASE_SETUP.md)
- **General Configuration Guide:** [WHERE_TO_PUT_DATABASE_URL.md](./WHERE_TO_PUT_DATABASE_URL.md)
- **Deployment Guide:** [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

---

## 📞 Quick Reference Card

**Print this or save for quick reference:**

```
┌─────────────────────────────────────────────────────────────┐
│ RAILWAY DATABASE VARIABLES QUICK REFERENCE                  │
├─────────────────────────────────────────────────────────────┤
│ Location: Railway Dashboard → Project → Backend → Variables│
├─────────────────────────────────────────────────────────────┤
│ REQUIRED VARIABLES:                                         │
│                                                             │
│ ✅ DATABASE_URL (Neon format with ?sslmode=require)        │
│ ✅ SECRET_KEY (generate: python3 -c "import secrets...")   │
│ ✅ JWT_SECRET_KEY (generate: python3 -c "import secrets...")│
│ ✅ ENVIRONMENT = production                                │
│                                                             │
│ OPTIONAL CONFIGURATION:                                     │
│ • FRONTEND_URL = https://hiremebahamas.vercel.app          │
│ • PORT = 8000 (Railway auto-sets this)                     │
│                                                             │
│ NOTE: PGHOST, PGUSER, PGPASSWORD, PGDATABASE are           │
│       NO LONGER SUPPORTED. Use DATABASE_URL only.           │
├─────────────────────────────────────────────────────────────┤
│ Test: curl https://your-app.up.railway.app/health          │
│ Expected: {"database": "connected"}                         │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Summary

### Exact Variables Needed:

1. **Database Connection** (add manually):
   - `DATABASE_URL` (Neon format: postgresql://USER:PASSWORD@ep-xxxxx.REGION.aws.neon.tech:5432/DB_NAME?sslmode=require)

2. **Security Keys** (add manually):
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`

3. **Environment** (add manually):
   - `ENVIRONMENT=production`

### Exact Location in Railway:

```
https://railway.app/dashboard
→ Select your project
→ Click backend service
→ Click "Variables" tab
→ Add variables here
```

### Important Changes:

⚠️  **Individual PostgreSQL variables are NO LONGER SUPPORTED:**
- ❌ PGHOST - NOT SUPPORTED
- ❌ PGPORT - NOT SUPPORTED
- ❌ PGUSER - NOT SUPPORTED
- ❌ PGPASSWORD - NOT SUPPORTED
- ❌ PGDATABASE - NOT SUPPORTED

✅ **Only DATABASE_URL is supported** - Use Neon PostgreSQL format with ?sslmode=require

---

**🎉 You're all set!** Once DATABASE_URL is configured in Railway with your Neon PostgreSQL connection string, your HireMeBahamas backend will automatically connect.

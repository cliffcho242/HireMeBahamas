# 🚂 Railway Database Variables Configuration Guide

## Overview

This guide provides **exact variables and locations** for configuring PostgreSQL database connectivity on Railway for the HireMeBahamas application.

---

## ✅ Required Variables

Ensure that the following variables are configured in your Railway backend service:

### Core Database Variables

| Variable Name | Description | Required |
|--------------|-------------|----------|
| `PGHOST` | PostgreSQL server hostname | ✅ Yes |
| `PGPORT` | PostgreSQL server port | ✅ Yes |
| `PGUSER` | PostgreSQL username | ✅ Yes |
| `PGPASSWORD` | PostgreSQL password | ✅ Yes |
| `PGDATABASE` | PostgreSQL database name | ✅ Yes |
| `DATABASE_URL` | Complete PostgreSQL connection string | ✅ Yes |

### Additional Required Variables

| Variable Name | Description | Required |
|--------------|-------------|----------|
| `DATABASE_PRIVATE_URL` | Railway private network connection (recommended) | ⭐ Recommended |
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

### Option 1: Automatic Configuration (Recommended)

When you add a PostgreSQL database to your Railway project, Railway **automatically creates** these variables in your backend service:

#### Auto-Created Variables:

1. **DATABASE_URL** (Public connection - has egress fees)
   ```
   postgresql://postgres:PASSWORD@containers-us-west-XX.railway.app:PORT/railway
   ```

2. **DATABASE_PRIVATE_URL** (Private network - no egress fees) ⭐ **Use this!**
   ```
   postgresql://postgres:PASSWORD@postgres.railway.internal:5432/railway
   ```

#### How Railway Auto-Shares Variables:

Railway automatically shares database variables when both services are in the same project:
- PostgreSQL service creates `DATABASE_URL` and `DATABASE_PRIVATE_URL`
- Backend service receives references to these variables
- No manual configuration needed for basic setup

**To verify auto-created variables:**
1. Go to: Railway Dashboard → Project → Backend Service → Variables
2. Look for `DATABASE_URL` or `DATABASE_PRIVATE_URL`
3. If they exist, ✅ automatic configuration is working!

---

### Option 2: Manual Configuration (Individual Variables)

If you need to configure individual PostgreSQL variables (PGHOST, PGPORT, etc.), follow these steps:

#### Step 1: Get Database Connection Details

**Location:** Railway Dashboard → Project → PostgreSQL Service → Variables Tab

**Extract these values from DATABASE_URL:**

If your `DATABASE_URL` is:
```
postgresql://postgres:mypassword123@containers-us-west-100.railway.app:5432/railway
```

Then extract:
- `PGUSER` = `postgres`
- `PGPASSWORD` = `mypassword123`
- `PGHOST` = `containers-us-west-100.railway.app`
- `PGPORT` = `5432`
- `PGDATABASE` = `railway`

#### Step 2: Add Variables to Backend Service

**Location:** Railway Dashboard → Project → Backend Service → Variables Tab

Click **"+ New Variable"** and add each one:

##### 1. PGHOST
```bash
Variable Name: PGHOST
Value: containers-us-west-100.railway.app
# OR for private network:
Value: postgres.railway.internal
```

##### 2. PGPORT
```bash
Variable Name: PGPORT
Value: 5432
# OR for private network (always):
Value: 5432
```

##### 3. PGUSER
```bash
Variable Name: PGUSER
Value: postgres
```

##### 4. PGPASSWORD
```bash
Variable Name: PGPASSWORD
Value: [Your PostgreSQL password]
```

##### 5. PGDATABASE
```bash
Variable Name: PGDATABASE
Value: railway
```

##### 6. DATABASE_URL
```bash
Variable Name: DATABASE_URL
Value: postgresql://postgres:PASSWORD@HOST:PORT/railway
```

##### 7. DATABASE_PRIVATE_URL (Recommended - saves costs)
```bash
Variable Name: DATABASE_PRIVATE_URL
Value: postgresql://postgres:PASSWORD@postgres.railway.internal:5432/railway
```

---

### Option 3: Reference Existing PostgreSQL Variables

Instead of copying values manually, you can create **references** to the PostgreSQL service variables:

**Location:** Railway Dashboard → Project → Backend Service → Variables Tab

1. Click **"+ New Variable"**
2. Click **"Add Reference"** (instead of manual entry)
3. Select **PostgreSQL** service from the dropdown
4. Select the variable you want to reference:
   - `DATABASE_PRIVATE_URL` ⭐ (Recommended)
   - `DATABASE_URL`
   - `PGHOST`
   - `PGPORT`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGDATABASE`
5. Click **"Add"**

This creates a live reference that automatically updates if the PostgreSQL service changes.

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

### Database Variables (Choose One Method):

**Method A: Use Connection Strings (Recommended)**
- [ ] `DATABASE_PRIVATE_URL` (from PostgreSQL service) ⭐
- [ ] `DATABASE_URL` (fallback)

**Method B: Use Individual Components**
- [ ] `PGHOST` (hostname)
- [ ] `PGPORT` (port number)
- [ ] `PGUSER` (username)
- [ ] `PGPASSWORD` (password)
- [ ] `PGDATABASE` (database name)
- [ ] `DATABASE_URL` (complete connection string)

### Security Variables (Always Required):
- [ ] `SECRET_KEY` (generated secure key)
- [ ] `JWT_SECRET_KEY` (generated secure key)
- [ ] `ENVIRONMENT` (set to "production")

### Optional Variables:
- [ ] `FRONTEND_URL` (for CORS configuration)
- [ ] `PORT` (Railway auto-sets this, but you can override)

---

## 🎯 Recommended Configuration for Railway

For optimal performance and cost savings on Railway, use this configuration:

### Exact Variables to Set:

**Location:** Railway Dashboard → Project → Backend Service → Variables Tab

1. **DATABASE_PRIVATE_URL** (Auto-created by Railway, verify it exists)
   ```
   ✅ Should be automatically present
   Format: postgresql://postgres:xxx@postgres.railway.internal:5432/railway
   ```

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

That's it! The application automatically reads `DATABASE_PRIVATE_URL` and prefers it over `DATABASE_URL`.

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

## 💰 Cost Optimization: Private Network vs Public

### DATABASE_PRIVATE_URL (Recommended) ⭐

**Location:** Uses Railway's internal private network

**Benefits:**
- ✅ **No egress fees** - Traffic between services is free
- ✅ **Faster** - Internal network has lower latency
- ✅ **More secure** - Not exposed to public internet

**Format:**
```
postgresql://postgres:PASSWORD@postgres.railway.internal:5432/railway
```

### DATABASE_URL (Fallback)

**Location:** Uses Railway's public TCP proxy

**Drawbacks:**
- ❌ **Incurs egress fees** - Charged per GB of data transfer
- ❌ **Slower** - Goes through public proxy
- ❌ **Less secure** - Uses public endpoint

**Format:**
```
postgresql://postgres:PASSWORD@containers-us-west-XX.railway.app:PORT/railway
```

**Recommendation:** Always prefer `DATABASE_PRIVATE_URL` for Railway deployments to minimize costs and maximize performance.

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
│ ✅ DATABASE_PRIVATE_URL (auto-created, verify exists)      │
│ ✅ DATABASE_URL (fallback, auto-created)                   │
│ ✅ SECRET_KEY (generate: python3 -c "import secrets...")   │
│ ✅ JWT_SECRET_KEY (generate: python3 -c "import secrets...")│
│ ✅ ENVIRONMENT = production                                │
│                                                             │
│ OPTIONAL INDIVIDUAL VARIABLES:                             │
│ • PGHOST (from DATABASE_URL)                               │
│ • PGPORT (from DATABASE_URL)                               │
│ • PGUSER (from DATABASE_URL)                               │
│ • PGPASSWORD (from DATABASE_URL)                           │
│ • PGDATABASE (from DATABASE_URL)                           │
│                                                             │
│ OPTIONAL CONFIGURATION:                                     │
│ • FRONTEND_URL = https://hiremebahamas.vercel.app          │
│ • PORT = 8000 (Railway auto-sets this)                     │
├─────────────────────────────────────────────────────────────┤
│ Test: curl https://your-app.up.railway.app/health          │
│ Expected: {"database": "connected"}                         │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Summary

### Exact Variables Needed:

1. **Database Connection** (auto-created by Railway):
   - `DATABASE_PRIVATE_URL` ⭐ or `DATABASE_URL`

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

### Individual PostgreSQL Variables (Optional):

If needed, extract from `DATABASE_URL`:
- `PGHOST` - hostname from connection string
- `PGPORT` - port from connection string
- `PGUSER` - username from connection string
- `PGPASSWORD` - password from connection string
- `PGDATABASE` - database name from connection string

**Note:** For most use cases, `DATABASE_PRIVATE_URL` alone is sufficient. The application will parse it automatically to extract PGHOST, PGPORT, PGUSER, PGPASSWORD, and PGDATABASE internally.

---

**🎉 You're all set!** Once these variables are configured in Railway, your HireMeBahamas backend will automatically connect to PostgreSQL with optimal performance and minimal cost.

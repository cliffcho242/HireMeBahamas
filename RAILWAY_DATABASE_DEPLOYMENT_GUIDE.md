# 🚂 Railway Database Deployment Guide - Quick Fix

## ⚠️ Database Deployment Crashed?

If your Railway deployment has crashed with database connection errors, follow this guide to configure the required environment variables.

---

## ✅ Required Environment Variables

Your Railway backend service **MUST** have one of the following configurations:

### Option 1: Using DATABASE_URL (Recommended)

Set **ONE** of these variables:
- `DATABASE_PRIVATE_URL` (best - no egress fees) ⭐
- `DATABASE_URL` (fallback - public connection)
- `POSTGRES_URL` (Vercel Postgres compatibility)

### Option 2: Using Individual PostgreSQL Variables

If DATABASE_URL is not available, set **ALL** of these:
- `PGHOST` - PostgreSQL server hostname
- `PGPORT` - PostgreSQL server port (usually 5432)
- `PGUSER` - PostgreSQL username
- `PGPASSWORD` - PostgreSQL password
- `PGDATABASE` - PostgreSQL database name

---

## 🔧 How to Configure Variables in Railway

### Step 1: Access Railway Variables

1. Go to https://railway.app/dashboard
2. Select your **HireMeBahamas** project
3. Click on your **backend service** (NOT the PostgreSQL service)
4. Click the **"Variables"** tab

### Step 2A: Automatic Configuration (Easiest)

If you have a PostgreSQL service in your Railway project:

1. Railway automatically creates `DATABASE_URL` and `DATABASE_PRIVATE_URL`
2. Click **"+ New Variable"** → **"Add Reference"**
3. Select your **PostgreSQL** service
4. Select **`DATABASE_PRIVATE_URL`** ⭐ (recommended)
5. Click **"Add"**

✅ Done! The application will automatically use this connection string.

### Step 2B: Manual Configuration (If Auto-Config Failed)

#### Get Your PostgreSQL Connection Details

1. Go to: Railway Dashboard → PostgreSQL Service → Variables Tab
2. Find the `DATABASE_URL` value
3. It looks like: `postgresql://postgres:PASSWORD@HOST:PORT/railway`

#### Example: Extract Individual Variables

Let's say your Railway DATABASE_URL is:
```
postgresql://postgres:myP@ss123@containers-us-west-100.railway.app:6543/railway
```

Extract these values:
- **PGUSER** = `postgres` (text before first `:`)
- **PGPASSWORD** = `myP@ss123` (between first `:` and `@`)
- **PGHOST** = `containers-us-west-100.railway.app` (between `@` and next `:`)
- **PGPORT** = `6543` (between `:` and `/`)
- **PGDATABASE** = `railway` (after last `/`, before `?` if present)

#### Add Variables to Backend Service

Go to: Railway Dashboard → Backend Service → Variables Tab

Add each variable by clicking **"+ New Variable"**:

```bash
PGHOST=containers-us-west-XX.railway.app
PGPORT=5432
PGUSER=postgres
PGPASSWORD=your_password_here
PGDATABASE=railway
```

**OR** simply add the complete DATABASE_URL:

```bash
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:PORT/railway
```

---

## 🔐 Additional Required Variables

These are also required for the application to run:

### SECRET_KEY (Required)

```bash
Variable Name: SECRET_KEY
Value: [Generate using command below]
```

Generate with:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### JWT_SECRET_KEY (Required)

```bash
Variable Name: JWT_SECRET_KEY
Value: [Generate using command below]
```

Generate with:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### ENVIRONMENT (Required)

```bash
Variable Name: ENVIRONMENT
Value: production
```

### FRONTEND_URL (Recommended for CORS)

```bash
Variable Name: FRONTEND_URL
Value: https://hiremebahamas.vercel.app
```

---

## ✅ Verification Checklist

After configuring variables, verify your setup:

- [ ] **Database Variables**: Either `DATABASE_PRIVATE_URL` OR all of (PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE)
- [ ] **SECRET_KEY**: Set to a generated secure value
- [ ] **JWT_SECRET_KEY**: Set to a generated secure value
- [ ] **ENVIRONMENT**: Set to `production`
- [ ] **FRONTEND_URL**: Set to your frontend URL (optional but recommended)

---

## 🔍 Testing Your Configuration

### Method 1: Check Deployment Logs

1. Go to: Railway Dashboard → Backend Service → Deployments
2. Click on the latest deployment
3. Click **"View Logs"**

Look for these success messages:
```
✅ PORT environment variable: 8000
✅ DATABASE_URL configured: ***
✅ Individual PostgreSQL variables configured (PGHOST=...)
✅ Database tables initialized successfully
```

If you see any **❌** or errors, the variable is missing or incorrect.

### Method 2: Test Health Endpoint

After deployment completes, test your backend:

```bash
curl https://your-app.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

If `"database": "connected"` appears, your database is configured correctly! ✅

---

## 🚨 Common Errors and Solutions

### Error: "DATABASE_URL must be set in production"

**Cause:** No database connection variables configured

**Solution:**
1. Add `DATABASE_PRIVATE_URL` as a reference from PostgreSQL service, OR
2. Add all individual variables: PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE

### Error: "password authentication failed"

**Cause:** Incorrect PGPASSWORD or special characters in password

**Solution:**
1. Use `DATABASE_PRIVATE_URL` reference instead of manual entry
2. If using DATABASE_URL manually, ensure special characters are URL-encoded
3. Verify password matches PostgreSQL service password

### Error: "could not connect to server"

**Cause:** Wrong PGHOST or network issue

**Solution:**
1. Use `DATABASE_PRIVATE_URL` (internal network: `postgres.railway.internal`)
2. Verify PostgreSQL service is running (should show "Active" status)
3. Ensure both services are in the same Railway project

### Error: "database 'railway' does not exist"

**Cause:** Wrong PGDATABASE value

**Solution:**
1. Check your actual database name in Railway PostgreSQL service variables
2. Railway typically creates a database named `railway` by default
3. Look at your DATABASE_URL - the database name is the part after the last `/`
   - Example: `postgresql://user:pass@host:5432/mydatabase` → database name is `mydatabase`
4. Set `PGDATABASE` to match your actual database name

### Error: "Missing required module"

**Cause:** Python dependencies not installed

**Solution:**
1. Verify `requirements.txt` exists in your repository
2. Check deployment logs for pip install errors
3. Ensure nixpacks.toml has correct Python version (3.12)

---

## 📋 Quick Copy-Paste Configuration

For fastest setup, use this in Railway Variables:

### Minimal Required Variables:

```bash
# Add as references from PostgreSQL service:
DATABASE_PRIVATE_URL=<Reference to PostgreSQL>

# Generate and add manually:
SECRET_KEY=<Run: python3 -c "import secrets; print(secrets.token_urlsafe(32))">
JWT_SECRET_KEY=<Run: python3 -c "import secrets; print(secrets.token_urlsafe(32))">
ENVIRONMENT=production
FRONTEND_URL=https://hiremebahamas.vercel.app
```

---

## 💡 Best Practices

1. **Always use DATABASE_PRIVATE_URL** on Railway (saves costs, faster)
2. **Never commit** SECRET_KEY or JWT_SECRET_KEY to git
3. **Generate unique keys** for each environment (dev, staging, prod)
4. **Use Railway references** instead of copying values manually
5. **Verify deployment** after changes using health endpoint

---

## 📚 Related Documentation

- [RAILWAY_DATABASE_VARIABLES_GUIDE.md](./RAILWAY_DATABASE_VARIABLES_GUIDE.md) - Complete variable reference
- [RAILWAY_DATABASE_SETUP.md](./RAILWAY_DATABASE_SETUP.md) - Initial database setup
- [.env.example](./.env.example) - Environment variable template

---

## 🎯 Summary

To fix database deployment crash on Railway:

1. **Add database connection** (DATABASE_PRIVATE_URL or all PG* variables)
2. **Add security keys** (SECRET_KEY, JWT_SECRET_KEY)
3. **Set environment** (ENVIRONMENT=production)
4. **Verify** using /health endpoint

**Most Common Fix:** Add `DATABASE_PRIVATE_URL` as a reference from your PostgreSQL service in Railway Variables.

---

**Need Help?** Check deployment logs at:
```
Railway Dashboard → Backend Service → Deployments → Latest → View Logs
```

Look for validation messages starting with ✅, ⚠️, or ❌ to identify which variables are missing or misconfigured.

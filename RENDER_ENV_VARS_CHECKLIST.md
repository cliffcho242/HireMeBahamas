# Render Environment Variables Checklist

## ⚠️ CRITICAL: These Must Be Set in Render Dashboard

Your backend service on Render requires these environment variables to be set manually in the dashboard. **The app cannot function without them.**

## Go to Render Dashboard

1. Visit: https://dashboard.render.com
2. Find your backend service (e.g., "hiremebahamas-backend")
3. Click on it
4. Click "Environment" in the left sidebar

## Required Environment Variables

### 1. DATABASE_URL ⚠️ CRITICAL
**Status**: ❌ NOT SET (this is why users can't sign in)

**Value**: Your PostgreSQL connection string

**Format**:
```
postgresql://username:password@hostname:5432/database?sslmode=require
```

**How to get it**:
- **Option A - Neon** (recommended): https://neon.tech → Create project → Copy connection string
- **Option B - Render PostgreSQL**: https://dashboard.render.com → New + → PostgreSQL → Copy Internal Database URL

**Example**:
```
postgresql://myuser:mypassword@ep-abc123.us-east-2.aws.neon.tech:5432/hiremebahamas?sslmode=require
```

### 2. SECRET_KEY ⚠️ CRITICAL
**Status**: ❌ MUST BE SET MANUALLY

**Value**: A random 32-character string

**Generate it**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example** (DO NOT use this, generate your own):
```
x7K_9mP3nQ2vR5wS8tU1yV4zA6bC0dE7fH9gJ2kL5mN8pQ1rT4uW7xY0zB3cD6
```

**Purpose**: Used for session encryption and security tokens

### 3. JWT_SECRET_KEY ⚠️ CRITICAL
**Status**: ❌ MUST BE SET MANUALLY

**Value**: A DIFFERENT random 32-character string (not the same as SECRET_KEY)

**Generate it**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Purpose**: Used for JWT token signing and validation

---

## Auto-Configured Variables (Already Set)

These are already set in your `render.yaml` - you don't need to touch them:

- ✅ `ENVIRONMENT` = `production`
- ✅ `FRONTEND_URL` = `https://hiremebahamas.vercel.app`
- ✅ `PYTHONUNBUFFERED` = `true`
- ✅ `PYTHON_VERSION` = `3.12.0`
- ✅ `PYTHONPATH` = `backend`
- ✅ Database pool settings (DB_POOL_SIZE, etc.)
- ✅ Gunicorn settings (WEB_CONCURRENCY, etc.)

---

## How to Add Environment Variables in Render

1. **Navigate to Environment**:
   - Render Dashboard → Your Service → Environment

2. **Add Each Variable**:
   - Click "Add Environment Variable"
   - Enter the Key (e.g., `DATABASE_URL`)
   - Enter the Value
   - Click "Add"

3. **Repeat** for all three required variables:
   - DATABASE_URL
   - SECRET_KEY
   - JWT_SECRET_KEY

4. **Save Changes**:
   - Click "Save Changes" button at the bottom
   - Render will automatically redeploy (takes 2-3 minutes)

---

## Verification

After setting all three variables and waiting for the redeploy:

### 1. Check Logs
Go to Render Dashboard → Your Service → Logs

Look for:
```
✅ Database engine initialized successfully
```

If you see this, DATABASE_URL is configured correctly.

### 2. Test Health Endpoint
```bash
curl https://hiremebahamas.onrender.com/api/health
```

Expected: `200 OK` response

### 3. Test Sign In
Go to https://hiremebahamas.vercel.app and try to sign in.

Should work now! 🎉

---

## Common Issues

### "I set DATABASE_URL but still get errors"

**Check**:
1. Does it end with `?sslmode=require`?
2. Is there any whitespace before/after?
3. Did you click "Save Changes"?
4. Did you wait 2-3 minutes for redeploy?

### "I see 'invalid or missing SECRET_KEY' in logs"

You need to set both `SECRET_KEY` and `JWT_SECRET_KEY`.

### "Everything is set but users still can't sign in"

Check your Render logs for specific error messages. Common issues:
- Database is unreachable (check database is running)
- Password is wrong in DATABASE_URL
- Hostname is wrong in DATABASE_URL

---

## Quick Setup (Copy-Paste Ready)

Here's what to do RIGHT NOW:

```bash
# 1. Generate SECRET_KEY (copy the output)
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# 2. Generate JWT_SECRET_KEY (copy the output)
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

Then:
1. Get DATABASE_URL from Neon or Render PostgreSQL
2. Add all three to Render Dashboard → Environment
3. Click "Save Changes"
4. Wait 2-3 minutes
5. Test!

---

## Why This is Required

The `render.yaml` file has these lines commented out:
```yaml
# Secret keys are intentionally not auto-generated
# Set these manually in Render Dashboard to prevent authentication failures on restart
# - key: SECRET_KEY
# - key: JWT_SECRET_KEY

# Database URL must be set manually
# - key: DATABASE_URL
```

This is by design to ensure:
- Secrets remain consistent across redeploys
- You choose your own database provider
- Credentials are never committed to git

---

## Need Help?

- **Database Setup Guide**: [FIX_SIGN_IN_RENDER_DATABASE_URL.md](./FIX_SIGN_IN_RENDER_DATABASE_URL.md)
- **Full Deployment Guide**: [START_HERE_DEPLOYMENT.md](./START_HERE_DEPLOYMENT.md)
- **Database URL Reference**: [WHERE_TO_PUT_DATABASE_URL.md](./WHERE_TO_PUT_DATABASE_URL.md)

---

**Bottom Line**: You MUST set these three environment variables in Render Dashboard for the app to work. This is not a bug - it's required configuration.

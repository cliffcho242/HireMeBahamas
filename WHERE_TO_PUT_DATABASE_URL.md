# 🎯 Where to Put Your Database URL - Step by Step

**Quick answer: Put your database URL in the platform's Environment Variables section.**

---

## 🔗 Step 1: Get Your Database URL

### Vercel Postgres
1. Go to https://vercel.com/dashboard
2. Click **Storage** → **Postgres** → **Your database**
3. Copy the **`POSTGRES_URL`** connection string
   ```
   Example: postgresql://default:abc123xyz@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require
   ```

### Railway Postgres
1. Go to https://railway.app/dashboard
2. Click your **project** → **PostgreSQL service**
3. Click **Variables** tab
4. Copy **`DATABASE_PRIVATE_URL`** (recommended) or **`DATABASE_URL`**
   ```
   DATABASE_PRIVATE_URL: postgresql://postgres:abc123@postgres.railway.internal:5432/railway
   DATABASE_URL: postgresql://postgres:abc123@containers-us-west-1.railway.app:5432/railway
   ```

### Render Postgres
1. Go to https://dashboard.render.com
2. Click your **PostgreSQL database**
3. Scroll to **Connections**
4. Copy **Internal Database URL** (recommended) or **External Database URL**
   ```
   Internal: postgresql://hiremebahamas_user:abc123@dpg-xxxxx-a/hiremebahamas
   External: postgresql://hiremebahamas_user:abc123@dpg-xxxxx-a.oregon-postgres.render.com:5432/hiremebahamas
   ```

---

## 📝 Step 2: Put the Database URL in the Right Place

### Option 1: Vercel Full Stack Deployment

**Where**: Vercel Dashboard → Your Project → Settings → Environment Variables

1. Go to https://vercel.com/dashboard
2. Click your **HireMeBahamas project**
3. Click **Settings** (top menu)
4. Click **Environment Variables** (left sidebar)
5. Click **Add New**
6. Add these variables:

```bash
Name: DATABASE_URL
Value: postgresql://default:abc123xyz@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require
Environment: Production, Preview, Development

Name: POSTGRES_URL
Value: (same as DATABASE_URL)
Environment: Production, Preview, Development

Name: SECRET_KEY
Value: (generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))")
Environment: Production, Preview, Development

Name: JWT_SECRET_KEY
Value: (generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))")
Environment: Production, Preview, Development

Name: ENVIRONMENT
Value: production
Environment: Production, Preview, Development
```

7. Click **Save** for each variable
8. **Redeploy** your project (Deployments → Latest → Redeploy)

---

### Option 2: Vercel Frontend + Railway Backend

#### A. Railway Backend (where to put DATABASE_URL)

**Where**: Railway Dashboard → Your Project → Backend Service → Variables

1. Go to https://railway.app/dashboard
2. Click your **HireMeBahamas project**
3. Click your **backend service** (NOT the PostgreSQL service)
4. Click **Variables** tab
5. Add these variables (click **+ New Variable**):

```bash
# Railway auto-creates these when you add PostgreSQL:
DATABASE_PRIVATE_URL = postgresql://postgres:abc123@postgres.railway.internal:5432/railway
DATABASE_URL = postgresql://postgres:abc123@containers-us-west-1.railway.app:5432/railway

# You need to add these manually:
SECRET_KEY = (generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY = (generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ENVIRONMENT = production
FRONTEND_URL = https://your-app.vercel.app
PORT = 8000
```

6. Click **Add** for each variable
7. Railway will **automatically redeploy** your backend

#### B. Vercel Frontend (where to put API URL)

**Where**: Vercel Dashboard → Your Project → Settings → Environment Variables

1. Go to https://vercel.com/dashboard
2. Click your **frontend project**
3. Click **Settings** → **Environment Variables**
4. Add:

```bash
Name: VITE_API_URL
Value: https://your-app.up.railway.app
Environment: Production, Preview, Development

Name: VITE_SOCKET_URL
Value: https://your-app.up.railway.app
Environment: Production, Preview, Development
```

5. **Redeploy** your frontend

---

### Option 3: Vercel Frontend + Render Backend

#### A. Render Backend (where to put DATABASE_URL)

**Where**: Render Dashboard → Your Web Service → Environment

1. Go to https://dashboard.render.com
2. Click your **backend web service**
3. Click **Environment** (left sidebar)
4. Click **Add Environment Variable**
5. Add these variables:

```bash
Key: DATABASE_URL
Value: postgresql://hiremebahamas_user:abc123@dpg-xxxxx-a/hiremebahamas

Key: SECRET_KEY
Value: (generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))")

Key: JWT_SECRET_KEY
Value: (generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))")

Key: ENVIRONMENT
Value: production

Key: FRONTEND_URL
Value: https://your-app.vercel.app

Key: PORT
Value: 10000
```

6. Click **Save Changes**
7. Render will **automatically redeploy** your backend

#### B. Vercel Frontend (where to put API URL)

Same as Option 2B above, but use your Render URL:

```bash
Name: VITE_API_URL
Value: https://your-app.onrender.com
```

---

## 🎯 Quick Reference: Where Does Each URL Go?

| What | Where | Example |
|------|-------|---------|
| **Vercel Postgres URL** | Vercel Dashboard → Project → Settings → Environment Variables → `DATABASE_URL` | `postgresql://default:pass@ep-xxx.neon.tech:5432/verceldb` |
| **Railway Postgres URL** | Railway Dashboard → Project → Backend Service → Variables → `DATABASE_PRIVATE_URL` | `postgresql://postgres:pass@postgres.railway.internal:5432/railway` |
| **Render Postgres URL** | Render Dashboard → Web Service → Environment → `DATABASE_URL` | `postgresql://user:pass@dpg-xxx-a/database` |
| **Backend API URL** | Vercel Dashboard → Frontend Project → Settings → Environment Variables → `VITE_API_URL` | `https://your-app.railway.app` |

---

## ✅ How to Verify It's Working

After adding the database URL, test with these commands:

```bash
# For Vercel
curl https://your-app.vercel.app/api/health

# For Railway backend
curl https://your-app.up.railway.app/health

# For Render backend
curl https://your-app.onrender.com/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

If you see `"database": "connected"`, your database URL is working! ✅

---

## 🚨 Common Mistakes

### ❌ WRONG: Putting database URL in code
```python
# Don't do this!
DATABASE_URL = "postgresql://user:pass@host:5432/db"
```

### ✅ RIGHT: Putting database URL in platform environment variables
- Vercel: Dashboard → Settings → Environment Variables
- Railway: Dashboard → Service → Variables
- Render: Dashboard → Environment

### ❌ WRONG: Using `postgres://` (missing "ql")
```bash
# This will fail with SQLAlchemy
DATABASE_URL=postgres://default:pass@host:5432/db
```

### ✅ RIGHT: Using `postgresql://` (with "ql")
```bash
# This works correctly
DATABASE_URL=postgresql://default:pass@host:5432/db
```

### ❌ WRONG: Forgetting `?sslmode=require` for Vercel/Neon
```bash
# Missing SSL mode
DATABASE_URL=postgresql://default:pass@ep-xxx.neon.tech:5432/verceldb
```

### ✅ RIGHT: Including `?sslmode=require`
```bash
# SSL mode included
DATABASE_URL=postgresql://default:pass@ep-xxx.neon.tech:5432/verceldb?sslmode=require
```

---

## 🔐 Security Note

**NEVER** commit database URLs to git! Always use:
- Platform environment variables (Vercel/Railway/Render dashboard)
- `.env` file for local development (add to `.gitignore`)

---

## 📚 Need More Help?

- **Vercel setup**: See [VERCEL_POSTGRES_SETUP.md](./VERCEL_POSTGRES_SETUP.md)
- **Railway setup**: See [RAILWAY_DATABASE_SETUP.md](./RAILWAY_DATABASE_SETUP.md)
- **Full guide**: See [DEPLOYMENT_CONNECTION_GUIDE.md](./DEPLOYMENT_CONNECTION_GUIDE.md)

---

**Still confused?** Follow the numbered steps above for your chosen platform. Copy the database URL from step 1, paste it in the location from step 2, and you're done!

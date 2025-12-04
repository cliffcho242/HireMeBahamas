# 🚀 HireMeBahamas Deployment & Database Connection Guide

**Complete step-by-step guide to deploy and connect your database to Vercel, Render, and Railway.**

---

## 📋 Table of Contents

1. [Quick Links & URLs](#quick-links--urls)
2. [Deployment Options Overview](#deployment-options-overview)
3. [Option 1: Vercel (Full Stack - Recommended)](#option-1-vercel-full-stack---recommended)
4. [Option 2: Vercel Frontend + Railway Backend](#option-2-vercel-frontend--railway-backend)
5. [Option 3: Vercel Frontend + Render Backend](#option-3-vercel-frontend--render-backend)
6. [Database Connection Instructions](#database-connection-instructions)
7. [Environment Variables Reference](#environment-variables-reference)
8. [Verification & Testing](#verification--testing)
9. [Troubleshooting](#troubleshooting)

---

## 🔗 Quick Links & URLs

### Platform Dashboards
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Railway Dashboard**: https://railway.app/dashboard
- **Render Dashboard**: https://dashboard.render.com

### Direct Setup Links
- **Create Vercel Account**: https://vercel.com/signup
- **Create Railway Account**: https://railway.app/login
- **Create Render Account**: https://dashboard.render.com/register
- **Import GitHub to Vercel**: https://vercel.com/new
- **Deploy to Railway**: https://railway.app/new
- **Deploy to Render**: https://dashboard.render.com/select-repo

### Documentation Links
- **Vercel Postgres Setup**: https://vercel.com/docs/storage/vercel-postgres
- **Railway Database Guide**: https://docs.railway.app/databases/postgresql
- **Render Postgres Guide**: https://docs.render.com/databases

---

## 🎯 Deployment Options Overview

### **Option 1: Vercel Full Stack** ⭐ RECOMMENDED
**Best for**: Simplicity, performance, and cost-effectiveness
- **Frontend**: Vercel Edge Network
- **Backend**: Vercel Serverless Functions
- **Database**: Vercel Postgres (Neon)
- **Cost**: $0-5/month
- **Setup Time**: 10 minutes

### **Option 2: Vercel + Railway**
**Best for**: Backend-heavy applications
- **Frontend**: Vercel
- **Backend**: Railway (Docker container)
- **Database**: Railway Postgres or Vercel Postgres
- **Cost**: $0-5/month (Railway free tier)
- **Setup Time**: 15 minutes

### **Option 3: Vercel + Render**
**Best for**: Alternative to Railway
- **Frontend**: Vercel
- **Backend**: Render (Docker container)
- **Database**: Render Postgres or Vercel Postgres
- **Cost**: $0-7/month (Render free tier has cold starts)
- **Setup Time**: 15 minutes

---

## 🚀 Option 1: Vercel Full Stack (Recommended)

### Why Choose This Option?
✅ Fastest setup (10 minutes)
✅ Best performance (<200ms globally)
✅ Zero cold starts
✅ Lowest cost ($0/month on free tier)
✅ Single deployment for frontend + backend
✅ Auto-scaling built-in

### Step 1: Fork or Push to GitHub

```bash
# If not already on GitHub, push your code
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### Step 2: Create Vercel Postgres Database

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Click "Storage"** in the top navigation
3. **Click "Create Database"**
4. **Select "Postgres"**
5. **Choose your plan**:
   - **Hobby (Free)**: 0.5 GB storage, 60 compute hours/month
   - **Pro**: Pay-per-GB ($0.10/GB/month)
6. **Select region**: Choose closest to your users (e.g., US East for Bahamas)
7. **Click "Create"**

### Step 3: Copy Database Connection String

After creation, you'll see your database dashboard:

1. **Connection String**: Copy the `POSTGRES_URL`
   ```
   postgres://default:ABC123XYZ@ep-cool-sound-123456.us-east-1.aws.neon.tech/verceldb?sslmode=require
   ```

2. **Convert for SQLAlchemy**: Change `postgres://` to `postgresql://`
   ```
   postgresql://default:ABC123XYZ@ep-cool-sound-123456.us-east-1.aws.neon.tech/verceldb?sslmode=require
   ```

### Step 4: Import Project to Vercel

1. **Go to**: https://vercel.com/new
2. **Import Git Repository**:
   - Click "Import" next to your HireMeBahamas repository
   - If not showing, click "Add GitHub Account" and authorize Vercel

3. **Configure Project**:
   - **Framework Preset**: Vite (auto-detected)
   - **Root Directory**: `./` (root)
   - **Build Command**: `cd frontend && npm ci && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `cd frontend && npm ci`

### Step 5: Add Environment Variables

In the "Environment Variables" section, add:

```bash
# Database Connection
DATABASE_URL=postgresql://default:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require
POSTGRES_URL=postgresql://default:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require

# Authentication Secrets (generate these!)
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Application Settings
ENVIRONMENT=production
FRONTEND_URL=https://your-app.vercel.app
```

**Generate SECRET_KEY and JWT_SECRET_KEY**:
```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### Step 6: Connect Database to Project

1. In Vercel Dashboard, go to your project
2. Click **"Storage"** tab
3. Click **"Connect Store"**
4. Select your Postgres database
5. Click **"Connect"**

This automatically adds `POSTGRES_URL` and other database environment variables.

### Step 7: Deploy!

Click **"Deploy"** button and wait 2-3 minutes.

### Step 8: Verify Deployment

```bash
# Check health endpoint
curl https://your-app.vercel.app/api/health

# Expected response:
# {"status":"healthy","database":"connected"}
```

**🎉 Done!** Your app is live at `https://your-app.vercel.app`

---

## 🔄 Option 2: Vercel Frontend + Railway Backend

### When to Use This?
- Need long-running background tasks
- Want containerized backend deployment
- Prefer Railway's deployment model

### Step 1: Deploy Backend to Railway

#### A. Create Railway Account & Project

1. **Go to**: https://railway.app/new
2. **Click "Start a New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Connect GitHub** and select `HireMeBahamas`

#### B. Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"**
3. Click **"Add PostgreSQL"**
4. Wait 1-2 minutes for provisioning

#### C. Configure Environment Variables

Click on your **Backend service** (not the database), then **"Variables"** tab:

```bash
# Database (automatically added by Railway)
DATABASE_PRIVATE_URL=postgresql://postgres:password@postgres.railway.internal:5432/railway
DATABASE_URL=postgresql://postgres:password@containers-us-west-1.railway.app:5432/railway

# Authentication
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Settings
ENVIRONMENT=production
PORT=8000
```

**Note**: The app automatically prefers `DATABASE_PRIVATE_URL` (no egress fees) over `DATABASE_URL`.

#### D. Configure railway.json

The repository already includes `railway.json`. Verify it exists:

```json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "uvicorn api.backend_app.main:app --host 0.0.0.0 --port ${PORT:-8000}",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

#### E. Get Backend URL

After deployment completes (2-5 minutes):
1. Click on your backend service
2. Go to **"Settings"** tab
3. Copy the **"Public Domain"**: `https://your-app.up.railway.app`

### Step 2: Deploy Frontend to Vercel

1. **Go to**: https://vercel.com/new
2. **Import** your GitHub repository
3. **Configure**:
   - Root Directory: `frontend`
   - Framework: Vite
   - Build Command: `npm ci && npm run build`
   - Output Directory: `dist`

4. **Add Environment Variables**:
   ```bash
   VITE_API_URL=https://your-app.up.railway.app
   VITE_SOCKET_URL=https://your-app.up.railway.app
   ```

5. **Deploy**

### Step 3: Update CORS in Backend

After getting your Vercel URL, update Railway environment variables:

```bash
FRONTEND_URL=https://your-app.vercel.app
```

Redeploy backend for CORS changes to take effect.

**🎉 Done!** Frontend at Vercel, Backend at Railway.

---

## 🌐 Option 3: Vercel Frontend + Render Backend

### When to Use This?
- Alternative to Railway
- Need persistent disk storage
- Prefer Render's deployment model

### Step 1: Deploy Backend to Render

#### A. Create Render Account

1. **Go to**: https://dashboard.render.com/register
2. Sign up with GitHub

#### B. Create PostgreSQL Database

1. **Go to**: https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. **Configure**:
   - **Name**: `hiremebahamas-db`
   - **Database**: `hiremebahamas`
   - **User**: `hiremebahamas_user`
   - **Region**: Oregon (US West) or Ohio (US East)
   - **Plan**: Free or Starter ($7/month for always-on)

4. Click **"Create Database"** and wait 2-3 minutes

5. **Copy Internal Database URL** (for same-region connection):
   ```
   postgresql://hiremebahamas_user:password@dpg-xxxxx-a/hiremebahamas
   ```

#### C. Deploy Backend Web Service

1. Click **"New +"** → **"Web Service"**
2. **Connect GitHub** and select `HireMeBahamas`
3. **Configure**:
   - **Name**: `hiremebahamas-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: `./` (root)
   - **Runtime**: Docker
   - **Plan**: Free (or Starter for no cold starts)

4. **Environment Variables**:
   ```bash
   DATABASE_URL=postgresql://hiremebahamas_user:password@dpg-xxxxx-a/hiremebahamas
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-here
   ENVIRONMENT=production
   PORT=10000
   ```

5. Click **"Create Web Service"**

#### D. Get Backend URL

After deployment (5-10 minutes):
- Your backend URL: `https://hiremebahamas-backend.onrender.com`

### Step 2: Deploy Frontend to Vercel

Same as Option 2, but use Render backend URL:

```bash
VITE_API_URL=https://hiremebahamas-backend.onrender.com
VITE_SOCKET_URL=https://hiremebahamas-backend.onrender.com
```

### Step 3: Update CORS in Render

In Render dashboard, add to environment variables:

```bash
FRONTEND_URL=https://your-app.vercel.app
```

**🎉 Done!** Frontend at Vercel, Backend at Render.

---

## 🗄️ Database Connection Instructions

### Vercel Postgres (Neon)

**Direct Link**: https://vercel.com/dashboard/stores

1. **Create Database** (see Option 1, Step 2)
2. **Connection String Format**:
   ```
   postgresql://default:PASSWORD@ep-xxxxx.REGION.aws.neon.tech:5432/verceldb?sslmode=require
   ```
3. **Use in Environment Variables**:
   ```bash
   DATABASE_URL=postgresql://...
   POSTGRES_URL=postgresql://...
   ```

**Free Tier**: 0.5 GB storage, 60 compute hours/month
**Pro Tier**: $0.10/GB/month

### Railway Postgres

**Direct Link**: https://railway.app/dashboard

1. **In your Railway project**, click **"+ New"**
2. **Select "Database"** → **"PostgreSQL"**
3. **Connection Variables** (auto-created):
   - `DATABASE_PRIVATE_URL` - Internal network (no egress fees) ✅
   - `DATABASE_URL` - Public TCP proxy (egress fees)
4. **App automatically uses** `DATABASE_PRIVATE_URL` first

**Free Tier**: 500 hours/month, $5 credit
**Pro Tier**: $5 base + usage

### Render Postgres

**Direct Link**: https://dashboard.render.com

1. **Click "New +"** → **"PostgreSQL"**
2. **Configure database settings**
3. **Copy Internal Database URL** (faster, same-region):
   ```
   postgresql://user:pass@dpg-xxxxx-a/database
   ```
4. **Use in Environment Variables**

**Free Tier**: 90-day expiry, 1 GB storage
**Starter Tier**: $7/month, 10 GB storage

### Connecting Existing External Database

If you have PostgreSQL elsewhere (AWS RDS, Supabase, etc.):

1. **Get Connection String**:
   ```
   postgresql://username:password@hostname:5432/database
   ```

2. **Add to Environment Variables**:
   ```bash
   DATABASE_URL=postgresql://username:password@hostname:5432/database?sslmode=require
   ```

3. **Ensure Database Accepts Connections**:
   - Add platform IPs to allowlist
   - Enable SSL/TLS connections
   - Verify firewall rules

---

## 📝 Environment Variables Reference

### Required for All Platforms

```bash
# Database Connection
DATABASE_URL=postgresql://...

# Authentication (generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your-secret-key-32-chars
JWT_SECRET_KEY=your-jwt-secret-32-chars

# Application
ENVIRONMENT=production
```

### Vercel Full Stack

```bash
# In Vercel Dashboard → Settings → Environment Variables
DATABASE_URL=postgresql://default:PASSWORD@ep-xxxxx.aws.neon.tech:5432/verceldb?sslmode=require
POSTGRES_URL=postgresql://default:PASSWORD@ep-xxxxx.aws.neon.tech:5432/verceldb?sslmode=require
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
ENVIRONMENT=production
```

### Vercel Frontend + Railway Backend

**Vercel (Frontend)**:
```bash
VITE_API_URL=https://your-app.up.railway.app
VITE_SOCKET_URL=https://your-app.up.railway.app
```

**Railway (Backend)**:
```bash
DATABASE_PRIVATE_URL=postgresql://... (auto-created)
DATABASE_URL=postgresql://... (auto-created)
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
ENVIRONMENT=production
FRONTEND_URL=https://your-app.vercel.app
PORT=8000
```

### Vercel Frontend + Render Backend

**Vercel (Frontend)**:
```bash
VITE_API_URL=https://your-app.onrender.com
VITE_SOCKET_URL=https://your-app.onrender.com
```

**Render (Backend)**:
```bash
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
ENVIRONMENT=production
FRONTEND_URL=https://your-app.vercel.app
PORT=10000
```

---

## ✅ Verification & Testing

### 1. Test Backend Health

```bash
# For Vercel Full Stack
curl https://your-app.vercel.app/api/health

# For Railway Backend
curl https://your-app.up.railway.app/health

# For Render Backend
curl https://your-app.onrender.com/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": 1234567890
}
```

### 2. Test Database Connection

```bash
# Visit API health endpoint
curl https://your-app.vercel.app/api/health

# Should show database status
```

### 3. Test User Registration

1. Go to your frontend URL
2. Click "Sign Up"
3. Register a new user
4. Login with credentials
5. Verify profile loads

### 4. Test Data Persistence

1. Create a test post
2. Logout and login again
3. Verify post is still there
4. Restart backend service
5. Verify data persists

---

## 🔧 Troubleshooting

### Vercel: "Function failed to load"

**Solution**:
1. Check `vercel.json` configuration
2. Verify Python runtime version: `python3.12`
3. Check build logs in Vercel dashboard
4. Ensure `api/index.py` exists

### Railway: "Database not connecting"

**Solution**:
1. Wait 30-60 seconds (cold start)
2. Verify `DATABASE_PRIVATE_URL` is set
3. Check PostgreSQL service is "Active"
4. Test with: `curl https://your-app.up.railway.app/api/database/wakeup`

### Render: "502 Bad Gateway"

**Solution**:
1. Render free tier sleeps after 15 min inactivity
2. Upgrade to Starter plan ($7/month) for always-on
3. Or use external pinger (UptimeRobot)
4. Or migrate to Vercel (no cold starts)

### CORS Errors

**Solution**:
1. Add frontend URL to backend environment:
   ```bash
   FRONTEND_URL=https://your-app.vercel.app
   ```
2. Verify CORS headers in API responses
3. Redeploy backend after changes

### Database Connection Timeout

**Solution**:
1. Increase connection timeout:
   ```bash
   DB_CONNECT_TIMEOUT=45
   ```
2. Verify database URL is correct
3. Check database service is running
4. Test connection manually:
   ```bash
   psql "$DATABASE_URL" -c "SELECT 1"
   ```

### Environment Variables Not Working

**Solution**:
1. Verify variables are set in correct platform dashboard
2. Check variable names match exactly (case-sensitive)
3. Redeploy after adding variables
4. Check deployment logs for errors

---

## 🎯 Quick Start Commands

### Generate Secret Keys
```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### Test Database Connection
```bash
# Set your DATABASE_URL
export DATABASE_URL="postgresql://..."

# Test connection
psql "$DATABASE_URL" -c "SELECT version()"
```

### Initialize Database Tables
```bash
# For development with sample data
python seed_data.py --dev

# For production (no sample data)
python create_posts_table.py
```

### Check Deployment Status
```bash
# Vercel
vercel ls

# Railway
railway status

# Render
# Check dashboard.render.com
```

---

## 📚 Additional Resources

### Official Documentation
- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Render Documentation](https://docs.render.com)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Project-Specific Guides
- [Vercel Postgres Setup Guide](./VERCEL_POSTGRES_SETUP.md)
- [Railway Database Setup Guide](./RAILWAY_DATABASE_SETUP.md)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [README](./README.md)

### Need Help?
- Open a GitHub Issue in the repository
- Review [Troubleshooting](#troubleshooting) section
- Consult platform-specific documentation

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] Backend health endpoint responds: `/api/health`
- [ ] Database connection works: `"database": "connected"`
- [ ] Frontend loads correctly
- [ ] User registration works
- [ ] User login works
- [ ] Profile page loads
- [ ] Posts can be created
- [ ] Data persists after restart
- [ ] CORS configured correctly
- [ ] SSL/HTTPS working
- [ ] Environment variables set
- [ ] No console errors in browser

**🎊 Congratulations!** Your HireMeBahamas app is fully deployed and connected!

---

*Last Updated: December 2025*
*For issues or questions, open a GitHub issue or check the troubleshooting section.*

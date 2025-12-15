# Quick Start: FINAL SPEED ARCHITECTURE

Get HireMeBahamas running in production with the FINAL SPEED ARCHITECTURE in **under 30 minutes**.

## 🎯 What You'll Deploy

```
Users → Vercel Edge CDN → Render FastAPI → Neon PostgreSQL
```

- Frontend: Vercel (Free)
- Backend: Render Standard ($25/month)
- Database: Neon (Free or $19/month)

## ⚡ 30-Minute Setup

### Prerequisites

- [ ] GitHub account
- [ ] Vercel account (sign up at [vercel.com](https://vercel.com))
- [ ] Render account (sign up at [render.com](https://render.com))
- [ ] Neon account (sign up at [neon.tech](https://neon.tech))

---

## Step 1: Database Setup (5 minutes)

### Create Neon PostgreSQL Database

1. **Go to [neon.tech](https://neon.tech)** → Sign up or log in
2. **Click "New Project"**
3. **Configure**:
   - Name: `hiremebahamas`
   - Region: `US West` (closest to Render Oregon)
   - PostgreSQL Version: `16` (latest)
4. **Copy Connection String**:
   ```
   postgresql://user:password@ep-xxxxx.us-west-2.aws.neon.tech/hiremebahamas?sslmode=require
   ```
5. **Save it** - you'll need this for Render

✅ **Checkpoint**: You have a Neon connection string

---

## Step 2: Backend Setup (10 minutes)

### Deploy to Render

1. **Go to [dashboard.render.com](https://dashboard.render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect GitHub** → Select `HireMeBahamas` repository
4. **Configure Service**:
   
   **Basic Settings**:
   - Name: `hiremebahamas-backend`
   - Region: `Oregon`
   - Branch: `main`
   - Root Directory: (leave blank)
   - Runtime: `Python 3`
   
   **Build & Start**:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`
   
   **Plan**:
   - Select: **Standard** ($25/month)
   - ⚠️ Important: Standard plan is required for Always On (no cold starts)

5. **Environment Variables** - Add these in Render Dashboard:

   ```env
   # Required
   ENVIRONMENT=production
   DATABASE_URL=<paste-your-neon-connection-string>
   SECRET_KEY=<generate-below>
   JWT_SECRET_KEY=<generate-below>
   FRONTEND_URL=https://hiremebahamas.vercel.app
   
   # System
   PYTHONUNBUFFERED=true
   PYTHON_VERSION=3.12.0
   
   # Database Pool Settings (optimized for Neon)
   DB_POOL_SIZE=5
   DB_MAX_OVERFLOW=10
   DB_POOL_TIMEOUT=30
   DB_POOL_RECYCLE=3600
   DB_ECHO=false
   
   # Performance
   WORKERS=1
   WORKER_CLASS=uvicorn.workers.UvicornWorker
   KEEPALIVE=5
   TIMEOUT=30
   FORWARDED_ALLOW_IPS=*
   ```

6. **Generate Secrets** (run locally):
   ```bash
   # Generate SECRET_KEY
   python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
   
   # Generate JWT_SECRET_KEY
   python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
   ```
   
   ⚠️ **IMPORTANT**: Save these values securely! You'll need them for Render.
   
   **Why not use Render's generateValue?**
   - Render regenerates secrets on every restart
   - This invalidates all existing JWT tokens
   - Users would be logged out on every deployment
   - Use manually generated secrets for consistency

7. **Health Check Settings**:
   - Click "Advanced" → "Health Check"
   - Health Check Path: `/health`
   - Grace Period: `60` seconds
   - Health Check Timeout: `10` seconds
   - Health Check Interval: `30` seconds

8. **Click "Create Web Service"**

   Render will now:
   - Clone your repository
   - Install dependencies
   - Start the FastAPI server
   - This takes ~5 minutes

9. **Wait for deployment** - Status will show "Live" when ready

10. **Test Backend**:
    ```bash
    curl https://hiremebahamas-backend.onrender.com/health
    ```
    Should return: `{"status": "ok"}`

✅ **Checkpoint**: Backend is live on Render

---

## Step 3: Initialize Database (2 minutes)

### Create Database Tables

You have two options:

**Option A: Using Render Shell** (recommended)

1. In Render Dashboard → Your service → "Shell" tab
2. Run:
   ```bash
   cd backend
   python create_all_tables.py
   ```

**Option B: Locally**

1. Set environment variable locally:
   ```bash
   export DATABASE_URL="<your-neon-connection-string>"
   ```
2. Run:
   ```bash
   cd backend
   python create_all_tables.py
   ```

✅ **Checkpoint**: Database tables created

---

## Step 4: Frontend Setup (10 minutes)

### Deploy to Vercel

1. **Go to [vercel.com/new](https://vercel.com/new)**
2. **Import Git Repository** → Select `HireMeBahamas`
3. **Configure Project**:
   
   **Framework Preset**: Vite
   
   **Root Directory**: `frontend`
   
   **Build Settings**:
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

4. **Environment Variables** - Add in Vercel Dashboard:

   **Option A: Separate Backend (Recommended)**
   ```env
   VITE_API_URL=https://hiremebahamas-backend.onrender.com
   ```

   **Option B: Same-Origin (No env var needed)**
   - Don't set `VITE_API_URL`
   - Frontend will use relative paths `/api/*`
   - Requires Vercel rewrites configuration (already in `vercel.json`)

5. **Click "Deploy"**

   Vercel will:
   - Install dependencies
   - Build the React app
   - Deploy to global CDN
   - This takes ~2 minutes

6. **Wait for deployment** - You'll get a URL like `https://hiremebahamas-xxxx.vercel.app`

7. **Test Frontend**:
   - Visit your Vercel URL
   - You should see the HireMeBahamas homepage

✅ **Checkpoint**: Frontend is live on Vercel

---

## Step 5: Connect Frontend to Backend (3 minutes)

### Update CORS Settings

1. **Update Render Environment Variables**:
   - Go to Render Dashboard → Your service → Environment
   - Update `FRONTEND_URL` to your actual Vercel URL:
     ```
     FRONTEND_URL=https://hiremebahamas-xxxx.vercel.app
     ```
   - Save (triggers redeploy)

2. **Update Vercel Environment Variables** (if using Option A):
   - Go to Vercel Dashboard → Your project → Settings → Environment Variables
   - Verify `VITE_API_URL` points to your Render backend:
     ```
     VITE_API_URL=https://hiremebahamas-backend.onrender.com
     ```
   - Redeploy if changed

3. **Test Connection**:
   - Visit your Vercel URL
   - Try to register a new account
   - Try to log in
   - Create a post

✅ **Checkpoint**: Frontend and backend are connected

---

## 🎉 Success! You're Live!

Your FINAL SPEED ARCHITECTURE is now running:

- ✅ Frontend: Fast global CDN
- ✅ Backend: Always On, zero cold starts
- ✅ Database: Serverless PostgreSQL
- ✅ SSL/TLS: Encrypted everywhere

### Your URLs

- Frontend: `https://hiremebahamas-xxxx.vercel.app`
- Backend: `https://hiremebahamas-backend.onrender.com`
- API Health: `https://hiremebahamas-backend.onrender.com/health`
- API Docs: `https://hiremebahamas-backend.onrender.com/docs` (if enabled)

---

## 📊 Monitor Your Deployment

### Vercel Analytics

1. Go to Vercel Dashboard → Your project → Analytics
2. See real-time traffic, performance metrics, Core Web Vitals

### Render Metrics

1. Go to Render Dashboard → Your service → Metrics
2. See CPU, memory, request latency, error rates

### Neon Insights

1. Go to Neon Console → Your project → Monitoring
2. See query performance, connections, storage usage

---

## 🔧 Troubleshooting

### Backend Not Starting

**Check Render Logs**:
1. Go to Render Dashboard → Your service → Logs
2. Look for error messages
3. Common issues:
   - Missing environment variables
   - Invalid DATABASE_URL
   - Python dependency errors

**Fix**: Verify all environment variables are set correctly

### Frontend Can't Connect to Backend

**Check CORS**:
1. Open browser console (F12)
2. Look for CORS errors
3. Verify `FRONTEND_URL` in Render matches your Vercel URL

**Fix**: Update `FRONTEND_URL` in Render environment variables

### Database Connection Fails

**Check Neon Connection**:
1. Verify Neon project is active (not hibernated)
2. Check connection string format:
   ```
   postgresql://user:password@host:5432/dbname?sslmode=require
   ```
3. Ensure `sslmode=require` is present

**Fix**: 
- Wake up Neon project (visit Neon console)
- Verify DATABASE_URL in Render

### 502 Bad Gateway on Render

**This shouldn't happen with Standard plan**, but if it does:

1. Check if service is starting correctly (Render Logs)
2. Verify health check endpoint responds:
   ```bash
   curl https://hiremebahamas-backend.onrender.com/health
   ```
3. Check Start Command is correct in Render settings

---

## 💰 Monthly Costs

| Service | Plan | Cost |
|---------|------|------|
| Vercel | Free | $0 |
| Render | Standard | $25 |
| Neon | Free* | $0 |
| **Total** | | **$25/month** |

*Neon Free tier: 0.5 GB storage, sufficient for most apps. Upgrade to Pro ($19/month) when needed.

---

## 🚀 Next Steps

1. **Custom Domain** (optional):
   - Add custom domain in Vercel
   - Update `FRONTEND_URL` in Render
   - Update CORS settings

2. **Monitoring** (recommended):
   - Set up Sentry for error tracking
   - Enable Vercel Analytics
   - Configure Render alerts

3. **Backups** (important):
   - Enable Neon point-in-time recovery
   - Set up automated database backups
   - Document your recovery process

4. **Scale** (as needed):
   - Upgrade Neon to Pro for more storage
   - Add more Render instances for high traffic
   - Enable Vercel Pro for team features

---

## 📚 Additional Resources

- [FINAL_SPEED_ARCHITECTURE.md](./FINAL_SPEED_ARCHITECTURE.md) - Complete architecture documentation
- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [Neon Documentation](https://neon.tech/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**🎉 Congratulations! Your FINAL SPEED ARCHITECTURE is live!**

*Fast. Stable. Global. Scalable. Industry-Standard.* ⚡🔒🌍💰🧠

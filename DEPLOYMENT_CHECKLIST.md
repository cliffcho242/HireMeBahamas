# Facebook/Instagram Optimization — Deployment Checklist

## 🎯 Target: < 1s load from Facebook/Instagram | 50-150ms API

Follow these steps in order for a successful deployment.

## Step 1: Neon PostgreSQL (5 minutes) ✅

- [ ] Go to [neon.tech](https://neon.tech)
- [ ] Create new project
- [ ] Select region: **US West 2 (Oregon)** for lowest latency to Render
  - Alternative: **US East (Ohio)** if your users are primarily on East Coast
  - Cross-region latency: ~70-100ms (still acceptable with pooling)
- [ ] Copy the **POOLED** connection string
  - Look for: `ep-xxxx-pooler.REGION.aws.neon.tech` (with `-pooler` suffix)
  - **NOT**: `ep-xxxx.REGION.aws.neon.tech` (direct endpoint)
- [ ] Add `?sslmode=require` to the end if not present
- [ ] Change prefix from `postgresql://` to `postgresql+asyncpg://`
- [ ] Save this connection string for Step 2

**Example format:**
```
# US West (Oregon) - Lowest latency to Render
postgresql+asyncpg://user:pass@ep-xxxx-pooler.us-west-2.aws.neon.tech:5432/db?sslmode=require

# US East (Ohio) - Good for East Coast users
postgresql+asyncpg://user:pass@ep-xxxx-pooler.us-east-1.aws.neon.tech:5432/db?sslmode=require
```

## Step 2: Render Backend (10 minutes) ✅

### 2.1 Create Service
- [ ] Go to [render.com](https://render.com)
- [ ] Click "New +" → "Web Service"
- [ ] Connect your GitHub repository
- [ ] Select repository: `cliffcho242/HireMeBahamas`

### 2.2 Configure Service
- [ ] Name: `hiremebahamas-fastapi`
- [ ] Region: **Oregon** (US West)
- [ ] Branch: `main` (or your production branch)
- [ ] Root Directory: Leave blank
- [ ] Environment: **Python 3**
- [ ] Build Command: `pip install --upgrade pip && pip install --only-binary=:all: -r backend/requirements.txt`
- [ ] Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --loop uvloop`

### 2.3 Select Plan
- [ ] Plan: **Standard ($25/month)**
  - Required for Always-On (zero cold starts)
  - 1GB RAM (sufficient for connection pool)
  - Auto-scaling support

### 2.4 Environment Variables
Add these in the Environment section:

```bash
ENVIRONMENT=production
SECRET_KEY=<generate-random-32-chars>
FRONTEND_URL=https://your-app.vercel.app

# Database (from Step 1)
DATABASE_URL=<your-neon-pooled-connection-string>
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=5
DB_POOL_RECYCLE=300
DB_CONNECT_TIMEOUT=10
DB_SSL_MODE=require

# Security
FORWARDED_ALLOW_IPS=*
DEBUG=false
```

- [ ] Click "Create Web Service"
- [ ] Wait for deployment (2-5 minutes)
- [ ] Copy your Render URL (e.g., `https://hiremebahamas-fastapi.onrender.com`)

### 2.5 Verify Deployment
- [ ] Test health endpoint:
  ```bash
  curl https://your-app.onrender.com/health
  ```
  Should return: `{"status": "ok"}`

- [ ] Test database connection:
  ```bash
  curl https://your-app.onrender.com/ready/db
  ```
  Should return: `{"status": "ready", "database": "connected"}`

## Step 3: Vercel Frontend (5 minutes) ✅

### 3.1 Deploy to Vercel
- [ ] Go to [vercel.com](https://vercel.com)
- [ ] Click "Add New..." → "Project"
- [ ] Import your GitHub repository
- [ ] Select repository: `cliffcho242/HireMeBahamas`

### 3.2 Configure Build
- [ ] Framework Preset: **Vite**
- [ ] Root Directory: `frontend`
- [ ] Build Command: `npm run build` (auto-detected)
- [ ] Output Directory: `dist` (auto-detected)

### 3.3 Environment Variables
Add these in the Environment Variables section:

```bash
VITE_API_URL=https://your-app.onrender.com
```

Optional (if using OAuth):
```bash
VITE_GOOGLE_CLIENT_ID=your-google-client-id
VITE_APPLE_CLIENT_ID=your-apple-client-id
```

- [ ] Click "Deploy"
- [ ] Wait for deployment (2-3 minutes)
- [ ] Copy your Vercel URL (e.g., `https://your-app.vercel.app`)

### 3.4 Update Frontend HTML
- [ ] Open `frontend/index.html`
- [ ] Find line ~79 (preconnect link)
- [ ] Update URL to your Render backend:
  ```html
  <link rel="preconnect" href="https://your-app.onrender.com" crossorigin />
  ```
- [ ] Commit and push changes
- [ ] Vercel will auto-deploy

### 3.5 Update Backend CORS
- [ ] Go to Render dashboard
- [ ] Select your web service
- [ ] Environment → Edit `FRONTEND_URL`
- [ ] Set to your Vercel URL: `https://your-app.vercel.app`
- [ ] Save (triggers redeploy)

## Step 4: Optional Redis Caching (5 minutes) 🚀

For sub-100ms API responses:

- [ ] Go to [upstash.com](https://upstash.com)
- [ ] Create free account
- [ ] Create Redis database
- [ ] Select region: **US East** (close to Neon)
- [ ] Copy Redis URL (format: `redis://:password@region.upstash.io:port`)
- [ ] Add to Render environment variables:
  ```bash
  REDIS_URL=redis://:password@region.upstash.io:port
  ```
- [ ] Save (triggers redeploy)

## Step 5: Verification (5 minutes) ✅

### 5.1 Test Health Endpoints
```bash
# Quick health check (< 5ms)
curl https://your-app.onrender.com/health

# Database health check (< 50ms)
curl https://your-app.onrender.com/ready/db

# Detailed health check
curl https://your-app.onrender.com/health/detailed
```

### 5.2 Test Frontend
- [ ] Open `https://your-app.vercel.app` in browser
- [ ] Open DevTools → Network tab
- [ ] Check load time: should be < 1s
- [ ] Check API calls: should be 50-150ms

### 5.3 Test from Mobile
- [ ] Open your Vercel URL on mobile
- [ ] Share on Facebook/Instagram
- [ ] Click link from Facebook/Instagram app
- [ ] Verify fast load (< 1s)

## Step 6: Monitor Performance 📊

### Render Metrics
- [ ] Go to Render dashboard
- [ ] Select your web service
- [ ] Click "Metrics" tab
- [ ] Monitor:
  - Response times (target: 50-150ms)
  - Memory usage (should be < 500MB)
  - CPU usage (should be < 30%)
  - Error rate (should be 0%)

### Vercel Analytics
- [ ] Go to Vercel dashboard
- [ ] Select your project
- [ ] Click "Analytics" tab
- [ ] Monitor:
  - Page load times (target: < 1s)
  - First contentful paint (target: < 500ms)
  - Time to interactive (target: < 2s)

## 🎉 Success Criteria

Your deployment is successful when all of these are true:

- ✅ `/health` responds in < 5ms
- ✅ `/ready/db` responds in < 50ms with "connected"
- ✅ `/api/jobs` responds in 50-150ms
- ✅ Frontend loads in < 1s from Facebook/Instagram
- ✅ No errors in Render logs
- ✅ No errors in Vercel logs
- ✅ Zero cold start delays
- ✅ Database pool is stable

## 🔧 Troubleshooting

### Backend not responding
1. Check Render logs for errors
2. Verify DATABASE_URL is correct (pooled endpoint)
3. Test database connection independently
4. Check environment variables

### Frontend can't connect to backend
1. Verify VITE_API_URL in Vercel
2. Check FRONTEND_URL in Render
3. Verify CORS is configured correctly
4. Test backend health endpoint directly

### High API latency (> 200ms)
1. Verify using Neon pooled endpoint (has `-pooler`)
2. Check Render plan is Standard (not Free)
3. Add Redis caching (Step 4)
4. Check Render metrics for resource usage

### Database connection errors
1. Verify connection string format
2. Check `sslmode=require` is present
3. Confirm using `postgresql+asyncpg://` prefix
4. Test connection from Render logs

## 📞 Support

If you encounter issues:

1. **Render Logs**: https://dashboard.render.com/logs
2. **Vercel Logs**: https://vercel.com/dashboard/deployments
3. **Neon Metrics**: https://console.neon.tech/app/projects
4. **Documentation**: See `FACEBOOK_OPTIMIZATION_GUIDE.md`

## 💡 Next Steps

After successful deployment:

1. **Custom Domain**: Add your domain to Vercel
2. **Monitoring**: Set up alerts in Render
3. **Backup**: Enable Neon point-in-time recovery
4. **CDN**: Leverage Vercel Edge Network (automatic)
5. **Security**: Enable Vercel firewall rules

## 📊 Cost Breakdown

- **Vercel**: Free (Hobby tier)
- **Render**: $25/month (Standard plan)
- **Neon**: Free (up to 3GB)
- **Upstash**: Free (10k requests/day)

**Total**: ~$25/month for production-grade performance

---

**Last Updated**: December 2025  
**Estimated Time**: 30 minutes total

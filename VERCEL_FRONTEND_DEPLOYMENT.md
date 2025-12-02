# Vercel Frontend Deployment Guide

## Overview

This guide ensures the HireMeBahamas frontend is properly deployed and active on Vercel with full Postgres backend integration.

---

## ✅ Prerequisites

- [ ] Vercel account created
- [ ] GitHub repository connected to Vercel
- [ ] Vercel Postgres database created (see [VERCEL_POSTGRES_MIGRATION_GUIDE.md](./VERCEL_POSTGRES_MIGRATION_GUIDE.md))

---

## 🚀 Step-by-Step Deployment

### Step 1: Connect Repository to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New Project"**
3. Select **"Import Git Repository"**
4. Choose **cliffcho242/HireMeBahamas**
5. Click **"Import"**

### Step 2: Configure Project Settings

On the project configuration page:

#### Framework Preset
- **Framework**: `Vite` (auto-detected)
- **Root Directory**: Leave as `.` (root)

#### Build & Development Settings
- **Build Command**: `cd frontend && npm ci && npm run build`
- **Output Directory**: `frontend/dist`
- **Install Command**: `cd frontend && npm ci`

These are already configured in `vercel.json`, so Vercel will use them automatically.

### Step 3: Set Environment Variables

Click **"Environment Variables"** and add the following:

#### Required Variables (Backend/Database)

| Variable Name | Value | Environment |
|--------------|-------|-------------|
| `DATABASE_URL` | `@postgres_url` | Production, Preview, Development |
| `POSTGRES_URL` | `@postgres_url` | Production, Preview, Development |
| `SECRET_KEY` | Generate with: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` | Production, Preview, Development |
| `JWT_SECRET_KEY` | Generate with: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` | Production, Preview, Development |
| `ENVIRONMENT` | `production` | Production |

**Note**: `@postgres_url` is a Vercel environment variable that gets automatically populated when you link your Vercel Postgres database.

#### Optional Variables (Frontend)

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `VITE_API_URL` | Leave empty for same-domain | API URL (optional) |
| `VITE_SOCKET_URL` | Leave empty for same-domain | WebSocket URL (optional) |
| `VITE_GOOGLE_CLIENT_ID` | Your Google OAuth client ID | OAuth (optional) |
| `VITE_APPLE_CLIENT_ID` | Your Apple OAuth client ID | OAuth (optional) |

**Note**: If `VITE_API_URL` is not set, the frontend will use the same domain for API calls (e.g., `https://your-app.vercel.app/api`).

### Step 4: Link Vercel Postgres Database

1. In your project dashboard, go to **Storage** tab
2. If you already created a Postgres database, click **"Connect Store"**
3. Select your existing Postgres database
4. Click **"Connect"**

This automatically sets the `POSTGRES_URL` environment variable.

### Step 5: Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes for build and deployment
3. Vercel will show deployment status

### Step 6: Verify Deployment

Once deployment completes:

#### Test Frontend
```bash
# Visit your app URL (shown in Vercel dashboard)
https://your-app.vercel.app

# Should show the HireMeBahamas homepage
```

#### Test API Health
```bash
curl https://your-app.vercel.app/health

# Expected: {"status":"healthy"}
```

#### Test Database Connection
```bash
curl https://your-app.vercel.app/ready

# Expected: {"status":"ready","database":"connected","initialized":true}
```

#### Test Full Functionality
1. Open https://your-app.vercel.app in browser
2. Click **"Register"** and create a test account
3. Verify email and password work
4. Check profile page loads
5. Create a test post
6. Verify post appears in feed

---

## 🔧 Troubleshooting

### Issue: "Build Failed" - Frontend not building

**Symptoms:**
- Vercel shows "Build Failed" error
- Frontend doesn't load

**Solution:**
1. Check build logs in Vercel dashboard
2. Verify `package.json` exists in `frontend/` directory
3. Check for missing dependencies:
   ```bash
   cd frontend && npm ci && npm run build
   ```
4. Look for TypeScript or ESLint errors in build logs

**Common Fixes:**
```bash
# If dependencies are missing, update package-lock.json
cd frontend
npm install
git add package-lock.json
git commit -m "Update frontend dependencies"
git push origin main
```

### Issue: "404 Not Found" - Routes not working

**Symptoms:**
- Homepage loads but other routes show 404
- API endpoints return 404

**Solution:**
Ensure `vercel.json` has proper routing configuration (already configured):
```json
{
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/$1"
    },
    {
      "handle": "filesystem"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

### Issue: "Cannot connect to database"

**Symptoms:**
- `/ready` endpoint returns 503
- Database queries fail

**Solution:**
1. Verify Postgres database is linked:
   - Go to **Storage** tab in Vercel
   - Check database status is "Active"
2. Verify environment variables are set:
   - Go to **Settings** → **Environment Variables**
   - Check `DATABASE_URL` and `POSTGRES_URL` are present
3. Check database connection string format:
   ```
   postgresql://default:PASSWORD@ep-xxxxx.neon.tech:5432/verceldb?sslmode=require
   ```
4. Redeploy to apply environment variable changes

### Issue: "API returns CORS errors"

**Symptoms:**
- Browser console shows CORS errors
- API calls fail from frontend

**Solution:**
Already handled! The backend (`backend/app/main.py`) includes CORS middleware:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

If you want to restrict origins:
1. Set `FRONTEND_URL` environment variable
2. Update CORS configuration to use it

### Issue: Frontend shows old version after deployment

**Symptoms:**
- Changes pushed to GitHub but not visible on Vercel
- Old content still showing

**Solution:**
1. **Clear Vercel cache**:
   - Go to Vercel Dashboard → Your Project
   - Click **"Deployments"**
   - Find latest deployment
   - Click **"..."** → **"Redeploy"**
   - Check **"Use existing Build Cache"** = OFF
   - Click **"Redeploy"**

2. **Clear browser cache**:
   - Press `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
   - Or use incognito/private browsing mode

### Issue: Environment variables not updating

**Symptoms:**
- Changed environment variables but app still uses old values

**Solution:**
1. Update environment variables in Vercel Dashboard
2. **Must redeploy** for changes to take effect:
   - Go to **Deployments**
   - Click **"..."** on latest deployment
   - Click **"Redeploy"**

---

## 📊 Monitoring Deployment Health

### Vercel Dashboard Metrics

Access: **Vercel Dashboard → Your Project → Analytics**

Monitor:
- **Response Time**: Should be <200ms for most requests
- **Error Rate**: Should be <1%
- **Bandwidth Usage**: Track monthly usage
- **Function Invocations**: Track API usage

### Database Metrics

Access: **Vercel Dashboard → Storage → Your Database → Insights**

Monitor:
- **Storage Usage**: Should stay under plan limits
- **Compute Hours**: Track monthly usage (Hobby plan: 60 hours/month)
- **Active Connections**: Should be <10 for most apps
- **Query Performance**: Identify slow queries

### Custom Monitoring

Add monitoring endpoints to your app:

```python
# Already implemented in backend/app/main.py
@app.get("/health")
async def health():
    """Basic health check"""
    return {"status": "healthy"}

@app.get("/ready")
async def ready():
    """Database health check"""
    # Returns database connection status
```

Test endpoints:
```bash
# Health check (no database)
curl https://your-app.vercel.app/health

# Readiness check (includes database)
curl https://your-app.vercel.app/ready
```

---

## 🔄 Continuous Deployment

### Automatic Deployments

Vercel automatically deploys when you push to GitHub:

- **Push to `main`**: Deploys to production
- **Push to other branches**: Creates preview deployment
- **Pull requests**: Creates preview deployment with URL

### Preview Deployments

For each PR, Vercel creates a preview deployment:

1. Go to your PR on GitHub
2. Vercel bot comments with preview URL
3. Test changes on preview URL
4. Merge PR to deploy to production

### Deployment Notifications

Configure Slack/Discord notifications:

1. Go to **Settings** → **Integrations**
2. Connect Slack or Discord
3. Choose notification preferences:
   - Deployment started
   - Deployment ready
   - Deployment failed

---

## 🚀 Production Best Practices

### 1. Custom Domain

Add your custom domain:

1. Go to **Settings** → **Domains**
2. Click **"Add"**
3. Enter domain: `hiremebahamas.com`
4. Follow DNS configuration instructions
5. Wait for DNS propagation (5-60 minutes)

### 2. HTTPS/SSL

Automatically enabled by Vercel:
- ✅ Free SSL certificates
- ✅ Automatic renewal
- ✅ HTTP to HTTPS redirect
- ✅ HSTS headers (already in `vercel.json`)

### 3. Performance Optimization

Already configured in `vercel.json`:
- ✅ Asset caching (1 year for immutable assets)
- ✅ Compression (Gzip/Brotli)
- ✅ Edge caching
- ✅ Security headers

### 4. Error Tracking

Consider adding:
- **Sentry**: Error monitoring
- **LogRocket**: Session replay
- **Google Analytics**: User tracking

Set in environment variables:
```bash
VITE_SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
VITE_GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

### 5. Backup Strategy

- **Database backups**: Automatic on Vercel Postgres
- **Code backups**: GitHub is the source of truth
- **Manual exports**: Use migration scripts from [VERCEL_POSTGRES_MIGRATION_GUIDE.md](./VERCEL_POSTGRES_MIGRATION_GUIDE.md)

---

## 📋 Deployment Checklist

Use this checklist for each deployment:

### Pre-Deployment
- [ ] All tests passing locally
- [ ] Environment variables documented
- [ ] Database migrations ready (if any)
- [ ] API endpoints tested
- [ ] Frontend builds successfully

### Deployment
- [ ] Push to GitHub `main` branch
- [ ] Monitor Vercel deployment status
- [ ] Check deployment logs for errors
- [ ] Wait for "Deployment Ready" notification

### Post-Deployment
- [ ] Test homepage loads
- [ ] Test user authentication
- [ ] Test API endpoints
- [ ] Test database connectivity
- [ ] Check performance metrics
- [ ] Verify custom domain (if configured)

### Health Checks
```bash
# Run these commands after each deployment
curl https://your-app.vercel.app/health
curl https://your-app.vercel.app/ready

# Should both return 200 OK
```

---

## 🎯 Quick Commands

```bash
# Test local build (before deploying)
cd frontend
npm ci
npm run build
npm run preview

# Deploy from CLI (alternative to GitHub push)
npm install -g vercel
vercel --prod

# Check deployment status
vercel ls

# View logs
vercel logs [deployment-url]

# Pull environment variables (for local dev)
vercel env pull
```

---

## 📞 Getting Help

If you encounter issues:

1. **Check Vercel Logs**: Dashboard → Deployments → [Latest] → Logs
2. **Review Documentation**: [Vercel Docs](https://vercel.com/docs)
3. **Check Status**: [Vercel Status Page](https://www.vercel-status.com/)
4. **Support**: [Vercel Support](https://vercel.com/support)

---

## ✅ Success Criteria

Your frontend is properly deployed when:

✅ Homepage loads at `https://your-app.vercel.app`  
✅ All routes work (no 404 errors)  
✅ API endpoints respond (`/health`, `/ready`)  
✅ User registration and login work  
✅ Database queries execute successfully  
✅ Images and assets load  
✅ Custom domain works (if configured)  
✅ HTTPS is enabled  
✅ Performance is good (<200ms response times)  

---

*Last Updated: December 2, 2025*  
*Deployment Guide Version: 1.0*

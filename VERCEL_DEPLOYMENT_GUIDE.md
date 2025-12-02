# HireMeBahamas - Complete Vercel Deployment Guide 🚀

## Overview

This guide will help you deploy the entire HireMeBahamas application (frontend + backend) to Vercel in under 15 minutes. Everything runs on Vercel's platform with zero additional infrastructure needed.

## What You Get

✅ **Frontend**: React/Vite app deployed globally via Vercel Edge Network  
✅ **Backend**: FastAPI serverless functions with all endpoints  
✅ **Database**: Vercel Postgres (or any PostgreSQL with asyncpg support)  
✅ **Zero Cost**: Free tier supports thousands of users  
✅ **Auto HTTPS**: SSL certificates automatically managed  
✅ **Global CDN**: <50ms latency worldwide  
✅ **Auto Scaling**: Handles traffic spikes automatically  

## Prerequisites

1. **GitHub Account** - Repository must be pushed to GitHub
2. **Vercel Account** - Sign up at [vercel.com](https://vercel.com) (free)
3. **Vercel Postgres** - Or any PostgreSQL database with connection string

## Step-by-Step Deployment

### Step 1: Prepare Your Database

#### Option A: Vercel Postgres (Recommended)

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click **Storage** → **Create Database** → **Postgres**
3. Choose a name (e.g., "hiremebahamas-db")
4. Select region closest to your users
5. Click **Create**
6. Save your connection strings (you'll need these)

#### Option B: External PostgreSQL

If using Railway, Neon, or another provider:
- Ensure your database allows connections from Vercel's IP ranges
- Have your connection string ready in this format:
  ```
  postgresql://user:password@host:5432/database
  ```

### Step 2: Deploy to Vercel

1. **Import Repository**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click **Import Git Repository**
   - Select your `HireMeBahamas` repository
   - Click **Import**

2. **Configure Project**
   - **Framework Preset**: Vite
   - **Root Directory**: `./` (leave as is)
   - **Build Command**: `cd frontend && npm ci && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `cd frontend && npm ci`

3. **Add Environment Variables**
   
   Click **Environment Variables** and add the following:

   **Required:**
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database
   SECRET_KEY=your-secret-key-here-generate-random-32-chars
   JWT_SECRET_KEY=your-jwt-secret-key-generate-random-32-chars
   ENVIRONMENT=production
   ```

   **Optional (if using Vercel Postgres):**
   ```env
   POSTGRES_URL=your-vercel-postgres-url
   POSTGRES_PRISMA_URL=your-prisma-url
   POSTGRES_URL_NON_POOLING=your-non-pooling-url
   ```

   **Generate Secrets:**
   ```bash
   # On Linux/Mac
   openssl rand -base64 32
   
   # On Windows (PowerShell)
   -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
   ```

4. **Deploy**
   - Click **Deploy**
   - Wait 2-3 minutes for build to complete
   - Your app will be live at `https://your-project.vercel.app`

### Step 3: Initialize Database

After first deployment, initialize your database tables:

1. **Run Migration Script**
   
   You have two options:

   **Option A: Using Vercel CLI (Recommended)**
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Login
   vercel login
   
   # Link to your project
   vercel link
   
   # Run initialization script
   vercel env pull .env.local
   python -c "from backend.app.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

   **Option B: Using Database Client**
   
   Connect to your database and run:
   ```sql
   -- Create tables (schema is in backend/app/models.py)
   -- You can also use the create_tables.py script
   ```

2. **Create Admin User**
   ```bash
   # Use Vercel CLI to run
   python create_admin.py
   ```

### Step 4: Verify Deployment

1. **Check API Health**
   - Visit: `https://your-project.vercel.app/api/health`
   - Should return: `{"status":"healthy","platform":"vercel-serverless"}`

2. **Check Database Connection**
   - Visit: `https://your-project.vercel.app/api/ready`
   - Should return: `{"status":"ready","database":"connected"}`

3. **Test Frontend**
   - Visit: `https://your-project.vercel.app`
   - You should see the HireMeBahamas landing page
   - Try registering a new user
   - Try logging in

### Step 5: Configure Custom Domain (Optional)

1. Go to your project settings in Vercel
2. Click **Domains**
3. Add your custom domain (e.g., `hiremebahamas.com`)
4. Follow DNS configuration instructions
5. Wait for DNS propagation (5-30 minutes)

## Architecture Overview

```
User Request
     ↓
Vercel Edge Network (Global CDN)
     ↓
     ├→ Static Files → frontend/dist/
     │   (HTML, CSS, JS, Images)
     │
     └→ API Requests → /api/*
         ↓
         Python Serverless Functions
         (api/index.py + backend_app/)
         ↓
         PostgreSQL Database
         (Vercel Postgres or External)
```

## File Structure

```
HireMeBahamas/
├── frontend/              # React/Vite frontend
│   ├── src/
│   ├── dist/             # Build output (generated)
│   └── package.json
├── api/                  # Vercel serverless functions
│   ├── index.py         # Main API handler
│   ├── backend_app/     # Backend modules (copy of backend/app/)
│   └── requirements.txt # Python dependencies
├── backend/             # Original backend source
│   └── app/            # FastAPI application
├── vercel.json         # Vercel configuration
└── .vercelignore      # Files to exclude from deployment
```

## Environment Variables Reference

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host/db` |
| `SECRET_KEY` | Flask session secret (32+ chars) | `your-random-secret-key` |
| `JWT_SECRET_KEY` | JWT token signing key (32+ chars) | `your-random-jwt-secret` |
| `ENVIRONMENT` | Deployment environment | `production` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_URL` | Vercel Postgres primary URL | (from Vercel) |
| `TOKEN_EXPIRATION_DAYS` | JWT token validity period | `365` |
| `CLOUDINARY_NAME` | Cloudinary account for images | (optional) |
| `SENDBIRD_APP_ID` | Sendbird for messaging | (optional) |

## Troubleshooting

### Build Failures

**Error: "ModuleNotFoundError"**
```
Solution: Check that api/requirements.txt includes all dependencies
```

**Error: "Build exceeded time limit"**
```
Solution: Optimize dependencies, remove unused packages
```

### Runtime Errors

**Error: "Database connection failed"**
```
Solution: 
1. Check DATABASE_URL format: must use postgresql+asyncpg://
2. Verify database is accessible from Vercel IPs
3. Check firewall rules allow connections
```

**Error: "500 Internal Server Error"**
```
Solution:
1. Check Vercel function logs: vercel logs [deployment-url]
2. Verify all environment variables are set
3. Check database connection in /api/ready endpoint
```

**Error: "CORS errors in browser"**
```
Solution: Verify frontend is using same-origin API calls
The frontend should automatically detect Vercel deployment
```

### Performance Issues

**Slow API Response**
```
Solution:
1. Check database query performance
2. Add indexes to frequently queried columns
3. Enable connection pooling in DATABASE_URL
4. Consider Vercel Postgres for lowest latency
```

**Cold Starts**
```
Note: First request after inactivity may take 1-2 seconds
This is normal for serverless functions on free tier
Pro plan reduces cold starts significantly
```

## Monitoring

### View Logs

```bash
# Install Vercel CLI
npm i -g vercel

# View real-time logs
vercel logs --follow

# View specific deployment
vercel logs [deployment-url]
```

### Built-in Monitoring

Vercel provides:
- **Analytics**: Page views, performance metrics
- **Function Logs**: All API requests and errors  
- **Error Tracking**: Automatic error alerts
- **Performance Insights**: Response times, success rates

Access from: `https://vercel.com/[your-username]/[project]/analytics`

## Updating Your Deployment

### Automatic Updates

Every push to `main` branch automatically triggers:
1. New build
2. Deploy to production
3. Zero-downtime switch to new version

### Manual Deployment

```bash
# Deploy from CLI
vercel --prod

# Deploy specific branch
vercel --prod --branch feature-name
```

### Rollback

If something goes wrong:
1. Go to Vercel Dashboard → Deployments
2. Find previous working deployment
3. Click **Promote to Production**

## Best Practices

### Security
- ✅ Use strong SECRET_KEY and JWT_SECRET_KEY (32+ random characters)
- ✅ Never commit secrets to git
- ✅ Use Vercel environment variables for all sensitive data
- ✅ Enable rate limiting in production
- ✅ Use HTTPS only (automatic with Vercel)

### Performance
- ✅ Use Vercel Postgres for best latency
- ✅ Enable connection pooling
- ✅ Add database indexes for common queries
- ✅ Use CDN for static assets (automatic)
- ✅ Implement caching where appropriate

### Reliability
- ✅ Monitor error rates in Vercel dashboard
- ✅ Set up health check monitoring (e.g., UptimeRobot)
- ✅ Keep database backups (automatic with Vercel Postgres)
- ✅ Test thoroughly before deploying to production

## Cost Estimate

### Free Tier Limits

**Vercel:**
- ✅ 100 GB bandwidth/month
- ✅ Unlimited requests
- ✅ 100 GB-hours serverless function execution
- ✅ 6,000 build minutes/month

**Vercel Postgres:**
- ✅ 256 MB storage
- ✅ 60 hours compute time/month
- ✅ Sufficient for 1,000-10,000 users

**Total Cost:** $0/month for small to medium apps

### When to Upgrade

Consider upgrading to Pro ($20/month) when:
- Traffic exceeds 100 GB/month
- Need faster cold starts
- Want team collaboration features
- Need more compute time

## Support

**Issues?**
- Check `/api/health` and `/api/ready` endpoints
- View Vercel function logs
- Check GitHub Issues
- Review this guide's Troubleshooting section

**Need Help?**
- Create issue on GitHub
- Check Vercel documentation: [vercel.com/docs](https://vercel.com/docs)
- Vercel support: [vercel.com/support](https://vercel.com/support)

## Success Checklist

- [ ] GitHub repository is up to date
- [ ] Vercel project created and linked
- [ ] Database created (Vercel Postgres or external)
- [ ] Environment variables configured
- [ ] Deployment successful (check build logs)
- [ ] `/api/health` returns healthy status
- [ ] `/api/ready` shows database connected
- [ ] Frontend loads successfully
- [ ] User registration works
- [ ] User login works
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up

## Next Steps

After successful deployment:

1. **Test All Features**
   - User registration and login
   - Job posting
   - Social features (posts, comments, likes)
   - Messaging
   - Profile updates

2. **Configure Monitoring**
   - Set up Vercel Analytics
   - Enable error alerts
   - Monitor performance metrics

3. **Optimize**
   - Add database indexes
   - Enable caching
   - Optimize images

4. **Scale**
   - Monitor usage
   - Upgrade tier if needed
   - Consider Vercel Postgres Pro for more storage

---

**Congratulations! Your app is now live on Vercel! 🎉**

Access your app at: `https://your-project.vercel.app`

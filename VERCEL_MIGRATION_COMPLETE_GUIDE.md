# Full Migration to Vercel - Complete Guide

## Overview
This guide walks you through migrating the HireMeBahamas platform from Render to Vercel, reducing costs to $0/month while improving performance with <200ms response times globally.

## Architecture Changes

### Before (Render)
- **Backend**: Render Web Service ($7+/month)
- **Keep-Alive**: Background Worker ($7/month)
- **Cron Jobs**: Keep-alive pings
- **Total Cost**: ~$14+/month

### After (Vercel)
- **Backend**: Vercel Serverless Functions (FREE for hobby tier)
- **Frontend**: Vercel Static Hosting (FREE)
- **Cron**: Vercel Cron Jobs (FREE)
- **Total Cost**: $0/month

## Step 1: Vercel Backend Deployment

### 1.1 Verify Configuration Files

The following files have been configured for Vercel deployment:

**Root `vercel.json`:**
```json
{
  "functions": {
    "api/main.py": {
      "runtime": "@vercel/python@1.3.1",
      "maxDuration": 30
    }
  },
  "routes": [
    { "src": "/api/(.*)", "dest": "api/main.py" }
  ]
}
```

**`api/main.py`:**
- Full FastAPI application with Mangum handler for serverless
- All routes from backend/app copied to api/ folder
- Imports updated to use `routes` instead of `api`

**`api/requirements.txt`:**
- Updated with all dependencies including `mangum==0.19.0`
- Binary-only packages to avoid compilation

### 1.2 Push to GitHub

```bash
# Changes are already committed and pushed
git push origin copilot/full-migration-to-vercel
```

### 1.3 Deploy to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New Project"
3. Import your GitHub repository: `cliffcho242/HireMeBahamas`
4. Configure project:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as root)
   - **Build Command**: (leave empty for Python serverless)
   - **Output Directory**: (leave empty)

5. Add Environment Variables:
   ```
   DATABASE_URL=<your-postgres-connection-string>
   SECRET_KEY=<your-secret-key>
   JWT_SECRET_KEY=<your-jwt-secret-key>
   FRONTEND_URL=https://hiremebahamas.vercel.app
   ENVIRONMENT=production
   ```

6. Click "Deploy"

### 1.4 Get Your Vercel Backend URL

After deployment completes:
- Your backend URL will be: `https://your-project-name.vercel.app`
- Test health endpoint: `https://your-project-name.vercel.app/api/health`

## Step 2: Update Frontend Configuration

### 2.1 Set Frontend Environment Variables

In Vercel Dashboard → Your Project → Settings → Environment Variables:

Add:
```
VITE_API_URL=https://your-backend-project.vercel.app
```

### 2.2 Redeploy Frontend

The frontend is already configured to use `VITE_API_URL`. Once you set the environment variable:

1. Go to Vercel Dashboard → Frontend Project
2. Click "Deployments" tab
3. Click "Redeploy" on the latest deployment

## Step 3: Test Deployment

### 3.1 Test Backend Endpoints

```bash
# Health check (should respond in <200ms)
curl https://your-backend.vercel.app/api/health

# Expected response:
# {"status":"healthy","platform":"vercel-serverless","region":"iad1","timestamp":1234567890}

# Ready check (with database)
curl https://your-backend.vercel.app/api/ready
```

### 3.2 Test Frontend

1. Open your frontend URL: `https://hiremebahamas.vercel.app`
2. Try to log in with test credentials
3. Open browser DevTools → Network tab
4. Verify API calls go to your Vercel backend
5. Check response times (should be <200ms)

### 3.3 Test on Mobile

1. Open the site on your phone
2. Try logging in
3. Check Vercel logs: Vercel Dashboard → Your Project → Logs
4. Verify request logs show your mobile traffic
5. Confirm response times are <200ms

## Step 4: Delete Render Services

⚠️ **IMPORTANT**: Only proceed after verifying Vercel deployment works completely!

### 4.1 Delete Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **hiremebahamas-backend** (Web Service)
3. Click **Settings** → Scroll to bottom
4. Click **Delete Service**
5. Type `hiremebahamas-backend` to confirm
6. Click **Delete**

### 4.2 Delete Background Worker (if exists)

1. Click **keep-alive** or **backend-keepalive** (Background Worker)
2. Click **Settings** → Scroll to bottom
3. Click **Delete Service**
4. Type the service name to confirm
5. Click **Delete**

### 4.3 Delete Cron Jobs (if exists)

If you have cron jobs:
1. Click each cron job service
2. Click **Settings** → Delete Service → Confirm

### 4.4 Verify $0 Billing

1. Go to [Render Billing](https://dashboard.render.com/billing)
2. Verify: **$0.00/month** after service deletion
3. Take a screenshot for your records

## Step 5: Configure Custom Domain (Optional)

### 5.1 Add Domain to Vercel

1. Go to Vercel Dashboard → Your Project
2. Click **Settings** → **Domains**
3. Add domain: `hiremebahamas.com`
4. Add domain: `www.hiremebahamas.com`

### 5.2 Update DNS Records

At your DNS provider (e.g., Namecheap):

1. Go to DNS Management
2. Delete old Render A/CNAME records
3. Add Vercel DNS records:

| Type  | Host | Value                | TTL  |
|-------|------|----------------------|------|
| A     | @    | 76.76.21.21          | Auto |
| CNAME | www  | cname.vercel-dns.com | Auto |

### 5.3 Verify Domain

1. Wait 1-5 minutes for DNS propagation
2. Check Vercel Dashboard → Domains for green checkmark ✅
3. Test: `https://hiremebahamas.com`

## Step 6: Monitor Performance

### 6.1 Check Vercel Analytics

1. Vercel Dashboard → Your Project → Analytics
2. Monitor:
   - Response times (should be <200ms)
   - Error rates (should be <1%)
   - Traffic patterns

### 6.2 Check Logs

1. Vercel Dashboard → Your Project → Logs
2. Filter by function: `api/main.py`
3. Verify requests are handled correctly

## Troubleshooting

### Backend Returns 500 Error

Check Vercel function logs:
1. Dashboard → Logs → Filter by "Error"
2. Common issues:
   - Missing environment variables
   - Database connection timeout
   - Python dependency not installed

Fix: Update environment variables or requirements.txt

### Frontend Can't Reach Backend

1. Check `VITE_API_URL` is set correctly
2. Verify CORS headers in vercel.json
3. Check browser console for errors

### Slow Response Times (>200ms)

1. Check database location (should be in same region as Vercel function)
2. Optimize database queries
3. Enable connection pooling
4. Consider upgrading Vercel plan for better performance

## Expected Performance

With Vercel deployment:
- **Cold start**: <1 second (first request)
- **Warm response**: <200ms (subsequent requests)
- **Global CDN**: Fast loading worldwide
- **99.9% uptime**: Vercel SLA

## Cost Comparison

| Service | Render | Vercel | Savings |
|---------|--------|--------|---------|
| Backend Hosting | $7/mo | $0 | $7/mo |
| Keep-Alive Worker | $7/mo | $0 | $7/mo |
| Cron Jobs | Included | $0 | $0 |
| **Total** | **$14/mo** | **$0** | **$14/mo** |

**Annual Savings**: $168/year

## Support

If you encounter issues:
1. Check Vercel Documentation: https://vercel.com/docs
2. Check Vercel Status: https://www.vercel-status.com/
3. GitHub Issues: https://github.com/cliffcho242/HireMeBahamas/issues

## Next Steps

After successful migration:
1. ✅ Monitor performance for 24-48 hours
2. ✅ Update any documentation with new URLs
3. ✅ Notify users of improved performance
4. ✅ Celebrate $0/month hosting! 🎉

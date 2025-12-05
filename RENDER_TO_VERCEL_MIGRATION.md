# 🚀 MASTERMIND FINAL MIGRATION: RENDER → VERCEL 100%

**Date**: 2025  
**Status**: ✅ **MIGRATION COMPLETE - Render References Removed**  
**Goal**: $0/month Render → 100% Vercel Edge + Serverless

---

## ✅ MIGRATION STATUS: COMPLETED

**Date Completed**: December 2025  
**Actions Taken**:
1. ✅ Disabled Render deployment workflow (deploy-backend-render.yml)
2. ✅ Removed Render backend monitoring from GitHub Actions workflows
3. ✅ Updated frontend to use single backend configuration (removed dual Render/Vercel routing)
4. ✅ Updated Python test scripts to use environment variables instead of hardcoded Render URLs
5. ✅ Updated backend code comments to remove Render-specific examples
6. ✅ Preserved legacy scripts with deprecation notices for reference

**Current Architecture**:
- Frontend: Vercel (Edge + Static) - https://hiremebahamas.vercel.app
- Backend: Railway (Python/Flask) OR Vercel Serverless Functions
- Database: Railway PostgreSQL OR Vercel Postgres
- Monitoring: GitHub Actions workflows (keep-database-awake.yml, scheduled-ping.yml, uptime-monitoring.yml)

**To Deploy Backend**:
- Railway: Configure RAILWAY_BACKEND_URL in GitHub Secrets
- Vercel: Backend is automatically deployed with frontend (api/ directory)

---

## LEGACY DOCUMENTATION (For Reference Only)

The sections below document the original migration plan from Render to Vercel.
This migration has been completed, and Render services should be deleted.

---

## SECTION 1: CANCEL RENDER WEB SERVICE + BACKGROUND WORKER

### Step 1.1: Cancel Web Service
1. Go to: https://dashboard.render.com/
2. Click **hiremebahamas-backend** (Web Service)
3. Click **Settings** → Scroll to bottom
4. Click **Delete Service**
5. Type `hiremebahamas-backend` to confirm
6. Click **Delete**

### Step 1.2: Cancel Keep-Alive Worker
1. Click **keep-alive** (Background Worker)
2. Click **Settings** → Scroll to bottom
3. Click **Delete Service**
4. Type `keep-alive` to confirm
5. Click **Delete**

### Step 1.3: Cancel Cron Jobs
1. Click **keepalive-ping** (Cron Job)
2. Click **Settings** → Delete Service → Confirm
3. Click **cache-warmer** (Cron Job)
4. Click **Settings** → Delete Service → Confirm

### Step 1.4: Verify Billing
1. Go to: https://dashboard.render.com/billing
2. Verify: **$0.00/month** after service deletion
3. Screenshot for records

---

## SECTION 2: CUSTOM DOMAIN hiremebahamas.com → VERCEL

### Step 2.1: Add Domain to Vercel
1. Go to: https://vercel.com/dashboard
2. Click your **HireMeBahamas** project
3. Click **Settings** → **Domains**
4. Add domain: `hiremebahamas.com`
5. Add domain: `www.hiremebahamas.com`

### Step 2.2: Update DNS at Namecheap
1. Go to: https://www.namecheap.com/domains/
2. Click **Manage** next to `hiremebahamas.com`
3. Click **Advanced DNS**
4. Delete old Render A/CNAME records
5. Add Vercel DNS records:

| Type  | Host | Value                    | TTL  |
|-------|------|--------------------------|------|
| A     | @    | 76.76.21.21              | Auto |
| CNAME | www  | cname.vercel-dns.com     | Auto |

### Step 2.3: Verify Domain (Wait 1-5 minutes)
1. Go back to Vercel → Settings → Domains
2. Wait for green checkmark ✅
3. Test: `https://hiremebahamas.com`

---

## SECTION 3: ENVIRONMENT VARIABLES → VERCEL

### Step 3.1: Export from Render (Before Deletion)
Copy these from Render Dashboard → Environment:

```bash
# Required Variables (copy values from Render)
SECRET_KEY=<your-secret-key>
JWT_SECRET_KEY=<your-jwt-secret-key>
DATABASE_URL=<your-railway-postgres-url>
DATABASE_PRIVATE_URL=<your-railway-private-url>
FRONTEND_URL=https://hiremebahamas.com
FLASK_ENV=production
ENVIRONMENT=production
```

### Step 3.2: Add to Vercel
1. Go to: https://vercel.com/dashboard → HireMeBahamas
2. Click **Settings** → **Environment Variables**
3. Add each variable:

| Key | Value | Environment |
|-----|-------|-------------|
| `VITE_API_URL` | `https://YOUR-BACKEND-URL` | Production |
| `VITE_SOCKET_URL` | `https://YOUR-BACKEND-URL` | Production |
| `DATABASE_URL` | `<railway-postgres-url>` | Production |
| `SECRET_KEY` | `<your-secret-key>` | Production |
| `JWT_SECRET_KEY` | `<your-jwt-secret-key>` | Production |
| `FRONTEND_URL` | `https://hiremebahamas.com` | Production |

**Note**: Replace `YOUR-BACKEND-URL` with your actual backend URL:
- If using Railway: `https://your-app.up.railway.app`
- If using custom domain: `https://api.hiremebahamas.com` (requires DNS setup)

### Step 3.3: Backend API on Vercel Serverless
Since Vercel is for frontend (static + serverless), the Flask backend needs:
- **Option A**: Deploy backend as Vercel Serverless Functions (Python)
- **Option B**: Keep backend on Railway (recommended for Python/Flask)
- **Option C**: Migrate backend to Vercel Edge Functions with Node.js

**Recommended**: Deploy Flask backend on **Railway** (already has PostgreSQL there)

---

## SECTION 4: REPLACE RENDER KEEP-ALIVE WITH VERCEL CRON

### Step 4.1: Create Vercel Cron Configuration
Add to `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/cron/health",
      "schedule": "*/5 * * * *"
    },
    {
      "path": "/api/cron/warm-cache",
      "schedule": "*/10 * * * *"
    }
  ]
}
```

### Step 4.2: Create Cron Endpoint (if using Vercel Serverless for backend)
Create `api/cron/health.ts`:

```typescript
import type { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // Verify cron secret (optional but recommended)
  if (req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  // Ping backend health endpoint
  try {
    const response = await fetch(`${process.env.BACKEND_URL}/health`);
    const data = await response.json();
    return res.status(200).json({ success: true, backend: data });
  } catch (error) {
    return res.status(500).json({ error: 'Backend health check failed' });
  }
}
```

### Step 4.3: Alternative - Use External Cron Service (Free)
If backend stays on Railway, use:
- **UptimeRobot** (free): https://uptimerobot.com/
- **Cron-job.org** (free): https://cron-job.org/
- **Railway Cron** (built-in)

---

## SECTION 5: RAILWAY POSTGRES CONFIRMATION

### Step 5.1: Verify Railway PostgreSQL
1. Go to: https://railway.app/dashboard
2. Click your PostgreSQL service
3. Copy connection string from **Connect** tab

### Step 5.2: Update Environment Variables
Ensure these are set in your backend deployment:

```bash
DATABASE_URL=postgresql://user:pass@host:5432/railway
DATABASE_PRIVATE_URL=postgresql://user:pass@internal-host:5432/railway
```

### Step 5.3: Test Database Connection
```bash
# Test from local
psql $DATABASE_URL -c "SELECT 1;"
```

### Step 5.4: Vercel Postgres (Optional Migration)
If migrating to Vercel Postgres:
1. Go to: Vercel Dashboard → Storage → Create Database
2. Select PostgreSQL
3. Use `pg_dump` to export Railway data
4. Import to Vercel Postgres
5. Update `DATABASE_URL` in Vercel environment

---

## SECTION 6: REDIRECT RULES (OLD RENDER → NEW VERCEL)

### Step 6.1: Add to vercel.json
```json
{
  "redirects": [
    {
      "source": "/api/:path*",
      "destination": "https://api.hiremebahamas.com/api/:path*",
      "permanent": true
    }
  ]
}
```

### Step 6.2: Handle Old Render URLs (DNS Level)
If you own the subdomain, add CNAME:
- `hiremebahamas.onrender.com` → Cannot redirect (Render owns this)

Instead, update all references in code from:
- `https://hiremebahamas.onrender.com` → `https://api.hiremebahamas.com`

### Step 6.3: Update Frontend Code References
Files to update:
- `frontend/src/services/api.ts`
- `frontend/src/graphql/client.ts`
- `frontend/src/lib/realtime.ts`
- `vercel.json`

---

## SECTION 7: FINAL CONFIGURATION FILES

### 7.1: vercel.json (Root - Complete)
```json
{
  "version": 2,
  "framework": "vite",
  "buildCommand": "cd frontend && npm ci && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm ci",
  "rewrites": [
    {
      "source": "/((?!api/.*).*)",
      "destination": "/index.html"
    }
  ],
  "redirects": [
    {
      "source": "/old-render-path/:path*",
      "destination": "/:path*",
      "permanent": true
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains; preload" },
        { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=(self), payment=()" },
        { "key": "X-DNS-Prefetch-Control", "value": "on" }
      ]
    },
    {
      "source": "/assets/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Vary", "value": "Accept-Encoding" }
      ]
    },
    {
      "source": "/(.*).woff2",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" },
        { "key": "Access-Control-Allow-Origin", "value": "*" }
      ]
    },
    {
      "source": "/(.*).js",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" },
        { "key": "Vary", "value": "Accept-Encoding" }
      ]
    },
    {
      "source": "/(.*).css",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" },
        { "key": "Vary", "value": "Accept-Encoding" }
      ]
    },
    {
      "source": "/(.*).png",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=604800, stale-while-revalidate=86400" }
      ]
    },
    {
      "source": "/(.*).jpg",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=604800, stale-while-revalidate=86400" }
      ]
    },
    {
      "source": "/(.*).jpeg",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=604800, stale-while-revalidate=86400" }
      ]
    },
    {
      "source": "/(.*).svg",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=604800, stale-while-revalidate=86400" }
      ]
    },
    {
      "source": "/(.*).webp",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=604800, stale-while-revalidate=86400" }
      ]
    },
    {
      "source": "/(.*).ico",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=604800" }
      ]
    },
    {
      "source": "/manifest.json",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=86400, stale-while-revalidate=3600" }
      ]
    },
    {
      "source": "/sw.js",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=0, must-revalidate" },
        { "key": "Service-Worker-Allowed", "value": "/" }
      ]
    },
    {
      "source": "/service-worker.js",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=0, must-revalidate" },
        { "key": "Service-Worker-Allowed", "value": "/" }
      ]
    }
  ]
}
```

### 7.2: frontend/.env.production
```bash
# Production Environment - Vercel
# Replace YOUR-BACKEND-URL with your actual backend URL
# Examples:
#   - Railway: https://your-app.up.railway.app
#   - Custom domain: https://api.hiremebahamas.com
VITE_API_URL=https://YOUR-BACKEND-URL
VITE_SOCKET_URL=https://YOUR-BACKEND-URL
VITE_GOOGLE_CLIENT_ID=your-google-client-id
VITE_APPLE_CLIENT_ID=com.hiremebahamas.signin
```

### 7.3: Update api.ts Production URL
In `frontend/src/services/api.ts`, the `DEFAULT_PROD_API` reads from `VITE_API_URL` environment variable.
Set this in Vercel Dashboard → Environment Variables for production.

### 7.4: Update graphql/client.ts
In `frontend/src/graphql/client.ts`, the `DEFAULT_PROD_API` also reads from `VITE_API_URL`.
Set the same environment variable in Vercel.

---

## SECTION 8: 10-STEP FINAL CHECKLIST

### ✅ PRE-MIGRATION (Do First)
- [ ] **Step 1**: Export all Render environment variables to a secure file
- [ ] **Step 2**: Backup current `vercel.json` and frontend code
- [ ] **Step 3**: Verify Railway PostgreSQL is accessible and healthy

### ✅ MIGRATION (Execute)
- [ ] **Step 4**: Update `frontend/src/services/api.ts` - change `DEFAULT_PROD_API`
- [ ] **Step 5**: Update `frontend/src/graphql/client.ts` - change `DEFAULT_PROD_API`
- [ ] **Step 6**: Update `vercel.json` env section with new API URL
- [ ] **Step 7**: Push changes to GitHub → Vercel auto-deploys
- [ ] **Step 8**: Add environment variables to Vercel Dashboard

### ✅ POST-MIGRATION (Verify)
- [ ] **Step 9**: Test all endpoints: login, register, jobs, messages, posts
- [ ] **Step 10**: Delete all Render services (Web Service, Worker, Cron Jobs)

---

## 🎯 EXPECTED RESULTS

| Metric | Before (Render) | After (Vercel) |
|--------|-----------------|----------------|
| Monthly Cost | $25-50 | $0 |
| Cold Start | 2-5 minutes | 0 (Edge) |
| 502 Errors | Frequent | None |
| 499 Errors | Frequent | None |
| Response Time | 500ms-2min | <100ms |
| Global CDN | No | Yes (Edge) |
| Keep-Alive Needed | Yes ($) | No |

---

## 🔥 RENDER IS DEAD. VERCEL LIVES.

**Execute this guide. No mercy. No looking back.**

---

## TROUBLESHOOTING

### If API calls fail after migration:
1. Check CORS settings in backend
2. Verify `VITE_API_URL` is set correctly in Vercel
3. Clear browser cache and service worker

### If domain shows old content:
1. Wait 5 minutes for DNS propagation
2. Clear CDN cache in Vercel Dashboard
3. Force refresh browser (Ctrl+Shift+R)

### If database connection fails:
1. Verify `DATABASE_URL` in Railway
2. Check SSL mode (`sslmode=require`)
3. Whitelist Vercel IPs in Railway if needed

---

*Last Updated: December 2025*
*Author: HireMeBahamas Migration Team*

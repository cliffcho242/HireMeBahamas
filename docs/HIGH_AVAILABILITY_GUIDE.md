# High Availability & Always-On Configuration Guide

## Overview

This guide provides complete instructions for achieving 24/7/365 high availability for HireMeBahamas with zero downtime and instant response times.

## Table of Contents

1. [Railway Configuration](#railway-configuration)
2. [Render Configuration](#render-configuration)
3. [Vercel Configuration](#vercel-configuration)
4. [External Uptime Monitoring](#external-uptime-monitoring)
5. [Backend Keepalive Service](#backend-keepalive-service)
6. [GitHub Actions Ping Workflows](#github-actions-ping-workflows)

---

## Railway Configuration

### Enable Always-On Mode

Railway's hobby plan ($5/month) includes always-on functionality. The `railway.json` configuration has been updated with:

```json
{
  "deploy": {
    "sleepApplication": false,
    "numReplicas": 1
  }
}
```

### Railway Dashboard Steps

1. Go to your Railway project dashboard
2. Click on your backend service
3. Navigate to **Settings** → **Deploy**
4. Ensure **Sleep** is set to "Never" (requires hobby plan or above)
5. Set **Restart Policy** to "On Failure" with max 10 retries

### Railway Environment Variables for Keepalive

Set these in your Railway dashboard under **Variables**:

```bash
# Database keepalive settings
DB_KEEPALIVE_ENABLED=true
DB_KEEPALIVE_INTERVAL=120

# Worker settings for stability
WEB_CONCURRENCY=2
WEB_THREADS=8
GUNICORN_TIMEOUT=55
GUNICORN_KEEPALIVE=5
```

---

## Render Configuration

### Upgrade to Starter Plan ($7/month)

The `render.yaml` has been configured for the Starter plan which:
- Never sleeps
- Supports auto-scaling
- Has better performance

### Render Dashboard Steps

1. Go to your Render dashboard
2. Select your backend service
3. Navigate to **Settings**
4. Change plan from "Free" to "Starter" or higher
5. Enable **Auto Deploy** for continuous deployment

### Health Check Configuration

The health check is configured at `/health` with automatic restarts on failure:

```yaml
healthCheckPath: /health
scaling:
  minInstances: 1
  maxInstances: 3
```

---

## Vercel Configuration

Vercel Edge Functions are serverless and always available. The `vercel.json` has been optimized with:

### Multi-Region Deployment

```json
{
  "regions": ["iad1", "sfo1", "cdg1", "sin1"]
}
```

This deploys your frontend to:
- **iad1**: Washington D.C. (US East)
- **sfo1**: San Francisco (US West)
- **cdg1**: Paris (Europe)
- **sin1**: Singapore (Asia Pacific)

### Aggressive Caching

Static assets are cached for 1 year with immutable headers:

```json
{
  "source": "/assets/(.*)",
  "headers": [
    {
      "key": "Cache-Control",
      "value": "public, max-age=31536000, immutable"
    }
  ]
}
```

---

## External Uptime Monitoring

### Option 1: UptimeRobot (Free)

1. Go to [UptimeRobot](https://uptimerobot.com)
2. Create a free account
3. Add monitors:

| Monitor Name | URL | Interval |
|-------------|-----|----------|
| HireMeBahamas Backend Ping | `https://your-backend.railway.app/ping` | 5 min |
| HireMeBahamas Backend Health | `https://your-backend.railway.app/api/health` | 5 min |
| HireMeBahamas Frontend | `https://hiremebahamas.vercel.app` | 5 min |

### Option 2: Cron-job.org (Free)

1. Go to [Cron-job.org](https://cron-job.org)
2. Create a free account
3. Add cron jobs:

```
# Ping every 5 minutes
*/5 * * * * GET https://your-backend.railway.app/ping

# Health check every 10 minutes
*/10 * * * * GET https://your-backend.railway.app/api/health

# Database keepalive every 2 minutes
*/2 * * * * POST https://your-backend.railway.app/api/database/ping
```

### Option 3: Healthchecks.io (Free tier: 20 checks)

1. Go to [Healthchecks.io](https://healthchecks.io)
2. Create a free account
3. Create checks with these settings:
   - **Period**: 5 minutes
   - **Grace**: 5 minutes
   - Integrate with Slack/Email for alerts

---

## Backend Keepalive Service

The backend includes a built-in database keepalive thread that:

1. Pings the database every 2 minutes
2. Prevents PostgreSQL from sleeping
3. Maintains warm connection pool
4. Auto-recovers on failure

### Endpoint Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ping` | GET | Simple keepalive (returns "pong") |
| `/health` | GET | Full health check with DB status |
| `/api/health` | GET | Detailed health with metrics |
| `/api/database/ping` | POST | Database-specific keepalive |

---

## GitHub Actions Ping Workflows

Two workflows are configured to keep the app alive:

### 1. Scheduled App Ping (`scheduled-ping.yml`)

Runs every **10 minutes**:
- Pings `/ping` endpoint
- Checks `/api/health` endpoint
- Works for both Railway and Render backends

### 2. Database Keepalive (`keep-database-awake.yml`)

Runs every **2 minutes**:
- Pings `/api/database/ping` endpoint
- Fallback to `/api/health` if primary fails
- More aggressive for database-specific keepalive

### Configuration

Add these repository variables in GitHub:

```bash
# For Railway
RAILWAY_BACKEND_URL=https://your-app.railway.app

# For Render
RENDER_BACKEND_URL=https://your-app.onrender.com
```

---

## Cost Summary

| Service | Plan | Cost/Month | Features |
|---------|------|------------|----------|
| Railway | Hobby | $5 | Always-on, custom domains |
| Render | Starter | $7 | Always-on, auto-scaling |
| Vercel | Hobby | $0 | Unlimited edge deployments |
| UptimeRobot | Free | $0 | 50 monitors, 5-min checks |
| Cron-job.org | Free | $0 | Unlimited cron jobs |
| **Total** | | **$12/mo** | Full 24/7 availability |

---

## Troubleshooting

### App Still Sleeping?

1. Check Railway/Render dashboard for sleep settings
2. Verify GitHub Actions workflows are running
3. Ensure environment variables are set correctly
4. Check logs for connection errors

### Cold Start Issues?

1. The keepalive system should prevent cold starts
2. If occurring, reduce ping interval to 2-3 minutes
3. Consider connection pool warmup on startup

### Database Disconnects?

1. Increase `DB_KEEPALIVE_INTERVAL` to more frequent pings
2. Check TCP keepalive settings in `gunicorn.conf.py`
3. Verify SSL connection settings

---

## Monitoring Dashboard

Create a status page using one of these free services:

- [Instatus](https://instatus.com) - Free for 1 page
- [Cachet](https://cachethq.io) - Self-hosted
- [Upptime](https://upptime.js.org) - GitHub-based

This provides users with real-time status information about the platform.

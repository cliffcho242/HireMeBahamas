# Render 502 Fix - Quick Start Guide

**Goal: Zero 502 errors, instant response times (<1 second), 24/7 availability**

## TL;DR - Do This Now

### Option 1: Upgrade to Starter Plan ($7/month) - GUARANTEED FIX

1. Go to https://dashboard.render.com
2. Click on your `hiremebahamas-backend` service
3. Click **Settings** in the left sidebar
4. Scroll to **Instance Type**
5. Change from **Free** to **Starter** ($7/month)
6. Click **Save Changes**

**Done!** Your service will never sleep again. No 502 errors ever.

---

### Option 2: Free Tier - Use Render Cron Job (RECOMMENDED)

Create a native Render Cron Job that pings your service every 5 minutes:

1. Go to https://dashboard.render.com → **New** → **Cron Job**
2. Configure these **exact settings**:
   - **Name:** `keepalive-ping`
   - **Region:** Oregon
   - **Schedule:** `*/5 * * * *`
   - **Docker Image:** `curlimages/curl:latest`
   - **Command:** `curl -f -L https://hiremebahamas.onrender.com/health || exit 1`
3. Click **Create Cron Job**

✅ Your backend will be pinged every 5 minutes and will **never sleep again**!

📖 See [RENDER_CRON_JOB_SETUP.md](./RENDER_CRON_JOB_SETUP.md) for the complete guide.

---

### Option 3: Free Tier - Use External Pinger (Alternative)

If you prefer an external service:

#### UptimeRobot (5 min interval, FREE forever)

1. Go to https://uptimerobot.com → **Register for FREE**
2. Click **Add New Monitor**
3. Enter these settings:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** HireMeBahamas Backend
   - **URL:** `https://hiremebahamas.onrender.com/ping`
   - **Monitoring Interval:** 5 minutes
4. Click **Create Monitor**

✅ Your backend will now be pinged every 5 minutes and stay awake!

#### cron-job.org (Alternative - 4 min interval, FREE)

1. Go to https://cron-job.org → Sign up
2. Click **CREATE CRONJOB**
3. Enter:
   - **Title:** Ping HireMeBahamas
   - **URL:** `https://hiremebahamas.onrender.com/ping`
   - **Execution schedule:** Every 4 minutes → `*/4 * * * *`
4. Save and Enable

---

## Endpoints for Monitoring

| Endpoint | URL | Purpose |
|----------|-----|---------|
| **Ping** | `https://hiremebahamas.onrender.com/ping` | Lightweight keepalive (use this!) |
| **Health** | `https://hiremebahamas.onrender.com/health` | Basic health status |
| **Full Health** | `https://hiremebahamas.onrender.com/api/health` | Detailed health with DB status |
| **DB Ping** | `https://hiremebahamas.onrender.com/api/database/ping` | Database keepalive |

---

## Verify It's Working

After 20 minutes, test your login:

```bash
time curl -X POST https://hiremebahamas.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpassword"}'
```

**Expected:** Response in <1 second, no 502 errors.

---

## Which Plan Do I Need?

| Plan | Price | Sleep Behavior | Recommendation |
|------|-------|----------------|----------------|
| **Free** | $0 | Sleeps after 15 min | Use external pinger |
| **Starter** | $7/mo | **Never sleeps** ✅ | Best for production |
| **Standard** | $25/mo | Never sleeps + auto-scaling | High traffic apps |

---

## Still Having Issues?

1. **Check Render Logs:** Dashboard → Your Service → Logs
2. **Check Database:** Make sure `DATABASE_URL` is set in Environment Variables
3. **See full guide:** [RENDER_502_FIX_GUIDE.md](./RENDER_502_FIX_GUIDE.md)

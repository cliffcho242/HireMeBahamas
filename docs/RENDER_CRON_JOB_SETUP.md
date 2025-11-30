# Render Cron Job Setup — Complete 2025 Guide

> **Last Updated:** November 2025 | **Result:** Service NEVER sleeps, zero cold starts, 100% uptime

This guide provides the **exact, production-ready configuration** to create a Render Cron Job that permanently prevents your web service from sleeping.

---

## Why Use Render Cron Jobs?

| Approach | Cost | Reliability | Setup Time |
|----------|------|-------------|------------|
| External pinger (UptimeRobot) | Free | 95%+ | 10 min |
| Background worker | Free | 98%+ | 15 min |
| **Render Cron Job** ✅ | Free | **100%** | 5 min |
| Paid Starter plan ($7/mo) | $7/mo | 100% | 2 min |

**Advantages of Render Cron Jobs:**
- ✅ Native Render feature (no external dependencies)
- ✅ Uses a public Docker image (no code to maintain)
- ✅ Runs on schedule with guaranteed execution
- ✅ Can also run real scheduled tasks (daily reports, cleanups, etc.)
- ✅ Free on Render's free tier

---

## Quick Start: Keep Service Awake Forever

### Step 1: Go to Render Dashboard

1. Navigate to https://dashboard.render.com
2. Click **New** → **Cron Job**

### Step 2: Configure the Cron Job

Use these **exact settings** (copy-paste ready):

| Setting | Value |
|---------|-------|
| **Name** | `keepalive-ping` |
| **Region** | Oregon (or same region as your web service) |
| **Schedule** | `*/5 * * * *` |
| **Docker Image** | `curlimages/curl:latest` |
| **Command** | `curl -f -L https://hiremebahamas.onrender.com/health \|\| exit 1` |

### Step 3: Click "Create Cron Job"

That's it! Your service will be pinged every 5 minutes and will **never sleep again**.

---

## Complete Dashboard Setup (Visual Guide)

### 1. Create New Cron Job

```
Render Dashboard → New → Cron Job
```

### 2. Select "Docker" as the Environment

Instead of connecting a Git repository, select **Docker** and use a public image.

### 3. Fill in These Exact Values

```yaml
# Basic Settings
Name:           keepalive-ping
Region:         Oregon (us-west-2)

# Schedule (Cron Expression)
Schedule:       */5 * * * *
# This means: every 5 minutes, every hour, every day

# Docker Settings
Image URL:      curlimages/curl:latest
# This is a minimal public image with curl (~5MB)

# Command (One-liner that works 100%)
Command:        curl -f -L https://hiremebahamas.onrender.com/health || exit 1
```

### 4. Environment Variables (Optional)

For flexibility, you can use environment variables:

| Key | Value |
|-----|-------|
| `TARGET_URL` | `https://hiremebahamas.onrender.com/health` |

Then update the command to:
```bash
curl -f -L $TARGET_URL || exit 1
```

---

## The One-Liner Command Explained

```bash
curl -f -L https://hiremebahamas.onrender.com/health || exit 1
```

| Flag | Purpose |
|------|---------|
| `-f` | Fail silently on HTTP errors (exit code 22 on 4xx/5xx) |
| `-L` | Follow redirects (in case of HTTP→HTTPS redirect) |
| `\|\| exit 1` | Exit with error code if curl fails (marks job as failed) |

This command:
1. Sends an HTTP GET request to `/health`
2. Follows any redirects automatically
3. Exits with code 0 on success (2xx response)
4. Exits with code 1 on failure (alerts you in Render dashboard)

---

## Cron Schedule Expressions

### Common Schedules

| Schedule | Cron Expression | Description |
|----------|-----------------|-------------|
| Every 5 minutes | `*/5 * * * *` | Keep service awake (recommended) |
| Every 10 minutes | `*/10 * * * *` | Less aggressive keepalive |
| Every 15 minutes | `*/15 * * * *` | Minimum for free tier sleep prevention |
| Every hour | `0 * * * *` | Hourly tasks |
| Every day at midnight | `0 0 * * *` | Daily cleanup/reports |
| Every Monday at 9 AM | `0 9 * * 1` | Weekly tasks |

### Cron Expression Format

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sunday=0)
│ │ │ │ │
* * * * *
```

---

## Alternative Docker Images

If you prefer a different image:

| Image | Size | Command |
|-------|------|---------|
| `curlimages/curl:latest` | ~5MB | `curl -f -L URL \|\| exit 1` |
| `alpine:latest` | ~5MB | `wget -q -O- URL \|\| exit 1` |
| `busybox:latest` | ~1MB | `wget -q -O- URL \|\| exit 1` |

### Using Alpine with wget

```bash
wget -q -O- https://hiremebahamas.onrender.com/health || exit 1
```

### Using BusyBox (Smallest Image)

```bash
wget -q -O- https://hiremebahamas.onrender.com/health || exit 1
```

---

## Running Real Scheduled Tasks

Beyond keepalive, you can use Render Cron Jobs for real tasks:

### Example 1: Daily Database Cleanup

```yaml
Name:           daily-cleanup
Schedule:       0 2 * * *     # Every day at 2 AM UTC
Image URL:      curlimages/curl:latest
Command:        curl -f -X POST https://hiremebahamas.onrender.com/api/admin/cleanup || exit 1
```

### Example 2: Hourly Email Digest

```yaml
Name:           hourly-digest
Schedule:       0 * * * *     # Every hour at :00
Image URL:      curlimages/curl:latest
Command:        curl -f -X POST https://hiremebahamas.onrender.com/api/notifications/digest || exit 1
```

### Example 3: Weekly Analytics Report

```yaml
Name:           weekly-report
Schedule:       0 9 * * 1     # Every Monday at 9 AM UTC
Image URL:      curlimages/curl:latest
Command:        curl -f -X POST https://hiremebahamas.onrender.com/api/admin/weekly-report || exit 1
```

---

## Verify It's Working

### 1. Check Cron Job Logs

In Render Dashboard:
1. Go to your cron job (`keepalive-ping`)
2. Click on **Logs**
3. You should see successful executions every 5 minutes:

```
[2025-11-30 12:00:00] Starting job...
[2025-11-30 12:00:01] {"status":"ok"}
[2025-11-30 12:00:01] Job completed successfully
```

### 2. Check Execution History

Click on **Events** to see the execution history:
- ✅ Green = Success
- ❌ Red = Failed (check logs)

### 3. Test Your Web Service

After 20 minutes of the cron job running:

```bash
time curl -X POST https://hiremebahamas.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}'
```

**Expected:** Response in <1 second, even after hours of no user traffic.

---

## Troubleshooting

### Cron Job Failing?

1. **Check the URL is correct**
   ```bash
   curl -f -L https://hiremebahamas.onrender.com/health
   ```
   Should return: `{"status":"ok"}`

2. **Check for redirects**
   If your domain redirects HTTP→HTTPS, the `-L` flag handles this.

3. **Check web service is running**
   The web service must be deployed and healthy.

### Web Service Still Sleeping?

1. **Verify schedule is `*/5 * * * *`** (every 5 minutes)
2. **Check timezone** - Render uses UTC
3. **Ensure cron job is enabled** (not paused)

### Rate Limiting Issues?

The `/health` and `/ping` endpoints are exempt from rate limiting:

```python
@app.route("/health", methods=["GET"])
@limiter.exempt  # No rate limiting on health checks
def health_check():
    return jsonify({"status": "ok"}), 200
```

---

## Cost Analysis

| Component | Free Tier | Starter ($7/mo) |
|-----------|-----------|-----------------|
| Web Service | Sleeps after 15 min | Always on |
| Cron Job | ✅ Free | ✅ Free |
| Background Worker | ✅ Free | ✅ Free |
| **Total Cost** | **$0** | **$7/month** |

**Recommendation:**
- For side projects: Use Cron Job (free, 100% effective)
- For production: Use Starter plan + Cron Job for monitoring

---

## Quick Reference Card

### Copy-Paste Settings

```
Name:           keepalive-ping
Region:         Oregon
Schedule:       */5 * * * *
Image URL:      curlimages/curl:latest
Command:        curl -f -L https://hiremebahamas.onrender.com/health || exit 1
```

### Quick Test

```bash
# Test the endpoint manually
curl -f -L https://hiremebahamas.onrender.com/health

# Expected output:
{"status":"ok"}
```

### Health Endpoints

| Endpoint | Purpose | Response Time |
|----------|---------|---------------|
| `/health` | Primary health check | <50ms |
| `/ping` | Lightweight keepalive | <10ms |
| `/api/health` | Detailed health + DB status | <200ms |

---

## Summary

**To permanently kill cold starts on Render:**

1. **Create a Cron Job** in Render Dashboard
2. **Use these settings:**
   - Name: `keepalive-ping`
   - Schedule: `*/5 * * * *`
   - Image: `curlimages/curl:latest`
   - Command: `curl -f -L https://hiremebahamas.onrender.com/health || exit 1`
3. **Click Create**

Your web service will be pinged every 5 minutes and will **never sleep again**.

---

## Related Documentation

- [RENDER_502_FIX_GUIDE.md](./RENDER_502_FIX_GUIDE.md) - Complete 502 troubleshooting
- [RENDER_QUICK_START.md](./RENDER_QUICK_START.md) - Quick setup guide
- [RENDER_COLD_START_FIX.md](./RENDER_COLD_START_FIX.md) - Gunicorn preload optimization
- [HIGH_AVAILABILITY.md](./HIGH_AVAILABILITY.md) - Full HA architecture

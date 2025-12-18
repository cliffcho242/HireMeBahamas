# PostgreSQL Keepalive - Quick Start Guide

## What Was Fixed

Render PostgreSQL databases on free/hobby tiers sleep after 15 minutes of inactivity. This has been fixed with an automatic database keepalive mechanism.

## How It Works

The application now automatically pings the PostgreSQL database every 5 minutes to keep it awake. For the first 2 hours after startup, it uses a more aggressive 2-minute interval. This happens automatically in production - no configuration needed!

## Verify It's Working

### Option 1: Check Health Endpoint

```bash
curl https://your-app.render.app/api/health
```

Look for the `keepalive` section:
```json
{
  "keepalive": {
    "enabled": true,
    "running": true,
    "last_ping": "2025-11-26T08:30:00.000Z"
  }
}
```

### Option 2: Check Logs

In Render Dashboard:
1. Go to your backend service
2. Click "Deployments" tab
3. Look for these messages:
   - `✅ Database keepalive thread started`
   - `✅ Initial database keepalive ping successful`
   - `✅ Database keepalive ping successful at ...` (every 10 minutes)

## Configuration (Optional)

The keepalive works perfectly with default settings. If you want to customize:

### Change Ping Interval

In Render Dashboard → Environment Variables:
```
DB_KEEPALIVE_INTERVAL_SECONDS=180  # 3 minutes (more aggressive)
```

**Recommended values:**
- `180` = 3 minutes (most aggressive, maximum reliability)
- `300` = 5 minutes (default, recommended)
- `600` = 10 minutes (less frequent, may be too close to sleep threshold)

## Troubleshooting

### Database Still Shows "Sleeping"

1. Check that `ENVIRONMENT=production` is set in Render
2. Check that `DATABASE_URL` is configured
3. Check logs for keepalive messages
4. Wait 10 minutes and check again

### No Keepalive in Health Check

Make sure you're checking the `/api/health` endpoint (not just `/health`):
```bash
curl https://your-app.render.app/api/health
```

## Benefits

- ✅ No more database cold starts
- ✅ Faster response times
- ✅ Better user experience
- ✅ Automatic - no manual intervention
- ✅ Minimal resource usage

## More Information

- **Full Documentation**: See `BACKEND_KEEPALIVE_SETUP.md`
- **Implementation Details**: See `POSTGRES_KEEPALIVE_IMPLEMENTATION.md`
- **Test Suite**: See `test_keepalive.py`

---

**Status**: ✅ Implemented and ready to deploy  
**Next**: Push to Render and verify in production

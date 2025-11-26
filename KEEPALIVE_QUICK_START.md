# PostgreSQL Keepalive - Quick Start Guide

## What Was Fixed

Railway PostgreSQL databases on free/hobby tiers sleep after 15 minutes of inactivity. This has been fixed with an automatic database keepalive mechanism.

## How It Works

The application now automatically pings the PostgreSQL database every 10 minutes to keep it awake. This happens automatically in production - no configuration needed!

## Verify It's Working

### Option 1: Check Health Endpoint

```bash
curl https://your-app.railway.app/api/health
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

In Railway Dashboard:
1. Go to your backend service
2. Click "Deployments" tab
3. Look for these messages:
   - `✅ Database keepalive thread started`
   - `✅ Initial database keepalive ping successful`
   - `✅ Database keepalive ping successful at ...` (every 10 minutes)

## Configuration (Optional)

The keepalive works perfectly with default settings. If you want to customize:

### Change Ping Interval

In Railway Dashboard → Environment Variables:
```
DB_KEEPALIVE_INTERVAL_SECONDS=300  # 5 minutes (more aggressive)
```

**Recommended values:**
- `300` = 5 minutes (for busy apps)
- `600` = 10 minutes (default, recommended)
- `900` = 15 minutes (maximum safe value)

## Troubleshooting

### Database Still Shows "Sleeping"

1. Check that `ENVIRONMENT=production` is set in Railway
2. Check that `DATABASE_URL` is configured
3. Check logs for keepalive messages
4. Wait 10 minutes and check again

### No Keepalive in Health Check

Make sure you're checking the `/api/health` endpoint (not just `/health`):
```bash
curl https://your-app.railway.app/api/health
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
**Next**: Push to Railway and verify in production

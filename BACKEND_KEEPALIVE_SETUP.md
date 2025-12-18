# PostgreSQL Database Keepalive

## Overview

This document explains the automatic database keepalive mechanism implemented in HireMeBahamas to prevent Render PostgreSQL databases from going to sleep due to inactivity.

## Problem

Render databases on free/hobby tiers automatically sleep after **15 minutes of inactivity** to save resources. When a database is sleeping:
- The first request after sleep takes significantly longer (cold start)
- Users experience increased latency
- The database needs to wake up before serving requests

## Solution

The application now includes an **automatic database keepalive** mechanism that:
- ✅ Pings the database every 5 minutes (default)
- ✅ Uses aggressive 2-minute intervals for the first 2 hours after startup
- ✅ Keeps the database connection active
- ✅ Prevents the database from sleeping
- ✅ Runs only in production environments
- ✅ Minimal resource overhead

## How It Works

### 1. Background Thread

A daemon thread runs in the background that:
- Executes every 5 minutes (configurable)
- Uses aggressive 2-minute intervals for first 2 hours after startup
- Performs a simple `SELECT 1` query
- Uses the connection pool for efficiency
- Tracks success/failure status

### 2. Automatic Activation

The keepalive automatically starts when:
- `ENVIRONMENT` is set to `production`
- `DATABASE_URL` is configured (PostgreSQL)
- The application starts successfully

### 3. Monitoring

You can monitor the keepalive status via the `/api/health` endpoint:

```bash
curl https://your-app.render.app/api/health
```

Response includes:
```json
{
  "status": "healthy",
  "database": "connected",
  "keepalive": {
    "enabled": true,
    "running": true,
    "mode": "normal",
    "current_interval_seconds": 300,
    "last_ping": "2025-11-26T08:30:00.000Z",
    "seconds_since_last_ping": 45.2,
    "consecutive_failures": 0
  }
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_KEEPALIVE_INTERVAL_SECONDS` | `300` | Time between keepalive pings in normal mode (in seconds) |
| `DB_KEEPALIVE_AGGRESSIVE_PERIOD_SECONDS` | `7200` | Duration of aggressive mode after startup (2 hours) |
| `DB_KEEPALIVE_AGGRESSIVE_INTERVAL_SECONDS` | `120` | Time between pings in aggressive mode (2 minutes) |
| `ENVIRONMENT` | `development` | Set to `production` to enable keepalive |
| `DATABASE_URL` | - | PostgreSQL connection string (required) |

### Adjusting Keepalive Interval

To change the ping interval, set the environment variable in Render:

```bash
DB_KEEPALIVE_INTERVAL_SECONDS=300  # Ping every 5 minutes (default)
```

**Recommended values:**
- `180` (3 minutes) - Most aggressive, maximum reliability
- `300` (5 minutes) - Default, recommended for Render
- `600` (10 minutes) - Less frequent, may be too close to sleep threshold

**Note:** Render sleeps after 15 minutes, so keep the interval well under 15 minutes (5 minutes recommended).

## Benefits

### For Users
- ✅ Faster response times (no cold starts)
- ✅ Consistent performance
- ✅ Better user experience

### For Developers
- ✅ No manual intervention needed
- ✅ Automatic monitoring
- ✅ Easy to configure
- ✅ Minimal resource usage

### For Production
- ✅ 24/7 database availability
- ✅ Reduced latency
- ✅ Improved reliability

## Technical Details

### Implementation

The keepalive is implemented in `final_backend_postgresql.py`:

1. **Thread Creation**: A daemon thread is created during app initialization
2. **Periodic Execution**: Thread sleeps for the configured interval
3. **Database Ping**: Executes `SELECT 1` query
4. **Error Handling**: Tracks failures and logs issues
5. **Graceful Shutdown**: Stops cleanly on application exit

### Why SELECT 1?

The `SELECT 1` query is optimal because:
- Minimal database overhead
- Doesn't modify data
- Fast execution
- Keeps connection active
- Standard across databases

### Connection Pool Integration

The keepalive uses the existing connection pool:
- No additional connections needed
- Reuses pooled connections
- Proper connection lifecycle management
- Returns connections to pool after ping

## Monitoring and Debugging

### Check Keepalive Status

```bash
# Check if keepalive is running
curl https://your-app.render.app/api/health | jq '.keepalive'
```

### View Keepalive Logs

In Render dashboard:
1. Go to your service
2. Click "Deployments" tab
3. View logs
4. Look for:
   - `✅ Database keepalive thread started`
   - `✅ Database keepalive ping successful`
   - `⚠️ Database keepalive ping failed` (if issues)

### Common Log Messages

| Log Message | Meaning |
|-------------|---------|
| `🔄 Database keepalive started` | Keepalive worker is running |
| `✅ Database keepalive ping successful` | Database ping succeeded |
| `⚠️ Database keepalive ping failed` | Database ping failed (temporary) |
| `⚠️ Multiple keepalive failures` | Connection issues detected |
| `🛑 Database keepalive stopped` | Keepalive stopped during shutdown |

## Troubleshooting

### Keepalive Not Starting

**Symptoms:**
- No keepalive status in `/api/health`
- Logs don't show keepalive messages

**Solutions:**
1. Verify `ENVIRONMENT=production` is set
2. Verify `DATABASE_URL` is configured
3. Check application logs for errors

### Keepalive Failures

**Symptoms:**
- `consecutive_failures` > 0 in health check
- Logs show ping failures

**Solutions:**
1. Check DATABASE_URL is correct
2. Verify PostgreSQL service is running
3. Check Render service status
4. Review connection pool settings

### Database Still Sleeping

**Symptoms:**
- Database shows "sleeping" in Render
- Keepalive appears to be running

**Possible Causes:**
1. Keepalive interval too long (> 15 minutes)
2. Keepalive thread crashed (check logs)
3. Database service restarted

**Solutions:**
1. Reduce `DB_KEEPALIVE_INTERVAL_SECONDS` to 300 (5 min)
2. Check logs for thread errors
3. Redeploy the application

## Best Practices

### For Production

1. **Keep Default Interval**: 10 minutes is optimal for most cases
2. **Monitor Regularly**: Check `/api/health` periodically
3. **Enable Logging**: Review logs for any keepalive issues
4. **Test After Deployment**: Verify keepalive starts correctly

### For Development

The keepalive is automatically disabled in development:
- Saves resources on your local machine
- Prevents unnecessary database connections
- SQLite doesn't need keepalive

To test keepalive locally:
```bash
export ENVIRONMENT=production
export DATABASE_URL=postgresql://...
python final_backend_postgresql.py
```

## FAQ

### Q: Does keepalive increase costs?

**A:** No. The keepalive uses minimal resources:
- Simple `SELECT 1` query every 10 minutes
- Uses existing connection pool
- Negligible CPU/memory usage
- No additional database storage

### Q: Can I disable keepalive?

**A:** Yes, set `ENVIRONMENT=development` or remove `DATABASE_URL`. However, this is not recommended for production as your database will sleep.

### Q: What if my Render plan doesn't have database sleep?

**A:** The keepalive won't harm anything. Render Pro and higher plans don't have database sleep, but the keepalive adds negligible overhead.

### Q: Does keepalive work with other database providers?

**A:** Yes! The keepalive works with any PostgreSQL database:
- Render PostgreSQL
- Heroku PostgreSQL
- AWS RDS
- Supabase
- Neon
- Any other PostgreSQL provider

### Q: How do I know if it's working?

**A:** Check the `/api/health` endpoint:
- `keepalive.enabled: true`
- `keepalive.running: true`
- `keepalive.last_ping` shows recent timestamp
- `keepalive.consecutive_failures: 0`

## Summary

The automatic database keepalive:
- ✅ Prevents Render PostgreSQL from sleeping
- ✅ Runs automatically in production
- ✅ Requires no manual configuration
- ✅ Provides monitoring via `/api/health`
- ✅ Minimal resource overhead
- ✅ Improves user experience

The keepalive is production-ready and enabled by default when deploying to Render with PostgreSQL configured.

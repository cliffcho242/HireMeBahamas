# ⚡ Gunicorn Lightning Fast Configuration

## Overview

This document describes the Gunicorn configuration optimized for lightning-fast performance on Render's always-on Standard plan.

## Configuration Values

### Core Settings

- **Workers**: `2` (default, configurable via `WEB_CONCURRENCY`)
- **Threads**: `4` per worker (configurable via `WEB_THREADS`)
- **Timeout**: `60` seconds (configurable via `GUNICORN_TIMEOUT`)
- **Worker Class**: `gthread` (optimized for I/O-bound operations)
- **Keepalive**: `5` seconds

### Total Capacity

```
2 workers × 4 threads = 8 concurrent requests
```

## Rationale

### Why Workers = 2?

- **Parallel Processing**: Two workers can handle requests in parallel, improving throughput
- **Memory Efficient**: Optimized for Render Standard plan (1GB RAM)
- **CPU Utilization**: Better utilization of available CPU cores
- **Redundancy**: If one worker is busy, the other can handle incoming requests

### Why Threads = 4?

- **Concurrency**: Each worker can handle 4 concurrent requests
- **I/O Operations**: Perfect for database-heavy operations (waiting for DB responses)
- **Memory Balance**: 4 threads per worker keeps memory usage reasonable
- **Total of 8**: Combined capacity handles typical traffic patterns efficiently

### Why Timeout = 60?

- **Always-On Service**: No cold starts means faster responses
- **Quick Failures**: 60s timeout prevents hanging requests
- **Database Queries**: Sufficient for most database operations
- **Not Too Lenient**: Forces optimization of slow endpoints

## Performance Benefits

### Before (workers=1, threads=4, timeout=120)
- Single worker could become bottleneck
- 120s timeout was overly generous
- Total capacity: 4 concurrent requests

### After (workers=2, threads=4, timeout=60)
- ✅ **2x worker capacity** for parallel request handling
- ✅ **Faster failure detection** with 60s timeout
- ✅ **8 concurrent requests** total capacity
- ✅ **Better CPU utilization** with multiple workers

## Configuration Files Updated

1. **gunicorn.conf.py**: Core Gunicorn configuration
   - Changed default `workers` from 1 to 2
   - Changed default `timeout` from 120 to 60
   - Kept `threads` at 4 (already optimal)

2. **render.yaml**: Render deployment configuration
   - Added explicit environment variables:
     - `WEB_CONCURRENCY=2`
     - `WEB_THREADS=4`
     - `GUNICORN_TIMEOUT=60`

3. **start.sh**: Startup script
   - Updated documentation to reflect new defaults
   - Updated echo statements for correct values

4. **docker-compose.local.yml**: Local development
   - Standardized all Gunicorn commands
   - Ensured consistency across all profiles

5. **api/render.yaml**: Deprecated config (for consistency)
   - Updated to match new values

## Environment Variable Overrides

All settings can be customized via environment variables:

```bash
# Override workers
export WEB_CONCURRENCY=3

# Override threads
export WEB_THREADS=8

# Override timeout
export GUNICORN_TIMEOUT=90
```

## Render Dashboard Setup

When deploying to Render, set these environment variables in the dashboard:

```
WEB_CONCURRENCY=2
WEB_THREADS=4
GUNICORN_TIMEOUT=60
```

These are now the defaults, but explicit settings ensure consistency.

## Testing

A test script `test_gunicorn_config.py` is provided to verify the configuration:

```bash
python3 test_gunicorn_config.py
```

This verifies:
- ✅ Workers default to 2
- ✅ Threads default to 4
- ✅ Timeout defaults to 60s
- ✅ Environment variable overrides work
- ✅ Total capacity: 8 concurrent requests

## Monitoring

After deployment, monitor these metrics:

1. **Response Times**: Should be faster with 2 workers
2. **Concurrent Requests**: Can now handle up to 8 simultaneously
3. **Worker Utilization**: Both workers should share the load
4. **Timeout Errors**: Should be rare with 60s timeout for always-on service

## Comparison with Other Plans

### Render Free Tier
```
WEB_CONCURRENCY=1  # Less RAM available
WEB_THREADS=2      # Reduce concurrency
GUNICORN_TIMEOUT=120  # Allow for cold starts
```

### Render Standard (Current)
```
WEB_CONCURRENCY=2  # Optimal for 1GB RAM
WEB_THREADS=4      # Good concurrency
GUNICORN_TIMEOUT=60  # Fast responses, no cold starts
```

### Render Pro
```
WEB_CONCURRENCY=4  # More RAM available
WEB_THREADS=4      # Keep threads moderate
GUNICORN_TIMEOUT=60  # Keep fast timeouts
```

## Troubleshooting

### If you see timeout errors:
```bash
# Increase timeout temporarily
export GUNICORN_TIMEOUT=90
```

### If memory usage is high:
```bash
# Reduce workers or threads
export WEB_CONCURRENCY=1
export WEB_THREADS=2
```

### If response times are slow:
```bash
# Check worker utilization
# Consider increasing workers if CPU allows
export WEB_CONCURRENCY=3
```

## Summary

This configuration provides **lightning-fast performance** by:
- 🚀 Doubling worker capacity (1 → 2)
- ⚡ Halving timeout for faster failure detection (120s → 60s)
- 📈 Increasing total concurrent request capacity (4 → 8)
- 🎯 Optimizing for Render Standard plan's 1GB RAM

The result is a more responsive, efficient, and scalable application on Render!

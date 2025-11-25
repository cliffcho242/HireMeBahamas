# PostgreSQL Database Initialization and Recovery Fix

## Problem Statement

The PostgreSQL container was experiencing improper shutdowns and recovery issues with the following symptoms:

```
PostgreSQL Database directory appears to contain a database; Skipping initialization
LOG:  database system was interrupted; last known up at 2025-11-25 05:57:26 UTC
LOG:  database system was not properly shut down; automatic recovery in progress
LOG:  invalid record length at 0/1FC6DA0: expected at least 24, got 0
```

### Root Cause

Docker containers can be stopped abruptly without giving PostgreSQL enough time to perform a graceful shutdown. This leads to:

1. **Dirty database state**: PostgreSQL's write-ahead log (WAL) files are left in an inconsistent state
2. **Automatic recovery on startup**: PostgreSQL has to replay WAL logs to restore consistency
3. **Potential data corruption**: In extreme cases, improper shutdowns can lead to data loss

## Solution Implemented

### 1. Proper Shutdown Signal Handling

Added `stop_signal` and `stop_grace_period` to all services in `docker-compose.yml`:

```yaml
postgres:
  stop_signal: SIGTERM      # Send proper termination signal
  stop_grace_period: 60s    # Wait 60 seconds for clean shutdown
```

**Why this matters:**
- `SIGTERM` tells PostgreSQL to perform a clean shutdown
- `stop_grace_period` gives PostgreSQL time to:
  - Complete pending transactions
  - Flush dirty buffers to disk
  - Update WAL files properly
  - Close all connections gracefully

### 2. Optimized PostgreSQL Configuration

Added PostgreSQL tuning parameters for better reliability:

```yaml
command: >
  postgres
  -c checkpoint_completion_target=0.9
  -c wal_buffers=16MB
  -c min_wal_size=1GB
  -c max_wal_size=4GB
```

**Key parameters:**
- `checkpoint_completion_target=0.9`: Spread checkpoints over 90% of the checkpoint interval (reduces I/O spikes)
- `wal_buffers=16MB`: Buffer size for WAL data before writing to disk
- `min_wal_size=1GB`: Minimum WAL size to keep (prevents constant WAL file creation/deletion)
- `max_wal_size=4GB`: Maximum WAL size before forcing a checkpoint

### 3. Enhanced Health Checks

Added `start_period` to PostgreSQL health check:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U hiremebahamas_user -d hiremebahamas"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s  # Give PostgreSQL 30s to start before health checks matter
```

**Why this helps:**
- Allows PostgreSQL time to complete recovery if needed
- Prevents premature failure of dependent services
- Gives time for WAL replay during startup

## How It Works

### Normal Shutdown Sequence

1. Docker sends `SIGTERM` to PostgreSQL container
2. PostgreSQL receives signal and initiates shutdown:
   - Stops accepting new connections
   - Waits for active transactions to complete
   - Flushes all dirty buffers to disk
   - Writes shutdown checkpoint to WAL
   - Closes all files properly
3. Container stops cleanly

### Recovery Scenario

If the database was improperly shut down (power loss, forced kill, etc.):

1. PostgreSQL detects incomplete shutdown on startup
2. Reads last valid checkpoint from WAL
3. Replays WAL records from that checkpoint forward
4. Restores database to consistent state
5. Writes new checkpoint
6. Normal operations resume

## Testing the Fix

### Test 1: Clean Shutdown

```bash
# Start the services
docker-compose up -d

# Check PostgreSQL logs (should show normal startup)
docker-compose logs postgres

# Stop services (should see clean shutdown)
docker-compose down

# Restart and check logs (should NOT see recovery messages)
docker-compose up -d
docker-compose logs postgres
```

**Expected behavior:**
- No "database system was interrupted" messages
- No "automatic recovery in progress" messages
- Quick startup without WAL replay

### Test 2: Recovery After Forced Stop

```bash
# Start services
docker-compose up -d

# Get PostgreSQL container ID
docker ps | grep postgres

# Force kill the container (simulates crash)
docker kill <container-id>

# Start again (will trigger recovery)
docker-compose up -d

# Check logs (recovery should complete successfully)
docker-compose logs postgres
```

**Expected behavior:**
- "database system was interrupted" message
- "automatic recovery in progress"
- "redo done" showing successful recovery
- Normal startup after recovery

## Benefits of This Fix

1. **Data Integrity**: Proper shutdowns prevent database corruption
2. **Faster Restarts**: Clean shutdowns mean no recovery needed on restart
3. **Better Performance**: Optimized WAL configuration reduces I/O overhead
4. **Reliability**: Even if crashes occur, recovery is fast and reliable

## Production Deployment

These changes are automatically applied when using:
- `docker-compose up` for local development
- Docker-based deployments (Railway, Render, etc.)

For Railway/Render deployments, the platform's container orchestration will respect the `stop_grace_period` settings.

## Monitoring

Watch for these log messages to ensure the fix is working:

**Good signs (clean shutdown):**
```
LOG:  received smart shutdown request
LOG:  database system is shut down
```

**Recovery (after crash, but working correctly):**
```
LOG:  database system was interrupted
LOG:  automatic recovery in progress
LOG:  redo done at 0/xxxxx
LOG:  checkpoint complete
```

**Bad signs (needs investigation):**
```
FATAL:  could not open file
PANIC:  could not write to file
ERROR:  database is corrupted
```

## Additional Resources

- [PostgreSQL WAL Configuration](https://www.postgresql.org/docs/current/wal-configuration.html)
- [Docker Stop Grace Period](https://docs.docker.com/compose/compose-file/compose-file-v3/#stop_grace_period)
- [PostgreSQL Crash Recovery](https://www.postgresql.org/docs/current/wal-intro.html)

## Rollback Plan

If issues occur, revert by:

```bash
git checkout HEAD~1 docker-compose.yml
docker-compose down -v  # WARNING: Deletes all data!
docker-compose up -d
```

## Maintenance

### Clean Up Old WAL Files

If disk space becomes an issue:

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U hiremebahamas_user -d hiremebahamas

# Check WAL location
SELECT pg_current_wal_lsn();

# Archive old WAL segments (done automatically by PostgreSQL)
```

### Monitor Database Health

```bash
# Check database size
docker-compose exec postgres psql -U hiremebahamas_user -d hiremebahamas -c "SELECT pg_size_pretty(pg_database_size('hiremebahamas'));"

# Check connection count
docker-compose exec postgres psql -U hiremebahamas_user -d hiremebahamas -c "SELECT count(*) FROM pg_stat_activity;"

# Check for long-running queries
docker-compose exec postgres psql -U hiremebahamas_user -d hiremebahamas -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"
```

-- =============================================================================
-- VERCEL POSTGRES MONITORING QUERIES
-- =============================================================================
--
-- MASTERMIND VERCEL POSTGRES OPTIMIZATION (2025)
--
-- Run these queries to monitor database performance and set up alerts.
--
-- =============================================================================

-- =============================================================================
-- 1. DATABASE HEALTH CHECK
-- =============================================================================
-- Target: < 1ms response time

SELECT 
    NOW() as current_time,
    pg_database_size(current_database()) / 1024 / 1024 as db_size_mb,
    (SELECT COUNT(*) FROM pg_stat_activity WHERE datname = current_database()) as active_connections;

-- =============================================================================
-- 2. CONNECTION POOL STATUS
-- =============================================================================
-- Alert thresholds:
-- - WARNING: > 70% connection usage
-- - CRITICAL: > 90% connection usage

SELECT 
    COUNT(*) FILTER (WHERE state = 'active') as active_connections,
    COUNT(*) FILTER (WHERE state = 'idle') as idle_connections,
    COUNT(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction,
    COUNT(*) as total_connections,
    (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_connections,
    ROUND(
        COUNT(*)::numeric / 
        (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') * 100,
        2
    ) as usage_percent
FROM pg_stat_activity
WHERE datname = current_database();

-- =============================================================================
-- 3. SLOW QUERIES (Top 10)
-- =============================================================================
-- Alert thresholds:
-- - WARNING: avg_time > 50ms
-- - CRITICAL: avg_time > 200ms

SELECT 
    query,
    calls,
    ROUND(total_exec_time::numeric, 2) as total_time_ms,
    ROUND((total_exec_time / calls)::numeric, 2) as avg_time_ms,
    ROUND(max_exec_time::numeric, 2) as max_time_ms,
    ROUND(stddev_exec_time::numeric, 2) as stddev_time_ms,
    rows as total_rows_affected,
    ROUND((rows::numeric / calls), 2) as avg_rows_per_call
FROM pg_stat_statements
WHERE calls > 10
ORDER BY total_exec_time DESC
LIMIT 10;

-- =============================================================================
-- 4. TABLE SIZE AND ROW COUNTS
-- =============================================================================

SELECT 
    schemaname,
    relname as table_name,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size,
    pg_size_pretty(pg_relation_size(relid)) as table_size,
    pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) as index_size,
    n_live_tup as row_count,
    n_dead_tup as dead_rows,
    last_vacuum,
    last_autovacuum,
    last_analyze
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- =============================================================================
-- 5. INDEX USAGE STATISTICS
-- =============================================================================
-- Look for unused indexes (idx_scan = 0)
-- Look for indexes with low hit rate

SELECT 
    schemaname,
    relname as table_name,
    indexrelname as index_name,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
    CASE 
        WHEN idx_scan = 0 THEN 'UNUSED - Consider dropping'
        WHEN idx_scan < 100 THEN 'LOW USAGE'
        ELSE 'ACTIVE'
    END as status
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- =============================================================================
-- 6. CACHE HIT RATIO
-- =============================================================================
-- Target: > 99% hit ratio
-- Alert threshold: < 95%

SELECT 
    'index' as type,
    ROUND(
        (sum(idx_blks_hit)) / 
        NULLIF((sum(idx_blks_hit) + sum(idx_blks_read)), 0) * 100,
        2
    ) as hit_ratio
FROM pg_statio_user_indexes

UNION ALL

SELECT 
    'table' as type,
    ROUND(
        (sum(heap_blks_hit)) / 
        NULLIF((sum(heap_blks_hit) + sum(heap_blks_read)), 0) * 100,
        2
    ) as hit_ratio
FROM pg_statio_user_tables;

-- =============================================================================
-- 7. LOCK MONITORING
-- =============================================================================
-- Alert if any locks held > 5 seconds

SELECT 
    pg_class.relname as table_name,
    pg_locks.locktype,
    pg_locks.mode,
    pg_locks.granted,
    pg_stat_activity.query,
    age(now(), pg_stat_activity.query_start) as lock_duration,
    pg_stat_activity.pid,
    pg_stat_activity.state
FROM pg_locks
JOIN pg_class ON pg_locks.relation = pg_class.oid
JOIN pg_stat_activity ON pg_locks.pid = pg_stat_activity.pid
WHERE pg_class.relnamespace = 'public'::regnamespace
  AND pg_locks.mode LIKE '%Exclusive%'
ORDER BY lock_duration DESC;

-- =============================================================================
-- 8. REPLICATION LAG (if using read replicas)
-- =============================================================================

SELECT 
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_size_pretty(pg_wal_lsn_diff(sent_lsn, replay_lsn)) as replication_lag
FROM pg_stat_replication;

-- =============================================================================
-- 9. TRANSACTION RATES
-- =============================================================================

SELECT 
    datname,
    xact_commit as commits,
    xact_rollback as rollbacks,
    ROUND(
        xact_rollback::numeric / NULLIF(xact_commit + xact_rollback, 0) * 100,
        2
    ) as rollback_percent,
    blks_read as disk_blocks_read,
    blks_hit as cache_blocks_hit,
    ROUND(
        blks_hit::numeric / NULLIF(blks_read + blks_hit, 0) * 100,
        2
    ) as cache_hit_ratio
FROM pg_stat_database
WHERE datname = current_database();

-- =============================================================================
-- 10. QUERY LATENCY PERCENTILES (requires pg_stat_statements)
-- =============================================================================
-- Target p99 < 100ms

SELECT 
    ROUND((mean_exec_time)::numeric, 2) as avg_latency_ms,
    ROUND((min_exec_time)::numeric, 2) as min_latency_ms,
    ROUND((max_exec_time)::numeric, 2) as max_latency_ms,
    ROUND((stddev_exec_time)::numeric, 2) as stddev_latency_ms,
    calls as total_queries,
    rows as total_rows
FROM pg_stat_statements
WHERE calls > 100
ORDER BY mean_exec_time DESC
LIMIT 20;

-- =============================================================================
-- ALERT THRESHOLD SUMMARY
-- =============================================================================
-- 
-- | Metric                    | Warning    | Critical   |
-- |---------------------------|------------|------------|
-- | Health check latency      | > 5ms      | > 20ms     |
-- | Connection usage          | > 70%      | > 90%      |
-- | Query avg time            | > 50ms     | > 200ms    |
-- | Query max time            | > 500ms    | > 2000ms   |
-- | Cache hit ratio           | < 98%      | < 95%      |
-- | Lock duration             | > 5s       | > 30s      |
-- | Rollback rate             | > 1%       | > 5%       |
-- | Dead rows per table       | > 10000    | > 100000   |
-- | Unused indexes            | any        | -          |
--
-- =============================================================================

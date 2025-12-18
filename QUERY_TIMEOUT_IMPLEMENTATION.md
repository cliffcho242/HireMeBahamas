# Query-Level Timeout Implementation

## Overview

This implementation adds per-query timeouts to prevent database exhaustion and long-running queries. The solution uses PostgreSQL's `SET LOCAL statement_timeout` which is:

✅ **Neon-safe** - Works with pooled connections (PgBouncer)  
✅ **Transaction-scoped** - Applies only inside transaction  
✅ **No startup errors** - Doesn't use startup parameters  
✅ **Safe retries** - Timeout resets automatically  
✅ **Traffic-spike protection** - Prevents resource exhaustion

## Architecture

### Core Module: `app/core/query_timeout.py`

Provides utilities for setting query timeouts:

```python
from app.core.query_timeout import (
    set_query_timeout,
    with_query_timeout,
    set_fast_query_timeout,
    set_slow_query_timeout,
)
```

### Timeout Levels

Three predefined timeout levels for different query types:

| Level | Default | Use Case | Environment Variable |
|-------|---------|----------|---------------------|
| Fast | 2000ms | Lookups, simple SELECTs | `DB_FAST_QUERY_TIMEOUT_MS` |
| Default | 5000ms | Standard operations | `DB_QUERY_TIMEOUT_MS` |
| Slow | 30000ms | Analytics, reports, aggregations | `DB_SLOW_QUERY_TIMEOUT_MS` |

## Usage Patterns

### Pattern 1: Fast Queries (Recommended for auth/lookups)

```python
from app.core.query_timeout import set_fast_query_timeout

async def login(db: AsyncSession = Depends(get_db)):
    # Set 2s timeout for login query
    await set_fast_query_timeout(db)
    
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
```

### Pattern 2: Default Timeout (Standard operations)

```python
from app.core.query_timeout import set_query_timeout

async def create_job(db: AsyncSession = Depends(get_db)):
    # Set 5s timeout (default)
    await set_query_timeout(db)
    
    db_job = Job(**job_data)
    db.add(db_job)
    await db.commit()
```

### Pattern 3: Context Manager (Explicit scope)

```python
from app.core.query_timeout import with_query_timeout

async def complex_operation(db: AsyncSession = Depends(get_db)):
    # All queries in this block have 3s timeout
    async with with_query_timeout(db, timeout_ms=3000):
        result1 = await db.execute(query1)
        result2 = await db.execute(query2)
    # Timeout automatically reset here
```

### Pattern 4: Slow Operations (Analytics/Reports)

```python
from app.core.query_timeout import set_slow_query_timeout

async def get_analytics(db: AsyncSession = Depends(get_db)):
    # Set 30s timeout for complex aggregation
    await set_slow_query_timeout(db)
    
    stats = await db.execute(
        select(
            func.count(Post.id),
            func.avg(Post.likes),
            func.date_trunc('day', Post.created_at)
        ).group_by(func.date_trunc('day', Post.created_at))
    )
```

## Implementation Status

### ✅ Completed

- [x] Core timeout utility module created
- [x] Comprehensive test suite
- [x] Auth routes updated (login, register)
- [x] Jobs API updated (create, list)
- [x] Feed/Posts routes updated
- [x] Documentation created

### 📝 Recommended Next Steps

1. **Add to remaining endpoints**:
   - Messages API
   - Notifications API
   - User profile routes
   - Admin routes

2. **Monitoring**:
   - Add timeout metrics to `/metrics` endpoint
   - Track timeout errors in application logs
   - Set up alerts for frequent timeouts

3. **Configuration**:
   - Fine-tune timeout values based on production metrics
   - Consider dynamic timeouts based on load

## Configuration

### Environment Variables

Add to your `.env` or Render/Vercel environment:

```bash
# Query timeout configuration (all values in milliseconds)
DB_QUERY_TIMEOUT_MS=5000        # Default: 5 seconds
DB_FAST_QUERY_TIMEOUT_MS=2000   # Fast queries: 2 seconds
DB_SLOW_QUERY_TIMEOUT_MS=30000  # Slow queries: 30 seconds
```

### Production Settings

Recommended values for production:

```bash
# Conservative timeouts for high-traffic production
DB_QUERY_TIMEOUT_MS=3000        # 3 seconds default
DB_FAST_QUERY_TIMEOUT_MS=1000   # 1 second for auth/lookups
DB_SLOW_QUERY_TIMEOUT_MS=15000  # 15 seconds for analytics
```

## Testing

### Run Tests

```bash
# Run all query timeout tests
cd backend
python test_query_timeout.py

# Or with pytest
pytest test_query_timeout.py -v
```

### Test Coverage

The test suite validates:

1. ✅ Timeout setting works correctly
2. ✅ Fast queries complete within timeout
3. ✅ Long-running queries are cancelled
4. ✅ Context manager works properly
5. ✅ Different timeout levels work
6. ✅ Timeouts reset between transactions
7. ✅ Error handling is robust
8. ✅ Real User model queries work with timeouts

## Error Handling

### Timeout Exceptions

When a query exceeds its timeout, PostgreSQL raises an `OperationalError`:

```python
from sqlalchemy.exc import OperationalError

try:
    await db.execute(slow_query)
except OperationalError as e:
    if "timeout" in str(e).lower():
        logger.error("Query timed out - consider optimizing or increasing timeout")
        raise HTTPException(
            status_code=503,
            detail="Query took too long. Please try again or refine your search."
        )
```

### Graceful Degradation

The timeout utility is designed to fail gracefully:

- If timeout setting fails, queries still execute (without timeout protection)
- Warnings are logged but application continues
- No breaking changes to existing code

## Production Deployment

### Pre-deployment Checklist

- [ ] Environment variables configured
- [ ] Tests passing
- [ ] Timeout values tuned for your workload
- [ ] Monitoring/alerting set up
- [ ] Documentation reviewed by team

### Deployment Steps

1. **Deploy to staging first**
   ```bash
   git push staging
   ```

2. **Monitor for timeout errors**
   - Check application logs
   - Monitor `/metrics` endpoint
   - Verify query performance

3. **Tune timeouts if needed**
   - Adjust environment variables
   - Redeploy

4. **Deploy to production**
   ```bash
   git push production
   ```

## Benefits

### 🎯 Database Protection

- **No exhaustion**: Queries can't run indefinitely
- **Resource control**: Predictable resource usage
- **Fair queuing**: No single query blocks others

### ⚡ Performance

- **Early failure**: Fast feedback on problematic queries
- **Traffic spikes**: System stays responsive under load
- **Predictable latency**: Upper bound on query time

### 🔒 Reliability

- **Safe retries**: Timeout resets between attempts
- **Clean shutdown**: No hanging connections
- **Neon compatible**: Works with pooled connections

## Troubleshooting

### Queries timing out frequently

**Symptoms**: Many timeout errors in logs

**Solutions**:
1. Check query performance with `EXPLAIN ANALYZE`
2. Add database indexes for commonly queried fields
3. Consider increasing timeout for specific endpoints
4. Use caching for expensive queries

### Timeout not being applied

**Symptoms**: Long-running queries not being cancelled

**Solutions**:
1. Check that `set_query_timeout()` is called before query
2. Verify environment variables are set correctly
3. Ensure using asyncpg driver (not psycopg2)
4. Check PostgreSQL logs for timeout settings

### Neon pooler issues

**Symptoms**: Errors about statement_timeout in connection string

**Solutions**:
- ✅ You're already using `SET LOCAL` (correct approach)
- ❌ Never use statement_timeout in DATABASE_URL
- ❌ Never use statement_timeout in server_settings at startup

## References

### PostgreSQL Documentation

- [SET LOCAL](https://www.postgresql.org/docs/current/sql-set.html)
- [statement_timeout](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-STATEMENT-TIMEOUT)

### Neon Documentation

- [PgBouncer pooling](https://neon.tech/docs/connect/connection-pooling)
- [Connection parameters](https://neon.tech/docs/connect/query-with-psql-editor)

### SQLAlchemy

- [Async engine](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Raw SQL execution](https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Connection.execute)

## Support

For issues or questions:

1. Check this documentation first
2. Review test suite for usage examples
3. Check application logs for timeout errors
4. Open a GitHub issue with:
   - Error message
   - Query that timed out
   - Current timeout setting
   - Expected vs actual behavior

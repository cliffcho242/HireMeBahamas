# SSL Mode Fix for asyncpg Driver

## Problem Statement

The application was failing to start with the error:
```
DB init skipped - Database warmup failed: connect() got an unexpected keyword argument 'sslmode'
```

## Root Cause

**Incompatibility between SQLAlchemy + asyncpg and `sslmode` parameter:**

1. **For psycopg2 (sync driver)**: `sslmode=require` can be included in the DATABASE_URL query string
   ```
   postgresql://user:pass@host:5432/db?sslmode=require
   ```

2. **For asyncpg (async driver)**: SQLAlchemy incorrectly passes `sslmode` from the URL as a keyword argument to `asyncpg.connect()`, which doesn't accept it.

3. **The Fix**: For asyncpg, SSL must be configured in `connect_args` as `ssl='require'` or `ssl=True`, NOT in the URL.

## Solution Implemented

### 1. Remove Blocking Guards
Removed the guards that were preventing URLs with `sslmode` parameter from these files:
- `app/database.py`
- `api/database.py`
- `api/backend_app/database.py`

### 2. Strip sslmode from URL for asyncpg
Added logic to automatically remove `sslmode` from DATABASE_URL when using asyncpg:

```python
# CRITICAL: Remove sslmode from URL for asyncpg compatibility
if "sslmode=" in DATABASE_URL:
    parsed_url = urlparse(DATABASE_URL)
    query_params = parse_qs(parsed_url.query)
    if 'sslmode' in query_params:
        del query_params['sslmode']
        logger.info("Removed sslmode from DATABASE_URL (asyncpg requires SSL in connect_args)")
    new_query = urlencode(query_params, doseq=True)
    DATABASE_URL = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query,
        parsed_url.fragment
    ))
```

### 3. Add SSL to connect_args
Added SSL configuration to `connect_args` in engine creation:

```python
connect_args={
    "timeout": CONNECT_TIMEOUT,
    "command_timeout": COMMAND_TIMEOUT,
    # SSL configuration for asyncpg
    # asyncpg does NOT accept sslmode in URL - it must be in connect_args
    "ssl": "require" if settings.ENVIRONMENT == "production" else True,
    "server_settings": {
        "jit": "off",
        "application_name": "hiremebahamas",
    },
}
```

## Files Modified

1. **app/database.py** - Removed sslmode blocking guard
2. **api/database.py** - Removed sslmode blocking guard
3. **api/backend_app/database.py** - Removed sslmode blocking guard
4. **backend/app/core/database.py** - Strip sslmode from URL, add SSL to connect_args
5. **backend/app/database.py** - Strip sslmode from URL, add SSL to connect_args

## Testing

Created `test_sslmode_fix.py` to verify:
- ✅ sslmode is stripped from DATABASE_URL for asyncpg
- ✅ SSL is correctly configured in connect_args
- ✅ No 'sslmode' keyword argument error occurs
- ✅ Functions gracefully handle connection failures

### Test Results
```
✅ ALL TESTS PASSED
- sslmode parameter is correctly handled
- No 'unexpected keyword argument' errors
- Functions gracefully handle connection failures
- Fix is working as expected
```

## Deployment Notes

### Environment Variables
The application now accepts DATABASE_URL with or without `sslmode`:

```bash
# With sslmode (will be auto-stripped for asyncpg)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?sslmode=require

# Without sslmode (SSL will be configured via connect_args)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
```

### SSL Configuration
- **Production**: Uses `ssl='require'` (enforces SSL)
- **Development/Test**: Uses `ssl=True` (enables SSL if available)

## Benefits

1. **Backward Compatibility**: Existing DATABASE_URLs with `sslmode=require` work without modification
2. **Automatic Handling**: The fix automatically detects and strips `sslmode` from URLs
3. **Proper SSL**: SSL is correctly configured for asyncpg via `connect_args`
4. **Graceful Degradation**: Functions handle connection failures gracefully
5. **No Breaking Changes**: Application can start even if database is temporarily unavailable

## References

- [asyncpg SSL documentation](https://magicstack.github.io/asyncpg/current/api/index.html#connection)
- [SQLAlchemy asyncpg documentation](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.asyncpg)
- PostgreSQL sslmode options: disable, allow, prefer, require, verify-ca, verify-full

## Security Summary

- ✅ No security vulnerabilities introduced
- ✅ SSL is properly enforced in production (`ssl='require'`)
- ✅ Connections are encrypted when connecting to remote databases
- ✅ CodeQL security scan passed with 0 alerts

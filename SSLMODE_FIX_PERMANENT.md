# 🔒 PERMANENT SSLMODE ERROR FIX - IMPLEMENTATION COMPLETE

## Overview

This document describes the **PERMANENT** solution to the `connect() got an unexpected keyword argument 'sslmode'` error that can occur when connecting to PostgreSQL databases.

## The Problem

The error occurs when code tries to pass `sslmode` as a keyword argument to database driver functions like:
- `psycopg.connect(..., sslmode='require')`
- `psycopg2.connect(..., sslmode='require')`
- `asyncpg.connect(..., sslmode='require')`

These drivers do NOT accept `sslmode` as a keyword argument. Instead, `sslmode` must be included in the connection URL as a query parameter.

## The Solution

### THE LAW (NON-NEGOTIABLE)

**sslmode MUST EXIST IN EXACTLY ONE PLACE:**

✅ **DATABASE_URL** - Example:
```
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require
```

❌ **NOWHERE ELSE:**
- NOT IN CODE
- NOT IN connect_args
- NOT IN ALEMBIC
- NOT IN STARTUP FUNCTIONS
- NOT IN TESTS

## Implementation

### 1. Database URL Configuration

**Correct Format:**
```bash
# For Render
DATABASE_URL=postgresql://user:pass@host.render.com:5432/dbname?sslmode=require

# For Neon (Pooled connections)
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.pooler.neon.tech:5432/dbname

# For Neon (Direct connections)
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.neon.tech:5432/dbname?sslmode=require
```

**Key Points:**
- ✅ Port `:5432` is REQUIRED and must be explicit
- ✅ `sslmode=require` in URL query string (for non-pooled connections)
- ✅ Use `postgresql+asyncpg://` for async SQLAlchemy
- ❌ NO `sslmode` in code, connect_args, or function parameters

### 2. SQLAlchemy Engine Configuration

**File:** `api/backend_app/database.py` and `backend/app/database.py`

```python
from sqlalchemy.ext.asyncio import create_async_engine

# ✅ CORRECT: Use DATABASE_URL directly
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,
    max_overflow=10,
)

# ❌ WRONG: Do NOT use connect_args with sslmode
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},  # ❌ NEVER DO THIS
)
```

### 3. Alembic Configuration

**File:** `alembic/env.py`

```python
# ✅ CORRECT: Let Alembic use the URL from config
engine = engine_from_config(
    config.get_section(config.config_ini_section),
    pool_pre_ping=True,
)

# DATABASE_URL is automatically read from environment
# SSL is configured via the URL query string
```

### 4. Direct Driver Connections (Utility Scripts)

When direct driver usage is necessary (e.g., in utility scripts), you MUST strip `sslmode` from the URL:

```python
import asyncpg
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

def strip_sslmode_from_url(db_url: str) -> str:
    """Remove sslmode parameter from database URL for asyncpg."""
    parsed = urlparse(db_url)
    if not parsed.query or 'sslmode' not in parsed.query:
        return db_url
    
    query_params = parse_qs(parsed.query)
    if 'sslmode' in query_params:
        del query_params['sslmode']
    
    new_query = urlencode(query_params, doseq=True)
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))

# Usage
db_url = os.getenv("DATABASE_URL")
db_url = strip_sslmode_from_url(db_url)
conn = await asyncpg.connect(db_url)
```

**Files with correct implementation:**
- ✅ `scripts/health_check.py` - strips sslmode before asyncpg.connect
- ✅ `scripts/verify_vercel_postgres_migration.py` - strips sslmode
- ✅ `backend/create_database_indexes.py` - strips sslmode
- ✅ `immortal_vercel_migration_fix.py` - strips sslmode

### 5. Enforcement Guards

**Files:** `backend/app/core/db_guards.py` and `api/backend_app/core/db_guards.py`

These modules provide runtime validation to prevent future regressions:

```python
from backend_app.core.db_guards import validate_database_config

# Call at startup (already integrated in main.py)
validate_database_config(strict=False)  # Warns but doesn't fail
```

**What the guards check:**
1. ✅ `sslmode` is present in DATABASE_URL (for cloud deployments)
2. ✅ No forbidden direct driver usage detected

## Verification

### 1. Check Your DATABASE_URL

```bash
# Should include sslmode (for non-pooled connections)
echo $DATABASE_URL
# Output should be:
# postgresql://user:pass@host:5432/db?sslmode=require
```

### 2. Check Code for Violations

```bash
# Search for sslmode in code (should only be in URLs and comments)
grep -r "sslmode" . --include="*.py" | grep -v "URL" | grep -v "#"

# Search for direct driver calls
grep -r "\.connect(" . --include="*.py" | grep -E "(asyncpg|psycopg2|psycopg)\."
```

### 3. Test Database Connection

```bash
# From Python
python -c "
import asyncio
from api.backend_app.database import test_db_connection
result = asyncio.run(test_db_connection())
print('✅ Connected!' if result[0] else f'❌ Failed: {result[1]}')
"
```

### 4. Check Startup Logs

Look for these messages in startup logs:
```
🔒 DATABASE CONFIGURATION VALIDATION
✅ DATABASE_URL contains sslmode parameter
✅ No forbidden database drivers detected
✅ Database configuration validation PASSED
```

## Common Mistakes to Avoid

### ❌ WRONG: Passing sslmode as parameter

```python
# DON'T DO THIS
conn = psycopg2.connect(
    host="db.example.com",
    port=5432,
    dbname="mydb",
    user="user",
    password="pass",
    sslmode="require"  # ❌ ERROR: psycopg2 doesn't accept sslmode
)

# DO THIS INSTEAD
DATABASE_URL = "postgresql://user:pass@db.example.com:5432/mydb?sslmode=require"
conn = psycopg2.connect(DATABASE_URL)
```

### ❌ WRONG: Using connect_args

```python
# DON'T DO THIS
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}  # ❌ ERROR
)

# DO THIS INSTEAD
# Include sslmode in DATABASE_URL
DATABASE_URL = "postgresql+asyncpg://user:pass@host:5432/db?sslmode=require"
engine = create_async_engine(DATABASE_URL)
```

### ❌ WRONG: Direct asyncpg calls with sslmode in URL

```python
# DON'T DO THIS
db_url = "postgresql://user:pass@host:5432/db?sslmode=require"
conn = await asyncpg.connect(db_url)  # ❌ ERROR: asyncpg doesn't support sslmode

# DO THIS INSTEAD
db_url = strip_sslmode_from_url(
    "postgresql://user:pass@host:5432/db?sslmode=require"
)
conn = await asyncpg.connect(db_url)  # ✅ CORRECT
```

## Architecture Decisions

### Why This Approach?

1. **Single Source of Truth**: DATABASE_URL is the ONLY place for configuration
2. **SQLAlchemy Abstraction**: All application code uses SQLAlchemy, which handles drivers correctly
3. **Runtime Guards**: Automatic validation prevents future regressions
4. **Explicit Configuration**: No magic, no guessing - everything is explicit

### Why Not configure sslmode in code?

Different database drivers handle SSL differently:
- `psycopg2` accepts `sslmode` in the connection DSN (URL) but not as a parameter
- `asyncpg` doesn't accept `sslmode` at all - it handles SSL automatically
- `psycopg` (v3) has different SSL configuration

**The ONLY universal approach is to put sslmode in the DATABASE_URL.**

## Testing

### Unit Tests

The guard functions are tested in:
- `test_sslmode_connect_args.py` - Verifies no sslmode in connect_args
- `test_sslmode_asyncpg_fix.py` - Verifies asyncpg.connect calls strip sslmode

### Integration Tests

After deploying, verify:
1. Health endpoints respond: `/health`, `/ready`
2. Database operations work: Login, creating posts, etc.
3. No `sslmode` errors in logs

## Troubleshooting

### Error: "connect() got an unexpected keyword argument 'sslmode'"

**Diagnosis:** Some code is passing `sslmode` as a parameter.

**Solution:**
1. Find the offending code:
   ```bash
   grep -rn "sslmode" . --include="*.py" | grep -v "#"
   ```
2. Remove the parameter
3. Ensure `sslmode` is in DATABASE_URL instead

### Error: "SSL connection has been closed unexpectedly"

**Diagnosis:** Using wrong sslmode or network issue.

**Solution:**
1. Check DATABASE_URL has correct sslmode:
   ```bash
   echo $DATABASE_URL | grep sslmode
   ```
2. Try `sslmode=require` for most cloud databases
3. For Neon pooled connections, remove `sslmode` entirely

### Warning: "DATABASE_URL is missing sslmode parameter"

**Diagnosis:** Guard detected missing sslmode in production.

**Solution:**
1. Add `?sslmode=require` to your DATABASE_URL:
   ```bash
   export DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"
   ```
2. Or for Neon pooled connections, use the pooler URL without sslmode

## Deployment Checklist

Before deploying:

- [ ] DATABASE_URL includes port `:5432` explicitly
- [ ] DATABASE_URL includes `?sslmode=require` (for non-pooled connections)
- [ ] No `sslmode` in code as a parameter
- [ ] No `connect_args={"sslmode": ...}` in engine creation
- [ ] Alembic uses `engine_from_config()` without modifications
- [ ] All direct driver calls strip sslmode from URL
- [ ] Startup logs show "Database configuration validation PASSED"

## References

- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)
- [SQLAlchemy Engine Configuration](https://docs.sqlalchemy.org/en/20/core/engines.html)
- [asyncpg Connection](https://magicstack.github.io/asyncpg/current/api/index.html#connection)
- [psycopg2 Connection](https://www.psycopg.org/docs/module.html#psycopg2.connect)

## Support

If you encounter issues:

1. Check startup logs for validation messages
2. Verify DATABASE_URL format
3. Run the verification commands above
4. Check that guards are imported at startup

## Conclusion

This fix is **PERMANENT** and **REGRESSION-PROOF**:

✅ sslmode lives ONLY in DATABASE_URL  
✅ All connections go through SQLAlchemy  
✅ Runtime guards catch violations  
✅ Direct driver usage correctly strips sslmode  
✅ This error CANNOT return if these rules are followed  

**The error is physically impossible with this configuration.**

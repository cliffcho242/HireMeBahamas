# SQLAlchemy Engine Configuration

## Overview

This document describes the production-ready SQLAlchemy engine configuration used across HireMeBahamas. The configuration is optimized for cloud deployments and works with multiple database drivers.

## Configuration

All database engine configurations in this project use the following parameters:

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Validate connections before use
    pool_size=5,             # Base pool size
    max_overflow=10,         # Maximum overflow connections
    pool_recycle=300,        # Recycle connections every 5 minutes
    connect_args={
        "timeout": 5,        # Connection timeout (asyncpg)
        "command_timeout": 30,  # Query timeout
    },
)
```

## Parameters Explained

### `pool_pre_ping=True`
- **Purpose**: Validates connections before use
- **Benefit**: Prevents hanging requests from stale connections
- **Required**: Yes

### `pool_size=5`
- **Purpose**: Base connection pool size
- **Default**: 5 (configurable via `DB_POOL_SIZE` env var)
- **Benefit**: Adequate for production load without overloading the database

### `max_overflow=10`
- **Purpose**: Maximum overflow connections beyond pool_size
- **Default**: 10 (configurable via `DB_MAX_OVERFLOW` env var)
- **Benefit**: Burst capacity for traffic spikes

### `pool_recycle=300`
- **Purpose**: Recycle connections every 5 minutes
- **Default**: 300 seconds (configurable via `DB_POOL_RECYCLE` env var)
- **Benefit**: Prevents dead connections from idle timeouts

### `connect_args`

#### For asyncpg (async driver)
```python
connect_args={
    "timeout": 5,           # Connection timeout
    "command_timeout": 30,  # Query timeout
}
```

#### For psycopg2/psycopg3 (sync drivers)
```python
connect_args={
    "connect_timeout": 5,   # Connection timeout
}
```

**Note**: The parameter name differs between drivers:
- **asyncpg**: Uses `"timeout"`
- **psycopg2/psycopg3**: Use `"connect_timeout"`

## Database Driver Compatibility

This configuration is compatible with:

### ✅ asyncpg (async)
- **URL format**: `postgresql+asyncpg://user:pass@host:port/db`
- **Connection parameter**: `timeout`
- **Best for**: High-performance async applications
- **Current implementation**: ✅ Active

### ✅ psycopg2 (sync)
- **URL format**: `postgresql://user:pass@host:port/db`
- **Connection parameter**: `connect_timeout`
- **Best for**: Traditional sync applications

### ✅ psycopg3 (sync/async)
- **URL format**: `postgresql+psycopg://user:pass@host:port/db`
- **Connection parameter**: `connect_timeout`
- **Best for**: Modern applications with async support

### ✅ Neon (cloud PostgreSQL)
- **Provider**: Neon Serverless PostgreSQL
- **Compatibility**: Works with all drivers above
- **Requirements**: SSL required (`?sslmode=require`)
- **Note**: Same configuration works seamlessly

### ✅ Render (cloud PostgreSQL)
- **Provider**: Render PostgreSQL
- **Compatibility**: Works with all drivers above
- **Requirements**: SSL required (`?sslmode=require`)
- **Note**: Same configuration works seamlessly

## Environment Variables

All configuration parameters are configurable via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_POOL_SIZE` | 5 | Base connection pool size |
| `DB_MAX_OVERFLOW` | 10 | Maximum overflow connections |
| `DB_POOL_RECYCLE` | 300 | Connection recycle time (seconds) |
| `DB_CONNECT_TIMEOUT` | 5 | Connection timeout (seconds) |
| `DB_COMMAND_TIMEOUT` | 30 | Query timeout (seconds) |

## Implementation Files

The configuration is implemented in:

1. **`api/database.py`**
   - Vercel serverless API configuration
   - Uses `create_async_engine` with asyncpg
   - Lightweight and optimized for cold starts

2. **`api/backend_app/database.py`**
   - Alternative backend configuration
   - Uses `create_async_engine` with asyncpg
   - Includes SSL context for Railway/Render

3. **`backend/app/core/database.py`**
   - Main backend configuration
   - Uses `create_async_engine` with asyncpg
   - Full-featured with lazy initialization

4. **`backend/app/core/config.py`**
   - Configuration settings
   - Centralizes all environment variable defaults

## Benefits

This configuration provides:

1. **Reliability**
   - `pool_pre_ping=True`: Detects stale connections
   - `pool_recycle=300`: Prevents connection timeouts
   - Connection validation before use

2. **Performance**
   - `pool_size=5`: Adequate base capacity
   - `max_overflow=10`: Handles traffic spikes
   - Connection pooling reduces overhead

3. **Fault Tolerance**
   - `timeout=5s`: Handles cold starts and DNS stalls
   - `command_timeout=30s`: Prevents runaway queries
   - Automatic connection retry logic

4. **Cloud Compatibility**
   - Works with Neon, Render, Railway
   - SSL support (`sslmode=require`)
   - Compatible with multiple drivers

## Testing

Run the test suite to verify configuration:

```bash
# Test production engine configuration
python test_production_engine_config.py

# Test driver compatibility
python test_sqlalchemy_engine_compatibility.py
```

## Migration Guide

### Switching Database Drivers

To switch from asyncpg to psycopg3:

1. Update `requirements.txt`:
   ```
   # Remove: asyncpg
   # Add: psycopg[binary,pool]
   ```

2. Update `DATABASE_URL`:
   ```
   # From: postgresql+asyncpg://...
   # To: postgresql+psycopg://...
   ```

3. Update `connect_args` in database.py:
   ```python
   # From:
   connect_args={"timeout": 5}
   
   # To:
   connect_args={"connect_timeout": 5}
   ```

### Switching Cloud Providers

The configuration works identically across providers. Simply update:

1. `DATABASE_URL` to point to new provider
2. Ensure `?sslmode=require` is in the URL
3. Verify connection with health check endpoint

## Troubleshooting

### Connection Timeouts

If experiencing connection timeouts:

1. Increase `DB_CONNECT_TIMEOUT`:
   ```bash
   export DB_CONNECT_TIMEOUT=10
   ```

2. Check database host accessibility
3. Verify SSL configuration

### Pool Exhaustion

If pool is exhausted:

1. Increase `DB_POOL_SIZE`:
   ```bash
   export DB_POOL_SIZE=10
   ```

2. Increase `DB_MAX_OVERFLOW`:
   ```bash
   export DB_MAX_OVERFLOW=20
   ```

3. Monitor connection usage

### Stale Connections

If experiencing stale connections:

1. Reduce `DB_POOL_RECYCLE`:
   ```bash
   export DB_POOL_RECYCLE=180  # 3 minutes
   ```

2. Verify `pool_pre_ping=True` is set
3. Check database connection limits

## References

- [SQLAlchemy Engine Configuration](https://docs.sqlalchemy.org/en/14/core/engines.html)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [psycopg3 Documentation](https://www.psycopg.org/psycopg3/docs/)
- [Neon Documentation](https://neon.tech/docs/)
- [Render PostgreSQL](https://render.com/docs/databases)

## Summary

The SQLAlchemy engine configuration in HireMeBahamas is production-ready and optimized for:

✅ **Reliability**: Connection validation and automatic recycling  
✅ **Performance**: Efficient pooling with burst capacity  
✅ **Compatibility**: Works with multiple drivers and cloud providers  
✅ **Maintainability**: Centralized configuration with environment variables  

All configurations have been tested and verified to work with psycopg2, psycopg3, asyncpg, Neon, and Render.

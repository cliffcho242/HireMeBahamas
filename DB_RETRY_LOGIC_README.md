# Safe Database Retry Logic

## Overview

This feature implements a safe retry mechanism for database operations with strict safety rules to prevent data corruption.

**✅ DO: Use only on idempotent read operations (SELECT queries)**  
**🚫 DON'T: Never use on write operations (INSERT, UPDATE, DELETE)**

## Location

- **Implementation**: `backend/app/core/db_retry.py`
- **Tests**: `backend/test_db_retry.py`
- **Examples**: `backend/example_db_retry_usage.py`
- **Demo**: `backend/demo_db_retry_simple.py`

## Features

- ✅ Configurable retry attempts (default: 3)
- ✅ Configurable delay between retries (default: 1 second)
- ✅ Automatic logging of retry attempts
- ✅ Supports both decorator and function-based usage
- ✅ Thread-safe implementation
- ✅ Preserves function metadata (`__name__`, `__doc__`)
- ✅ Works with any exception type

## Installation

The module is already integrated into the backend. No additional installation required.

```python
from app.core.db_retry import db_retry, retry_db_operation
```

## Usage

### Basic Usage (Decorator)

```python
from app.core.db_retry import db_retry

# ✅ SAFE: Read-only operation
@db_retry
async def get_user_by_email(email: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
```

### Custom Retry Parameters

```python
# Retry up to 5 times with 2-second delays
@db_retry(retries=5, delay=2.0)
async def get_user_statistics():
    async with AsyncSessionLocal() as session:
        # Complex query that might timeout
        return await session.execute(...)
```

### Inline Usage (Without Decorator)

```python
from app.core.db_retry import retry_db_operation

result = retry_db_operation(
    lambda: session.query(User).filter(User.id == user_id).first(),
    retries=3,
    delay=1.0
)
```

## Safety Rules

### ✅ Safe Use Cases (DO)

1. **SELECT queries** - Reading data
   ```python
   @db_retry
   async def get_all_active_users():
       return await session.execute(select(User).where(User.is_active == True))
   ```

2. **COUNT operations** - Counting records
   ```python
   @db_retry
   async def count_users():
       return await session.execute(select(func.count(User.id)))
   ```

3. **Idempotent reads** - Same result every time
   ```python
   @db_retry
   async def check_user_exists(email: str):
       result = await session.execute(select(User).where(User.email == email))
       return result.scalar_one_or_none() is not None
   ```

### 🚫 Unsafe Use Cases (DON'T)

1. **INSERT operations** - Creating new records
   ```python
   # ❌ BAD - Could create duplicate records
   # @db_retry  # DON'T DO THIS
   async def create_user(user_data):
       user = User(**user_data)
       session.add(user)
       await session.commit()
   ```

2. **UPDATE operations** - Modifying existing records
   ```python
   # ❌ BAD - Could update multiple times
   # @db_retry  # DON'T DO THIS
   async def update_user_status(user_id, status):
       await session.execute(
           update(User).where(User.id == user_id).values(status=status)
       )
   ```

3. **DELETE operations** - Removing records
   ```python
   # ❌ BAD - Could cause data loss
   # @db_retry  # DON'T DO THIS
   async def delete_user(user_id):
       await session.execute(delete(User).where(User.id == user_id))
   ```

4. **Non-idempotent operations** - Different result on each call
   ```python
   # ❌ BAD - Generates new value each time
   # @db_retry  # DON'T DO THIS
   async def create_unique_token():
       token = generate_random_token()
       user.token = token
       await session.commit()
   ```

## How It Works

1. The function is executed
2. If it succeeds, the result is returned immediately
3. If it fails with an exception:
   - A warning is logged with the attempt number
   - The system waits for the configured delay
   - The function is retried
4. This continues until either:
   - The function succeeds (returns result)
   - Maximum retries are exhausted (raises last exception)

### Example Log Output

```
WARNING - DB attempt 1/3 failed: ConnectionError: Connection timeout
WARNING - DB attempt 2/3 failed: ConnectionError: Connection timeout
INFO - Operation succeeded on attempt 3
```

## Testing

Run the comprehensive test suite:

```bash
cd /home/runner/work/HireMeBahamas/HireMeBahamas
python -m pytest backend/test_db_retry.py -v
```

Run the interactive demo:

```bash
cd backend
python demo_db_retry_simple.py
```

## Test Coverage

The test suite includes 23 tests covering:

- ✅ Successful execution without retries
- ✅ Retry on transient failures
- ✅ Maximum retry limit enforcement
- ✅ Delay timing validation
- ✅ Logging output verification
- ✅ Different exception types
- ✅ Function metadata preservation
- ✅ Edge cases (zero retries, very small delays, None returns)
- ✅ Safety documentation validation

## Parameters

### `db_retry` Decorator

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `retries` | `int` | `3` | Maximum number of retry attempts |
| `delay` | `float` | `1.0` | Delay in seconds between retries |

### `retry_db_operation` Function

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `operation` | `Callable` | Required | The function to retry |
| `*args` | `Any` | - | Positional arguments for the operation |
| `retries` | `int` | `3` | Maximum number of retry attempts |
| `delay` | `float` | `1.0` | Delay in seconds between retries |
| `**kwargs` | `Any` | - | Keyword arguments for the operation |

## Best Practices

1. **Only use on reads**: Never use on INSERT, UPDATE, or DELETE operations
2. **Verify idempotency**: Ensure the operation produces the same result when called multiple times
3. **Use appropriate retry counts**: 
   - Fast operations: 3 retries (default)
   - Slow/complex queries: 5 retries
   - Critical operations: Consider not using retry at all
4. **Set reasonable delays**:
   - Fast network: 0.5-1 second
   - Slow network: 2-3 seconds
   - Cold start scenarios: 5-10 seconds
5. **Log and monitor**: Review retry logs to identify persistent issues
6. **Handle final failures**: Always have error handling for when all retries fail

## Performance Considerations

- **Latency**: Each retry adds `delay` seconds to the operation
- **Maximum latency**: `retries * delay` seconds (e.g., 3 retries × 1s = 3s max)
- **No exponential backoff**: Uses linear delay for predictability
- **Thread-safe**: Can be used in multi-threaded environments

## When NOT to Use

1. **Write operations** - Could cause duplicate/corrupted data
2. **Time-sensitive operations** - Retry delay may be unacceptable
3. **Operations with side effects** - External API calls, sending emails, etc.
4. **Already-resilient code** - If the database client already handles retries
5. **Testing/debugging** - May hide underlying issues

## Troubleshooting

### Too Many Retries in Logs

```python
# Reduce retry attempts for faster failure
@db_retry(retries=2, delay=0.5)
async def quick_operation():
    # ...
```

### Operations Timing Out

```python
# Increase delay between retries
@db_retry(retries=5, delay=3.0)
async def slow_operation():
    # ...
```

### Want to Disable Retries

```python
# Simply don't use the decorator
async def no_retry_operation():
    # Direct database call
    # ...
```

## Related Documentation

- **Database Configuration**: `backend/app/database.py`
- **Database Health Checks**: `backend/app/core/db_health.py`
- **Production Config**: `PRODUCTION_CONFIG_ABSOLUTE_BANS.md`

## Credits

- **Author**: GitHub Copilot
- **Date**: December 2025
- **Purpose**: Implement safe retry logic for transient database failures
- **Issue**: #2 SAFE RETRY LOGIC (NO STORM)

## License

Part of the HireMeBahamas project. See repository LICENSE for details.

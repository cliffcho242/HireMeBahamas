# Request Timeout Guard

## Overview

The Request Timeout Guard feature provides comprehensive timeout protection for async operations in the HireMeBahamas application. This prevents long-running requests from blocking resources, which is critical for:

- **External API calls** - Prevent slow external services from hanging your app
- **File uploads** - Cancel uploads that take too long
- **Heavy database queries** - Stop queries that exceed reasonable time limits

## Features

✅ **Generic timeout wrapper** for any async operation  
✅ **Traffic-spike protection** prevents resource exhaustion  
✅ **Memory-efficient** timeout handling using Python's asyncio  
✅ **FastAPI compatible** - works seamlessly with FastAPI endpoints  
✅ **Graceful degradation** - handle timeouts without breaking the app  
✅ **Configurable timeouts** - adjust per operation type  

## Installation

The timeout utilities are already integrated into the application. No additional installation required.

## Usage

### Basic Usage

```python
import asyncio
from app.core.request_timeout import with_timeout

async def my_endpoint():
    try:
        # Wrap any async operation with timeout (default: 8 seconds)
        result = await with_timeout(
            slow_external_api_call(),
            timeout=8
        )
        return result
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Operation timed out. Please try again."
        )
```

### File Upload with Timeout

```python
from app.core.request_timeout import with_upload_timeout

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Automatically uses 10-second timeout for uploads
        result = await with_upload_timeout(
            process_and_save_file(file)
        )
        return {"url": result}
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="Upload timed out. Try a smaller file."
        )
```

### External API Call with Timeout

```python
from app.core.request_timeout import with_api_timeout
import httpx

@app.get("/external-data")
async def fetch_external():
    try:
        async with httpx.AsyncClient() as client:
            # Automatically uses 8-second timeout for API calls
            response = await with_api_timeout(
                client.get("https://api.example.com/data")
            )
            return response.json()
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="External API timed out."
        )
```

### Heavy Query with Timeout

```python
from app.core.request_timeout import with_heavy_query_timeout

@app.get("/analytics")
async def get_analytics(db: AsyncSession = Depends(get_db)):
    try:
        # Automatically uses 15-second timeout for heavy operations
        stats = await with_heavy_query_timeout(
            db.execute(complex_aggregation_query)
        )
        return stats
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Query timed out. Try a narrower date range."
        )
```

### Graceful Degradation

Instead of failing completely, return partial data when operations timeout:

```python
from app.core.request_timeout import with_timeout

@app.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db)):
    dashboard_data = {}
    
    # Try to get user count with timeout
    try:
        dashboard_data["user_count"] = await with_timeout(
            get_user_count(db),
            timeout=2
        )
    except asyncio.TimeoutError:
        dashboard_data["user_count"] = "unavailable"
    
    # Try to get post count with timeout
    try:
        dashboard_data["post_count"] = await with_timeout(
            get_post_count(db),
            timeout=2
        )
    except asyncio.TimeoutError:
        dashboard_data["post_count"] = "unavailable"
    
    return dashboard_data
```

## Configuration

Default timeouts are configured in `app/core/request_timeout.py`:

```python
DEFAULT_TIMEOUT_SECONDS = 8        # General operations
UPLOAD_TIMEOUT_SECONDS = 10        # File uploads
EXTERNAL_API_TIMEOUT_SECONDS = 8   # External API calls
HEAVY_QUERY_TIMEOUT_SECONDS = 15   # Heavy database queries
```

You can override these by specifying custom timeout values:

```python
# Custom timeout for specific operation
result = await with_timeout(operation(), timeout=5)

# Or get recommended timeout for operation type
timeout = get_timeout_for_operation('upload')
result = await with_timeout(operation(), timeout=timeout)
```

## API Reference

### `with_timeout(coro, timeout=8)`

Execute an async operation with timeout protection.

**Parameters:**
- `coro` - The coroutine to execute
- `timeout` - Maximum time in seconds (default: 8)

**Returns:** Result of the coroutine if completed within timeout

**Raises:** `asyncio.TimeoutError` if operation exceeds timeout

### `with_upload_timeout(coro)`

Convenience wrapper for file upload operations (10-second timeout).

### `with_api_timeout(coro)`

Convenience wrapper for external API calls (8-second timeout).

### `with_heavy_query_timeout(coro)`

Convenience wrapper for heavy operations (15-second timeout).

### `get_timeout_for_operation(operation_type)`

Get recommended timeout for an operation type.

**Parameters:**
- `operation_type` - One of: 'upload', 'api', 'heavy', 'default'

**Returns:** Timeout in seconds

## Integration with Database Query Timeouts

This module complements `app/core/query_timeout.py`, which provides PostgreSQL-level timeouts. For comprehensive protection, use both:

```python
from app.core.request_timeout import with_timeout
from app.core.query_timeout import with_query_timeout

@app.get("/users/search")
async def search_users(query: str, db: AsyncSession = Depends(get_db)):
    try:
        async def search_operation():
            # PostgreSQL-level timeout
            async with with_query_timeout(db, timeout_ms=5000):
                result = await db.execute(
                    select(User).where(User.username.ilike(f"%{query}%"))
                )
                return result.scalars().all()
        
        # Python asyncio-level timeout
        users = await with_timeout(search_operation(), timeout=8)
        return {"users": users}
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Search timed out."
        )
```

## Testing

Run the timeout tests:

```bash
cd backend
python test_request_timeout_simple.py
```

Expected output:
```
============================================================
REQUEST TIMEOUT UTILITY TESTS
============================================================

✓ get_timeout_for_operation returns correct values
✓ Fast operation completed successfully
✓ Slow operation timed out as expected
✓ Exception propagated correctly
✓ Upload timeout wrapper works correctly
✓ API timeout wrapper works correctly
✓ Heavy query timeout wrapper works correctly
✓ Small file upload succeeded
✓ Multiple concurrent operations completed successfully

============================================================
ALL TESTS PASSED ✓
============================================================
```

## Examples

See `backend/example_request_timeout_usage.py` for comprehensive examples including:

- File upload with timeout
- External API calls with timeout
- Heavy database queries with timeout
- Custom timeout values
- Multiple operations with different timeouts
- Combining request and query timeouts
- Graceful degradation patterns

## Best Practices

1. **Always wrap external operations** - API calls, uploads, cloud storage
2. **Use appropriate timeouts** - Upload: 10s, API: 8s, Heavy Query: 15s
3. **Handle TimeoutError gracefully** - Return meaningful error messages
4. **Consider graceful degradation** - Return partial data instead of failing completely
5. **Combine with database timeouts** - Use both request and query timeouts for comprehensive protection
6. **Log timeout events** - Monitor which operations are timing out
7. **Test timeout scenarios** - Ensure your code handles timeouts correctly

## Security Considerations

✅ **Prevents DoS attacks** - Limits resource consumption from slow operations  
✅ **Protects against hanging connections** - Cancels operations that hang indefinitely  
✅ **Memory efficient** - Uses asyncio's native timeout mechanism  
✅ **No SQL injection risk** - Pure Python implementation, no database interaction  

## Production Deployment

The timeout guards are automatically active in production. Monitor logs for timeout warnings:

```
Operation timed out after 8 seconds. This may indicate a slow external service or heavy processing.
```

If you see frequent timeouts:

1. **Investigate the operation** - Is it inherently slow?
2. **Optimize if possible** - Can you make it faster?
3. **Adjust timeout if needed** - Some operations legitimately need more time
4. **Consider async alternatives** - Use background tasks for very slow operations

## Related Documentation

- `backend/app/core/query_timeout.py` - PostgreSQL-level query timeouts
- `backend/app/core/upload.py` - File upload utilities with timeout protection
- `backend/example_request_timeout_usage.py` - Comprehensive usage examples
- `backend/test_request_timeout_simple.py` - Test suite

## Support

For questions or issues related to request timeouts, check:

1. The examples in `example_request_timeout_usage.py`
2. The test suite in `test_request_timeout_simple.py`
3. The inline documentation in `app/core/request_timeout.py`

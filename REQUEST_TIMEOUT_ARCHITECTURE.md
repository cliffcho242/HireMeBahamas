# Request Timeout Guard Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FastAPI Application                         │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                        API Endpoints                            │ │
│  │  • /upload/avatar                                               │ │
│  │  • /upload/portfolio                                            │ │
│  │  • /upload/document                                             │ │
│  │  • /analytics                                                   │ │
│  │  • /external-data                                               │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                ↓                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              Request Timeout Guard Layer                        │ │
│  │                                                                  │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │ │
│  │  │with_upload   │  │with_api      │  │with_heavy    │         │ │
│  │  │_timeout()    │  │_timeout()    │  │_query_timeout│         │ │
│  │  │  (10s)       │  │  (8s)        │  │    (15s)     │         │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘         │ │
│  │                          ↓                                       │ │
│  │                   with_timeout()                                │ │
│  │              (Generic timeout wrapper)                          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                ↓                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    Business Logic Layer                         │ │
│  │                                                                  │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │ │
│  │  │Upload Ops    │  │External APIs │  │Heavy Queries │         │ │
│  │  │• Local       │  │• Cloudinary  │  │• Analytics   │         │ │
│  │  │• GCS         │  │• 3rd party   │  │• Reports     │         │ │
│  │  │• Cloudinary  │  │  services    │  │• Aggregations│         │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘         │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
        ┌────────────────────────────────────────────┐
        │            External Resources              │
        │                                            │
        │  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
        │  │ Cloud    │  │ External │  │Database │ │
        │  │ Storage  │  │   APIs   │  │  (SQL)  │ │
        │  └──────────┘  └──────────┘  └─────────┘ │
        └────────────────────────────────────────────┘
```

## Request Flow with Timeout Protection

### Example 1: File Upload Flow

```
User Request
    ↓
FastAPI Endpoint: POST /upload/avatar
    ↓
with_upload_timeout()  ←─────────── 10 second timeout guard
    ↓
upload_image()
    ↓
├─ Read file content (async)
├─ Resize image (sync)
└─ Save to storage (async)
    ↓
    ├─ Local Storage  → Success ✓
    ├─ Google Cloud   → Success ✓ (or timeout → fallback)
    └─ Cloudinary     → Success ✓ (or timeout → fallback)
    ↓
Response to User
    ↓
    ├─ 200 OK: File uploaded successfully
    └─ 408 Timeout: Upload timed out, please try again
```

### Example 2: External API Call Flow

```
User Request
    ↓
FastAPI Endpoint: GET /external-data
    ↓
with_api_timeout()  ←─────────── 8 second timeout guard
    ↓
httpx.get(external_api_url)
    ↓
    ├─ Fast API (< 8s) → Success ✓
    └─ Slow API (> 8s) → TimeoutError → 504 Gateway Timeout
    ↓
Response to User
    ↓
    ├─ 200 OK: External data retrieved
    └─ 504 Timeout: External service timed out
```

### Example 3: Heavy Query Flow

```
User Request
    ↓
FastAPI Endpoint: GET /analytics
    ↓
with_heavy_query_timeout()  ←─────────── 15 second timeout guard
    ↓
with_query_timeout()  ←─────────── 5 second PostgreSQL timeout
    ↓
db.execute(complex_aggregation_query)
    ↓
    ├─ Normal Query (< 15s) → Success ✓
    └─ Slow Query (> 15s) → TimeoutError → 504 Gateway Timeout
    ↓
Response to User
    ↓
    ├─ 200 OK: Analytics data
    └─ 504 Timeout: Query timed out, try narrower date range
```

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        request_timeout.py                        │
│                      (Core Timeout Module)                       │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    with_timeout()                         │   │
│  │  • Uses asyncio.wait_for()                               │   │
│  │  • Cancels operation if timeout exceeded                 │   │
│  │  • Logs timeout events                                   │   │
│  │  • Returns result or raises TimeoutError                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Convenience Wrappers:                                           │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │with_upload    │  │with_api       │  │with_heavy     │       │
│  │_timeout()     │  │_timeout()     │  │_query_timeout │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
│         ↓                  ↓                    ↓                │
└─────────┼──────────────────┼────────────────────┼────────────────┘
          │                  │                    │
          │                  │                    │
          ↓                  ↓                    ↓
┌─────────────────┐  ┌──────────────┐  ┌──────────────────┐
│   upload.py     │  │External APIs │  │ Query Operations │
│ • upload_image  │  │ • httpx.get  │  │ • db.execute()   │
│ • upload_to_gcs │  │ • API calls  │  │ • Aggregations   │
│ • upload_to_    │  └──────────────┘  └──────────────────┘
│   cloudinary    │
└─────────────────┘
```

## Timeout Configuration Matrix

| Operation Type     | Timeout | Use Case                        | Wrapper Function          |
|-------------------|---------|----------------------------------|---------------------------|
| File Upload       | 10s     | Upload to local/cloud storage    | `with_upload_timeout()`   |
| External API      | 8s      | 3rd party API calls             | `with_api_timeout()`      |
| Heavy Query       | 15s     | Analytics, reports, aggregations | `with_heavy_query_timeout()` |
| Custom            | Variable| Any async operation             | `with_timeout(timeout=N)` |

## Error Handling Flow

```
Operation Started
    ↓
Timeout Guard Applied
    ↓
    ├─ Operation Completes (< timeout)
    │  ↓
    │  Return Result ✓
    │
    ├─ Timeout Exceeded
    │  ↓
    │  Cancel Operation
    │  ↓
    │  Log Warning
    │  ↓
    │  Raise asyncio.TimeoutError
    │  ↓
    │  Caught by Endpoint Handler
    │  ↓
    │  Return HTTPException
    │  ↓
    │  ├─ 408 Request Timeout (uploads)
    │  └─ 504 Gateway Timeout (APIs/queries)
    │
    └─ Other Exception
       ↓
       Propagate Exception ⚠
       ↓
       Handle in Endpoint
```

## Integration Points

### 1. Upload Operations (upload.py)

```python
# Before: No timeout protection
async with aiofiles.open(file_path, "wb") as f:
    content = await file.read()
    await f.write(content)

# After: With timeout protection
await with_upload_timeout(
    async_save_operation()
)
```

### 2. External API Calls

```python
# Before: No timeout protection
response = await httpx_client.get(url)

# After: With timeout protection
response = await with_api_timeout(
    httpx_client.get(url)
)
```

### 3. Heavy Database Queries

```python
# Before: Only PostgreSQL timeout
async with with_query_timeout(db, timeout_ms=5000):
    result = await db.execute(query)

# After: Double protection
async def query_operation():
    async with with_query_timeout(db, timeout_ms=5000):
        return await db.execute(query)

result = await with_heavy_query_timeout(query_operation())
```

## Performance Characteristics

```
┌─────────────────────────────────────────────────────────────┐
│                    Timeout Guard Performance                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Overhead per Request:      ~microseconds                    │
│  Memory Footprint:          Minimal (native asyncio)         │
│  CPU Impact:                Negligible                       │
│  Concurrency Support:       Unlimited                        │
│  Thread Safety:             Yes (asyncio-based)              │
│                                                               │
│  Performance Impact:                                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Fast Operations (< timeout):  No impact            ✓ │   │
│  │ Slow Operations (> timeout):  Immediate cancel     ✓ │   │
│  │ Resource Protection:          Significant gain     ✓ │   │
│  │ User Experience:              Better error messages ✓│   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Graceful Degradation Pattern

```
Dashboard Endpoint
    ↓
Try: Get User Count (2s timeout)
    ├─ Success → user_count = 1234
    └─ Timeout → user_count = "unavailable"
    ↓
Try: Get Post Count (2s timeout)
    ├─ Success → post_count = 5678
    └─ Timeout → post_count = "unavailable"
    ↓
Try: Get Recent Activity (3s timeout)
    ├─ Success → recent_activity = [...]
    └─ Timeout → recent_activity = "unavailable"
    ↓
Return Partial Dashboard Data ✓
```

## Best Practices Summary

```
┌────────────────────────────────────────────────────────────┐
│                      DO's                                   │
├────────────────────────────────────────────────────────────┤
│ ✓ Use timeout guards for all external operations          │
│ ✓ Choose appropriate timeout for operation type           │
│ ✓ Handle TimeoutError gracefully                          │
│ ✓ Log timeout events for monitoring                       │
│ ✓ Return meaningful error messages to users               │
│ ✓ Consider graceful degradation for non-critical ops      │
│ ✓ Combine with database query timeouts                    │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                     DON'Ts                                  │
├────────────────────────────────────────────────────────────┤
│ ✗ Don't use timeouts for internal synchronous operations  │
│ ✗ Don't set timeouts too low (causes false positives)     │
│ ✗ Don't ignore TimeoutError exceptions                    │
│ ✗ Don't use for operations that must complete             │
│ ✗ Don't retry indefinitely on timeout                     │
└────────────────────────────────────────────────────────────┘
```

## Monitoring and Observability

```
Application Logs
    ↓
┌─────────────────────────────────────────────────────┐
│ Timeout Events:                                      │
│                                                      │
│ [WARNING] Operation timed out after 8 seconds.      │
│           This may indicate a slow external         │
│           service or heavy processing.              │
│                                                      │
│ Recommendation:                                      │
│ • Track frequency of timeouts by operation type     │
│ • Monitor which endpoints timeout most often        │
│ • Adjust timeouts based on real-world performance   │
│ • Investigate root cause of slow operations         │
└─────────────────────────────────────────────────────┘
```

## Security Considerations

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Benefits                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  DoS Protection:                                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Slow POST/PUT Attacks    → Mitigated ✓           │     │
│  │ Resource Exhaustion      → Prevented ✓            │     │
│  │ Connection Pool Starvation → Avoided ✓           │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  Attack Vectors Addressed:                                   │
│  • Slowloris attacks                                         │
│  • Slow read attacks                                         │
│  • Amplification attacks via slow external services          │
│  • Resource exhaustion via hung connections                  │
│                                                               │
│  Security Properties:                                        │
│  ✓ No sensitive data in timeout error messages              │
│  ✓ No SQL injection risk (pure Python)                      │
│  ✓ Memory safe (native asyncio)                             │
│  ✓ Thread safe (async/await)                                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

**Architecture Version:** 1.0  
**Last Updated:** 2025-12-17  
**Status:** ✅ Production Ready

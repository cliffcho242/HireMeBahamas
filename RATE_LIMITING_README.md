# Rate Limiting Implementation

## Overview

HireMeBahamas includes **two rate limiting implementations** to protect against DDoS attacks and API abuse:

1. **Serverless Rate Limiting** (Vercel) - In-memory, no Redis required
2. **Backend Rate Limiting** (Railway/Render) - Redis-based with in-memory fallback

Both implementations provide:

- **DDoS Protection**: Limits requests per IP address to prevent overwhelming the database
- **Configurable Limits**: Easily adjust rate limits via environment variables
- **High Availability**: Automatic fallback to in-memory storage if Redis is unavailable
- **Smart IP Detection**: Handles proxies and load balancers correctly

## Default Configuration

- **Limit**: 100 requests per 60 seconds per IP address
- **Response**: HTTP 429 (Too Many Requests) when limit exceeded
- **Retry-After Header**: Indicates when the client can retry

## Implementation 1: Serverless Rate Limiting (Vercel)

**Location**: `api/index.py`

Simple in-memory rate limiting for Vercel serverless functions. Perfect for serverless environments where Redis may not be available or is overkill.

### Features
- ✔ **No Redis Required**: Pure in-memory implementation
- ✔ **Zero Dependencies**: Works out of the box in serverless
- ✔ **Proxy-Aware**: Extracts real IP from X-Forwarded-For and X-Real-IP headers
- ✔ **Privacy-Compliant**: Logs truncated IPs for GDPR compliance
- ✔ **Type-Safe**: Full type annotations for better code quality

### How It Works
```python
# Simple dictionary tracks requests per IP
RATE_LIMIT: Dict[str, List[float]] = {}

# On each request:
# 1. Extract client IP (handles proxy headers)
# 2. Remove timestamps older than 60 seconds
# 3. Check if count >= 100
# 4. Return 429 if exceeded, otherwise allow
```

### Testing
Run serverless-specific tests:
```bash
python test_rate_limiting_vercel.py
```

### Benefits for Serverless
- No external service dependencies
- Works in cold starts
- Minimal memory footprint
- Compatible with Vercel's execution model

---

## Implementation 2: Backend Rate Limiting (Redis-Based)

## Environment Variables

Configure rate limiting behavior via environment variables:

```bash
# Number of requests allowed per window
RATE_LIMIT_REQUESTS=100

# Time window in seconds
RATE_LIMIT_WINDOW=60

# Redis connection (uses first available)
REDIS_URL=redis://localhost:6379
# OR
REDIS_PRIVATE_URL=redis://...
# OR
UPSTASH_REDIS_REST_URL=https://...
```

## Excluded Paths

The following endpoints are **excluded** from rate limiting to ensure monitoring and health checks work reliably:

- `/health`
- `/health/ping`
- `/live`
- `/ready`
- `/metrics`

## Architecture

### Redis Backend (Primary)
When Redis is available:
- Uses atomic `INCR` and `EXPIRE` operations
- Distributed rate limiting across multiple instances
- Low latency (<5ms overhead)

### In-Memory Fallback
When Redis is unavailable:
- Automatically falls back to in-memory storage
- Thread-safe with proper locking
- Expires old timestamps automatically
- Works in single-instance deployments

## How It Works

1. **Request Arrives**: Middleware extracts client IP from request headers
2. **Check Rate Limit**: 
   - Try Redis first (if available)
   - Fall back to in-memory storage if Redis fails
3. **Increment Counter**: Atomic increment of request count for the IP
4. **Enforce Limit**: 
   - If count > limit: Return HTTP 429 with Retry-After header
   - If count ≤ limit: Allow request to proceed
5. **Add Headers**: Response includes X-RateLimit-Limit and X-RateLimit-Window

## IP Address Extraction

The rate limiter correctly handles proxies and load balancers by checking headers in order:

1. `X-Forwarded-For` (takes first IP in list)
2. `X-Real-IP`
3. Direct client IP
4. Fallback to "unknown" if none available

## Monitoring

### Rate Limiter Statistics

Check rate limiter performance at the detailed health endpoint:

```bash
GET /health/detailed
```

Response includes:
```json
{
  "rate_limiter": {
    "total_requests": 1234,
    "rate_limited": 42,
    "redis_hits": 1192,
    "memory_hits": 42,
    "backend": "redis",
    "limit": "100 requests per 60s"
  }
}
```

### Response Headers

Every response includes rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Window: 60
```

When rate limited:
```
Retry-After: 60
```

## Testing

Comprehensive test suite with 16 tests covering:

- Rate limit enforcement
- Redis integration
- In-memory fallback
- 429 responses
- IP extraction
- Header validation
- Excluded paths

Run tests:
```bash
pytest test_rate_limiter.py -v
```

## Security Benefits

1. **DDoS Protection**: Prevents overwhelming the database with excessive requests
2. **Abuse Prevention**: Stops malicious actors from scraping or attacking the API
3. **Resource Protection**: Ensures fair access for all users
4. **Graceful Degradation**: Works even if Redis fails
5. **Proper Error Responses**: Returns standard HTTP 429 with retry information

## Performance Impact

- **Redis Mode**: <5ms overhead per request
- **Memory Mode**: <1ms overhead per request
- **No Database Impact**: Rate limiting happens before database queries

## Integration

The rate limiter is automatically enabled in the FastAPI application. No code changes needed in individual endpoints.

### Middleware Order (Important!)

1. Timeout Middleware (outermost)
2. **Rate Limiting Middleware** ← Added here
3. CORS Middleware
4. Cache Headers Middleware
5. Security Headers Middleware
6. Request Processing

This order ensures:
- Timeouts apply to all middleware
- Rate limiting happens early to protect downstream services
- Rate-limited requests don't consume other resources

## Troubleshooting

### Rate Limiter Using Memory Instead of Redis

Check Redis connection:
```bash
# Verify Redis URL is set
echo $REDIS_URL

# Test Redis connectivity
redis-cli ping
```

If Redis is unavailable, the rate limiter automatically falls back to in-memory storage. This is normal and expected for development environments.

### False Positives (Users Being Blocked)

If legitimate users are being rate limited:

1. Check current limit: Default is 100 requests per 60 seconds
2. Increase limit if needed: Set `RATE_LIMIT_REQUESTS=200`
3. Verify IP extraction is working correctly (check logs)

### Testing Rate Limiting

Use curl to test:
```bash
# Make multiple requests quickly
for i in {1..110}; do
  curl -i https://your-domain.com/api/test
done

# Should see HTTP 429 after 100 requests
```

## Implementation Details

### Serverless Implementation
- **Module**: `api/index.py` (lines 423-470)
- **Tests**: `test_rate_limiting_vercel.py`
- **Lines of Code**: ~48 lines
- **Test Coverage**: 4 comprehensive tests, 100% pass rate

### Backend Implementation
- **Module**: `api/backend_app/core/rate_limiter.py`
- **Integration**: `api/backend_app/main.py`
- **Tests**: `test_rate_limiter.py`
- **Lines of Code**: ~370 lines (including docs)
- **Test Coverage**: 16 tests, 100% pass rate

## Which Implementation Is Used?

- **Vercel Serverless** (`/api/*`): Uses serverless rate limiting (api/index.py)
- **Backend Server** (Railway/Render): Uses Redis-based rate limiting (backend_app/main.py)

Both protect the same resources but are optimized for their respective deployment environments.

## Future Enhancements

Potential improvements for future versions:

1. **Per-User Rate Limiting**: Different limits for authenticated users
2. **Per-Endpoint Limits**: Stricter limits for expensive operations
3. **Rate Limit Tiers**: Different limits based on user roles
4. **Burst Allowance**: Allow short bursts above the limit
5. **Geographic Rate Limiting**: Different limits per region
6. **Dynamic Rate Limits**: Adjust based on server load

## References

- [RFC 6585](https://tools.ietf.org/html/rfc6585) - HTTP 429 Too Many Requests
- [IETF Draft](https://tools.ietf.org/id/draft-polli-ratelimit-headers-00.html) - RateLimit Header Fields
- [Redis INCR](https://redis.io/commands/incr/) - Atomic increment command

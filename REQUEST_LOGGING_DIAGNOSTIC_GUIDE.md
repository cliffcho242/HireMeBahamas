# Request Logging Middleware - Diagnostic Enhancement

## Problem Addressed

**Issue**: Login requests were experiencing extremely slow response times (192+ seconds) causing HTTP 499 (Client Closed Request) errors. Without detailed logging, it was impossible to diagnose where the performance bottleneck was occurring.

**Log Example**:
```
[POST]499hiremebahamas.onrender.com/api/auth/login
clientIP="64.150.199.51" requestID="830a5cf9-2aef-4c40" 
responseTimeMS=192511 responseBytes=29
```

This indicates:
- Request took 192,511 milliseconds (over 3 minutes!)
- Client closed connection (HTTP 499)
- Occurred on mobile device (iPhone iOS 18.7)

## Solution Implemented

Added comprehensive request logging middleware to `final_backend_postgresql.py` that provides:

### 1. Request Tracking
- **Unique Request IDs**: Each request gets a unique ID (e.g., `[a19276d2]`) for tracking through logs
- **Client Information**: Logs client IP and User-Agent for debugging
- **Request/Response Markers**: Clear `-->` for incoming, `<--` for outgoing requests

### 2. Detailed Timing Information
- **Total Response Time**: Milliseconds for complete request
- **Operation Breakdown**: Individual timings for:
  - Database queries (email lookup)
  - Password verification (bcrypt)
  - Token creation (JWT)

### 3. Performance Monitoring
- **Slow Request Warnings**: Alerts when requests exceed 3 seconds
- **Very Slow Request Warnings**: Critical alerts for requests > 10 seconds
- **Performance Breakdown**: Shows which operation is causing delays

### 4. Error Diagnostics
- **Authentication Errors**: Detailed error messages for login failures
- **Status Code Logging**: All HTTP status codes with context
- **Connection Pool Monitoring**: Warnings for pool exhaustion

## Log Format

### Successful Login
```
[b18f25ea] --> POST /api/auth/login clientIP="127.0.0.1" userAgent="Mozilla/5.0..."
[b18f25ea] Database query (email lookup) completed in 15ms for user@example.com
[b18f25ea] Password verification completed in 230ms
[b18f25ea] Token creation completed in 5ms
[b18f25ea] Login successful - user: user@example.com, user_id: 42, 
           user_type: user, total_time: 252ms 
           (db: 15ms, password_verify: 230ms, token_create: 5ms)
[b18f25ea] <-- 200 POST /api/auth/login responseTimeMS=253 responseBytes=461 clientIP="127.0.0.1"
```

### Slow Login (Performance Warning)
```
[cf7f31e0] --> POST /api/auth/login clientIP="64.150.199.51" userAgent="iPhone..."
[cf7f31e0] Database query (email lookup) completed in 5500ms for user@example.com
[cf7f31e0] Password verification completed in 250ms
[cf7f31e0] Token creation completed in 10ms
[cf7f31e0] ⚠️ SLOW LOGIN: Total time 5760ms - 
           Breakdown: DB=5500ms, Password=250ms, Token=10ms. 
           Consider checking connection pool, database performance, or bcrypt configuration.
[cf7f31e0] <-- 200 POST /api/auth/login responseTimeMS=5762 clientIP="64.150.199.51"
[cf7f31e0] ⚠️ SLOW REQUEST: POST /api/auth/login took 5762ms (>3000ms threshold). 
           This may cause HTTP 499 (Client Closed Request) errors.
```

### Failed Login
```
[1d8f9ae5] --> POST /api/auth/login clientIP="127.0.0.1" userAgent="Mozilla/5.0..."
[1d8f9ae5] Database query (email lookup) completed in 12ms for user@example.com
[1d8f9ae5] Password verification completed in 230ms
[1d8f9ae5] Login failed - Invalid password for user: user@example.com
[1d8f9ae5] <-- 401 POST /api/auth/login responseTimeMS=243 clientIP="127.0.0.1" 
           errorDetail="Invalid email or password"
```

### Connection Pool Exhaustion
```
[a19276d2] --> POST /api/auth/login clientIP="192.168.1.100" userAgent="Mobile..."
[a19276d2] ⚠️ Connection pool exhausted for login attempt: user@example.com
[a19276d2] <-- 503 POST /api/auth/login responseTimeMS=5001 clientIP="192.168.1.100"
```

## Diagnosing Performance Issues

### 1. Slow Database Queries (> 1000ms)
**Symptoms**: High `db` time in login breakdown
```
[xxx] Database query (email lookup) completed in 5500ms
```

**Possible Causes**:
- Database connection pool exhausted
- Database server under load
- Missing or inefficient indexes
- Network latency to database

**Solutions**:
- Check connection pool configuration (`DB_POOL_MAX_CONNECTIONS`)
- Verify database indexes are created (`users_email_lower_idx`)
- Check database server resources
- Consider database in same region as application

### 2. Slow Password Verification (> 500ms)
**Symptoms**: High `password_verify` time
```
[xxx] Password verification completed in 5000ms
```

**Possible Causes**:
- Bcrypt rounds too high (default is 12, should be 10)
- Server CPU overload
- Too many concurrent bcrypt operations

**Solutions**:
- Set `BCRYPT_ROUNDS=10` environment variable
- Increase server CPU resources
- Check server CPU usage during peak times
- Consider rate limiting login attempts

### 3. Connection Pool Exhaustion
**Symptoms**: 503 errors with pool exhaustion warnings
```
⚠️ Connection pool exhausted for login attempt
```

**Possible Causes**:
- Too many concurrent requests
- Slow queries holding connections too long
- Connection leaks (not properly returned to pool)
- Pool size too small

**Solutions**:
- Increase `DB_POOL_MAX_CONNECTIONS` (default: 20)
- Reduce `STATEMENT_TIMEOUT_MS` to release connections faster
- Check for connection leaks in application code
- Add more application instances

### 4. Mobile Clients Timing Out
**Symptoms**: Mobile user agents with HTTP 499 errors
```
User-Agent: "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7..."
responseTimeMS=192511
Status: 499
```

**Possible Causes**:
- Mobile connections have shorter timeouts (30-60 seconds)
- Network instability on mobile
- Server overload affecting all clients

**Solutions**:
- Optimize all operations to complete under 1 second
- Consider implementing request queuing
- Add retry logic on client side with exponential backoff
- Cache authentication tokens longer

## Monitoring Best Practices

### 1. Set Up Alerts
Monitor for:
- Login requests > 1 second (warning)
- Login requests > 3 seconds (critical)
- Connection pool exhaustion (critical)
- High rate of 401/503 errors (warning)

### 2. Track Metrics
Key metrics to dashboard:
- Average login time (p50, p95, p99)
- Database query time (p50, p95, p99)
- Password verification time (p50, p95, p99)
- Connection pool utilization
- Rate of HTTP 499 errors

### 3. Log Aggregation
Use log aggregation tools to:
- Track request IDs across distributed systems
- Correlate errors with performance degradation
- Identify patterns in slow requests
- Alert on anomalies

## Configuration

### Environment Variables

```bash
# Bcrypt rounds (default: 10)
# Lower = faster but less secure, Higher = slower but more secure
BCRYPT_ROUNDS=10

# Database connection pool (default: 20)
DB_POOL_MAX_CONNECTIONS=20

# Statement timeout in milliseconds (default: 30000 = 30 seconds)
STATEMENT_TIMEOUT_MS=30000

# Pool checkout timeout (default: 5 seconds)
POOL_TIMEOUT_SECONDS=5
```

### Recommended Settings

**For high-traffic production**:
```bash
BCRYPT_ROUNDS=10
DB_POOL_MAX_CONNECTIONS=40
STATEMENT_TIMEOUT_MS=30000
POOL_TIMEOUT_SECONDS=5
```

**For low-traffic or development**:
```bash
BCRYPT_ROUNDS=10
DB_POOL_MAX_CONNECTIONS=10
STATEMENT_TIMEOUT_MS=30000
POOL_TIMEOUT_SECONDS=10
```

## Testing

The middleware has been tested with:
- ✅ Successful logins (shows all timing breakdowns)
- ✅ Failed logins (shows where failure occurred)  
- ✅ 404 errors (proper error logging)
- ✅ Long user agents (proper truncation)
- ✅ Connection pool exhaustion (503 handling)
- ✅ Slow requests (warning generation)

## Security Considerations

- ✅ No sensitive data logged (passwords never logged)
- ✅ Error messages sanitized (generic auth failures)
- ✅ CodeQL security scan passed
- ✅ Connection pool properly managed
- ✅ Request IDs are not predictable (UUID-based)

## Files Changed

1. `final_backend_postgresql.py`:
   - Added `uuid` import for request IDs
   - Added `g` import from Flask for request context
   - Added `log_request_start()` before_request handler
   - Added `log_request_end()` after_request handler
   - Enhanced login endpoint with detailed timing logs

## Deployment

No changes required for deployment:
- Middleware is automatically active on app start
- No database migrations needed
- No breaking changes to API
- Backward compatible with existing clients

## Support

If you see frequent slow request warnings after deploying:
1. Check the timing breakdown to identify the bottleneck
2. Review the configuration recommendations above
3. Monitor database and server resources
4. Consider scaling horizontally (more app instances)
5. Check network latency between app and database

---

**Related Documentation**:
- [LOGIN_PERFORMANCE_FIX.md](./LOGIN_PERFORMANCE_FIX.md) - Bcrypt optimization
- [gunicorn.conf.py](./gunicorn.conf.py) - Server configuration
- [final_backend_postgresql.py](./final_backend_postgresql.py) - Backend implementation

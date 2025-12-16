# Startup Logging Guide

## Overview

The HireMeBahamas API now includes comprehensive startup logging to help validate production deployments. These logs provide critical information about the application's configuration, making it easy to verify that everything is set up correctly.

## What's Logged

### 1. Deployment Environment Information
```
📍 Environment: production
📍 Vercel Environment: production
📍 Production Mode: True
📍 Development Mode: False
```

This section shows:
- The `ENVIRONMENT` variable value
- The `VERCEL_ENV` variable value (if deploying on Vercel)
- Whether the application is running in production mode
- Whether the application is running in development mode

### 2. Database Configuration
```
💾 Database Driver: postgresql+asyncpg
💾 Database Host: ep-xxxxx.aws.neon.tech
💾 Database Port: 5432
💾 Database Name: mydb
💾 Database SSL: ✅ enabled
```

This section shows:
- The database driver being used
- The database hostname (without credentials)
- The database port
- The database name
- Whether SSL is enabled

**Security Note:** Credentials (username/password) are NEVER logged.

### 3. CORS Configuration
```
🌐 CORS Origins: 4 allowed origins
   - https://hiremebahamas.com
   - https://www.hiremebahamas.com
   - https://*.vercel.app
   - http://localhost:3000
🌐 CORS Credentials: ✅ enabled (for secure cookies)
```

This section shows:
- The number of allowed CORS origins
- Each allowed origin
- Whether credentials (cookies) are enabled

### 4. Server Configuration
```
🖥️  Server Port: 8000
🖥️  Host: 0.0.0.0 (all interfaces)
```

This section shows:
- The port the server is listening on
- The host interface (0.0.0.0 means all interfaces)

### 5. Health Endpoints
```
🏥 Health Endpoints:
   - GET /health (instant, no DB)
   - GET /live (instant, no DB)
   - GET /ready (instant, no DB)
   - GET /ready/db (with DB check)
   - GET /health/detailed (comprehensive)
```

This section lists all available health check endpoints and their characteristics.

### 6. Environment Variables Check
```
🔑 Environment Variables Check:
   - DATABASE_URL: ✅ set
   - REDIS_URL: ℹ️  not set (optional)
   - JWT_SECRET_KEY: ⚠️  not set (using default)
   - ENVIRONMENT: production
   - VERCEL_ENV: production
```

This section shows which critical environment variables are set:
- ✅ = Variable is set
- ❌ = Required variable is not set
- ⚠️  = Variable not set, using default (may be insecure)
- ℹ️  = Optional variable not set

**Security Note:** Only the presence/absence of variables is logged, not their values.

### 7. Initialization Summary
```
📊 INITIALIZATION SUMMARY:
   ✅ Health endpoints ready (instant response)
   ✅ CORS configured for production
   ✅ Request logging middleware active
   ✅ Timeout middleware configured (60s)
   ✅ Rate limiting middleware active

🔄 LAZY INITIALIZATION PATTERN:
   - Database engine will initialize on first request
   - NO database connections at startup
   - NO warm-up pings
   - NO background keepalive loops

🚦 READY TO ACCEPT TRAFFIC
```

This final section summarizes what was initialized and confirms the application is ready.

## How to Read the Logs

### Deployment Validation Checklist

When deploying to production, verify these items in the startup logs:

1. **Environment is Production**
   - ✅ `📍 Production Mode: True`
   - ❌ `📍 Production Mode: False` (should be True in production)

2. **Database is Configured**
   - ✅ `💾 Database Host: ep-xxxxx.aws.neon.tech` (shows actual host)
   - ✅ `💾 Database SSL: ✅ enabled`
   - ❌ `💾 Database URL: ⚠️  NOT CONFIGURED`

3. **CORS is Correct**
   - ✅ Should see your production domain in the origins list
   - ❌ Should NOT see localhost in production mode

4. **Environment Variables are Set**
   - ✅ `DATABASE_URL: ✅ set`
   - ✅ `JWT_SECRET_KEY: ✅ set` (or verify you're okay with default)
   - ℹ️  `REDIS_URL: ℹ️  not set (optional)` (optional, but recommended for production)

5. **Application is Ready**
   - ✅ `🚦 READY TO ACCEPT TRAFFIC` appears at the end

## Example: Full Startup Log

Here's what a complete startup log looks like in production:

```
================================================================================
🚀 Starting HireMeBahamas API
================================================================================
📍 Environment: production
📍 Vercel Environment: production
📍 Production Mode: True
📍 Development Mode: False
💾 Database Driver: postgresql+asyncpg
💾 Database Host: ep-cool-frog-12345.us-east-1.aws.neon.tech
💾 Database Port: 5432
💾 Database Name: hiremebahamas_prod
💾 Database SSL: ✅ enabled
🌐 CORS Origins: 3 allowed origins
   - https://hiremebahamas.com
   - https://www.hiremebahamas.com
   - https://*.vercel.app
🌐 CORS Credentials: ✅ enabled (for secure cookies)
🖥️  Server Port: 8000
🖥️  Host: 0.0.0.0 (all interfaces)
🏥 Health Endpoints:
   - GET /health (instant, no DB)
   - GET /live (instant, no DB)
   - GET /ready (instant, no DB)
   - GET /ready/db (with DB check)
   - GET /health/detailed (comprehensive)
🔑 Environment Variables Check:
   - DATABASE_URL: ✅ set
   - REDIS_URL: ✅ set
   - JWT_SECRET_KEY: ✅ set
   - ENVIRONMENT: production
   - VERCEL_ENV: production
================================================================================
Starting component initialization (NO database connections)...
================================================================================
Bcrypt pre-warmed successfully
✅ Redis cache connected successfully
================================================================================
✅ HireMeBahamas API Initialization Complete
================================================================================

📊 INITIALIZATION SUMMARY:
   ✅ Health endpoints ready (instant response)
   ✅ CORS configured for production
   ✅ Request logging middleware active
   ✅ Timeout middleware configured (60s)
   ✅ Rate limiting middleware active

🔄 LAZY INITIALIZATION PATTERN:
   - Database engine will initialize on first request
   - NO database connections at startup
   - NO warm-up pings
   - NO background keepalive loops

🚦 READY TO ACCEPT TRAFFIC
================================================================================
```

## Troubleshooting

### Issue: Database not configured
If you see:
```
💾 Database URL: ⚠️  NOT CONFIGURED
```

**Solution:** Set the `DATABASE_URL` environment variable in your deployment platform (Vercel, Railway, Render, etc.)

### Issue: SSL disabled in production
If you see:
```
💾 Database SSL: ⚠️  disabled
```

**Solution:** Add `?sslmode=require` to the end of your `DATABASE_URL`

### Issue: Wrong environment mode
If you see `Production Mode: False` in production:

**Solution:** Set `ENVIRONMENT=production` in your deployment platform's environment variables

### Issue: JWT using default key
If you see:
```
JWT_SECRET_KEY: ⚠️  not set (using default)
```

**Solution:** Set a secure `JWT_SECRET_KEY` environment variable. Using the default key is insecure for production.

## Testing

You can test the startup logging parsing logic by running:

```bash
python test_startup_logging.py
```

This validates:
- Database URL parsing
- Environment variable checks
- Log message formatting

## Implementation Details

The startup logging is implemented in `api/backend_app/main.py` in the `lazy_import_heavy_stuff()` function, which is called during the FastAPI `startup` event.

The logging:
- Uses Python's standard `logging` module
- Logs at `INFO` level for normal information
- Logs at `WARNING` level for potential issues
- Never logs sensitive data (passwords, tokens, etc.)
- Uses emojis for visual clarity in logs

## Related Documentation

- [Deployment Verification Checklist](DEPLOYMENT_VERIFICATION_CHECKLIST.md)
- [Production Config Guide](PRODUCTION_CONFIG_ABSOLUTE_BANS.md)
- [Database Setup](WHERE_TO_PUT_DATABASE_URL.md)

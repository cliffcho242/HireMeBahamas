# Railway Deployment Troubleshooting Guide

## Current Issue
Nixpacks build failed with TOML syntax error, which has been fixed, but deployment still fails.

## What We've Fixed
✅ Fixed nixpacks.toml syntax error (nested quotes issue)
✅ Verified local backend imports successfully
✅ Confirmed Procfile is correct
✅ Requirements.txt has all dependencies
✅ Removed pg_stat_statements extension (requires server-side configuration unavailable on Railway)

## PostgreSQL Extensions (pg_stat_statements)

### About pg_stat_statements
The `pg_stat_statements` extension provides query performance statistics tracking. However, it **cannot be used on managed PostgreSQL services like Railway** because it requires server-side configuration (`shared_preload_libraries`) that is not available to users.

### Common Error
If you see an error like:
```
ERROR: pg_stat_statements must be loaded via "shared_preload_libraries"
STATEMENT: SET statement_timeout = '30s'; SELECT * FROM public."pg_stat_statements" LIMIT 10
```

This error typically occurs when:
1. The `pg_stat_statements` extension was previously installed but cannot function
2. Railway's monitoring dashboard attempts to query the extension's statistics
3. The extension is not loaded in `shared_preload_libraries` (server-side config)

### Solution
The application now automatically **removes** the `pg_stat_statements` extension and any orphaned database objects during startup:

1. **Checks if extension is installed** on the PostgreSQL server
2. **Drops the extension with CASCADE** if it exists but cannot function
3. **Drops orphaned tables/views** named `pg_stat_statements` in the public schema
4. **Logs the cleanup** for visibility

This cleanup is performed in the `cleanup_orphaned_extensions()` function which runs during database initialization.

For managed PostgreSQL providers (Railway, Render, Heroku, etc.):
- The `pg_stat_statements` extension cannot be properly configured
- The application automatically removes orphaned extensions that require `shared_preload_libraries`
- The application also removes orphaned tables/views that cause monitoring errors
- The application will continue to work normally without this extension

### Note About External Monitoring Errors
If you see `pg_stat_statements` errors in your Railway logs like:
```
ERROR: pg_stat_statements must be loaded via "shared_preload_libraries"
STATEMENT: SET statement_timeout = '30s'; SELECT * FROM public."pg_stat_statements" LIMIT 10
```

**These errors come from Railway's internal monitoring system, NOT from your application code.**

Railway's monitoring dashboard periodically queries `pg_stat_statements` to collect query performance metrics. This is a Railway platform feature that runs independently of your application.

**Why the errors occur:**
1. Railway creates PostgreSQL databases without `pg_stat_statements` in `shared_preload_libraries`
2. Railway's monitoring still tries to query the `pg_stat_statements` view
3. PostgreSQL returns an error because the extension cannot function without the library preloaded

**What our application does:**
- Automatically cleans up any orphaned `pg_stat_statements` tables/views during startup
- Does NOT use `pg_stat_statements` in any application queries

**What you can do:**
- These errors are harmless to your application and data
- They do not affect application functionality
- If the errors are excessive, contact Railway support to either:
  - Add `pg_stat_statements` to `shared_preload_libraries` (requires server config access)
  - Disable the monitoring queries for your database

## Possible Remaining Issues

### 1. Database Dependency
The backend might require a database connection that isn't available during build.

**Solution**: Add database URL as environment variable in Railway dashboard:
- Go to Railway project settings
- Add `DATABASE_URL` environment variable
- Use Railway's PostgreSQL add-on or external database

### 2. Missing Environment Variables
The backend might need these variables:
- `SECRET_KEY` (Flask secret)
- `JWT_SECRET_KEY` (JWT signing)
- `DATABASE_URL` (database connection)

### 3. Build Dependencies
Some packages might need system libraries during build.

## Quick Fix Attempts

### Option A: Use Simple Backend (Test)
```bash
# Update Procfile temporarily
echo "web: gunicorn -w 4 -b 0.0.0.0:\$PORT test_app:app --timeout 120" > Procfile
railway up
```

### Option B: Add Environment Variables
In Railway dashboard:
1. Go to Variables tab
2. Add:
   - `SECRET_KEY` = "your-secret-key"
   - `JWT_SECRET_KEY` = "your-jwt-key"  
   - `DATABASE_URL` = "sqlite:///hiremebahamas.db" (for testing)

### Option C: Simplified Dependencies
Create minimal requirements.txt:
```
Flask==2.3.3
Flask-CORS==4.0.0
gunicorn==21.2.0
```

## Railway Build Logs
Check the build logs at the provided URL to see specific error details.

## Next Steps
1. Check Railway dashboard for detailed error logs
2. Try Option A (simple backend) to verify basic deployment works
3. If successful, gradually add complexity back to final_backend.py
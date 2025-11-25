# Railway Deployment Troubleshooting Guide

## Current Issue
Nixpacks build failed with TOML syntax error, which has been fixed, but deployment still fails.

## What We've Fixed
✅ Fixed nixpacks.toml syntax error (nested quotes issue)
✅ Verified local backend imports successfully
✅ Confirmed Procfile is correct
✅ Requirements.txt has all dependencies
✅ Added pg_stat_statements extension initialization

## PostgreSQL Extensions (pg_stat_statements)

### About pg_stat_statements
The `pg_stat_statements` extension provides query performance statistics tracking. It's useful for:
- Monitoring slow queries
- Identifying frequently executed queries
- Performance tuning and optimization

### Common Error
If you see an error like:
```
ERROR: pg_stat_statements must be loaded via "shared_preload_libraries"
```

This means the extension requires server-side configuration.

### Solution
The application now automatically attempts to initialize the `pg_stat_statements` extension during database startup:

1. **Checks if extension is available** on the PostgreSQL server
2. **Creates the extension** if available and not already installed
3. **Gracefully handles errors** if the extension cannot be loaded

For managed PostgreSQL providers (Railway, Render, Heroku, etc.):
- The extension may or may not be available depending on your plan
- Contact your provider to enable `shared_preload_libraries` if needed
- The application will continue to work even if the extension is unavailable

### Manual Extension Setup (if you have admin access)
If you have PostgreSQL admin access, add to `postgresql.conf`:
```
shared_preload_libraries = 'pg_stat_statements'
```
Then restart PostgreSQL and run:
```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

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
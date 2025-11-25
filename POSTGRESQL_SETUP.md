# PostgreSQL Setup Guide for HireMeBahamas

## Supported PostgreSQL Versions

This application is tested and compatible with **PostgreSQL 17.x** (recommended) and PostgreSQL 16.x.

The Docker setup uses PostgreSQL 17 by default. When deploying to Railway, Render, or other platforms, PostgreSQL 17 is recommended for the latest features and security updates.

> **Note**: For information about PostgreSQL initialization and recovery fixes (handling improper shutdowns), see [POSTGRESQL_INITIALIZATION_FIX.md](./POSTGRESQL_INITIALIZATION_FIX.md).

## ⚠️ Important: PostgreSQL is REQUIRED for Production

**SQLite is NOT suitable for production use** because:
- Data does not persist in containerized environments (Railway, Docker, Render, etc.)
- Users and all data will be lost on every deployment or restart
- No support for concurrent access at scale
- No backup/restore capabilities in cloud environments

## Quick Start

### For Production Deployment (Railway, Render, etc.)

1. **Add PostgreSQL to your project:**
   - Railway: Add PostgreSQL plugin to your project
   - Render: Add a PostgreSQL database
   - Other: Use any PostgreSQL provider (e.g., ElephantSQL, Supabase, Neon)

2. **Set the DATABASE_URL environment variable:**
   ```bash
   DATABASE_URL=postgresql://username:password@hostname:5432/database
   ```

3. **Set ENVIRONMENT to production:**
   ```bash
   ENVIRONMENT=production
   ```

4. **Deploy your application** - it will automatically use PostgreSQL

## Railway Setup (Recommended)

Railway makes PostgreSQL setup easy:

1. **Add PostgreSQL Plugin:**
   - Go to your Railway project
   - Click "New" → "Database" → "PostgreSQL"
   - Railway will automatically create the database

2. **Connect to your app:**
   - Railway automatically sets the `DATABASE_URL` variable
   - Your app will detect and use PostgreSQL automatically

3. **Verify setup:**
   - Check your app logs for: `🗄️ Database Mode: PostgreSQL (Production)`
   - Should show: `✅ PostgreSQL URL detected: postgresql://...`

## Local Development

### Option 1: Use SQLite (Quick & Easy)

For local development only:

1. **Don't set DATABASE_URL** (or comment it out in .env)
2. **App will use SQLite** at `hiremebahamas.db`
3. **⚠️ Remember:** This is for development only!

### Option 2: Use Local PostgreSQL

For testing production-like setup:

1. **Install PostgreSQL:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS (Homebrew)
   brew install postgresql
   brew services start postgresql
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create database:**
   ```bash
   # Connect to PostgreSQL
   psql postgres
   
   # Create database and user
   CREATE DATABASE hiremebahamas;
   CREATE USER hiremebahamas_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE hiremebahamas TO hiremebahamas_user;
   \q
   ```

3. **Set DATABASE_URL in .env:**
   ```bash
   DATABASE_URL=postgresql://hiremebahamas_user:your_password@localhost:5432/hiremebahamas
   ```

## Verifying Your Setup

### Check Database Connection

Run this to verify PostgreSQL is configured:

```bash
python3 -c "
import os
os.environ['ENVIRONMENT'] = 'production'
os.environ['DATABASE_URL'] = 'postgresql://...'  # Your URL here

import final_backend_postgresql
print('✅ PostgreSQL is configured correctly!')
"
```

### Check Application Logs

When you start the app, look for:

```
🗄️ Database Mode: PostgreSQL (Production)
✅ PostgreSQL URL detected: postgresql://...
✅ Database config parsed: user@host:5432/database
```

### If You See Errors

**Error: "Production environment REQUIRES PostgreSQL!"**
- Solution: Set the DATABASE_URL environment variable
- Make sure ENVIRONMENT is set to "production"

**Error: Connection refused**
- Solution: Check if PostgreSQL is running
- Verify hostname, port, username, and password
- Check firewall settings

**Error: database does not exist**
- Solution: Create the database first (see "Create database" above)

## Database Migrations

When deploying updates that change the database schema:

1. **Backup your data** (Railway/Render usually do this automatically)
2. **Deploy the new version**
3. **Database tables are auto-created** on first run
4. **Check logs** to verify successful initialization

## Environment Variables

Required for production:

```bash
# PostgreSQL connection (REQUIRED)
DATABASE_URL=postgresql://username:password@hostname:5432/database

# Environment setting (REQUIRED)
ENVIRONMENT=production

# Security keys (REQUIRED - generate secure random strings)
SECRET_KEY=<generate-secure-random-key>
JWT_SECRET_KEY=<generate-secure-random-key>

# Optional
TOKEN_EXPIRATION_DAYS=7
PORT=8080
```

## Troubleshooting

### Data Not Persisting

**Problem:** Users are deleted after restart
**Solution:** 
1. Verify DATABASE_URL is set correctly
2. Check logs show PostgreSQL mode
3. Make sure ENVIRONMENT is set to "production"
4. Restart the application

### Connection Pool Exhausted

**Problem:** "Too many connections" error
**Solution:**
- PostgreSQL has connection limits
- Application uses pool_size=10, max_overflow=20
- Consider upgrading your PostgreSQL plan
- Check for connection leaks in custom code

### Slow Queries

**Problem:** Database queries are slow
**Solution:**
- Enable query logging: set DB_ECHO=True in .env
- Add indexes to frequently queried columns
- Consider query optimization
- Check PostgreSQL performance metrics

## Security Best Practices

1. **Never commit DATABASE_URL to git**
   - Use environment variables
   - Keep .env in .gitignore

2. **Use strong passwords**
   - Generate random secure passwords
   - Rotate credentials periodically

3. **Enable SSL connections**
   - Production uses `sslmode=require`
   - Configured automatically in the app

4. **Regular backups**
   - Railway/Render: Enable automatic backups
   - Self-hosted: Set up pg_dump cron jobs

## Database Schema

The application automatically creates these tables:

- `users` - User accounts and profiles
- `posts` - User posts and content
- `jobs` - Job listings
- `comments` - Comments on posts
- `likes` - Post likes
- `stories` - Temporary stories (24h expiry)

All tables use:
- Primary keys (auto-increment)
- Foreign keys (with CASCADE delete)
- Indexes on frequently queried columns
- Timestamps for created_at

## Monitoring

### Check Database Health

```sql
-- Connect to your database
psql $DATABASE_URL

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check number of records
SELECT 'users' as table_name, COUNT(*) FROM users
UNION ALL
SELECT 'posts', COUNT(*) FROM posts
UNION ALL
SELECT 'jobs', COUNT(*) FROM jobs;
```

### Application Health Check

Access: `https://your-app-url/health`

Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "mode": "postgresql"
}
```

### Understanding PostgreSQL Checkpoint Logs

You may see checkpoint log messages like this in your PostgreSQL logs:

```
LOG: checkpoint complete: wrote 1 buffers (0.0%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.101 s, sync=0.002 s, total=0.113 s; sync files=1, longest=0.002 s, average=0.002 s; distance=8 kB, estimate=2262 kB
```

**This is completely normal and not an error.** Checkpoints are a routine PostgreSQL operation that:

- Writes all modified data from memory to disk
- Ensures data durability and crash recovery
- Runs automatically based on time or WAL size (default: every 5 minutes or 1GB of WAL, whichever occurs first)

**What the message means:**
- `wrote X buffers` - Number of data pages written to disk
- `WAL file(s) added/removed/recycled` - Write-ahead log file management
- `write/sync/total` - Time spent on different phases
- `distance/estimate` - Amount of data processed

**When to be concerned:**
- ❌ `checkpoints are occurring too frequently` - May need tuning
- ❌ Long sync times (several seconds) - May indicate disk I/O issues
- ✅ Normal checkpoint completion messages - Everything is working correctly

## Support

If you encounter issues:

1. Check application logs for error messages
2. Verify environment variables are set correctly
3. Test database connection manually
4. Review this guide's troubleshooting section
5. Check Railway/Render platform status

## Summary

✅ **DO:**
- Use PostgreSQL for production
- Set DATABASE_URL environment variable
- Set ENVIRONMENT=production
- Enable automatic backups
- Monitor database health

❌ **DON'T:**
- Use SQLite in production
- Commit DATABASE_URL to git
- Use weak passwords
- Skip backups
- Ignore connection pool limits

---

**Remember:** PostgreSQL is required for data persistence in production. The application will fail to start if ENVIRONMENT=production but DATABASE_URL is not set.

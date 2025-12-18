# Complete PostgreSQL Migration Guide: Render/Render → Vercel Postgres

## Overview

This guide provides step-by-step instructions for migrating your HireMeBahamas PostgreSQL database from Render or Render to Vercel Postgres (powered by Neon). The migration ensures zero downtime and preserves all data.

## Prerequisites

- ✅ Access to Vercel Dashboard
- ✅ PostgreSQL client tools installed (`pg_dump`, `pg_restore`, `psql`)
- ✅ Current Render or Render database credentials
- ✅ Backup of environment variables from current deployment

## Migration Strategy

This migration follows a phased approach:
1. **Setup**: Create Vercel Postgres database
2. **Export**: Backup data from Render/Render
3. **Import**: Restore data to Vercel Postgres
4. **Verify**: Validate data integrity
5. **Switch**: Update environment variables
6. **Test**: Verify application functionality
7. **Cleanup**: Set old database to read-only (7-day grace period)

---

## Phase 1: Setup Vercel Postgres Database

### Step 1.1: Create Vercel Postgres Instance

1. Navigate to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your **HireMeBahamas** project
3. Go to **Storage** tab
4. Click **"Create Database"**
5. Select **"Postgres"**
6. Choose your plan:
   - **Hobby Plan**: Free, 0.5GB storage (good for development/testing)
   - **Pro Plan**: $0.10/GB/month (recommended for production)
7. Select region: **US East (N. Virginia)** or closest to your users
8. Click **"Create Database"**
9. Wait 30-60 seconds for provisioning

### Step 1.2: Copy Connection Strings

Vercel provides multiple connection strings:

```bash
# Primary connection (with connection pooling)
POSTGRES_URL="postgresql://default:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"

# Non-pooling connection (for migrations and pg_dump)
POSTGRES_URL_NON_POOLING="postgresql://default:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"

# For Prisma ORM (if applicable)
POSTGRES_PRISMA_URL="postgresql://default:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require&pgbouncer=true"
```

**Important**: Save these to a secure location. You'll need them for the migration.

---

## Phase 2: Export Data from Render/Render

### Step 2.1: Set Environment Variables

```bash
# Export from Render
export RAILWAY_DATABASE_URL="postgresql://user:pass@containers-us-west-123.render.app:5432/render"

# Or export from Render
export RENDER_DATABASE_URL="postgresql://user:pass@dpg-xxxxx-a.oregon-postgres.render.com:5432/hiremebahamas"

# Set source based on your current provider
export SOURCE_DATABASE_URL="${RAILWAY_DATABASE_URL:-$RENDER_DATABASE_URL}"
```

### Step 2.2: Create Database Backup

```bash
# Create backup with timestamp
pg_dump "$SOURCE_DATABASE_URL" \
  --no-owner \
  --no-acl \
  --format=custom \
  --compress=0 \
  --jobs=8 \
  --file="hiremebahamas_backup_$(date +%Y%m%d_%H%M%S).dump"
```

**Flags explained:**
- `--no-owner`: Don't restore ownership (Vercel uses different users)
- `--no-acl`: Don't restore access control lists
- `--format=custom`: Custom format for parallel restore
- `--compress=0`: No compression for faster restore
- `--jobs=8`: Parallel dump for speed

### Step 2.3: Verify Backup

```bash
# Check backup file size
ls -lh hiremebahamas_backup_*.dump

# Quick validation (should show no errors)
pg_restore --list hiremebahamas_backup_*.dump | head -20
```

---

## Phase 3: Import Data to Vercel Postgres

### Step 3.1: Set Vercel Environment Variables

```bash
# Use NON_POOLING URL for migration
export VERCEL_POSTGRES_URL="$POSTGRES_URL_NON_POOLING"
```

### Step 3.2: Import Database

```bash
# Import with parallel jobs
pg_restore \
  --no-owner \
  --no-acl \
  --jobs=8 \
  --dbname="$VERCEL_POSTGRES_URL" \
  hiremebahamas_backup_*.dump
```

**Note**: You may see warnings about existing objects (e.g., `public` schema). These are normal and can be ignored.

### Step 3.3: Verify Import Success

```bash
# Check if restore completed
echo $?  # Should return 0 for success

# If there were errors, check the output above for "ERROR" messages
# Warnings are acceptable, but ERRORs need investigation
```

---

## Phase 4: Verify Data Integrity

### Step 4.1: Compare Row Counts

```bash
# Check source database
psql "$SOURCE_DATABASE_URL" -t -c "
SELECT 
  'users' as table_name, COUNT(*)::text as count FROM users
  UNION ALL SELECT 'posts', COUNT(*)::text FROM posts
  UNION ALL SELECT 'jobs', COUNT(*)::text FROM jobs
  UNION ALL SELECT 'messages', COUNT(*)::text FROM messages
  UNION ALL SELECT 'notifications', COUNT(*)::text FROM notifications
  ORDER BY table_name;
"

# Check target database (should match)
psql "$VERCEL_POSTGRES_URL" -t -c "
SELECT 
  'users' as table_name, COUNT(*)::text as count FROM users
  UNION ALL SELECT 'posts', COUNT(*)::text FROM posts
  UNION ALL SELECT 'jobs', COUNT(*)::text FROM jobs
  UNION ALL SELECT 'messages', COUNT(*)::text FROM messages
  UNION ALL SELECT 'notifications', COUNT(*)::text FROM notifications
  ORDER BY table_name;
"
```

### Step 4.2: Verify Table Structure

```bash
# List all tables
psql "$VERCEL_POSTGRES_URL" -c "\dt"

# Check indexes
psql "$VERCEL_POSTGRES_URL" -c "
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
"

# Check constraints
psql "$VERCEL_POSTGRES_URL" -c "
SELECT conname, contype, conrelid::regclass as table_name
FROM pg_constraint
WHERE connamespace = 'public'::regnamespace
ORDER BY conrelid::regclass::text, conname;
"
```

### Step 4.3: Test Sample Queries

```bash
# Test user authentication query
psql "$VERCEL_POSTGRES_URL" -c "
SELECT id, email, created_at 
FROM users 
LIMIT 5;
"

# Test posts query
psql "$VERCEL_POSTGRES_URL" -c "
SELECT id, content, created_at 
FROM posts 
ORDER BY created_at DESC 
LIMIT 5;
"
```

---

## Phase 5: Update Application Configuration

### Step 5.1: Update Vercel Environment Variables

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your **HireMeBahamas** project
3. Go to **Settings** → **Environment Variables**
4. Add/Update these variables for **Production**, **Preview**, and **Development**:

```bash
# Primary database connection (use pooling URL)
DATABASE_URL=postgresql://default:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require

# Alternative names (for compatibility)
POSTGRES_URL=postgresql://default:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require

# Database configuration
DB_POOL_SIZE=2
DB_MAX_OVERFLOW=3
DB_POOL_RECYCLE=120
DB_SSL_MODE=require
DB_FORCE_TLS_1_3=true
DB_CONNECT_TIMEOUT=45
DB_COMMAND_TIMEOUT=30
```

### Step 5.2: Update Backend Configuration (if needed)

The existing `backend/app/database.py` already supports Vercel Postgres! No code changes needed because it:

- ✅ Automatically detects `DATABASE_URL` environment variable
- ✅ Converts `postgres://` to `postgresql+asyncpg://` format
- ✅ Configures SSL with TLS 1.3 for Neon/Vercel Postgres
- ✅ Uses connection pooling with pre-ping validation
- ✅ Implements connection recycling to prevent SSL EOF errors

### Step 5.3: Deploy Application

```bash
# Commit any local changes (if any)
git add .
git commit -m "Configure Vercel Postgres database"
git push origin main
```

Vercel will automatically deploy with the new database configuration.

---

## Phase 6: Test Application Functionality

### Step 6.1: Health Check

```bash
# Test health endpoint
curl https://hiremebahamas.com/health

# Expected response:
# {"status":"healthy"}

# Test ready endpoint (includes database)
curl https://hiremebahamas.com/ready

# Expected response:
# {"status":"ready","database":"connected","initialized":true}
```

### Step 6.2: User Authentication Test

1. Visit your application: `https://hiremebahamas.com`
2. **Login** with existing credentials
3. Verify profile page loads
4. **Logout** and **login** again
5. Check that session persists

### Step 6.3: Create Content Test

1. **Create a new post**
   - Write content and submit
   - Verify it appears in feed
   - Reload page - should still be there

2. **Send a message**
   - Open messages
   - Send a test message
   - Verify delivery

3. **Browse jobs**
   - Navigate to jobs page
   - Verify job listings load
   - Create a test job post (if you have permissions)

### Step 6.4: Performance Test

```bash
# Test response time
time curl -s https://hiremebahamas.com/health > /dev/null

# Should be under 100ms for first request
# Under 50ms for subsequent requests (edge caching)
```

---

## Phase 7: Set Old Database to Read-Only (Grace Period)

### Step 7.1: Mark Render/Render Database as Read-Only

```bash
# Extract database name
DB_NAME=$(echo "$SOURCE_DATABASE_URL" | sed -E 's|.*://[^/]+/([^?]+).*|\1|')

# Set read-only (7-day grace period for rollback)
psql "$SOURCE_DATABASE_URL" -c "ALTER DATABASE \"$DB_NAME\" SET default_transaction_read_only = on;"
```

This allows:
- ✅ Quick rollback if issues arise (just revert `DATABASE_URL`)
- ✅ 7-day safety net for data recovery
- ✅ No accidental writes to old database

### Step 7.2: Document Rollback Procedure

If you need to rollback:

```bash
# 1. Update DATABASE_URL in Vercel Dashboard back to Render/Render URL
# 2. Redeploy application
# 3. Remove read-only from old database:
DB_NAME=$(echo "$SOURCE_DATABASE_URL" | sed -E 's|.*://[^/]+/([^?]+).*|\1|')
psql "$SOURCE_DATABASE_URL" -c "ALTER DATABASE \"$DB_NAME\" SET default_transaction_read_only = off;"
```

---

## Phase 8: Final Cleanup (After 7 Days)

### Step 8.1: Verify Stability

After 7 days of running on Vercel Postgres:
- ✅ Monitor application performance
- ✅ Check for any database errors in logs
- ✅ Verify no data loss or corruption
- ✅ Confirm all features working correctly

### Step 8.2: Delete Old Database

Once confident the migration is successful:

**For Render:**
1. Go to [Render Dashboard](https://render.app/dashboard)
2. Select your PostgreSQL service
3. Click **Settings**
4. Scroll to bottom
5. Click **Delete Service**
6. Confirm deletion

**For Render:**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your PostgreSQL instance
3. Click **Settings**
4. Scroll to bottom
5. Click **Delete Service**
6. Confirm deletion

### Step 8.3: Update Documentation

Update these files to reflect the new database:
- `README.md` - Update database setup section
- `.env.example` - Update example DATABASE_URL
- Deployment docs - Remove Render/Render references

---

## Troubleshooting

### Issue: "Connection timeout" during import

**Solution:**
```bash
# Increase timeout for import
export PGOPTIONS='-c statement_timeout=600000'
pg_restore ... # retry import
```

### Issue: "SSL error: unexpected eof while reading"

**Solution:** Already handled by the application! But if you see this:
```bash
# Add these environment variables in Vercel
DB_POOL_RECYCLE=120
DB_FORCE_TLS_1_3=true
DB_SSL_MODE=require
```

### Issue: Row counts don't match

**Solution:**
1. Check if source database is still being written to
2. Set source to read-only before export
3. Re-run export and import
4. Verify counts again

### Issue: "Permission denied" in Vercel Postgres

**Solution:**
```bash
# Connect to Vercel Postgres
psql "$POSTGRES_URL"

# Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "default";
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "default";
```

### Issue: Application can't connect after migration

**Solution:**
1. Verify `DATABASE_URL` is set correctly in Vercel Dashboard
2. Check that URL includes `?sslmode=require`
3. Ensure format is `postgresql://` not `postgres://`
4. Check Vercel deployment logs for errors
5. Test connection manually:
   ```bash
   psql "$DATABASE_URL" -c "SELECT 1"
   ```

---

## Post-Migration Monitoring

### Key Metrics to Watch

1. **Response Time**: Should be <100ms for API endpoints
2. **Error Rate**: Should be near 0%
3. **Connection Pool**: Monitor pool exhaustion
4. **Database Size**: Track growth over time

### Vercel Postgres Dashboard

Access monitoring:
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select **Storage**
3. Click your Postgres database
4. View **Insights** tab

Monitor:
- Storage usage
- Compute hours (Hobby plan)
- Query performance
- Connection statistics

---

## Migration Checklist

Use this checklist to track your progress:

### Pre-Migration
- [ ] Backup current database
- [ ] Document current environment variables
- [ ] Create Vercel Postgres instance
- [ ] Copy Vercel connection strings

### Migration
- [ ] Export data from Render/Render
- [ ] Import data to Vercel Postgres
- [ ] Verify row counts match
- [ ] Verify table structure
- [ ] Test sample queries

### Deployment
- [ ] Update Vercel environment variables
- [ ] Deploy application
- [ ] Test health endpoints
- [ ] Test user authentication
- [ ] Test content creation

### Post-Migration
- [ ] Set old database to read-only
- [ ] Document rollback procedure
- [ ] Monitor for 7 days
- [ ] Delete old database (after grace period)
- [ ] Update documentation

---

## Cost Comparison

### Before (Render/Render)
- **Render Postgres**: $5-20/month
- **Render Postgres**: $7/month (Starter)
- **Total**: $7-20/month

### After (Vercel Postgres)
- **Hobby Plan**: Free (0.5GB storage, 60 compute hours)
- **Pro Plan**: ~$1-5/month for small apps
- **Total**: $0-5/month

**Savings**: $7-20/month → $0-5/month

---

## Automated Migration Script

For automated migration, use the provided script:

```bash
# Set environment variables
export RAILWAY_DATABASE_URL="postgresql://..."
export VERCEL_POSTGRES_URL="postgresql://..."

# Run migration script
python scripts/migrate_render_to_vercel.py

# Set old database to read-only
python scripts/migrate_render_to_vercel.py --set-readonly
```

See [scripts/migrate_render_to_vercel.py](./scripts/migrate_render_to_vercel.py) for details.

---

## Support

If you encounter issues:

1. Check [Troubleshooting](#troubleshooting) section above
2. Review [Vercel Postgres Documentation](https://vercel.com/docs/storage/vercel-postgres)
3. Check [Neon Documentation](https://neon.tech/docs/introduction)
4. Open an issue on GitHub with:
   - Error messages
   - Steps to reproduce
   - Environment details

---

## Summary

This guide walked you through:
✅ Creating Vercel Postgres database
✅ Exporting data from Render/Render
✅ Importing to Vercel Postgres
✅ Verifying data integrity
✅ Updating application configuration
✅ Testing functionality
✅ Setting up grace period for rollback
✅ Final cleanup after verification

Your HireMeBahamas application is now running on Vercel Postgres with improved performance, lower costs, and better reliability!

---

*Last Updated: December 2025*
*Migration Guide Version: 1.0*

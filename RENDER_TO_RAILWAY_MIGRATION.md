# Migrating from Render PostgreSQL to Railway PostgreSQL

## ⚠️ Important Notice

If your HireMeBahamas deployment is still using Render PostgreSQL, you may experience connection issues and users may be unable to sign in. This guide will help you migrate to Railway PostgreSQL, which is the current recommended database provider.

## Why Migrate?

1. **Better Performance**: Railway offers faster connection times and lower latency
2. **Private Networking**: Zero egress fees when using Railway's private network
3. **Better Compatibility**: Optimized SSL/TLS configuration for Railway
4. **Active Support**: Current deployment architecture is built for Railway
5. **Cost Effective**: Free tier includes 512MB RAM and 1GB storage

## Prerequisites

- Access to your Render Dashboard (to backup data)
- Railway account ([railway.app](https://railway.app))
- Access to your Vercel Dashboard (to update environment variables)

## Migration Steps

### Step 1: Backup Your Current Database (Render)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Navigate to your PostgreSQL database
3. Click on **Info** tab
4. Scroll to **Connections** section
5. Copy the **External Database URL**
6. Create a backup:

```bash
# Install PostgreSQL client if not already installed
# For Ubuntu/Debian:
sudo apt-get install postgresql-client

# For macOS:
brew install postgresql

# For Windows:
# Download from: https://www.postgresql.org/download/windows/

# Export your database URL to avoid exposing credentials in shell history
export RENDER_DB_URL="postgresql://user:pass@host.render.com:5432/db"

# Create backup using the exported variable
pg_dump "$RENDER_DB_URL" > hiremebahamas_backup.sql
```

### Step 2: Set Up Railway PostgreSQL

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Create a new project or select your existing HireMeBahamas project
3. Click **+ New** → **Database** → **Add PostgreSQL**
4. Wait for PostgreSQL to provision (takes ~30 seconds)
5. Click on the PostgreSQL service
6. Go to **Variables** tab
7. Copy the following connection variables:
   - `DATABASE_URL` (for external connections)
   - `DATABASE_PRIVATE_URL` (for Railway internal services)

### Step 3: Restore Your Data to Railway

1. In Railway Dashboard, go to your PostgreSQL service
2. Copy the `DATABASE_URL` from the Variables tab
3. Restore your backup:

```bash
# Export your Railway database URL to avoid exposing credentials in shell history
export RAILWAY_DB_URL="postgresql://user:pass@host.railway.app:PORT/railway"

# Restore backup to Railway using the exported variable
psql "$RAILWAY_DB_URL" < hiremebahamas_backup.sql
```

### Step 4: Update Vercel Environment Variables

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your **HireMeBahamas** project
3. Go to **Settings** → **Environment Variables**
4. Update the following variables:

```bash
# Replace with your Railway DATABASE_URL (from Step 2)
DATABASE_URL = postgresql://user:pass@host.railway.app:PORT/railway?sslmode=require

# Add Railway-specific configuration
DB_POOL_RECYCLE = 120
DB_SSL_MODE = require
DB_CONNECT_TIMEOUT = 45
```

5. Click **Save** for each variable

### Step 5: Redeploy Vercel

1. In Vercel Dashboard, go to **Deployments**
2. Click **⋯** menu on the latest deployment
3. Click **Redeploy**
4. Wait 2-3 minutes for deployment to complete

### Step 6: Test the Migration

1. Go to https://hiremebahamas.vercel.app
2. Click **Sign In**
3. Try logging in with your credentials
4. Verify that:
   - ✅ Sign in works correctly
   - ✅ User data is preserved
   - ✅ Posts and jobs are visible
   - ✅ No connection errors in browser console (F12)

### Step 7: Monitor for Issues

Monitor your application for 24-48 hours:

```bash
# Check Vercel logs
vercel logs your-project-url

# Check Railway PostgreSQL metrics
# Go to Railway Dashboard → PostgreSQL → Metrics tab
```

### Step 8: Decommission Render (Optional)

Once you've verified everything works correctly for 1-2 weeks:

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Navigate to your PostgreSQL database
3. Click **Settings**
4. Scroll to **Danger Zone**
5. Click **Delete PostgreSQL Database**

**⚠️ Warning**: This is permanent. Make sure you have verified the migration is successful before deleting.

## Troubleshooting

### "Connection timeout" errors

If you see timeout errors after migration:

1. Check that `DATABASE_URL` in Vercel includes `?sslmode=require`
2. Verify `DB_CONNECT_TIMEOUT=45` is set in Vercel
3. Ensure `DB_POOL_RECYCLE=120` is set in Vercel

### "SSL error: unexpected eof while reading"

This should be resolved by the Railway configuration, but if you still see it:

1. Verify `DB_SSL_MODE=require` is set in Vercel
2. Check that your Railway database is using TLS 1.3
3. Review the `backend/app/database.py` file for SSL configuration

### Data not appearing after migration

If your data doesn't appear after migration:

1. Verify the backup was created successfully (check file size)
2. Check for errors during the `psql` restore command
3. Connect to Railway database and verify tables exist:

```bash
psql "postgresql://user:pass@host.railway.app:PORT/railway" -c "\dt"
```

### Users can't sign in

If users still can't sign in after migration:

1. Check Vercel logs for authentication errors
2. Verify `SECRET_KEY` and `JWT_SECRET_KEY` are set in Vercel
3. Test database connection:

```bash
# In Railway Dashboard → PostgreSQL → Query tab, run:
SELECT * FROM users LIMIT 5;
```

## Environment Variable Reference

Here are all the environment variables you should have in Vercel after migration:

```bash
# Database Configuration (Railway)
DATABASE_URL=postgresql://user:pass@host.railway.app:PORT/railway?sslmode=require
DB_POOL_RECYCLE=120
DB_SSL_MODE=require
DB_CONNECT_TIMEOUT=45
DB_POOL_SIZE=5
DB_POOL_MAX_OVERFLOW=10

# Authentication
SECRET_KEY=your-secret-key-32-chars
JWT_SECRET_KEY=your-jwt-secret-32-chars

# Application
ENVIRONMENT=production
FRONTEND_URL=https://hiremebahamas.vercel.app
```

## Need Help?

If you encounter issues during migration:

1. Check the logs in Vercel Dashboard
2. Check the metrics in Railway Dashboard
3. Review the comprehensive guides:
   - `DEPLOYMENT_CONNECTION_GUIDE.md` - Complete deployment guide
   - `RAILWAY_DATABASE_SETUP.md` - Railway setup instructions
   - `FIX_SIGN_IN_DEPLOYMENT_GUIDE.md` - Sign-in troubleshooting

## Benefits After Migration

After completing the migration, you'll experience:

- ✅ Faster database connections (sub-50ms)
- ✅ No SSL EOF errors
- ✅ Reliable user authentication
- ✅ Better scalability
- ✅ Lower latency for users
- ✅ Zero egress fees with private networking

---

**Last Updated**: December 2025  
**Status**: Recommended Migration Path  
**Estimated Time**: 30 minutes

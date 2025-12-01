# Vercel Postgres Database Setup Guide

Complete step-by-step guide for setting up Vercel Postgres (powered by Neon) for HireMeBahamas.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Integration](#step-by-step-integration)
4. [Environment Configuration](#environment-configuration)
5. [Database Migration](#database-migration)
6. [Testing the Connection](#testing-the-connection)
7. [Troubleshooting](#troubleshooting)
8. [Cost Management](#cost-management)
9. [Advanced Configuration](#advanced-configuration)

---

## Overview

Vercel Postgres is a serverless PostgreSQL database powered by Neon, optimized for Vercel deployments. It offers:

- ✅ **Serverless Architecture**: Automatic scaling and hibernation
- ✅ **Edge Network**: Low latency worldwide via Vercel Edge Network
- ✅ **Free Tier**: 0.5 GB storage (Hobby plan)
- ✅ **Paid Tier**: Pay-per-GB pricing starting at $0.10/GB (Pro plan)
- ✅ **Branching**: Database branches for preview deployments
- ✅ **Connection Pooling**: Built-in via Neon
- ✅ **Automatic Backups**: Point-in-time recovery

---

## Prerequisites

Before you begin, ensure you have:

- ✅ A Vercel account ([sign up free](https://vercel.com/signup))
- ✅ A Vercel project deployed (HireMeBahamas frontend)
- ✅ Command line access (for database migration)
- ✅ PostgreSQL client tools installed (optional, for manual operations)

---

## Step-by-Step Integration

### Step 1: Create Vercel Postgres Instance

1. **Navigate to Vercel Dashboard**
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Select your project: **HireMeBahamas**

2. **Access Storage Tab**
   - Click on the **Storage** tab in your project
   - Or visit: `https://vercel.com/[your-team]/hiremebahamas/stores`

3. **Create Database**
   - Click **"Create Database"** button
   - Select **"Postgres"** from the database options
   - Click **"Continue"**

4. **Choose Your Plan**

   | Plan | Storage | Price | Best For |
   |------|---------|-------|----------|
   | **Hobby** | 0.5 GB | Free | Development, small apps |
   | **Pro** | Pay-per-GB | $0.10/GB/month | Production, scaling apps |

   - **Hobby Plan (Free)**: Perfect for development and small production apps
     - 0.5 GB storage
     - 60 hours of compute per month
     - Automatic hibernation after inactivity
   
   - **Pro Plan ($0.10/GB)**: For production workloads
     - Pay only for what you use
     - No compute hour limits
     - Faster performance
     - Database branches for preview deployments

   Select your plan and click **"Create"**

5. **Database Region Selection**
   - Choose region closest to your users
   - Recommended for Bahamas: **US East (N. Virginia)** or **US East (Ohio)**
   - Click **"Create Database"**

6. **Wait for Provisioning**
   - Database creation takes 30-60 seconds
   - You'll see a progress indicator

### Step 2: Copy Connection String

Once created, you'll see the database details page:

1. **Connection Strings Available**
   - `POSTGRES_URL`: Full connection string (includes password)
   - `POSTGRES_URL_NON_POOLING`: Direct connection (no pooler)
   - `POSTGRES_PRISMA_URL`: For Prisma ORM
   - `POSTGRES_URL_NO_SSL`: Without SSL (not recommended)

2. **Copy the Connection String**
   ```
   Connection String Format:
   postgres://default:ENCRYPTED_PASSWORD@ep-xxxxx.us-east-2.aws.neon.tech/verceldb?sslmode=require
   ```

   Example:
   ```
   postgres://default:AbCdEfGh123456@ep-cool-sound-12345678.us-east-1.aws.neon.tech/verceldb?sslmode=require
   ```

3. **Important**: Keep this connection string **secret**! It contains your database password.

### Step 3: Configure Environment Variables

#### Option A: Vercel Dashboard (Recommended for Production)

1. Go to **Settings → Environment Variables**
2. Add the following variables:

   | Variable Name | Value | Environment |
   |--------------|-------|-------------|
   | `DATABASE_URL` | `postgresql://default:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require` | Production, Preview, Development |
   | `POSTGRES_URL` | (Same as DATABASE_URL) | Production, Preview, Development |

   **Note**: Convert `postgres://` to `postgresql://` for SQLAlchemy compatibility

3. Click **"Save"** for each variable

#### Option B: Local Development (.env file)

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your Vercel Postgres connection string:
   ```bash
   # Vercel Postgres Database (Neon)
   DATABASE_URL=postgresql://default:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require
   
   # Alternative: Use POSTGRES_URL (same value)
   POSTGRES_URL=postgresql://default:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require
   ```

3. **Important**: Add `.env` to `.gitignore` (already done in this project)

### Step 4: Update Database Configuration

The application is already configured to use Vercel Postgres! The database connection code in `backend/app/database.py` automatically:

- ✅ Detects PostgreSQL connection strings
- ✅ Converts to asyncpg driver format
- ✅ Configures SSL for secure connections
- ✅ Sets optimal connection pool settings

No code changes needed! Just set the `DATABASE_URL` environment variable.

### Step 5: Deploy and Test

1. **Redeploy Your Application**
   ```bash
   git add .
   git commit -m "Configure Vercel Postgres database"
   git push origin main
   ```

2. **Automatic Deployment**
   - Vercel automatically deploys on push to main
   - GitHub Actions may also trigger deployment
   - Wait for deployment to complete (2-3 minutes)

3. **Verify Connection**
   ```bash
   # Test health endpoint
   curl https://your-app.vercel.app/api/health
   
   # Should return: {"status": "healthy", "database": "connected"}
   ```

---

## Environment Configuration

### Required Environment Variables

Add these to your Vercel project settings:

```bash
# Database Connection (Vercel Postgres)
DATABASE_URL=postgresql://default:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require

# Authentication Secrets
SECRET_KEY=your-secret-key-generate-with-python
JWT_SECRET_KEY=your-jwt-secret-generate-with-python

# Application Settings
ENVIRONMENT=production
FRONTEND_URL=https://your-app.vercel.app

# Optional: Redis for caching
REDIS_URL=redis://your-redis-url:6379

# Optional: OAuth providers
GOOGLE_CLIENT_ID=your-google-client-id
APPLE_CLIENT_ID=com.hiremebahamas.signin
```

### Generate Secret Keys

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Database Migration

### Option 1: Migrate from Railway Postgres

If you're currently using Railway Postgres, follow these steps:

1. **Backup Current Database**
   ```bash
   # Export from Railway
   pg_dump "$RAILWAY_DATABASE_URL" \
     --no-owner \
     --no-acl \
     --format=custom \
     --compress=0 \
     --file=railway_backup_$(date +%Y%m%d_%H%M%S).dump
   ```

2. **Import to Vercel Postgres**
   ```bash
   # Get Vercel Postgres URL from dashboard
   export VERCEL_POSTGRES_URL="postgresql://default:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"
   
   # Import database
   pg_restore \
     --no-owner \
     --no-acl \
     --dbname="$VERCEL_POSTGRES_URL" \
     railway_backup_*.dump
   ```

3. **Verify Data**
   ```bash
   # Connect to Vercel Postgres
   psql "$VERCEL_POSTGRES_URL"
   
   # Check row counts
   SELECT 'users' as table_name, COUNT(*) FROM users
   UNION ALL
   SELECT 'posts', COUNT(*) FROM posts
   UNION ALL
   SELECT 'jobs', COUNT(*) FROM jobs;
   ```

4. **Update Environment Variables**
   - Go to Vercel Dashboard → Settings → Environment Variables
   - Update `DATABASE_URL` to Vercel Postgres connection string
   - Redeploy application

### Option 2: Fresh Database Setup

For new installations or development:

1. **Set DATABASE_URL** in Vercel dashboard or `.env` file

2. **Run Database Initialization**
   ```bash
   # Initialize tables
   python backend/app/create_tables.py
   
   # Or use seed data for development
   python seed_data.py --dev
   ```

3. **Verify Tables Created**
   ```bash
   psql "$DATABASE_URL" -c "\dt"
   ```

---

## Testing the Connection

### Test 1: Health Check Endpoint

```bash
# Test basic health
curl https://your-app.vercel.app/health

# Test detailed health with database status
curl https://your-app.vercel.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1234567890,
  "database": "connected",
  "pool": {
    "pool_size": 2,
    "checked_out": 0,
    "overflow": 0
  }
}
```

### Test 2: Python Database Connection

```python
# Test connection from Python
import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL, connect_timeout=30)
cur = conn.cursor()
cur.execute("SELECT version()")
print("PostgreSQL version:", cur.fetchone()[0])
cur.close()
conn.close()
```

### Test 3: User Registration/Login

1. Visit your app: `https://your-app.vercel.app`
2. Register a new user
3. Login with credentials
4. Verify profile loads successfully

---

## Troubleshooting

### Issue: "Connection timeout" or "Could not connect"

**Solution**:
1. Verify connection string is correct (check for typos)
2. Ensure `?sslmode=require` is at the end of the URL
3. Check Vercel Postgres dashboard shows "Active" status
4. Increase connection timeout in environment:
   ```bash
   DB_CONNECT_TIMEOUT=45
   ```

### Issue: "SSL error: unexpected eof while reading"

**Solution**: 
Already handled by the application! The database configuration includes:
- TLS 1.3 enforcement
- Connection pooling with pre-ping
- Automatic connection recycling (every 2 minutes)

If you still see this error:
```bash
# Add these environment variables
DB_POOL_RECYCLE=120
DB_SSL_MODE=require
DB_FORCE_TLS_1_3=true
```

### Issue: "Database not found" or "Permission denied"

**Solution**:
1. Verify you're using `POSTGRES_URL` from Vercel dashboard
2. Check database name in connection string is `verceldb`
3. Ensure user has permissions:
   ```sql
   -- Connect as superuser (Vercel console)
   GRANT ALL PRIVILEGES ON DATABASE verceldb TO "default";
   ```

### Issue: "Too many connections"

**Solution**:
Vercel Postgres (Neon) uses connection pooling automatically. If you see this:
1. Use `POSTGRES_URL` (includes pooler) instead of `POSTGRES_URL_NON_POOLING`
2. Reduce pool size in environment:
   ```bash
   DB_POOL_SIZE=1
   DB_MAX_OVERFLOW=2
   ```

### Issue: Hobby Plan "Database hibernated"

**Solution**:
Free tier databases hibernate after inactivity. They wake up automatically but first request may be slow.

Options:
1. **Upgrade to Pro plan** - no hibernation
2. **Use Vercel Cron Jobs** - ping database every 5 minutes:
   ```json
   // In vercel.json
   {
     "crons": [{
       "path": "/api/cron/health",
       "schedule": "*/5 * * * *"
     }]
   }
   ```

---

## Cost Management

### Hobby Plan (Free)

- ✅ 0.5 GB storage
- ✅ 60 compute hours/month
- ✅ Automatic hibernation (wakes on request)
- ✅ Perfect for development and small apps

**Tips to Stay on Free Tier**:
- Keep database size under 500 MB
- Use Vercel Cron Jobs to prevent full hibernation
- Optimize queries to reduce compute time

### Pro Plan Pricing

| Resource | Price |
|----------|-------|
| Storage | $0.10/GB/month |
| Compute | $0.16/hour (baseline) |
| Data Transfer | Free within Vercel |

**Cost Estimation**:
- **Small app** (1GB, low traffic): ~$1-5/month
- **Medium app** (5GB, moderate traffic): ~$10-30/month
- **Large app** (20GB, high traffic): ~$50-150/month

**Cost Optimization**:
- Use connection pooling (already configured)
- Optimize indexes for faster queries
- Archive old data regularly
- Monitor usage in Vercel dashboard

---

## Advanced Configuration

### Connection Pool Tuning

For high-traffic applications, adjust pool settings:

```bash
# Environment variables
DB_POOL_SIZE=5           # Concurrent connections
DB_MAX_OVERFLOW=10        # Burst capacity
DB_POOL_TIMEOUT=30        # Wait time for connection
DB_POOL_RECYCLE=120       # Recycle every 2 minutes
```

### Database Branches (Pro Plan)

Create database branches for preview deployments:

1. Go to Vercel Dashboard → Storage → Your Database
2. Click **"Branches"** tab
3. Click **"Create Branch"**
4. Name it (e.g., `preview`, `staging`)
5. Use branch-specific connection string for preview deployments

### Read Replicas (Enterprise)

For high-read workloads:

1. Contact Vercel support for read replica setup
2. Configure read/write splitting in application
3. Use read replica connection string for SELECT queries

### Monitoring

Vercel Dashboard provides:
- Storage usage
- Compute hours
- Query performance metrics
- Connection statistics

Access: `Vercel Dashboard → Storage → [Your Database] → Insights`

---

## Additional Resources

- **Vercel Postgres Documentation**: https://vercel.com/docs/storage/vercel-postgres
- **Neon Documentation**: https://neon.tech/docs/introduction
- **Migration from Railway**: See [VERCEL_POSTGRES_MIGRATION.md](./VERCEL_POSTGRES_MIGRATION.md)
- **Database Security**: See [DOCKER_SECURITY.md](./DOCKER_SECURITY.md)
- **Environment Variables**: See [.env.example](./.env.example)

---

## Quick Reference

### Connection String Format

```
postgresql://default:PASSWORD@ep-xxxxx.REGION.aws.neon.tech:5432/verceldb?sslmode=require
```

### Essential Environment Variables

```bash
DATABASE_URL=postgresql://default:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
ENVIRONMENT=production
```

### Quick Test

```bash
# Test connection
psql "$DATABASE_URL" -c "SELECT 1"

# Test health endpoint
curl https://your-app.vercel.app/api/health
```

---

**🎉 Congratulations!** Your Vercel Postgres database is now configured and ready to use.

For issues or questions, check the [Troubleshooting](#troubleshooting) section or open an issue on GitHub.

---

*Last Updated: December 2025*

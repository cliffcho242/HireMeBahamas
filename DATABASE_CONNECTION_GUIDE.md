# 🔗 Database Connection Guide - HireMeBahamas

**Complete guide with direct links and step-by-step instructions to connect your database URL to HireMeBahamas on Vercel, Render, and Render.**

---

## ⚡ Quick Links

Choose your platform and jump directly to the setup guide:

| Platform | Best For | Cost | Setup Time | Link |
|----------|----------|------|------------|------|
| **Vercel** ⭐ | Production, global users | $0-5/mo | 10 min | [Setup Guide](#vercel-setup---recommended) |
| **Render** | Simple deployment | $5-20/mo | 5 min | [Setup Guide](#render-setup) |
| **Render** | Legacy projects | $7-25/mo | 15 min | [Setup Guide](#render-setup) |
| **Local** | Development | $0 | 5 min | [Setup Guide](#local-development-setup) |

**Direct Dashboard Links:**
- 🔗 [Vercel Dashboard](https://vercel.com/dashboard)
- 🔗 [Vercel Storage (Create DB)](https://vercel.com/dashboard/stores)
- 🔗 [Render Dashboard](https://render.app/dashboard)
- 🔗 [Render Dashboard](https://dashboard.render.com/)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Vercel Setup](#vercel-setup---recommended)
3. [Render Setup](#render-setup)
4. [Render Setup](#render-setup)
5. [Local Development Setup](#local-development-setup)
6. [Troubleshooting](#troubleshooting)

---

## Overview

HireMeBahamas requires a PostgreSQL database to store user data, posts, and other information. This guide shows you exactly where to find and configure your database connection on each deployment platform.

### What You'll Need

- A PostgreSQL database (created on your chosen platform)
- Access to your deployment platform dashboard
- 5-10 minutes

### Database URL Format

All PostgreSQL connection strings follow this format:
```
postgresql://username:password@hostname:port/database
```

For asyncpg (required for Vercel serverless):
```
postgresql+asyncpg://username:password@hostname:port/database
```

---

## Vercel Setup - ⭐ Recommended

**Best for:** Zero cold starts, fastest performance, $0-5/month

### Step 1: Create Vercel Postgres Database

**Direct Link:** 🔗 [https://vercel.com/dashboard/stores](https://vercel.com/dashboard/stores)

1. Click **"Create Database"** button
2. Select **"Postgres"** (powered by Neon)
3. Enter a database name (e.g., "hiremebahamas-db")
4. Select region closest to your users
5. Choose plan:
   - **Hobby** (Free): 256 MB storage - Good for testing
   - **Pro** ($0.10/GB): Auto-scaling - Good for production
6. Click **"Create"**
7. Wait 30-60 seconds for provisioning

### Step 2: Get Your Database Connection Strings

After creation, you'll see your database dashboard with these tabs:
- **Quickstart** | **.env.local** | **Data** | **Settings**

**Click on the ".env.local" tab** to see your connection strings:

```env
POSTGRES_URL="postgresql://default:abc123...@ep-name-12345.region.aws.neon.tech:5432/verceldb?sslmode=require"
POSTGRES_PRISMA_URL="postgresql://default:abc123...@ep-name-12345-pooler.region.aws.neon.tech:5432/verceldb?sslmode=require&pgbouncer=true"
POSTGRES_URL_NON_POOLING="postgresql://default:abc123...@ep-name-12345.region.aws.neon.tech:5432/verceldb?sslmode=require"
```

**Copy the `POSTGRES_URL` value** - this is your main connection string.

> ⚠️ **Security Note:** Never share your database URL publicly. It contains sensitive credentials.

### Step 3: Connect Database to Your HireMeBahamas Project

**Direct Link:** 🔗 [https://vercel.com/dashboard](https://vercel.com/dashboard)

#### Navigation Path:
```
Vercel Dashboard → Your HireMeBahamas Project → Settings → Environment Variables
```

#### Detailed Steps:

1. **Go to your project:**
   - Visit [https://vercel.com/dashboard](https://vercel.com/dashboard)
   - Click on your **"HireMeBahamas"** project

2. **Open Settings:**
   - Click the **"Settings"** tab (top navigation bar)

3. **Add Environment Variables:**
   - Click **"Environment Variables"** in the left sidebar
   - Click **"Add New"** button

4. **Add DATABASE_URL:**
   ```
   Key: DATABASE_URL
   Value: [Paste your POSTGRES_URL here, but change postgresql:// to postgresql+asyncpg://]
   Environments: ☑️ Production ☑️ Preview ☑️ Development
   ```
   
   **Example:**
   ```
   DATABASE_URL=postgresql+asyncpg://default:abc123...@ep-name-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require
   ```
   
   > Note: Region format (e.g., `us-east-1.aws.neon.tech`) may vary depending on where you created your database.

5. **Add POSTGRES_URL (optional but recommended):**
   ```
   Key: POSTGRES_URL
   Value: [Paste the original POSTGRES_URL]
   Environments: ☑️ Production ☑️ Preview ☑️ Development
   ```

6. **Add Required Secrets:**
   
   Generate secure keys:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   
   Add these variables:
   ```
   Key: SECRET_KEY
   Value: [Generated key from above command]
   Environments: ☑️ All
   
   Key: JWT_SECRET_KEY
   Value: [Generate another different key]
   Environments: ☑️ All
   
   Key: ENVIRONMENT
   Value: production
   Environments: ☑️ All
   ```

7. **Click "Save"** for each variable

### Step 4: Verify Connection

After adding variables, trigger a new deployment:

1. Go to **"Deployments"** tab
2. Click **"Redeploy"** on the latest deployment
3. Wait for deployment to complete (2-3 minutes)
4. Visit your site and test:
   - Health check: `https://your-app.vercel.app/api/health`
   - Database check: `https://your-app.vercel.app/api/ready`

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "platform": "vercel"
}
```

✅ **Done!** Your database is connected to Vercel.

---

## Render Setup

**Best for:** Simple deployment, private networking, $5-20/month

### Step 1: Create Render PostgreSQL Database

**Direct Link:** 🔗 [https://render.app/dashboard](https://render.app/dashboard)

#### Navigation Path:
```
Render Dashboard → Your Project → + New → Database → PostgreSQL
```

#### Detailed Steps:

1. **Open your project:**
   - Visit [https://render.app/dashboard](https://render.app/dashboard)
   - Click on your **HireMeBahamas** project

2. **Add PostgreSQL:**
   - Click the **"+ New"** button (top right)
   - Select **"Database"**
   - Click **"Add PostgreSQL"**
   - Wait 1-2 minutes for provisioning

3. **PostgreSQL service appears** in your project canvas

### Step 2: Get Your Database Connection String

Render automatically creates connection variables when you add PostgreSQL.

1. Click on the **PostgreSQL service** (the elephant icon 🐘)
2. Go to the **"Variables"** tab
3. You'll see these variables:

```
DATABASE_URL = postgresql://postgres:password@hostname.render.app:5432/render
DATABASE_PRIVATE_URL = postgresql://postgres:password@postgres.render.internal:5432/render
```

**Use `DATABASE_PRIVATE_URL` for zero egress fees** (recommended)

### Step 3: Connect Database to Your Backend Service

Render should automatically share the database URL with your backend service. To verify:

1. Click on your **Backend service** (not the PostgreSQL service)
2. Go to **"Variables"** tab
3. Look for `DATABASE_PRIVATE_URL` or `DATABASE_URL`

If not present, add it manually:

1. Click **"+ New Variable"**
2. Select **"Reference"** (not "Variable")
3. Choose:
   - **Service:** PostgreSQL
   - **Variable:** DATABASE_PRIVATE_URL
4. Click **"Add"**

### Step 4: Add Required Environment Variables

While in the Backend service Variables tab:

1. Click **"+ New Variable"**
2. Add each of these:

```
Variable: SECRET_KEY
Value: [Generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"]

Variable: JWT_SECRET_KEY  
Value: [Generate another key]

Variable: ENVIRONMENT
Value: production
```

### Step 5: Deploy and Verify

1. Render auto-deploys when you add variables
2. Check the **"Deployments"** tab to see deployment progress
3. Once deployed, verify:
   - Visit: `https://your-app.render.app/health`
   - Should return: `{"status": "healthy", "database": "connected"}`

✅ **Done!** Your database is connected to Render.

**💡 Pro Tip:** Using `DATABASE_PRIVATE_URL` instead of `DATABASE_URL` routes traffic through Render's internal network, avoiding egress fees.

---

## Render Setup

> 💡 **Note:** While Render is still a fully supported and valid deployment option, it has become less cost-effective ($7-25/month) and has slower cold start times compared to newer alternatives like Vercel ($0-5/month) and Render ($5-20/month). We recommend Vercel or Render for new deployments to get better performance at lower costs. However, if you're already using Render, are comfortable with its interface, or have specific reasons to prefer it, this section provides complete setup instructions.

**Direct Link:** 🔗 [https://dashboard.render.com/](https://dashboard.render.com/)

### Step 1: Create Render PostgreSQL Database

1. **Open Render Dashboard:**
   - Visit [https://dashboard.render.com/](https://dashboard.render.com/)

2. **Create new PostgreSQL:**
   - Click **"New +"** button (top right)
   - Select **"PostgreSQL"**
   - Fill in details:
     - **Name:** hiremebahamas-db
     - **Database:** hiremebahamas
     - **User:** hiremebahamas_user
     - **Region:** Oregon (or closest to you)
   - Select plan:
     - **Free:** Limited storage, may spin down
     - **Starter ($7/mo):** Better performance
   - Click **"Create Database"**

3. **Wait for provisioning** (2-3 minutes)

### Step 2: Get Your Database Connection String

After creation:

1. Click on your PostgreSQL database
2. Scroll down to **"Connections"** section
3. Copy the **"Internal Database URL"** (preferred) or **"External Database URL"**

```
Internal: postgresql://user:pass@hostname.internal:5432/database
External: postgresql://user:pass@hostname.render.com:5432/database
```

**Use Internal URL** if your web service is also on Render (faster, no external traffic charges).

### Step 3: Connect Database to Your Web Service

1. **Go to your web service:**
   - Click on your HireMeBahamas web service

2. **Open Environment tab:**
   - Click **"Environment"** in the left sidebar

3. **Add DATABASE_URL:**
   - Click **"Add Environment Variable"**
   - Enter:
     ```
     Key: DATABASE_URL
     Value: [Paste your Internal Database URL]
     ```
   - Click **"Save Changes"**

4. **Add other required variables:**
   ```
   Key: SECRET_KEY
   Value: [Generated secure key]
   
   Key: JWT_SECRET_KEY
   Value: [Another generated key]
   
   Key: ENVIRONMENT
   Value: production
   
   Key: FRONTEND_URL
   Value: https://hiremebahamas.vercel.app
   ```

### Step 4: Deploy and Verify

1. Render automatically redeploys when you save environment variables
2. Check the **"Logs"** tab to see deployment progress
3. Look for: `🗄️ Database Mode: PostgreSQL (Production)`
4. Verify at: `https://your-app.onrender.com/health`

✅ **Done!** Your database is connected to Render.

---

## Local Development Setup

For running HireMeBahamas on your local machine:

### Option 1: Use Docker (Recommended)

1. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

2. **Start PostgreSQL with Docker:**
   ```bash
   docker-compose up -d postgres
   ```

3. **Your local DATABASE_URL is automatically set:**
   ```
   DATABASE_URL=postgresql://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas
   ```

4. **Start the application:**
   ```bash
   # Backend
   python app.py
   
   # Frontend (in another terminal)
   cd frontend && npm run dev
   ```

### Option 2: Use Local PostgreSQL

1. **Install PostgreSQL:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   ```

2. **Create database:**
   ```bash
   sudo -u postgres psql
   ```
   
   In PostgreSQL shell:
   ```sql
   CREATE DATABASE hiremebahamas;
   CREATE USER hiremebahamas_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE hiremebahamas TO hiremebahamas_user;
   \q
   ```

3. **Update `.env` file:**
   ```env
   DATABASE_URL=postgresql://hiremebahamas_user:your_password@localhost:5432/hiremebahamas
   SECRET_KEY=your-generated-secret-key
   JWT_SECRET_KEY=your-generated-jwt-secret
   ENVIRONMENT=development
   ```

4. **Initialize database:**
   ```bash
   python seed_data.py --dev
   ```

---

## Troubleshooting

### "Database connection failed"

**Check these in order:**

1. **Verify DATABASE_URL format:**
   ```
   ✅ Correct: postgresql://user:pass@host:5432/db
   ❌ Wrong: postgres://user:pass@host:5432/db (missing 'ql')
   ❌ Wrong: postgresql://user:pass@host/db (missing port)
   ```

2. **For Vercel, use asyncpg:**
   ```
   ✅ Correct: postgresql+asyncpg://...
   ❌ Wrong: postgresql://... (won't work in serverless)
   ```

3. **Check if database is running:**
   - Vercel: Go to [Storage dashboard](https://vercel.com/dashboard/stores)
   - Render: Check PostgreSQL service status
   - Render: Check database status in dashboard

4. **Verify environment variables are set:**
   - They should appear in your platform's environment variables section
   - Click "Redeploy" after adding them

### "SSL connection error"

For cloud databases, ensure SSL is enabled:

```
# Add to your DATABASE_URL:
?sslmode=require

# Full example:
postgresql://user:pass@host:5432/db?sslmode=require
```

### "Authentication failed"

1. **Double-check credentials:** Copy the DATABASE_URL exactly from your database provider
2. **Special characters in password:** If your password has special characters, they must be URL-encoded:
   - `@` → `%40`
   - `#` → `%23`
   - `/` → `%2F`
   - `:` → `%3A`

### "Too many connections"

If you see this error:

1. **Check connection pool settings** in your `.env`:
   ```env
   DB_POOL_SIZE=5
   DB_MAX_OVERFLOW=10
   ```

2. **For Vercel:** Use the pooled connection URL:
   ```
   POSTGRES_PRISMA_URL=postgresql://...pooler...pgbouncer=true
   ```

3. **For Render:** Use DATABASE_PRIVATE_URL (includes built-in pooling)

### "Database does not exist"

The database hasn't been created yet:

1. **Vercel:** Database is auto-created, check your `.env.local` tab
2. **Render:** Database named `render` is auto-created
3. **Render:** Verify database name matches what you specified
4. **Local:** Run `CREATE DATABASE hiremebahamas;` in PostgreSQL

### Environment Variables Not Taking Effect

1. **Redeploy your application** after adding variables
2. **Check all environments** are selected (Production, Preview, Development)
3. **Clear build cache** if available on your platform
4. **Check variable spelling** - they are case-sensitive

### Health Check Failing

Visit these endpoints to diagnose:

- `/health` - Basic health check (no database)
- `/api/health` - Includes database status
- `/api/ready` - Full readiness check

**Example healthy response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-12-03T10:00:00Z"
}
```

---

## Platform Comparison

| Platform | Cost | Setup Time | Performance | Best For |
|----------|------|------------|-------------|----------|
| **Vercel** | $0-5/mo | 10 min | ⭐⭐⭐⭐⭐ Fastest | Production apps, global users |
| **Render** | $5-20/mo | 5 min | ⭐⭐⭐⭐ Fast | Simple deployment, private network |
| **Render** | $7-25/mo | 15 min | ⭐⭐⭐ Good | Legacy projects |
| **Local** | $0 | 5 min | ⭐⭐⭐⭐ Fast | Development only |

---

## Quick Reference Links

### Direct Dashboard Links

- **Vercel Dashboard:** [https://vercel.com/dashboard](https://vercel.com/dashboard)
- **Vercel Storage:** [https://vercel.com/dashboard/stores](https://vercel.com/dashboard/stores)
- **Render Dashboard:** [https://render.app/dashboard](https://render.app/dashboard)
- **Render Dashboard:** [https://dashboard.render.com/](https://dashboard.render.com/)

### Documentation Links

- **Vercel Postgres Docs:** [https://vercel.com/docs/storage/vercel-postgres](https://vercel.com/docs/storage/vercel-postgres)
- **Render Database Docs:** [https://docs.render.app/databases/postgresql](https://docs.render.app/databases/postgresql)
- **Render PostgreSQL Docs:** [https://render.com/docs/databases](https://render.com/docs/databases)

### Generate Secure Keys

```bash
# SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# JWT_SECRET_KEY (generate a different one)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Additional Resources

- **[DATABASE_URL_LOCATION_GUIDE.md](./DATABASE_URL_LOCATION_GUIDE.md)** - Detailed Vercel navigation with visual guidance
- **[RAILWAY_DATABASE_SETUP.md](./RAILWAY_DATABASE_SETUP.md)** - Comprehensive Render setup guide with troubleshooting
- **[VERCEL_DEPLOYMENT_GUIDE.md](./VERCEL_DEPLOYMENT_GUIDE.md)** - Full Vercel deployment walkthrough
- **[.env.example](./.env.example)** - Template for all environment variables with comments

---

## Summary Checklist

Before your app can connect to the database, ensure you have:

- [ ] PostgreSQL database created on your chosen platform
- [ ] DATABASE_URL copied from database dashboard
- [ ] DATABASE_URL added to your app's environment variables
- [ ] SECRET_KEY and JWT_SECRET_KEY generated and added
- [ ] ENVIRONMENT set to "production"
- [ ] Application redeployed after adding variables
- [ ] Health check endpoint returning "connected"
- [ ] Test user registration and login working

---

**Need help?** Create an issue on GitHub or check the troubleshooting section above.

**Last Updated:** December 2024

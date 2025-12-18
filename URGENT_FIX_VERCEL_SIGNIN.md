# 🚨 URGENT: Vercel Sign-In Issues - Quick Fix

## Problem
Users cannot sign in to HireMeBahamas on Vercel because the database connection is not properly configured.

## Root Cause
The application may still be connected to Render PostgreSQL database, which can cause backend connectivity issues preventing users from signing in. The recommended deployment uses Render PostgreSQL for better performance and reliability.

**⚠️ If you're still using Render PostgreSQL**: Follow the [Render to Render Migration Guide](./RENDER_TO_RAILWAY_MIGRATION.md) to migrate to Render PostgreSQL (recommended, 30 minutes).

**If you're already using Render**: Verify that Vercel environment variables are properly configured to connect to Render PostgreSQL.

## Quick Solution

### Step 1: Identify Your Database Location

Your database should be on **Render** (recommended):
- **Render** (https://render.app/dashboard)

**⚠️ If you're still using Render PostgreSQL**: 
Follow the **[Render to Render Migration Guide](./RENDER_TO_RAILWAY_MIGRATION.md)** before proceeding with this fix.

### Step 2: Get Render Database Connection URL

1. Go to https://render.app/dashboard
2. Click on your HireMeBahamas project
3. Click on the PostgreSQL service
4. Go to **Variables** tab
5. Copy `DATABASE_URL` (for external connections like Vercel)

### Step 3: Configure Vercel Environment Variables

1. Go to **Vercel Dashboard**: https://vercel.com/dashboard
2. Click on your **HireMeBahamas** project
3. Go to **Settings** → **Environment Variables**
4. Add these variables:

```bash
DATABASE_URL = [Your Render PostgreSQL URL from Step 2]
SECRET_KEY = [Generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"]
JWT_SECRET_KEY = [Generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"]
ENVIRONMENT = production
DB_POOL_RECYCLE = 120
DB_SSL_MODE = require
DB_CONNECT_TIMEOUT = 45
```

### Step 4: Redeploy

1. In Vercel Dashboard, go to **Deployments**
2. Click **⋯** menu on latest deployment
3. Click **Redeploy**
4. Wait 2-3 minutes for deployment

### Step 5: Test Sign-In

1. Go to https://hiremebahamas.vercel.app
2. Click **Sign In**
3. Use: `admin@hiremebahamas.com` / `AdminPass123!`

## Complete Fix Guide

For detailed step-by-step instructions with screenshots and troubleshooting:

📖 **[FIX_VERCEL_DATABASE_CONNECTION.md](./FIX_VERCEL_DATABASE_CONNECTION.md)**

## Diagnostic Tool

Run this to identify issues:

```bash
python3 diagnose_vercel_issue.py
```

This will check:
- ✓ Environment variables
- ✓ Database URL format
- ✓ Python dependencies
- ✓ Database connectivity
- ✓ Vercel configuration

## Architecture

Current recommended setup:
- **Frontend**: Vercel (https://hiremebahamas.vercel.app)
- **Backend**: Vercel Serverless Functions (`/api/*`)
- **Database**: Render PostgreSQL (recommended)
- **Old Render Backend**: Should be decommissioned (see migration guide)

## Key Files

- `api/index.py` - Vercel serverless backend handler
- `vercel.json` - Vercel deployment configuration
- `requirements.txt` - Python dependencies (includes asyncpg)
- `FIX_VERCEL_DATABASE_CONNECTION.md` - Complete fix guide
- `diagnose_vercel_issue.py` - Diagnostic tool

## Common Issues

### "Network Error" when signing in
→ Frontend can't reach backend. Check browser console (F12).
→ Backend URL should be same-origin (Vercel serverless).

### "Database connection failed"
→ DATABASE_URL not set or incorrect in Vercel.
→ Follow Step 3 above to configure environment variables.

### "Invalid credentials"
→ Database is empty or using wrong database.
→ Check DATABASE_URL points to correct database.
→ You may need to create admin user (see fix guide).

## Next Steps

1. ✅ Configure Vercel environment variables (Step 3)
2. ✅ Redeploy Vercel (Step 4)
3. ✅ Test sign-in (Step 5)
4. ✅ Run diagnostic tool to verify
5. ✅ Suspend Render backend if no longer needed

## Need Help?

See complete guides in the repository:
- `FIX_VERCEL_DATABASE_CONNECTION.md` - Main fix guide
- `DEPLOYMENT_CONNECTION_GUIDE.md` - Full deployment guide
- `WHERE_TO_PUT_DATABASE_URL.md` - Database configuration guide
- `VERCEL_POSTGRES_SETUP.md` - Vercel Postgres setup

---

**Last Updated**: December 2025
**Status**: Active - Fix Required
**Priority**: 🚨 CRITICAL - Users Cannot Sign In

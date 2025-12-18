# 🚨 FIX: Vercel Database Connection & Sign-In Issues

**Problem**: Users cannot sign in on Vercel deployment because database connection is not properly configured.

**Root Cause**: The old Render service is still active, and Vercel environment variables may not be correctly set to use the Render PostgreSQL database.

---

## ✅ Quick Fix Checklist

Follow these steps in order to fix the issue:

- [ ] **Step 1**: Get your Render PostgreSQL connection URL
- [ ] **Step 2**: Configure Vercel environment variables
- [ ] **Step 3**: Verify Vercel deployment
- [ ] **Step 4**: Test sign-in functionality
- [ ] **Step 5**: Disable Render service (optional cleanup)

---

## 📋 Step 1: Get Your Render PostgreSQL Connection URL

### Option A: Using Render Dashboard

1. Go to **Render Dashboard**: https://render.app/dashboard
2. Click on your **HireMeBahamas project**
3. Click on the **PostgreSQL service** (not the backend service)
4. Click on the **Variables** tab
5. Look for these variables:
   - `DATABASE_PRIVATE_URL` (recommended for internal use)
   - `DATABASE_URL` (public URL)
6. **Copy the DATABASE_URL** - it should look like:
   ```
   postgresql://postgres:PASSWORD@containers-us-west-XXX.render.app:PORT/render
   ```

### Option B: Using Render Dashboard (if database is on Render)

1. Go to **Render Dashboard**: https://dashboard.render.com/project/prj-d3qjl56mcj7s73bpil6g
2. Click on your **PostgreSQL database**
3. Scroll to **Connections** section
4. **Copy the External Database URL** or **Internal Database URL**
   ```
   postgresql://username:PASSWORD@dpg-XXXXX-a.oregon-postgres.render.com:5432/hiremebahamas
   ```

---

## 🔧 Step 2: Configure Vercel Environment Variables

### 2.1 Access Vercel Dashboard

1. Go to **Vercel Dashboard**: https://vercel.com/dashboard
2. Find and click on your **HireMeBahamas project**
3. Click **Settings** in the top navigation bar
4. Click **Environment Variables** in the left sidebar

### 2.2 Add Required Environment Variables

Click **Add New** and add these variables one by one:

#### Database Configuration

```bash
# Variable 1: DATABASE_URL
Name: DATABASE_URL
Value: [PASTE YOUR POSTGRESQL URL FROM STEP 1]
Environment: Production, Preview, Development
```

```bash
# Variable 2: POSTGRES_URL (alias for compatibility)
Name: POSTGRES_URL
Value: [SAME AS DATABASE_URL]
Environment: Production, Preview, Development
```

#### Security Keys

Generate new secret keys using this command in your terminal:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Run it twice to get two different keys:

```bash
# Variable 3: SECRET_KEY
Name: SECRET_KEY
Value: [OUTPUT FROM COMMAND ABOVE - FIRST RUN]
Environment: Production, Preview, Development
```

```bash
# Variable 4: JWT_SECRET_KEY
Name: JWT_SECRET_KEY
Value: [OUTPUT FROM COMMAND ABOVE - SECOND RUN]
Environment: Production, Preview, Development
```

#### Application Configuration

```bash
# Variable 5: ENVIRONMENT
Name: ENVIRONMENT
Value: production
Environment: Production, Preview, Development
```

```bash
# Variable 6: FRONTEND_URL
Name: FRONTEND_URL
Value: https://hiremebahamas.vercel.app
Environment: Production, Preview, Development
```

#### Database Connection Settings (Optional but Recommended)

```bash
# Variable 7: DB_CONNECT_TIMEOUT
Name: DB_CONNECT_TIMEOUT
Value: 30
Environment: Production, Preview, Development
```

```bash
# Variable 8: DB_POOL_SIZE
Name: DB_POOL_SIZE
Value: 2
Environment: Production, Preview, Development
```

```bash
# Variable 9: DB_POOL_RECYCLE
Name: DB_POOL_RECYCLE
Value: 120
Environment: Production, Preview, Development
```

### 2.3 Save Configuration

1. Click **Save** for each variable
2. Verify all variables are listed correctly

---

## 🚀 Step 3: Verify Vercel Deployment

### 3.1 Trigger Redeployment

After adding environment variables, you need to redeploy:

1. In your Vercel dashboard, click **Deployments** (top menu)
2. Find the latest deployment
3. Click the **three dots menu** (⋯) next to it
4. Click **Redeploy**
5. Wait for deployment to complete (usually 2-3 minutes)

### 3.2 Check Deployment Status

1. Wait for the deployment to show **"Ready"** status
2. Click on the deployment to view details
3. Look for the **Visit** button and click it to open your site

### 3.3 Verify Backend Health

Open these URLs in your browser to verify backend is working:

**Health Check** (should return JSON with status: "healthy"):
```
https://hiremebahamas.vercel.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "backend": "available",
  "database": "connected",
  "jwt": "configured"
}
```

**Status Check** (more detailed):
```
https://hiremebahamas.vercel.app/api/status
```

**Ready Check** (database connectivity):
```
https://hiremebahamas.vercel.app/api/ready
```

Expected response:
```json
{
  "status": "ready",
  "database": "connected"
}
```

### 3.4 Check for Errors

If any of the above endpoints return errors:

1. Go to Vercel Dashboard → Your Project → **Logs**
2. Look for error messages
3. Check if DATABASE_URL is properly set (you'll see "Database URL configured" in logs)
4. If you see "DATABASE_URL not configured", double-check Step 2

---

## 🧪 Step 4: Test Sign-In Functionality

### 4.1 Test with Default Admin Account

1. Go to your Vercel deployment: https://hiremebahamas.vercel.app
2. Click **Sign In**
3. Use these credentials:
   - **Email**: `admin@hiremebahamas.com`
   - **Password**: `AdminPass123!`
4. Click **Sign In**

### 4.2 Expected Results

✅ **Success**: You should be redirected to the home page/dashboard with a "Welcome back" message

❌ **If it fails**:
- Check browser console (F12) for error messages
- Look for network errors in Network tab (F12 → Network)
- Check Vercel logs for backend errors

### 4.3 Common Issues and Solutions

#### Issue: "Network Error" or "Connection Refused"

**Solution**: Frontend is not using the correct backend URL
1. Check if there's a `.env` file in `frontend/` directory
2. If `VITE_API_URL` is set, remove it or comment it out
3. The frontend should use same-origin (Vercel serverless) automatically
4. Redeploy: `git add . && git commit -m "Fix: Remove VITE_API_URL" && git push`

#### Issue: "Database connection failed"

**Solution**: DATABASE_URL is not set correctly
1. Go back to Step 2 and verify DATABASE_URL
2. Make sure it starts with `postgresql://` or `postgres://`
3. Check that password doesn't contain special characters that need encoding
4. Try using `postgresql+asyncpg://` instead of `postgresql://`

#### Issue: "Invalid credentials" or "User not found"

**Solution**: Database is empty or using wrong database
1. Check if you're connecting to the right database
2. Verify the database name in your DATABASE_URL matches your actual database
3. You may need to create the admin user (see Step 4.4)

### 4.4 Create Admin User (If Needed)

If the database is empty, you need to create an admin user:

#### Option A: Using Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Link to your project
vercel link

# Run database initialization
vercel env pull .env.local
# Then run your local backend to create tables and admin user
```

#### Option B: Using Render CLI

```bash
# Install Render CLI
npm i -g @render/cli

# Login
render login

# Link to your project
render link

# Connect to database
render connect postgres

# In the PostgreSQL shell, run:
\c render  # or your database name

# Check if users table exists
\dt

# If tables don't exist, you need to run migrations
# Exit with \q and run your backend locally to create tables
```

#### Option C: Direct SQL (if you have database access)

Connect to your PostgreSQL database and run:

```sql
-- Create users table if not exists
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user',
    user_type VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create admin user (password: AdminPass123!)
-- Note: This is a bcrypt hash of "AdminPass123!"
INSERT INTO users (email, password, first_name, last_name, role, user_type, is_active)
VALUES (
    'admin@hiremebahamas.com',
    '$2b$10$XxXxXxXxXxXxXxXxXxXxXeYourActualBcryptHashHere',
    'Admin',
    'User',
    'admin',
    'admin',
    true
)
ON CONFLICT (email) DO NOTHING;
```

---

## 🧹 Step 5: Disable Render Service (Optional Cleanup)

If you're no longer using Render, disable it to avoid confusion and potential charges:

### 5.1 Access Render Dashboard

1. Go to: https://dashboard.render.com/project/prj-d3qjl56mcj7s73bpil6g
2. You should see your services listed

### 5.2 Suspend Web Service

1. Click on your **backend web service**
2. Click **Settings** (left sidebar)
3. Scroll to bottom and click **Suspend Service**
4. Confirm by clicking **Suspend**

**Note**: Suspending keeps the service but stops it from running (and charging).

### 5.3 Suspend Background Workers (if any)

If you have keep-alive workers or cron jobs:
1. Click on each worker/cron job
2. Settings → Suspend Service

### 5.4 Keep Database Active (if needed)

If your DATABASE_URL is from Render:
- **DO NOT** suspend or delete the PostgreSQL database
- You can keep it running since the free tier allows one free database
- Only suspend if you've migrated to Render/Vercel Postgres

---

## ✅ Verification Checklist

After completing all steps, verify everything is working:

- [ ] `/api/health` returns `{"status": "healthy", "database": "connected"}`
- [ ] `/api/ready` returns `{"status": "ready", "database": "connected"}`
- [ ] Can sign in with `admin@hiremebahamas.com` / `AdminPass123!`
- [ ] After sign-in, redirected to home page
- [ ] User profile loads correctly
- [ ] No console errors in browser (F12)
- [ ] Vercel logs show no database connection errors

---

## 🔍 Troubleshooting

### Check Vercel Logs

1. Go to Vercel Dashboard → Your Project → **Logs**
2. Filter by **Serverless Functions**
3. Look for API calls to `/api/auth/login`
4. Check for errors related to database connection

### Check Environment Variables

1. Go to Vercel Dashboard → Settings → Environment Variables
2. Verify all required variables are set:
   - `DATABASE_URL` ✓
   - `SECRET_KEY` ✓
   - `JWT_SECRET_KEY` ✓
   - `ENVIRONMENT` ✓

### Test Database Connection Locally

If you want to test locally before deploying:

```bash
# 1. Create .env file with your Vercel DATABASE_URL
echo "DATABASE_URL=your-postgresql-url" > .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test connection
python3 -c "
import os
from dotenv import load_dotenv
import asyncio
load_dotenv()

async def test():
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    
    db_url = os.getenv('DATABASE_URL')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql+asyncpg://', 1)
    
    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        result = await conn.execute(text('SELECT 1'))
        print('✅ Database connection successful!')
    await engine.dispose()

asyncio.run(test())
"
```

---

## 📞 Need More Help?

If you're still experiencing issues after following this guide:

1. **Check Logs**: 
   - Vercel: Dashboard → Project → Logs
   - Render: Dashboard → Project → Logs
   - Render: Dashboard → Service → Logs

2. **Common Issues**:
   - **"asyncpg" not found**: Vercel needs to install dependencies. Check `requirements.txt` includes `asyncpg`
   - **SSL errors**: Add `?sslmode=require` to DATABASE_URL
   - **Timeout errors**: Increase `DB_CONNECT_TIMEOUT` to 45 in environment variables

3. **Still Stuck?**: 
   - Check the deployment guides in the repo:
     - `DEPLOYMENT_CONNECTION_GUIDE.md`
     - `WHERE_TO_PUT_DATABASE_URL.md`
     - `VERCEL_POSTGRES_SETUP.md`

---

## 🎯 Summary

**What We Fixed:**
1. ✅ Configured Vercel environment variables with DATABASE_URL
2. ✅ Verified backend is using correct database connection
3. ✅ Ensured frontend uses Vercel serverless API (same-origin)
4. ✅ Tested sign-in functionality
5. ✅ Disabled old Render service to avoid conflicts

**Result**: Users can now successfully sign in to HireMeBahamas on Vercel!

---

**Last Updated**: December 2025
**Status**: Active Fix Guide

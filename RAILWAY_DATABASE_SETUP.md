# 🗄️ Railway Database Setup Guide

This guide provides step-by-step instructions for adding and configuring the database connection in Railway for the HireMeBahamas application.

## 📋 Why You Need PostgreSQL

**CRITICAL**: SQLite is NOT suitable for production deployment in Railway because:
- ❌ Data is lost on every deployment or restart
- ❌ User accounts and all content will disappear
- ❌ No support for concurrent access

**PostgreSQL provides**:
- ✅ Persistent data storage
- ✅ Data survives deployments and restarts
- ✅ Scalable and production-ready

## 💰 Cost Optimization: Using Private Network

**IMPORTANT**: Railway provides two database connection options:
- **DATABASE_PUBLIC_URL** (uses `RAILWAY_TCP_PROXY_DOMAIN`) - **Incurs egress fees** ❌
- **DATABASE_PRIVATE_URL** (uses `RAILWAY_PRIVATE_DOMAIN`) - **No egress fees** ✅

Our application is configured to automatically prefer `DATABASE_PRIVATE_URL` over `DATABASE_URL` to minimize costs by using Railway's internal private network instead of the public TCP proxy.

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Access Railway Dashboard

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Log in with your GitHub account
3. Open your **HireMeBahamas** project

### Step 2: Add PostgreSQL Database

1. Click the **"+ New"** button (top right corner of your project)
2. Select **"Database"** from the dropdown
3. Click **"Add PostgreSQL"**
4. Wait 1-2 minutes for the database to provision

### Step 3: Verify Database Connection Variables

Railway automatically creates database connection variables when you add PostgreSQL to your project.

1. Click on your **Backend service** (not the PostgreSQL service)
2. Go to the **"Variables"** tab
3. Look for `DATABASE_PRIVATE_URL` or `DATABASE_URL` in the list

**Preferred setup** (uses private network, no egress fees):
```
DATABASE_PRIVATE_URL = postgresql://postgres:abc123xyz@postgres.railway.internal:5432/railway
```

**Fallback** (uses public proxy, incurs egress fees if DATABASE_PRIVATE_URL not available):
```
DATABASE_URL = postgresql://postgres:abc123xyz@containers-us-west-1.railway.app:5432/railway
```

The application will automatically use `DATABASE_PRIVATE_URL` if available, otherwise it falls back to `DATABASE_URL`.

### Step 4: Add Required Environment Variables

While in the Variables tab, add these additional variables:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `SECRET_KEY` | `<generate-random-key>` | Flask secret key |
| `JWT_SECRET_KEY` | `<generate-random-key>` | JWT signing key |
| `ENVIRONMENT` | `production` | Enables PostgreSQL mode |

**Generate secure keys with:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Redeploy Your Application

1. Go to the **"Deployments"** tab
2. Click the **⋮** menu on the latest deployment
3. Select **"Redeploy"**
4. Wait for deployment to complete (2-3 minutes)

### Step 6: Verify Success

Check the deployment logs for these messages:
```
🗄️ Database Mode: PostgreSQL (Production)
✅ PostgreSQL URL detected: postgresql://...
✅ Database tables created successfully!
🚀 Starting HireMeBahamas backend...
```

---

## 📖 Detailed Setup Instructions

### Option 1: Adding PostgreSQL Through Railway UI

#### 1. Create PostgreSQL Service

1. **Navigate to your project** in [Railway Dashboard](https://railway.app/dashboard)
2. **Click "+ New"** in the top right corner
3. **Select "Database"** → **"PostgreSQL"**
4. Railway will create a new PostgreSQL instance

#### 2. Connect PostgreSQL to Your Backend

Railway automatically shares the `DATABASE_URL` variable between services in the same project. If it's not appearing:

1. Click on the **PostgreSQL service**
2. Go to **"Variables"** tab
3. Copy the **"DATABASE_URL"** value
4. Click on your **Backend service**
5. Go to **"Variables"** → **"+ New Variable"**
6. Add:
   - **Name**: `DATABASE_URL`
   - **Value**: Paste the PostgreSQL URL

#### 3. Verify Variable is Available

Your backend service should now have:
```
DATABASE_URL=postgresql://postgres:password@host:5432/railway
```

### Option 2: Manual DATABASE_URL Configuration

If you're using an external PostgreSQL provider (e.g., Supabase, Neon, ElephantSQL):

#### 1. Get Your PostgreSQL Connection String

Your provider will give you a connection string like:
```
postgresql://username:password@hostname:5432/database_name
```

#### 2. Add to Railway

1. Go to your **Backend service** in Railway
2. Click **"Variables"** tab
3. Click **"+ New Variable"**
4. Add:
   - **Name**: `DATABASE_URL`
   - **Value**: Your PostgreSQL connection string

**Example:**
```
DATABASE_URL=postgresql://myuser:mypassword@db.supabase.co:5432/mydb
```

---

## ⚙️ Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Flask session secret | `your-secure-random-key-here` |
| `JWT_SECRET_KEY` | JWT token signing key | `another-secure-random-key` |
| `ENVIRONMENT` | Set to "production" | `production` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port (auto-set by Railway) | `8080` |
| `TOKEN_EXPIRATION_DAYS` | JWT token expiration | `7` |
| `FRONTEND_URL` | Frontend URL for CORS | `https://hiremebahamas.vercel.app` |

---

## 🔧 Troubleshooting

### "Database not connecting" in Railway Data Tab

**Cause**: Railway's web interface cannot establish a connection to the PostgreSQL database container.

**Symptoms**:
- Railway Dashboard Data tab shows: "Database Connection - Attempting to connect to the database... Database not connecting :/"
- The message "This service has all the necessary variables that this UI uses to connect to the database" appears

**Solution**:
1. **Wait 30-60 seconds** - This is the most common fix. The database container may be:
   - Starting up after inactivity (cold start)
   - Recovering from a restart
   - Transitioning between Railway infrastructure

2. **Refresh the Railway Dashboard** - After waiting, click the refresh button or reload the page

3. **Check PostgreSQL Service Status**:
   - Look at the PostgreSQL service card in your project
   - Status should show "Active" (green indicator)
   - If showing "Deploying", "Starting", or "Sleeping", wait for it to complete

4. **Use the Database Wake-Up Endpoint** (Recommended):
   - Visit `https://your-app.railway.app/api/database/wakeup`
   - This endpoint performs multiple connection attempts to wake up the database
   - Wait for a successful response, then refresh Railway's Data tab
   - Example response when successful:
     ```json
     {
       "success": true,
       "message": "Database is awake and accepting connections...",
       "attempts": 1
     }
     ```

5. **Verify Database is Healthy via API**:
   - Visit `https://your-app.railway.app/api/health`
   - If this returns `{"database": "connected"}`, the database is working
   - The issue is only with Railway's UI, not your application

6. **Restart PostgreSQL Service** (if still not working):
   - Click on your PostgreSQL service in Railway
   - Click the **⋮** menu → **Restart**
   - Wait 1-2 minutes for restart to complete

7. **Check Railway Status Page**:
   - Visit [Railway Status](https://status.railway.app)
   - Look for any ongoing incidents affecting database connectivity

**Note**: This error only affects Railway's Data tab UI. Your application handles database connections independently and includes automatic retry logic for transient connection issues.

### "Unable to connect to the database via SSH" Error

**Cause**: The PostgreSQL database container is starting up or transitioning

**Symptoms**:
- Railway Dashboard shows: "Unable to connect to the database via SSH"
- Message: "The database container is starting up or transitioning"

**Solution**:
1. **Wait 30-60 seconds** - This is normal during:
   - Cold starts (first access after inactivity)
   - Database restarts
   - Railway infrastructure updates
   - Container migrations

2. **Refresh the page** after waiting

3. **Check database status**:
   - In Railway dashboard, verify PostgreSQL shows "Active"
   - If it shows "Deploying" or "Starting", wait for it to complete

4. **Access via API instead**:
   - The application handles container transitions automatically
   - Users can continue using the app normally
   - API endpoints at `/api/health` and `/api/database/recovery-status` show current status

5. **If issue persists**:
   - Try restarting the PostgreSQL service in Railway
   - Check Railway status page for any ongoing incidents

**Note**: This error only affects direct database access from Railway's Data tab. The application itself handles container transitions gracefully and will retry connections automatically.

### DATABASE_URL Not Appearing

**Cause**: PostgreSQL service not linked to backend

**Solution**:
1. Delete the PostgreSQL service
2. Click **"+ New"** → **"Database"** → **"PostgreSQL"** again
3. Ensure both services are in the same project
4. Check the Variables tab after 1-2 minutes

### "Connection Refused" Error

**Cause**: PostgreSQL service not running or wrong URL

**Solution**:
1. Verify PostgreSQL service status (should show "Active")
2. Copy DATABASE_URL directly from PostgreSQL service
3. Paste into backend service variables manually

### "Database Does Not Exist" Error

**Cause**: Database was deleted or not created

**Solution**:
1. Check PostgreSQL service is running
2. Railway auto-creates the database named `railway`
3. If using external provider, create the database first

### Users Disappearing After Restart

**Cause**: App still using SQLite instead of PostgreSQL

**Solution**:
1. Verify `ENVIRONMENT=production` is set
2. Verify `DATABASE_URL` is set and correct
3. Check logs for "Database Mode: PostgreSQL"
4. Redeploy the application

### Authentication Errors After Setting DATABASE_URL

**Cause**: Missing SECRET_KEY or JWT_SECRET_KEY

**Solution**:
1. Add `SECRET_KEY` to environment variables
2. Add `JWT_SECRET_KEY` to environment variables
3. Generate secure random values for both
4. Redeploy

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] PostgreSQL service is "Active" in Railway
- [ ] `DATABASE_URL` appears in backend Variables tab
- [ ] `ENVIRONMENT=production` is set
- [ ] `SECRET_KEY` and `JWT_SECRET_KEY` are set
- [ ] Deployment logs show "Database Mode: PostgreSQL"
- [ ] Health check at `/health` returns OK
- [ ] Users can register and login
- [ ] Data persists after restart

---

## 📊 Testing Data Persistence

### Test 1: Create Test User

1. Go to your deployed site
2. Register a new user
3. Note down email and password

### Test 2: Restart Backend

1. In Railway dashboard, click on backend service
2. Click **⋮** menu → **"Restart"**
3. Wait for restart to complete

### Test 3: Verify Data Persisted

1. Go back to your site
2. Login with the test user credentials
3. **If login succeeds** → PostgreSQL is working! ✅
4. **If login fails** → Check troubleshooting section above

---

## 🔗 Useful Links

- [Railway Dashboard](https://railway.app/dashboard)
- [Railway Documentation](https://docs.railway.app)
- [Railway PostgreSQL Guide](https://docs.railway.app/databases/postgresql)
- [PostgreSQL Setup Guide](./POSTGRESQL_SETUP.md) - More detailed PostgreSQL configuration
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Complete deployment instructions

---

## 📝 Quick Reference Commands

### Generate Secure Keys
```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY  
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Test Database Connection Locally
```bash
# Set your DATABASE_URL
export DATABASE_URL="postgresql://user:pass@host:5432/db"

# Test connection
python3 -c "
import os
from sqlalchemy import create_engine
engine = create_engine(os.environ['DATABASE_URL'])
conn = engine.connect()
print('✅ Connected to PostgreSQL!')
conn.close()
"
```

### Check Database Mode in Application
```bash
curl https://your-app.railway.app/health
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "mode": "postgresql"
}
```

---

## 🎉 Success!

Once configured, your HireMeBahamas application will:
- ✅ Store all user data persistently
- ✅ Survive deployments and restarts
- ✅ Scale with your user base
- ✅ Provide reliable production service

---

**Need more help?** Check the [POSTGRESQL_SETUP.md](./POSTGRESQL_SETUP.md) for advanced configuration options.

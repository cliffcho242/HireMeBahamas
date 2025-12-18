# 🚀 Migrating from Render to Vercel/Render

## ⚠️ Are You Currently on Render?

If your HireMeBahamas application is currently deployed on Render, follow this guide to migrate to a more cost-effective and performant platform.

**Why Migrate?**
- 💰 **Save Money**: $0-7/month vs $25-50/month on Render
- ⚡ **Better Performance**: <200ms response time vs 2-5 minute cold starts
- 🚀 **Zero Downtime**: No cold starts or 502 errors
- 🌍 **Global CDN**: Faster for users worldwide

---

## 📋 Migration Checklist

Follow these steps in order:

### ✅ Step 1: Follow the Migration Documentation

We have comprehensive guides for your migration path:

**Option A: Migrate to Vercel (Recommended - $0/month)**
- 📖 Read: [`RENDER_TO_VERCEL_MIGRATION.md`](./RENDER_TO_VERCEL_MIGRATION.md)
- Best for: Full-stack deployment with frontend + serverless backend
- Cost: Free tier covers most use cases

**Option B: Migrate to Render (Alternative - $5-7/month)**
- 📖 Read: [`RENDER_TO_RAILWAY_MIGRATION.md`](./RENDER_TO_RAILWAY_MIGRATION.md)
- Best for: Traditional backend deployment with PostgreSQL
- Cost: $5 for backend + $5 for PostgreSQL (starter plan)

### ✅ Step 2: Backup Your Database

**CRITICAL**: Always backup your database before migration!

#### Option 2A: Manual Backup with pg_dump

```bash
# 1. Get your Render database URL
# Go to: https://dashboard.render.com → Your PostgreSQL Database → Connections
# Copy the "External Database URL"

# 2. Set environment variable (to avoid exposing password in shell history)
export RENDER_DB_URL="postgresql://user:password@dpg-xxxxx.render.com:5432/database"

# 3. Create backup file
pg_dump "$RENDER_DB_URL" > hiremebahamas_render_backup_$(date +%Y%m%d).sql

# 4. Verify backup was created
ls -lh hiremebahamas_render_backup_*.sql

# 5. Keep this file safe! You'll use it to restore on the new platform
```

#### Option 2B: Use Our Automated Backup Script

```bash
# Download and run the backup script
python3 scripts/backup_database.py --source render --output ./backups/

# This will:
# ✅ Prompt you for your Render DATABASE_URL
# ✅ Create a timestamped backup file
# ✅ Verify the backup integrity
# ✅ Show backup statistics (tables, rows, size)
```

**Important Notes:**
- The backup file contains ALL your data: users, posts, jobs, messages
- Store the backup file securely (it contains sensitive data)
- Keep the backup until you verify the migration was successful
- Test the backup by restoring to a test database if possible

### ✅ Step 3: Deploy to Vercel or Render

Choose your target platform and follow the deployment guide:

#### Deploy to Vercel

**Quick Steps:**
1. **Push your code to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Prepare for Vercel migration"
   git push origin main
   ```

2. **Import to Vercel**
   - Go to https://vercel.com/new
   - Click "Import Git Repository"
   - Select your GitHub repository
   - Click "Import"

3. **Configure Environment Variables**
   - Click "Environment Variables" during setup
   - Add these required variables:
   ```bash
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   SECRET_KEY=your-secret-key-32-chars
   JWT_SECRET_KEY=your-jwt-secret-32-chars
   ENVIRONMENT=production
   FRONTEND_URL=https://your-app.vercel.app
   ```

4. **Deploy!**
   - Click "Deploy"
   - Wait 2-3 minutes for build to complete
   - Your app will be live at `https://your-app.vercel.app`

📖 **Complete Vercel Guide**: [`VERCEL_DEPLOYMENT_GUIDE.md`](./VERCEL_DEPLOYMENT_GUIDE.md)

#### Deploy to Render

**Quick Steps:**
1. **Create Render Account**
   - Go to https://render.app
   - Sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Select your HireMeBahamas repository

3. **Add PostgreSQL Database**
   - Click "+ New" → "Database" → "Add PostgreSQL"
   - Render will automatically set `DATABASE_URL`

4. **Configure Environment Variables**
   - Go to your backend service
   - Click "Variables" tab
   - Add these variables:
   ```bash
   SECRET_KEY=your-secret-key-32-chars
   JWT_SECRET_KEY=your-jwt-secret-32-chars
   ENVIRONMENT=production
   PORT=8000
   ```

5. **Deploy!**
   - Render will automatically deploy
   - Get your backend URL from the "Settings" tab
   - Note: `https://your-app.up.render.app`

📖 **Complete Render Guide**: [`RAILWAY_DATABASE_SETUP.md`](./RAILWAY_DATABASE_SETUP.md)

### ✅ Step 4: Restore Your Database Backup

After deploying to your new platform, restore your data:

#### Restore to Vercel Postgres

```bash
# 1. Get your Vercel Postgres connection string
# Go to: Vercel Dashboard → Your Project → Storage → Your Database
# Copy the connection string (starts with postgresql://)

# 2. Set environment variable
export VERCEL_DB_URL="postgresql://user:password@ep-xxxxx.vercel.com:5432/verceldb"

# 3. Restore backup
psql "$VERCEL_DB_URL" < hiremebahamas_render_backup_YYYYMMDD.sql

# 4. Verify restoration
psql "$VERCEL_DB_URL" -c "SELECT COUNT(*) FROM users;"
psql "$VERCEL_DB_URL" -c "SELECT COUNT(*) FROM posts;"
```

#### Restore to Render Postgres

```bash
# 1. Get your Render Postgres connection string
# Go to: Render Dashboard → Your PostgreSQL Service → Connect
# Copy the connection string

# 2. Set environment variable
export RAILWAY_DB_URL="postgresql://user:password@containers.render.app:5432/render"

# 3. Restore backup
psql "$RAILWAY_DB_URL" < hiremebahamas_render_backup_YYYYMMDD.sql

# 4. Verify restoration
psql "$RAILWAY_DB_URL" -c "SELECT COUNT(*) FROM users;"
psql "$RAILWAY_DB_URL" -c "SELECT COUNT(*) FROM posts;"
```

### ✅ Step 5: Update Frontend Environment Variables

After your backend is deployed, update your frontend to point to the new backend URL.

#### Option A: Using Vercel Serverless Backend (Same Domain)

If you deployed the backend to Vercel serverless functions:

```bash
# In Vercel Dashboard → Your Project → Settings → Environment Variables
# NO NEED to set VITE_API_URL - it auto-detects!
# The frontend will automatically use /api/* on the same domain
```

#### Option B: Using Separate Backend (Render/Render)

If you deployed the backend to Render or another platform:

```bash
# In Vercel Dashboard → Your Project → Settings → Environment Variables
# Add this variable:

VITE_API_URL=https://your-backend.up.render.app

# Or if still using Render temporarily:
VITE_API_URL=https://your-app.onrender.com
```

**To Update:**
1. Go to https://vercel.com/dashboard
2. Select your project
3. Click "Settings" → "Environment Variables"
4. Find `VITE_API_URL` or add it if missing
5. Set the value to your backend URL
6. Click "Save"
7. Redeploy: Go to "Deployments" → Click "⋯" → "Redeploy"

#### Remove VITE_API_URL (For Vercel Serverless Only)

If you're using Vercel for both frontend AND backend:

1. Go to Vercel Dashboard → Settings → Environment Variables
2. Find `VITE_API_URL`
3. Click "⋯" → "Remove"
4. Redeploy

This allows the frontend to use the serverless backend on the same domain automatically.

### ✅ Step 6: Test Your Migration

After everything is deployed, test that your application works:

#### Automated Testing

```bash
# Test your deployed application
python3 scripts/test_deployment.py --url https://your-app.vercel.app

# Or test specific endpoints
python3 scripts/test_api_endpoints.py --url https://your-app.vercel.app
```

#### Manual Testing Checklist

Visit your new deployment URL and verify:

- [ ] ✅ Homepage loads correctly
- [ ] ✅ Sign in with existing account works
- [ ] ✅ Create new post works
- [ ] ✅ View posts from before migration
- [ ] ✅ Upload profile picture works
- [ ] ✅ Send/receive messages works
- [ ] ✅ Job postings are visible
- [ ] ✅ No console errors (Press F12 → Console tab)

### ✅ Step 7: Update Domain (Optional)

If you have a custom domain (e.g., hiremebahamas.com):

#### For Vercel:

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Click "Add" and enter your domain
3. Follow Vercel's instructions to update DNS records
4. Wait 5-10 minutes for DNS propagation
5. Verify: Visit your custom domain

#### For Render (Backend Only):

1. Go to Render Dashboard → Your Service → Settings
2. Click "Generate Domain" or "Custom Domain"
3. Add your domain (e.g., api.hiremebahamas.com)
4. Update DNS records as instructed
5. Update `VITE_API_URL` in Vercel to use your custom domain

### ✅ Step 8: Monitor for 24-48 Hours

After migration, monitor your application:

**Vercel Monitoring:**
- Go to Vercel Dashboard → Your Project → Analytics
- Check for errors in the Logs tab
- Monitor response times

**Render Monitoring:**
- Go to Render Dashboard → Your Service → Metrics
- Check CPU and memory usage
- Monitor database connections

**What to Watch For:**
- ✅ Response times < 500ms (should be much faster than Render)
- ✅ No 500 errors in logs
- ✅ Database connections stable
- ✅ All features working as expected

### ✅ Step 9: Delete Render Services (After Verification)

**ONLY after 1-2 weeks of successful operation on the new platform:**

1. Go to https://dashboard.render.com
2. Stop each service (don't delete yet):
   - Click your Web Service → Settings → "Suspend Service"
   - Wait 24 hours to ensure nothing breaks
3. If everything still works, delete services:
   - Web Service: Settings → "Delete Service"
   - Background Workers: Settings → "Delete Service"
   - Cron Jobs: Settings → "Delete Service"
4. Finally, delete PostgreSQL database (keep backup file!):
   - PostgreSQL Service → Settings → "Delete Database"
5. Verify billing: https://dashboard.render.com/billing
   - Should show $0.00/month

**⚠️ WARNING**: Deleting services is permanent. Make sure you have:
- ✅ Database backup file saved securely
- ✅ All data restored on new platform
- ✅ Application working perfectly for 1-2 weeks
- ✅ Users report no issues

---

## 🚨 Troubleshooting

### "Database connection failed"

**Problem**: Your app can't connect to the database after migration.

**Solution**:
1. Verify `DATABASE_URL` is set correctly in Vercel/Render
2. Check that `?sslmode=require` is in the DATABASE_URL
3. Test connection:
   ```bash
   psql "$DATABASE_URL" -c "SELECT 1;"
   ```
4. If using Render, try the `DATABASE_PRIVATE_URL` instead

### "Frontend shows blank page"

**Problem**: Frontend loads but shows nothing.

**Solution**:
1. Open browser console (F12)
2. Check for API errors
3. Verify `VITE_API_URL` is set correctly (or removed for Vercel serverless)
4. Check Network tab for failed requests
5. Redeploy frontend after changing environment variables

### "Sign in doesn't work"

**Problem**: Users can't log in after migration.

**Solution**:
1. Verify database backup was restored correctly:
   ```bash
   psql "$DATABASE_URL" -c "SELECT email FROM users LIMIT 5;"
   ```
2. Check that `SECRET_KEY` and `JWT_SECRET_KEY` match your old values
   - If you changed these, users need to re-authenticate
3. Clear browser cookies and try again
4. Check Vercel/Render logs for authentication errors

### "Some data is missing"

**Problem**: Posts, users, or other data is missing after migration.

**Solution**:
1. Check your backup file size (should be > 1KB)
2. Restore the backup again:
   ```bash
   psql "$DATABASE_URL" < hiremebahamas_render_backup_YYYYMMDD.sql
   ```
3. Verify table counts match:
   ```bash
   # On new database
   psql "$NEW_DB_URL" -c "SELECT COUNT(*) FROM posts;"
   
   # Compare to old database (if still accessible)
   psql "$RENDER_DB_URL" -c "SELECT COUNT(*) FROM posts;"
   ```

### "502 Bad Gateway on new platform"

**Problem**: You still see 502 errors after migrating.

**Solution**:
- **On Vercel**: This shouldn't happen. Check:
  - Serverless function logs for errors
  - Database connection string is correct
  - Function timeout isn't being exceeded (max 30s)
- **On Render**: Check:
  - Service health in dashboard
  - Memory/CPU usage (upgrade plan if needed)
  - Database connection pool settings

---

## 📚 Additional Resources

### Documentation
- [`RENDER_TO_VERCEL_MIGRATION.md`](./RENDER_TO_VERCEL_MIGRATION.md) - Detailed Vercel migration guide
- [`RENDER_TO_RAILWAY_MIGRATION.md`](./RENDER_TO_RAILWAY_MIGRATION.md) - Detailed Render migration guide
- [`VERCEL_DEPLOYMENT_GUIDE.md`](./VERCEL_DEPLOYMENT_GUIDE.md) - Complete Vercel deployment guide
- [`RAILWAY_DATABASE_SETUP.md`](./RAILWAY_DATABASE_SETUP.md) - Render database configuration
- [`DEPLOYMENT_CONNECTION_GUIDE.md`](./DEPLOYMENT_CONNECTION_GUIDE.md) - All deployment platforms

### Support
- 🐛 Report issues: [GitHub Issues](https://github.com/cliffcho242/HireMeBahamas/issues)
- 💬 Community: [GitHub Discussions](https://github.com/cliffcho242/HireMeBahamas/discussions)
- 📖 Wiki: [GitHub Wiki](https://github.com/cliffcho242/HireMeBahamas/wiki)

---

## ✅ Migration Complete!

After following all steps, you should have:
- ✅ Application deployed to Vercel or Render
- ✅ All data migrated from Render
- ✅ Frontend pointing to new backend
- ✅ Custom domain configured (if applicable)
- ✅ Old Render services deleted (after verification period)
- ✅ Monthly costs reduced significantly

**Estimated Time**: 30-60 minutes  
**Cost Savings**: $20-45/month  
**Performance Improvement**: 10-100x faster response times

**Last Updated**: December 15, 2024  
**Status**: Production Ready

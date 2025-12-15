# ⚡ Quick Start: Migrating from Render

**Time Required**: 30-60 minutes  
**Cost Savings**: $20-45/month  
**Difficulty**: Easy (step-by-step instructions provided)

---

## 📋 Before You Start

Make sure you have:
- [ ] Access to your Render dashboard
- [ ] GitHub account with this repository
- [ ] PostgreSQL client installed (for backups)
  ```bash
  # Ubuntu/Debian
  sudo apt-get install postgresql-client
  
  # macOS
  brew install postgresql
  
  # Windows
  # Download from: https://www.postgresql.org/download/windows/
  ```

---

## 🚀 Migration Steps (30-60 minutes)

### Step 1: Read the Documentation (5 minutes)

Choose your migration path:

**Option A: Migrate to Vercel** (Recommended - $0/month)
- 📖 Read: [`MIGRATE_FROM_RENDER.md`](./MIGRATE_FROM_RENDER.md)
- 📖 Detailed guide: [`RENDER_TO_VERCEL_MIGRATION.md`](./RENDER_TO_VERCEL_MIGRATION.md)

**Option B: Migrate to Railway** ($5-7/month)
- 📖 Read: [`MIGRATE_FROM_RENDER.md`](./MIGRATE_FROM_RENDER.md)
- 📖 Detailed guide: [`RENDER_TO_RAILWAY_MIGRATION.md`](./RENDER_TO_RAILWAY_MIGRATION.md)

### Step 2: Backup Your Database (10 minutes)

```bash
# Automated backup (recommended)
python3 scripts/backup_database.py --source render --output ./backups/

# OR Manual backup
export RENDER_DB_URL="postgresql://user:pass@host.render.com:5432/database"
pg_dump "$RENDER_DB_URL" > backup_$(date +%Y%m%d).sql
```

**✅ Verify backup was created:**
```bash
ls -lh backups/  # or ls -lh backup_*.sql
```

### Step 3: Deploy to New Platform (15-20 minutes)

#### For Vercel:

```bash
# 1. Push code to GitHub (if needed)
git push origin main

# 2. Go to https://vercel.com/new
# 3. Import your GitHub repository
# 4. Add environment variables:
#    - DATABASE_URL (from your new database)
#    - SECRET_KEY (generate new: python3 -c "import secrets; print(secrets.token_urlsafe(32))")
#    - JWT_SECRET_KEY (generate new: python3 -c "import secrets; print(secrets.token_urlsafe(32))")
#    - ENVIRONMENT=production

# 5. Click "Deploy" and wait 2-3 minutes
```

#### For Railway:

```bash
# 1. Go to https://railway.app
# 2. Create new project from GitHub repo
# 3. Add PostgreSQL database (+ New → Database → PostgreSQL)
# 4. Add environment variables:
#    - SECRET_KEY
#    - JWT_SECRET_KEY
#    - ENVIRONMENT=production
# 5. Railway will auto-deploy
```

### Step 4: Restore Database (10 minutes)

```bash
# Get your new database URL from Vercel/Railway dashboard

# For Vercel
export NEW_DB_URL="postgresql://user:pass@ep-xxxxx.vercel.com:5432/verceldb"

# For Railway
export NEW_DB_URL="postgresql://user:pass@containers.railway.app:5432/railway"

# Restore backup
psql "$NEW_DB_URL" < backups/hiremebahamas_render_backup_*.sql

# Verify restoration
psql "$NEW_DB_URL" -c "SELECT COUNT(*) FROM users;"
psql "$NEW_DB_URL" -c "SELECT COUNT(*) FROM posts;"
```

### Step 5: Update Frontend Config (5 minutes)

#### For Vercel Serverless (Same Domain):

```bash
# In Vercel Dashboard → Settings → Environment Variables
# REMOVE or leave VITE_API_URL unset
# Frontend will auto-detect and use /api/* on same domain
```

#### For Railway Backend (Separate Domain):

```bash
# In Vercel Dashboard → Settings → Environment Variables
# Set:
VITE_API_URL=https://your-backend.up.railway.app

# Then redeploy frontend:
# Vercel Dashboard → Deployments → Latest → Redeploy
```

### Step 6: Test Migration (5 minutes)

```bash
# Automated testing
python3 scripts/test_deployment.py --url https://your-app.vercel.app

# OR Manual testing - visit your site and verify:
# ✅ Homepage loads
# ✅ Sign in works
# ✅ Posts are visible
# ✅ Can create new post
# ✅ No console errors (F12)
```

### Step 7: Monitor for 24-48 Hours

Watch for:
- ✅ No errors in logs (Vercel/Railway dashboard)
- ✅ Fast response times (<500ms)
- ✅ All features working
- ✅ No user complaints

### Step 8: Delete Render Services (After 1-2 weeks)

**ONLY after everything works perfectly:**

```bash
# 1. Go to https://dashboard.render.com
# 2. Suspend services first (don't delete yet)
# 3. Wait 24 hours
# 4. If everything still works, delete:
#    - Web Service
#    - Background Workers
#    - Cron Jobs
#    - PostgreSQL Database (LAST - keep backup!)
# 5. Verify billing shows $0.00/month
```

---

## 🆘 Common Issues

### "Database connection failed"

**Fix:**
```bash
# Check DATABASE_URL includes ?sslmode=require
# Correct: postgresql://user:pass@host:5432/db?sslmode=require
# Wrong:   postgresql://user:pass@host:5432/db

# Test connection
psql "$DATABASE_URL" -c "SELECT 1;"
```

### "Frontend shows blank page"

**Fix:**
```bash
# 1. Open browser console (F12)
# 2. Check for API errors
# 3. Verify VITE_API_URL is correct (or removed for Vercel serverless)
# 4. Redeploy frontend after changing env vars
```

### "Sign in doesn't work"

**Fix:**
```bash
# 1. Verify database was restored correctly
psql "$DATABASE_URL" -c "SELECT email FROM users LIMIT 5;"

# 2. Check SECRET_KEY and JWT_SECRET_KEY are set
# 3. Clear browser cookies and try again
```

### "502 Bad Gateway"

**Fix:**
- **Vercel**: Check serverless function logs for errors
- **Railway**: Check service health and memory usage
- Verify DATABASE_URL is correct
- Check function timeout settings

---

## 📚 Full Documentation

- 📖 **[Complete Migration Guide](./MIGRATE_FROM_RENDER.md)** - Comprehensive step-by-step guide
- 📖 **[Render to Vercel](./RENDER_TO_VERCEL_MIGRATION.md)** - Detailed Vercel migration
- 📖 **[Render to Railway](./RENDER_TO_RAILWAY_MIGRATION.md)** - Detailed Railway migration
- 🔧 **[Database Backup Script](./scripts/backup_database.py)** - Automated backup tool
- ✅ **[Deployment Testing](./scripts/test_deployment.py)** - Verify migration success

---

## 💡 Tips

1. **Don't delete Render immediately** - Wait 1-2 weeks to ensure stability
2. **Keep your database backup** - Store it securely until migration is verified
3. **Test thoroughly** - Verify all features work before deleting Render
4. **Monitor logs** - Check Vercel/Railway logs daily for the first week
5. **Update bookmarks** - Point users to new URL if domain changed

---

## ✅ Success Checklist

After migration, you should have:
- [ ] ✅ Application deployed to Vercel or Railway
- [ ] ✅ All data restored from backup
- [ ] ✅ Frontend pointing to correct backend
- [ ] ✅ Sign in working for existing users
- [ ] ✅ All posts and data visible
- [ ] ✅ No console errors (F12)
- [ ] ✅ Response time < 500ms
- [ ] ✅ Monitored for 1-2 weeks
- [ ] ✅ Render services deleted
- [ ] ✅ Saving $20-45/month

---

**Last Updated**: December 15, 2024  
**Status**: Production Ready  
**Estimated Success Rate**: 95%+ (when following instructions)

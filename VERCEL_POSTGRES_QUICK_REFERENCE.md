# Vercel Postgres Quick Reference Card

## 🚀 Quick Setup (5 Minutes)

### 1. Create Database
```bash
# In Vercel Dashboard
1. Go to: https://vercel.com/dashboard → Your Project → Storage
2. Click "Create Database" → Select "Postgres"
3. Choose plan: Hobby (free) or Pro ($0.10/GB)
4. Select region: US East (recommended for Bahamas)
5. Copy POSTGRES_URL from dashboard
```

### 2. Set Environment Variable
```bash
# In Vercel Dashboard: Settings → Environment Variables
DATABASE_URL=postgresql://default:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require

# Or use Vercel CLI
vercel env add DATABASE_URL
```

### 3. Deploy
```bash
git push origin main
# Vercel auto-deploys with new database
```

---

## 🔄 Migration from Railway/Render

### One-Command Migration
```bash
# Set source and target URLs
export RAILWAY_DATABASE_URL="postgresql://user:pass@railway.app:5432/railway"
export VERCEL_POSTGRES_URL="postgresql://default:pass@ep-xxxxx.neon.tech:5432/verceldb"

# Run migration script
python scripts/migrate_railway_to_vercel.py

# Verify migration
python scripts/verify_vercel_postgres_migration.py
```

### Manual Migration (3 Steps)
```bash
# 1. Export from Railway/Render
pg_dump "$RAILWAY_DATABASE_URL" \
  --no-owner --no-acl --format=custom \
  --file=backup.dump

# 2. Import to Vercel Postgres
pg_restore \
  --no-owner --no-acl \
  --dbname="$VERCEL_POSTGRES_URL" \
  backup.dump

# 3. Update DATABASE_URL in Vercel Dashboard
```

---

## 📝 Environment Variables

### Required
```bash
DATABASE_URL=postgresql://default:PASSWORD@ep-xxxxx.neon.tech:5432/verceldb?sslmode=require
```

### Recommended (Optimal Performance)
```bash
DB_POOL_SIZE=2              # Small pool for serverless
DB_MAX_OVERFLOW=3           # Burst capacity
DB_POOL_RECYCLE=120         # Recycle every 2 minutes
DB_SSL_MODE=require         # Enforce SSL
DB_FORCE_TLS_1_3=true       # Use TLS 1.3 only
DB_CONNECT_TIMEOUT=45       # Connection timeout (seconds)
```

---

## 🔍 Connection Strings

### Vercel Provides Multiple URLs

| Variable | Use Case |
|----------|----------|
| `POSTGRES_URL` | **Primary** - Connection pooling (use this!) |
| `POSTGRES_URL_NON_POOLING` | Migrations, pg_dump/restore |
| `POSTGRES_PRISMA_URL` | Prisma ORM |
| `POSTGRES_URL_NO_SSL` | ❌ Don't use in production |

### Format Conversion
```bash
# Vercel gives you:
postgres://default:pass@host:5432/db

# Application expects:
postgresql://default:pass@host:5432/db?sslmode=require
#         ^^^ (add 'ql' and '?sslmode=require')
```

---

## ✅ Verification Checklist

### After Migration
```bash
# 1. Test connection
psql "$DATABASE_URL" -c "SELECT 1"

# 2. Check row counts
psql "$DATABASE_URL" -c "
  SELECT 'users' as table, COUNT(*) FROM users
  UNION ALL SELECT 'posts', COUNT(*) FROM posts
"

# 3. Test health endpoint
curl https://your-app.vercel.app/health

# 4. Run verification script
python scripts/verify_vercel_postgres_migration.py
```

---

## 🐛 Common Issues

### "Connection timeout"
```bash
# Increase timeout
DB_CONNECT_TIMEOUT=45
```

### "SSL error: unexpected eof"
```bash
# Already fixed in backend/app/database.py!
# But if you still see it:
DB_POOL_RECYCLE=120
DB_FORCE_TLS_1_3=true
```

### "Database not found"
```bash
# Check URL format - must end with database name
postgresql://.../.../verceldb  # ✓ correct
postgresql://.../...           # ✗ missing database name
```

### "Permission denied"
```bash
# Use POSTGRES_URL (not POSTGRES_URL_NON_POOLING) for app
# NON_POOLING is only for migrations/dumps
```

---

## 💰 Cost Comparison

| Provider | Plan | Storage | Price |
|----------|------|---------|-------|
| **Vercel Postgres** | Hobby | 0.5 GB | **FREE** |
| **Vercel Postgres** | Pro | 1 GB | **$1/mo** |
| Railway | Shared | 1 GB | $5/mo |
| Render | Starter | 1 GB | $7/mo |

**Savings**: $7-20/month → $0-5/month

---

## 📚 Documentation Links

- 📖 [Complete Setup Guide](./VERCEL_POSTGRES_SETUP.md)
- 📖 [Migration Guide](./VERCEL_POSTGRES_MIGRATION_GUIDE.md)
- 📖 [Vercel Docs](https://vercel.com/docs/storage/vercel-postgres)
- 📖 [Neon Docs](https://neon.tech/docs/introduction)

---

## 🔥 Why Vercel Postgres?

✅ **Zero cold starts** - Database stays warm  
✅ **<50ms latency** - Edge network optimization  
✅ **Auto-scaling** - Serverless architecture  
✅ **Built-in pooling** - Connection management  
✅ **Free tier** - 0.5GB perfect for small apps  
✅ **Better integration** - Same platform as frontend  

---

## 🎯 Quick Commands

```bash
# Connect to database
psql "$DATABASE_URL"

# List tables
psql "$DATABASE_URL" -c "\dt"

# Check database size
psql "$DATABASE_URL" -c "
  SELECT pg_size_pretty(pg_database_size('verceldb'))
"

# Export backup
pg_dump "$DATABASE_URL" > backup.sql

# Import from backup
psql "$DATABASE_URL" < backup.sql

# Run migrations
python scripts/migrate_railway_to_vercel.py

# Verify setup
python scripts/verify_vercel_postgres_migration.py
```

---

*Last Updated: December 2025*
*Quick Reference Version: 1.0*

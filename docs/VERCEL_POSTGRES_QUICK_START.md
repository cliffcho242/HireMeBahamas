# Vercel Postgres Quick Start Guide

**5-Minute Setup** for Vercel Postgres (Neon) with HireMeBahamas.

---

## 📦 What You'll Get

- ✅ Serverless PostgreSQL database (powered by Neon)
- ✅ Free tier: 0.5 GB storage
- ✅ Automatic scaling and connection pooling
- ✅ Low latency via Vercel Edge Network
- ✅ Simple 5-step setup

---

## 🚀 5-Step Setup

### Step 1: Create Database (2 minutes)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your **HireMeBahamas** project
3. Click **Storage** tab → **Create Database**
4. Select **Postgres** → Choose plan:
   - **Hobby**: Free, 0.5 GB (perfect for development)
   - **Pro**: $0.10/GB (for production)
5. Select region: **US East (N. Virginia)** or **US East (Ohio)**
6. Click **Create**

### Step 2: Copy Connection String (30 seconds)

Once created, copy the connection string:

```
postgres://default:AbCdEf123@ep-cool-sound-12345.us-east-1.aws.neon.tech/verceldb?sslmode=require
```

⚠️ **Important**: Keep this secret! It contains your database password.

### Step 3: Add to Vercel Environment Variables (1 minute)

1. Go to **Settings → Environment Variables**
2. Add variable:
   - **Name**: `DATABASE_URL`
   - **Value**: Your connection string (replace `postgres://` with `postgresql://`)
   - **Environment**: Production, Preview, Development
3. Click **Save**

Example:
```
DATABASE_URL=postgresql://default:AbCdEf123@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require
```

### Step 4: Redeploy Application (1 minute)

1. Go to **Deployments** tab
2. Click most recent deployment → **"..."** menu → **Redeploy**
3. Wait for deployment to complete (~2 minutes)

### Step 5: Verify Connection (30 seconds)

Test your application:

```bash
# Test health endpoint
curl https://your-app.vercel.app/api/health

# Expected response:
# {"status": "healthy", "database": "connected"}
```

---

## ✅ You're Done!

Your Vercel Postgres database is now live and connected.

### Next Steps

- **Create tables**: Application auto-creates tables on first run
- **Test features**: Register user, create post, verify data persistence
- **Monitor usage**: Vercel Dashboard → Storage → Your Database → Insights

---

## 📖 Full Documentation

For detailed setup, migration, and troubleshooting:
- **[Complete Setup Guide](../VERCEL_POSTGRES_SETUP.md)**
- **[Migration from Render](../VERCEL_POSTGRES_MIGRATION.md)**

---

## 💡 Tips

### Keep Hobby Plan Free
- Keep database under 500 MB
- Use Vercel Cron Jobs to prevent hibernation
- Optimize queries to reduce compute time

### Upgrade to Pro
When you need:
- More than 0.5 GB storage
- Higher performance
- Database branches for preview deployments
- No hibernation

Cost: ~$1-5/month for small apps

---

## 🆘 Troubleshooting

### "Connection timeout"
- Verify connection string is correct
- Check `?sslmode=require` is at the end
- Increase timeout: `DB_CONNECT_TIMEOUT=45`

### "Database hibernated" (Hobby plan)
- Database wakes automatically (first request may be slow)
- Use Vercel Cron Jobs to keep warm
- Or upgrade to Pro plan

### "Too many connections"
- Use `POSTGRES_URL` with pooler (not `POSTGRES_URL_NON_POOLING`)
- Reduce pool size: `DB_POOL_SIZE=1`

---

## 📊 Connection String Format

```
postgresql://USER:PASSWORD@HOST:PORT/DATABASE?sslmode=require
```

Example:
```
postgresql://default:AbCdEf123@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require
```

Key components:
- `postgresql://` - Driver (use this, not `postgres://`)
- `default` - Username
- `AbCdEf123` - Password (keep secret!)
- `ep-cool-sound-12345.us-east-1.aws.neon.tech` - Host
- `5432` - Port
- `verceldb` - Database name
- `?sslmode=require` - SSL configuration

---

*Last Updated: December 2025*

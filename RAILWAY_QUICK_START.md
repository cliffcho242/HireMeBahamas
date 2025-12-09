# Railway Deployment Quick Start Guide

## Problem Solved

Railway was attempting to run PostgreSQL server as root, causing deployment failures with error:
```
"root" execution of the PostgreSQL server is not permitted.
```

**Root Cause**: Railway was using `docker-compose.yml` which includes a PostgreSQL server container.

**Solution**: Excluded `docker-compose.yml` from Railway deployment. Railway now uses Nixpacks and managed PostgreSQL.

## Quick Deployment Steps

### 1. In Railway Dashboard

#### A. Create PostgreSQL Database
1. Go to https://railway.app/dashboard
2. Select your project
3. Click "New" → "Database" → "Add PostgreSQL"
4. Railway creates managed database and auto-generates credentials

#### B. Deploy Backend Service
1. Click "New" → "GitHub Repo"
2. Select `cliffcho242/HireMeBahamas`
3. Select branch: `main`
4. Railway auto-detects:
   - `railway.json` → Uses Nixpacks builder
   - `nixpacks.toml` → Installs dependencies
   - `Procfile` → Sets start command

#### C. Connect Services
1. Go to Backend Service → Variables
2. Add connection to PostgreSQL:
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   ```
   Or Railway auto-connects services in same project

#### D. Deploy
1. Push code to GitHub
2. Railway auto-deploys
3. Check logs for successful connection

### 2. Verify Deployment

Check health endpoint:
```bash
curl https://your-app.railway.app/health
# Should return: {"status": "ok", ...}
```

Check Railway logs:
```
✅ Should see: "Connected to PostgreSQL"
✅ Should see: "Uvicorn running on http://0.0.0.0:8000"
❌ Should NOT see: "root execution not permitted"
```

## File Structure

### What Gets Deployed to Railway
```
✅ Python backend code (api/, backend/)
✅ requirements.txt
✅ nixpacks.toml
✅ railway.json
✅ Procfile
```

### What Gets Ignored (via .railwayignore)
```
❌ docker-compose.yml (PostgreSQL server - Railway provides this)
❌ Dockerfile (Railway uses Nixpacks)
❌ frontend/ (deployed separately to Vercel)
❌ admin_panel/
❌ node_modules/
```

## Architecture

```
Railway Project
├── Backend Service (Nixpacks)
│   ├── Builds from: nixpacks.toml
│   ├── Starts via: Procfile
│   └── Connects to → PostgreSQL
│
└── PostgreSQL Service (Managed)
    ├── Created in Railway dashboard
    ├── Auto-generates credentials
    └── Injects DATABASE_URL
```

## Environment Variables

Railway automatically provides:
```bash
# From Railway platform
PORT=8000  # Auto-set by Railway

# From PostgreSQL service
DATABASE_URL=postgresql://postgres:[REDACTED]@hostname:5432/railway
PGHOST=hostname.railway.internal
PGPORT=5432
PGUSER=postgres
PGPASSWORD=[REDACTED]
PGDATABASE=railway
```

Add manually (in Railway dashboard):
```bash
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
ENVIRONMENT=production
```

## Common Issues & Solutions

### Issue: "root execution not permitted"
**Solution**: Ensure `docker-compose.yml` is in `.railwayignore` ✅ (Fixed in this PR)

### Issue: "Failed to connect to database"
**Solutions**:
1. Verify PostgreSQL service is created in Railway
2. Check `DATABASE_URL` is set in backend service
3. Check services are in same project for auto-networking

### Issue: "Module not found"
**Solutions**:
1. Verify `requirements.txt` includes the module
2. Check Railway build logs for installation errors
3. Rebuild from Railway dashboard

### Issue: "Port already in use"
**Solution**: Remove hardcoded port, use Railway's `PORT` environment variable

## Local Development vs Railway

### Local (uses docker-compose.yml)
```bash
# Start all services including PostgreSQL
docker-compose up

# PostgreSQL runs in container
# Backend connects to local PostgreSQL
```

### Railway (uses managed services)
```bash
# Only backend code is deployed
# Railway provides PostgreSQL separately
# Backend connects via DATABASE_URL
```

## Next Steps

1. ✅ Push this branch to GitHub
2. ✅ Merge to main branch
3. ✅ Railway auto-deploys from main
4. ✅ Verify deployment in Railway dashboard
5. ✅ Test health endpoint
6. ✅ Test API endpoints

## Documentation

For detailed information, see:
- `RAILWAY_POSTGRES_FIX.md` - Complete technical documentation
- `RAILWAY_DEPLOYMENT_TROUBLESHOOTING.md` - Troubleshooting guide
- Railway Docs: https://docs.railway.app/

## Support

If deployment still fails:
1. Check Railway build logs
2. Check Railway runtime logs
3. Verify all environment variables are set
4. Contact Railway support with service details

# Railway PostgreSQL Setup Guide - Critical Information

## ⚠️ IMPORTANT: Do NOT Deploy PostgreSQL as a Container on Railway

**Railway provides managed PostgreSQL database services.** You should **NEVER** try to deploy PostgreSQL as a container/application on Railway.

### Common Error

If you see this error on Railway:
```
"root" execution of the PostgreSQL server is not permitted.
The server must be started under an unprivileged user ID to prevent
possible system security compromise.
```

This means you are trying to deploy PostgreSQL as a **container/application** instead of using Railway's **managed database service**.

## ✅ Correct Way: Use Railway's Managed PostgreSQL Service

### Step 1: Add PostgreSQL Database Service

1. Go to your [Railway Dashboard](https://railway.app/dashboard)
2. Open your **HireMeBahamas** project
3. Click the **"+ New"** button in the top right
4. Select **"Database"** from the dropdown
5. Choose **"Add PostgreSQL"**
6. Wait 1-2 minutes for Railway to provision the database

**That's it!** Railway will:
- ✅ Create a fully managed PostgreSQL database
- ✅ Run it as a non-root user (secure by default)
- ✅ Automatically inject `DATABASE_URL` and `DATABASE_PRIVATE_URL` into your backend service
- ✅ Handle backups, scaling, and maintenance
- ✅ Provide monitoring and metrics

### Step 2: Verify Database Connection Variables

1. Click on your **Backend service** (NOT the PostgreSQL service)
2. Go to the **"Variables"** tab
3. Verify these environment variables exist:
   - `DATABASE_PRIVATE_URL` (preferred - uses internal network, no egress fees)
   - `DATABASE_URL` (fallback - uses public TCP proxy)

Example values:
```bash
# Preferred (internal network, $0 egress)
DATABASE_PRIVATE_URL=postgresql://postgres:password@postgres.railway.internal:5432/railway

# Fallback (public proxy, incurs egress fees)
DATABASE_URL=postgresql://postgres:password@containers-us-west-1.railway.app:7654/railway
```

### Step 3: Add Required Environment Variables

Add these variables to your **Backend service** (if not already present):

| Variable | Value | Description |
|----------|-------|-------------|
| `SECRET_KEY` | `<random-string>` | Flask session secret |
| `JWT_SECRET_KEY` | `<random-string>` | JWT signing key |
| `ENVIRONMENT` | `production` | Enables production mode |

Generate secure keys:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 4: Deploy Your Backend

1. Go to the **"Deployments"** tab of your backend service
2. Click **"Redeploy"** or push new code
3. Monitor the deployment logs
4. Look for: `✅ Database connected successfully`

## ❌ What NOT to Do

### DON'T: Deploy PostgreSQL as a Container

**Never** try to:
- Deploy a PostgreSQL Dockerfile on Railway
- Use `docker-compose.yml` on Railway (it's for local dev only)
- Create a PostgreSQL service from a container image
- Run PostgreSQL in your application container

**Why?** 
- PostgreSQL containers require root privileges for initialization
- Railway's container runtime doesn't allow root execution
- Data would be lost on every deployment
- You'd lose Railway's managed database benefits (backups, scaling, monitoring)

### DON'T: Use Railway PostgreSQL Images Locally in Production

The `ghcr.io/railwayapp-templates/postgres-ssl:13.23` image is Railway's internal image and should only be used:
- In Railway's managed database service (automatically handled)
- For local development with proper user configuration

## 🏠 Local Development Setup

For **local development only**, use docker-compose.yml:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    user: postgres  # Run as postgres user, not root
    environment:
      POSTGRES_DB: hiremebahamas
      POSTGRES_USER: hiremebahamas_user
      POSTGRES_PASSWORD: hiremebahamas_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

This is **ONLY for local testing**. On Railway, you use the managed PostgreSQL service instead.

## 🔍 Troubleshooting

### Error: "root execution of the PostgreSQL server is not permitted"

**Cause:** You're trying to deploy PostgreSQL as a container on Railway.

**Solution:**
1. Delete any PostgreSQL container/application services from your Railway project
2. Add a managed PostgreSQL database service (see Step 1 above)
3. Redeploy your backend application

### Database Connection Refused

**Cause:** DATABASE_URL not configured or database service not running

**Solution:**
1. Verify PostgreSQL service status in Railway dashboard (should show "Active")
2. Check that `DATABASE_URL` or `DATABASE_PRIVATE_URL` appears in your backend's Variables tab
3. Restart the backend service

### Data Lost After Deployment

**Cause:** Using SQLite instead of PostgreSQL, or DATABASE_URL not set

**Solution:**
1. Ensure `ENVIRONMENT=production` is set
2. Verify `DATABASE_URL` or `DATABASE_PRIVATE_URL` is configured
3. Check logs for "Database Mode: PostgreSQL"
4. If SQLite mode is detected, add the database variables and redeploy

## 📊 Verifying Your Setup

After setup, verify everything works:

### Check 1: Database Service Status
- PostgreSQL service shows "Active" status in Railway dashboard
- No error messages in PostgreSQL service logs

### Check 2: Environment Variables
Run this in your backend service logs or Railway CLI:
```bash
railway run env | grep DATABASE
```

Should show:
```
DATABASE_PRIVATE_URL=postgresql://...
DATABASE_URL=postgresql://...
```

### Check 3: Application Logs
Look for these messages in your backend deployment logs:
```
🗄️ Database Mode: PostgreSQL (Production)
✅ PostgreSQL URL detected
✅ Database connection verified
✅ Database tables created successfully
```

### Check 4: Health Endpoint
Test your deployed backend:
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

### Check 5: Data Persistence
1. Register a test user on your deployed app
2. Restart the backend service in Railway
3. Try logging in with the test user
4. **If successful** → PostgreSQL is working correctly! ✅

## 💰 Cost Optimization

Use `DATABASE_PRIVATE_URL` instead of `DATABASE_URL` to avoid egress fees:

The application automatically prefers `DATABASE_PRIVATE_URL` when available. This uses Railway's internal private network, which:
- ✅ Has **zero egress fees** (no data transfer costs)
- ✅ Is **faster** (internal network routing)
- ✅ Is **more secure** (not exposed to public internet)

## 📚 Additional Resources

- [Railway Database Setup Guide](./RAILWAY_DATABASE_SETUP.md) - Detailed database configuration
- [Railway Deployment Troubleshooting](./RAILWAY_DEPLOYMENT_TROUBLESHOOTING.md) - Fix common issues
- [Railway Documentation](https://docs.railway.app/databases/postgresql) - Official Railway docs
- [PostgreSQL Setup Guide](./POSTGRESQL_SETUP.md) - PostgreSQL configuration details

## 🎯 Summary

**DO:**
- ✅ Use Railway's managed PostgreSQL database service
- ✅ Add database via Railway dashboard (+ New → Database → PostgreSQL)
- ✅ Use `DATABASE_PRIVATE_URL` for zero egress fees
- ✅ Set `ENVIRONMENT=production` in backend service

**DON'T:**
- ❌ Deploy PostgreSQL as a container/application on Railway
- ❌ Try to run PostgreSQL in your application Dockerfile
- ❌ Use docker-compose.yml on Railway (local dev only)
- ❌ Run PostgreSQL containers as root user

---

**Need help?** Check [RAILWAY_DATABASE_SETUP.md](./RAILWAY_DATABASE_SETUP.md) for detailed instructions.

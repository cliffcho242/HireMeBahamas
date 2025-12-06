# 🚀 Deployment Setup Guide

This guide explains how to set up automated deployments for HireMeBahamas using GitHub Actions, Vercel, and optionally Railway.

## Overview

HireMeBahamas supports multiple deployment strategies:

1. **Vercel Serverless** (Recommended) - Frontend + Backend API on Vercel
2. **Railway Backend** (Optional) - Separate backend instance on Railway
3. **Flexible Setup** - Choose what works best for you

The deployment workflows are designed to be **gracefully degrading** - they will skip deployment steps if credentials are not configured, allowing you to set up services incrementally.

## Quick Start

### Minimum Required Setup (Vercel Only)

For a basic deployment with Vercel serverless backend:

1. Add these GitHub Secrets:
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`

2. Add these Vercel Environment Variables:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`

3. Push to `main` branch - deployment happens automatically!

### Full Setup (Vercel + Railway)

For deploying both Vercel frontend and Railway backend:

1. Set up all Vercel secrets (above)
2. Additionally add Railway secrets:
   - `RAILWAY_TOKEN`
   - `RAILWAY_PROJECT_ID`

3. Configure Railway environment variables in Railway dashboard

## Detailed Setup Instructions

### 1. GitHub Actions Secrets

GitHub Actions secrets are used to authenticate with deployment services.

**Location:** `https://github.com/YOUR_USERNAME/HireMeBahamas/settings/secrets/actions`

#### Vercel Secrets (Required for Vercel deployment)

| Secret | Description | How to Get |
|--------|-------------|------------|
| `VERCEL_TOKEN` | Authentication token for Vercel API | 1. Go to https://vercel.com/account/tokens<br>2. Click "Create Token"<br>3. Name it "GitHub Actions"<br>4. Copy the token |
| `VERCEL_ORG_ID` | Your Vercel organization/team ID | 1. Go to https://vercel.com<br>2. Click Settings<br>3. Copy "Team ID" (starts with `team_`) |
| `VERCEL_PROJECT_ID` | Your project's unique ID | 1. Go to project dashboard<br>2. Settings → General<br>3. Copy "Project ID" (starts with `prj_`) |

#### Railway Secrets (Optional, for Railway deployment)

| Secret | Description | How to Get |
|--------|-------------|------------|
| `RAILWAY_TOKEN` | Authentication token for Railway API | 1. Go to https://railway.app/account/tokens<br>2. Click "Create Token"<br>3. Copy the token |
| `RAILWAY_PROJECT_ID` | Your Railway project ID | 1. Go to your project<br>2. Settings<br>3. Copy "Project ID" |

#### Database & Security Secrets

| Secret | Description | How to Generate |
|--------|-------------|-----------------|
| `DATABASE_URL` | PostgreSQL connection string | Get from Railway/Render/Vercel Postgres<br>Format: `postgresql://user:pass@host:5432/db?sslmode=require` |
| `SECRET_KEY` | Application secret key | `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `JWT_SECRET_KEY` | JWT signing key | `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` |

### 2. Vercel Environment Variables

These must be set in your Vercel project dashboard.

**Location:** `https://vercel.com/YOUR_USERNAME/hiremebahamas/settings/environment-variables`

| Variable | Value | Environments |
|----------|-------|--------------|
| `DATABASE_URL` | Your PostgreSQL connection string | Production, Preview, Development |
| `SECRET_KEY` | Same value as GitHub secret | Production, Preview, Development |
| `JWT_SECRET_KEY` | Same value as GitHub secret | Production, Preview, Development |
| `ENVIRONMENT` | `production` | Production only |
| `DEBUG` | `false` | Production only |

**Important:** The `SECRET_KEY` and `JWT_SECRET_KEY` must be identical between GitHub Secrets and Vercel Environment Variables for JWT tokens to work across deployments.

### 3. Railway Environment Variables (Optional)

If using Railway backend, configure these in Railway project settings:

- `DATABASE_URL` - Your Railway PostgreSQL connection string
- `SECRET_KEY` - Same as other deployments
- `JWT_SECRET_KEY` - Same as other deployments
- `ENVIRONMENT` - Set to `production`
- `PORT` - Railway will provide this automatically

### 4. GitHub Repository Variables (Optional)

These are used for health checks and monitoring.

**Location:** `https://github.com/YOUR_USERNAME/HireMeBahamas/settings/variables/actions`

| Variable | Description | Example |
|----------|-------------|---------|
| `VERCEL_URL` | Your Vercel deployment URL | `https://hiremebahamas.vercel.app` |
| `RAILWAY_BACKEND_URL` | Your Railway backend URL (if using) | `https://hiremebahamas.railway.app` |

## Deployment Workflows

### Automatic Deployments

Deployments are triggered automatically by:

1. **Push to `main` branch** - Triggers all configured deployments
2. **Pull Request** - Runs CI tests (no deployment)
3. **Manual trigger** - Via GitHub Actions UI

### Workflow Behavior

#### deploy-vercel.yml
- **Triggers:** Push to `main`, manual dispatch
- **Behavior:** 
  - ✅ Runs if all Vercel secrets are configured
  - ⏭️ Skips gracefully if secrets are missing
  - 📊 Shows summary in GitHub Actions

#### deploy-backend.yml (Railway)
- **Triggers:** Push to `main` (when backend files change), manual dispatch
- **Behavior:**
  - ✅ Runs if Railway token is configured
  - ⏭️ Skips gracefully if token is missing
  - 📊 Shows summary in GitHub Actions

#### ci.yml
- **Triggers:** Pull requests, push to `main`
- **Behavior:**
  - ✅ Always runs - validates code quality
  - ✅ Runs tests with PostgreSQL test database
  - ✅ Validates frontend build
  - ✅ Checks vercel.json configuration

## Health Check Endpoints

The application provides several health check endpoints:

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/api/health` | Basic health check | Status, timestamp, database connection |
| `/api/status` | Detailed status | Backend modules, capabilities, configuration |
| `/api/ready` | Readiness check | Database connectivity validation |
| `/api/diagnostic` | Debug information | Full system diagnostics (debug mode only) |

### Using Health Checks

```bash
# Quick health check
curl https://your-deployment.vercel.app/api/health

# Expected response
{
  "status": "healthy",
  "platform": "vercel-serverless",
  "timestamp": 1234567890,
  "backend": "available",
  "database": "connected"
}
```

## Monitoring & Keepalive

### Vercel Keepalive Workflow

**File:** `.github/workflows/vercel-keepalive.yml`

- Runs every 5 minutes
- Pings `/api/health` endpoint
- Keeps serverless functions warm
- Prevents cold starts

### Uptime Monitoring Workflow

**File:** `.github/workflows/uptime-monitoring.yml`

- Runs every 15 minutes
- Checks Railway backend (if configured)
- Creates GitHub issues on critical failures
- Provides status summaries

## Troubleshooting

### "Deployment skipped" in GitHub Actions

**Cause:** Required secrets are not configured

**Solution:** This is intentional! Add the required secrets to enable deployment:
- For Vercel: Add `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`
- For Railway: Add `RAILWAY_TOKEN`, `RAILWAY_PROJECT_ID`

### "Database connection failed"

**Cause:** DATABASE_URL not set or incorrect

**Solution:**
1. Verify `DATABASE_URL` is set in Vercel environment variables
2. Check the connection string format includes `?sslmode=require`
3. Test connection from Vercel Function logs
4. Ensure database accepts connections from Vercel IPs

### "JWT token validation failed"

**Cause:** SECRET_KEY or JWT_SECRET_KEY mismatch

**Solution:**
1. Ensure keys are identical in GitHub Secrets and Vercel Environment Variables
2. Redeploy after updating keys
3. Clear browser cookies and try signing in again

### "Health endpoint returns 404"

**Cause:** API routes not properly configured

**Solution:**
1. Verify `vercel.json` has correct rewrites
2. Check Vercel deployment logs for build errors
3. Ensure `api/index.py` is present and valid
4. Redeploy the project

### Viewing Deployment Logs

**Vercel:**
1. Go to https://vercel.com/dashboard
2. Select your project
3. Click on "Deployments"
4. Select the deployment
5. View "Functions" tab for API logs

**Railway:**
1. Go to https://railway.app/dashboard
2. Select your project
3. Click on the service
4. View "Deployments" tab
5. Click "View Logs"

**GitHub Actions:**
1. Go to your repository
2. Click "Actions" tab
3. Select the workflow run
4. Click on the job
5. Expand steps to view logs

## Best Practices

### Security

1. **Never commit secrets** - Use GitHub Secrets and environment variables
2. **Rotate tokens regularly** - Generate new tokens every 6 months
3. **Use strong secret keys** - At least 32 characters, randomly generated
4. **Enable 2FA** - On GitHub, Vercel, and Railway accounts
5. **Restrict token permissions** - Use minimum required permissions

### Performance

1. **Enable caching** - Vercel automatically caches static assets
2. **Use CDN** - Vercel Edge Network handles this automatically
3. **Optimize images** - Use Vercel Image Optimization
4. **Monitor cold starts** - Keepalive workflow prevents this
5. **Database connection pooling** - Configured in `api/index.py`

### Maintenance

1. **Monitor deployments** - Check GitHub Actions regularly
2. **Review logs** - Look for errors in Vercel/Railway logs
3. **Update dependencies** - Keep packages up to date
4. **Test before merging** - Use pull requests for changes
5. **Backup database** - Regular backups of PostgreSQL data

## Testing Your Deployment

### Frontend Tests

```bash
# Visit your deployment
https://your-deployment.vercel.app

# Check console for errors
F12 → Console tab
```

### Backend API Tests

```bash
# Health check
curl https://your-deployment.vercel.app/api/health

# Status check
curl https://your-deployment.vercel.app/api/status

# Auth endpoint (should return 401)
curl https://your-deployment.vercel.app/api/auth/me

# Test login
curl -X POST https://your-deployment.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hiremebahamas.com","password":"AdminPass123!"}'
```

### Expected Responses

- Health check: `200 OK` with status JSON
- Status check: `200 OK` with detailed status
- Auth without token: `401 Unauthorized`
- Login with valid credentials: `200 OK` with JWT token

## Support & Resources

### Official Documentation

- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

### Repository Resources

- `FIX_SIGN_IN_DEPLOYMENT_GUIDE.md` - Sign-in specific troubleshooting
- `ARCHITECTURE.md` - System architecture overview
- `.github/workflows/` - Workflow configurations
- `api/index.py` - Backend API implementation

### Getting Help

1. Check this guide and troubleshooting section
2. Review GitHub Actions logs for specific errors
3. Check Vercel/Railway deployment logs
4. Create a GitHub issue with:
   - Error message and logs
   - Steps to reproduce
   - What you've tried
   - Deployment platform used

## Next Steps

After successful deployment:

1. ✅ Test all application features
2. ✅ Set up monitoring alerts
3. ✅ Configure custom domain (optional)
4. ✅ Enable analytics (Vercel Analytics)
5. ✅ Set up error tracking (Sentry, etc.)
6. ✅ Create backup strategy for database
7. ✅ Document any custom configuration

---

**Last Updated:** December 6, 2025  
**Maintainer:** GitHub Copilot Agent  
**Status:** Active and maintained

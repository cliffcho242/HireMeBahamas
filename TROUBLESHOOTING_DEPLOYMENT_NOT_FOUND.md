# Troubleshooting: 404 DEPLOYMENT_NOT_FOUND Error

## Error Description

```
404: NOT_FOUND
Code: DEPLOYMENT_NOT_FOUND
ID: iad1::w8sw2-1764947401263-a8632abddccc
```

This error occurs when Vercel cannot find or serve a deployment at the requested URL.

## Quick Diagnosis

Run the verification script to check your configuration:

```bash
python3 scripts/verify-vercel-deployment.py
```

This will check:
- ✅ vercel.json configuration
- ✅ No conflicting configuration files
- ✅ API structure
- ✅ Frontend build output
- ✅ Required dependencies

## Common Causes & Solutions

### 1. Deployment Was Deleted or Doesn't Exist

**Symptoms:**
- Accessing a URL that worked before but now shows 404
- The deployment ID in the URL doesn't exist anymore

**Solutions:**

#### A. Check Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Select your project
3. Check the "Deployments" tab
4. Verify recent deployments are showing as "Ready"

#### B. Redeploy from GitHub
If no active deployments exist:

```bash
# Push to main branch to trigger new deployment
git push origin main
```

Or manually deploy:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy to production
vercel --prod
```

### 2. Incorrect Vercel Project Configuration

**Symptoms:**
- Deployments fail during build
- Build logs show configuration errors
- Environment variables are missing

**Solutions:**

#### A. Verify GitHub Secrets (for automated deployment)

Go to your repository: `Settings > Secrets and variables > Actions`

Required secrets:
- `VERCEL_TOKEN` - Get from https://vercel.com/account/tokens
- `VERCEL_ORG_ID` - Get from https://vercel.com/[your-team]/settings
- `VERCEL_PROJECT_ID` - Get from project Settings > General

#### B. Verify Vercel Environment Variables

Go to Vercel Dashboard: `Project > Settings > Environment Variables`

Required variables:
```
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
SECRET_KEY=your-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-min-32-chars
ENVIRONMENT=production
```

#### C. Check Build Configuration

Verify `vercel.json` in project root:

```json
{
  "version": 2,
  "buildCommand": "cd frontend && npm ci && npm run build",
  "outputDirectory": "frontend/dist",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/index.py"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

**Important:** Do NOT mix old API (`builds`/`routes`) with new API (`outputDirectory`/`buildCommand`)

### 3. Build Failures

**Symptoms:**
- Deployment shows "Failed" status
- Build logs show errors
- No output directory generated

**Solutions:**

#### A. Test Build Locally

```bash
cd frontend
npm ci
npm run build

# Verify dist directory exists
ls -la dist/
ls -la dist/index.html  # Should exist
```

#### B. Check Build Logs in Vercel

1. Go to Vercel Dashboard
2. Click on the failed deployment
3. Review "Build Logs" tab
4. Look for error messages

Common build errors:
- Missing dependencies → Update `package.json` or `requirements.txt`
- TypeScript errors → Fix type issues in code
- Out of memory → Optimize build process

### 4. DNS/Domain Issues

**Symptoms:**
- Custom domain shows 404
- Vercel deployment URL works but custom domain doesn't

**Solutions:**

#### A. Check Domain Configuration

1. Go to Vercel Dashboard
2. Project > Settings > Domains
3. Verify domain is connected and DNS is configured correctly
4. Check nameservers point to Vercel

#### B. Wait for DNS Propagation

DNS changes can take 24-48 hours to propagate globally. Test with:

```bash
# Check DNS resolution
nslookup yourdomain.com

# Check from different DNS servers
nslookup yourdomain.com 8.8.8.8
```

### 5. API Route Configuration Issues

**Symptoms:**
- Frontend loads but API calls return 404
- `/api/*` endpoints not working

**Solutions:**

#### A. Verify API Structure

Required files:
```
api/
  ├── index.py          ← Entry point (exports 'handler')
  ├── requirements.txt  ← Must include 'mangum' and 'fastapi'
  └── ...
```

#### B. Check api/index.py

Must export a handler for Vercel:

```python
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

# ... your routes ...

# CRITICAL: Export handler for Vercel
handler = Mangum(app, lifespan="off")
```

#### C. Verify API Dependencies

Check `api/requirements.txt` includes:
```
fastapi==0.115.6
mangum==0.19.0
pydantic==2.10.3
```

### 6. Cached Configuration Issues

**Symptoms:**
- Configuration changes don't take effect
- Old deployment still showing

**Solutions:**

#### A. Clear Vercel Cache

1. Go to Vercel Dashboard
2. Project > Settings > General
3. Scroll to "Clear Cache" section
4. Click "Clear Cache"
5. Redeploy

#### B. Force Redeploy

```bash
# Trigger new deployment with empty commit
git commit --allow-empty -m "Force redeploy"
git push origin main
```

## Step-by-Step Troubleshooting Process

### Step 1: Verify Local Configuration

```bash
# Run verification script
python3 scripts/verify-vercel-deployment.py

# Should show all green checkmarks
```

### Step 2: Check Build Process

```bash
# Build frontend locally
cd frontend && npm run build

# Verify output
ls -la dist/index.html  # Should exist
```

### Step 3: Check Vercel Dashboard

1. Login to https://vercel.com/dashboard
2. Find your project
3. Check latest deployment status
4. Review build logs if failed

### Step 4: Verify Secrets and Environment Variables

#### GitHub Secrets (Repository Settings)
- VERCEL_TOKEN ✓
- VERCEL_ORG_ID ✓
- VERCEL_PROJECT_ID ✓

#### Vercel Environment Variables (Project Settings)
- DATABASE_URL ✓
- SECRET_KEY ✓
- JWT_SECRET_KEY ✓

### Step 5: Test Deployment

```bash
# Trigger GitHub Actions deployment
git push origin main

# Or deploy manually with Vercel CLI
vercel --prod
```

### Step 6: Monitor Deployment

1. Watch GitHub Actions workflow
2. Check for errors in workflow logs
3. Wait for "Ready" status in Vercel
4. Test the deployment URL

## Verification Checklist

Use this checklist to ensure everything is configured correctly:

- [ ] `vercel.json` exists in project root
- [ ] `vercel.json` uses modern API (no `builds`/`routes` when using `outputDirectory`)
- [ ] No conflicting `frontend/vercel.json` file
- [ ] `api/index.py` exports `handler = Mangum(app)`
- [ ] `api/requirements.txt` includes `mangum` and `fastapi`
- [ ] `runtime.txt` specifies Python version (e.g., `python-3.12.0`)
- [ ] Frontend builds successfully locally (`npm run build`)
- [ ] `frontend/dist/index.html` exists after build
- [ ] GitHub secrets configured (VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID)
- [ ] Vercel environment variables configured (DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY)
- [ ] Latest deployment in Vercel shows "Ready" status
- [ ] Build logs show no errors

## Getting Help

If you've followed all troubleshooting steps and still see the error:

1. **Check Vercel Status**: https://www.vercel-status.com/
   - Vercel may be experiencing issues

2. **Review Documentation**:
   - [VERCEL_DEPLOYMENT_404_FIX.md](./VERCEL_DEPLOYMENT_404_FIX.md) - Detailed fix guide
   - [FIX_SIGN_IN_DEPLOYMENT_GUIDE.md](./FIX_SIGN_IN_DEPLOYMENT_GUIDE.md) - Setup guide
   - [DEPLOYMENT_CONNECTION_GUIDE.md](./DEPLOYMENT_CONNECTION_GUIDE.md) - Complete deployment guide

3. **Check GitHub Actions Logs**:
   ```bash
   # View recent workflow runs
   # Go to: https://github.com/[username]/[repo]/actions
   ```

4. **Vercel Support**:
   - Vercel Community: https://github.com/vercel/vercel/discussions
   - Vercel Support: Available for Pro and Enterprise plans

## Prevention

To prevent this error in the future:

1. **Use the verification script** before deploying:
   ```bash
   python3 scripts/verify-vercel-deployment.py
   ```

2. **Test builds locally** before pushing:
   ```bash
   cd frontend && npm run build
   ```

3. **Monitor deployments** in Vercel Dashboard after each push

4. **Use preview deployments** to test changes before merging to main:
   - Create a PR
   - Vercel automatically creates a preview deployment
   - Test the preview URL
   - Merge only if preview works

5. **Keep environment variables updated**:
   - Document all required variables
   - Update them in Vercel when changed
   - Don't hardcode secrets in code

## Related Files

- `/vercel.json` - Root Vercel configuration
- `/api/index.py` - Serverless API handler
- `/api/requirements.txt` - Python dependencies
- `/runtime.txt` - Python version specification
- `/.github/workflows/deploy-vercel.yml` - Automated deployment workflow
- `/scripts/verify-vercel-deployment.py` - Verification script

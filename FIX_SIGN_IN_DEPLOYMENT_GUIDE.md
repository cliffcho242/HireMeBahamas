# 🚨 FIX SIGN-IN ERROR - Complete Deployment Guide

## Current Issue

**Users cannot sign in because Vercel deployments are failing.** The GitHub Actions workflow is missing required secrets.

## Quick Fix (5 Minutes)

### Step 1: Configure GitHub Secrets

You need to add these secrets to your GitHub repository:

1. Go to: https://github.com/cliffcho242/HireMeBahamas/settings/secrets/actions
2. Click **"New repository secret"** for each of the following:

#### Required Secrets:

| Secret Name | How to Get It | Example Value |
|------------|---------------|---------------|
| `VERCEL_TOKEN` | https://vercel.com/account/tokens | `xxxxxxxxxxxxxxxxxxxxxx` |
| `VERCEL_ORG_ID` | https://vercel.com → Settings → General | `team_xxxxxxxxxxxxxx` |
| `VERCEL_PROJECT_ID` | Vercel Project → Settings → General | `prj_xxxxxxxxxxxxxx` |
| `DATABASE_URL` | Railway/Render PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Generate with: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` | `abc123...` |
| `JWT_SECRET_KEY` | Generate with: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` | `xyz789...` |

#### Optional Secrets (for Railway backend):

| Secret Name | How to Get It | When Needed |
|------------|---------------|-------------|
| `RAILWAY_TOKEN` | https://railway.app/account/tokens | If using Railway for backend hosting |
| `RAILWAY_PROJECT_ID` | Railway Project → Settings | If using Railway for backend hosting |

**Note:** Railway deployment is optional. If you're using Vercel serverless backend (recommended), you can skip these secrets. The deployment workflow will automatically skip Railway deployment if these secrets are not configured.

### Step 2: Configure Vercel Environment Variables

1. Go to: https://vercel.com/dashboard
2. Select your **HireMeBahamas** project
3. Go to **Settings** → **Environment Variables**
4. Add the following variables:

| Variable Name | Value | Environment |
|--------------|-------|-------------|
| `DATABASE_URL` | `postgresql://user:pass@host:5432/db?sslmode=require` | Production, Preview, Development |
| `SECRET_KEY` | (Generate a new 32-char random string) | Production, Preview, Development |
| `JWT_SECRET_KEY` | (Generate a new 32-char random string) | Production, Preview, Development |
| `ENVIRONMENT` | `production` | Production only |

**Important:** Use the same `SECRET_KEY` and `JWT_SECRET_KEY` values in both GitHub Secrets and Vercel Environment Variables.

### Step 3: Redeploy

After adding all secrets:

1. Go to your repository: https://github.com/cliffcho242/HireMeBahamas
2. Click on **Actions** tab
3. Find the **"Deploy to Vercel"** workflow
4. Click **"Re-run all jobs"**

Or simply push a new commit to the `main` branch:

```bash
git commit --allow-empty -m "Trigger deployment after configuring secrets"
git push origin main
```

### Step 4: Verify Deployment

1. Wait for the GitHub Actions workflow to complete (2-3 minutes)
2. Visit your Vercel deployment URL (e.g., `https://hiremebahamas.vercel.app`)
3. Try signing in with: `admin@hiremebahamas.com` / `AdminPass123!`

---

## Detailed Setup Instructions

### Getting Your Vercel Credentials

#### 1. Get VERCEL_TOKEN

1. Visit: https://vercel.com/account/tokens
2. Click **"Create Token"**
3. Give it a name like "GitHub Actions Deploy"
4. Choose scope: **Full Access** or select specific projects
5. Click **"Create"**
6. **Copy the token immediately** (you won't be able to see it again)

#### 2. Get VERCEL_ORG_ID

1. Go to: https://vercel.com
2. Click on your profile/organization in the top-right
3. Go to **Settings**
4. Copy the **Team ID** (starts with `team_...`)
   - If using a personal account, this might be your username

#### 3. Get VERCEL_PROJECT_ID

1. Go to your Vercel dashboard: https://vercel.com/dashboard
2. Click on your **HireMeBahamas** project
3. Go to **Settings** → **General**
4. Copy the **Project ID** (starts with `prj_...`)

### Getting Your Database Connection String

#### Option A: Railway PostgreSQL

1. Go to: https://railway.app/dashboard
2. Click on your **HireMeBahamas** project
3. Click on the **Postgres** service
4. Copy the **DATABASE_URL** or **DATABASE_PRIVATE_URL**
5. Example format: `postgresql://postgres:password@containers-us-west-XXX.railway.app:7432/railway`

**Important:** Add `?sslmode=require` to the end of the URL for secure connections:
```
postgresql://postgres:password@host:7432/railway?sslmode=require
```

#### Option B: Render PostgreSQL

1. Go to: https://dashboard.render.com
2. Navigate to your PostgreSQL database
3. Copy the **External Database URL**
4. Example format: `postgres://user:pass@dpg-xxx-a.render.com/dbname`

**Important:** Replace `postgres://` with `postgresql://` and add `?sslmode=require`:
```
postgresql://user:pass@dpg-xxx-a.render.com/dbname?sslmode=require
```

### Generating Secret Keys

Run these commands to generate secure random keys:

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Important:** Keep these keys secret and never commit them to your repository!

---

## Troubleshooting

### Issue: "Vercel deployment still failing"

**Solution:** Check the GitHub Actions logs for detailed error messages:

1. Go to: https://github.com/cliffcho242/HireMeBahamas/actions
2. Click on the latest failed workflow run
3. Click on the failed job
4. Read the error messages
5. Common issues:
   - Missing secret: Add the missing secret to GitHub
   - Invalid token: Regenerate the Vercel token
   - Vercel project not found: Check `VERCEL_PROJECT_ID` is correct

### Issue: "Users still can't sign in after deployment succeeds"

**Possible causes:**

1. **Database not connected:**
   - Verify `DATABASE_URL` is set in Vercel environment variables
   - Test the connection string manually
   - Check if Railway/Render database is running

2. **Secret keys mismatch:**
   - Ensure `SECRET_KEY` and `JWT_SECRET_KEY` match between GitHub and Vercel
   - These keys must be identical for JWT tokens to work

3. **Database tables missing:**
   - The backend will automatically create tables on first connection
   - Check Vercel Function logs for database initialization errors

### Issue: "Railway backend deployment failing"

**Solution:**

Railway deployment is optional and will be automatically skipped if not configured. If you want to use Railway:

1. Verify `RAILWAY_TOKEN` is set in GitHub Secrets
2. Verify `RAILWAY_PROJECT_ID` is correct
3. Check if you have Railway CLI access
4. Note: Railway backend is optional if using Vercel serverless backend

**To skip Railway deployment entirely:**
- Simply don't add the `RAILWAY_TOKEN` secret to GitHub
- The workflow will automatically skip Railway deployment steps
- The build will succeed with a warning message

### Issue: "Vercel deployment workflow skipped"

**Solution:**

If you see "Vercel deployment skipped" in your GitHub Actions logs:

1. This means one or more required Vercel secrets are missing
2. Check that all three secrets are configured:
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`
3. Follow the setup instructions above to add missing secrets
4. The workflow will not fail - it will just skip deployment with a warning

**Why this is designed this way:**
- Allows the repository to work without requiring all deployment services
- You can set up deployments incrementally
- CI tests will still run even if deployments are not configured

### Viewing Vercel Logs

To debug sign-in issues:

1. Go to your Vercel project dashboard
2. Click on **Deployments**
3. Click on your latest deployment
4. Click on **Functions** tab
5. Click on any `/api/*` function
6. View the function logs for errors

### Testing Backend Connection

You can test if the Vercel backend is working:

```bash
# Test health endpoint
curl https://hiremebahamas.vercel.app/api/health

# Test authentication endpoint (should return 401 Unauthorized)
curl https://hiremebahamas.vercel.app/api/auth/me
```

Expected responses:
- Health check: `200 OK` with status information
- Auth check: `401 Unauthorized` (this is correct - means backend is working)

---

## Architecture Overview

### Current Setup:

```
┌─────────────────────────────────────────────────────────┐
│ GitHub Repository (cliffcho242/HireMeBahamas)          │
│                                                         │
│  ┌─────────────────┐    ┌──────────────────┐          │
│  │ Frontend (React)│    │ Backend (FastAPI)│          │
│  │ frontend/       │    │ api/             │          │
│  └─────────────────┘    └──────────────────┘          │
└─────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                  │
          ▼                                  ▼
┌──────────────────────┐         ┌──────────────────────┐
│ Vercel               │         │ Railway/Render       │
│ - Frontend hosting   │         │ - PostgreSQL DB      │
│ - Serverless backend │         │ - Optional backend   │
│ - /api/* endpoints   │         │                      │
└──────────────────────┘         └──────────────────────┘
          │                                  │
          └──────────────┬──────────────────┘
                         │
                         ▼
                    DATABASE_URL
                    Connection String
```

### Sign-In Flow:

1. User enters credentials on frontend (React)
2. Frontend sends POST request to `/api/auth/login` (Vercel serverless)
3. Backend validates credentials against PostgreSQL database
4. Backend generates JWT token with SECRET_KEY
5. Frontend stores token and redirects to homepage
6. Subsequent requests include JWT token in Authorization header
7. Backend validates token using JWT_SECRET_KEY

### Why Sign-In Fails:

- ❌ Vercel deployment not configured → Backend not accessible
- ❌ DATABASE_URL not set → Can't verify credentials
- ❌ SECRET_KEY not set → Can't generate valid JWT tokens
- ❌ Environment variables mismatch → Token validation fails

---

## Verification Checklist

After completing the setup, verify everything is working:

- [ ] GitHub Actions workflows complete successfully (may skip deployment if secrets not configured)
- [ ] If Vercel configured: Vercel project shows latest deployment as "Ready"
- [ ] If Vercel configured: `https://hiremebahamas.vercel.app` loads successfully
- [ ] If Vercel configured: `https://hiremebahamas.vercel.app/api/health` returns 200 OK
- [ ] If Vercel configured: Database connection shown as "connected" in health check
- [ ] Sign-in page loads without errors
- [ ] Can sign in with test credentials: `admin@hiremebahamas.com` / `AdminPass123!`
- [ ] After sign-in, redirected to homepage
- [ ] User profile shows in top-right corner
- [ ] Can navigate to different pages without logging out

**Note:** If you haven't configured deployment secrets yet, that's OK! The CI tests will still run and verify code quality. You can set up deployments later.

---

## Support

If you're still experiencing issues after following this guide:

1. **Check the logs:**
   - GitHub Actions workflow logs
   - Vercel Function logs
   - Browser console (F12 → Console tab)

2. **Common error messages and solutions:**
   
   | Error | Solution |
   |-------|----------|
   | "Network Error" | Backend not accessible - check Vercel deployment |
   | "Invalid credentials" | Database not connected - check DATABASE_URL |
   | "Token expired" | SECRET_KEY mismatch - ensure keys match |
   | "404 Not Found" | API routes not registered - check backend logs |
   | "Internal Server Error" | Check Vercel Function logs for details |

3. **Still stuck?** Create a GitHub issue with:
   - Error message (screenshot or text)
   - GitHub Actions workflow log (if deployment failed)
   - Vercel Function logs (if sign-in failed)
   - Browser console errors (if frontend issue)

---

## Next Steps

After fixing sign-in:

1. **Test all features:**
   - User registration
   - Job posting
   - Profile editing
   - Messaging

2. **Monitor performance:**
   - Vercel Analytics
   - Error tracking in Function logs
   - Database query performance

3. **Optimize:**
   - Enable Vercel Edge Config for faster configuration loading
   - Set up Vercel KV for session storage
   - Configure CDN caching for static assets

---

**Last Updated:** December 5, 2025  
**Author:** GitHub Copilot Agent  
**Issue:** Users cannot sign in - deployment configuration missing

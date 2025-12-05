# Quick Fix Guide: 404 DEPLOYMENT_NOT_FOUND

## 🚨 Error

```
404: NOT_FOUND
Code: DEPLOYMENT_NOT_FOUND
ID: iad1::w8sw2-1764947401263-a8632abddccc
```

## ⚡ Quick Fix (5 Minutes)

### Step 1: Run Verification Script

```bash
python3 scripts/verify-vercel-deployment.py
```

**Expected Output:**
- ✅ All checks should pass
- If any fail, follow the error messages

### Step 2: Check GitHub Secrets

Go to: `https://github.com/[your-username]/HireMeBahamas/settings/secrets/actions`

**Required Secrets:**
- ✅ `VERCEL_TOKEN` - Get from https://vercel.com/account/tokens
- ✅ `VERCEL_ORG_ID` - Get from https://vercel.com/account/settings
- ✅ `VERCEL_PROJECT_ID` - Get from project settings

**Need help?** Run:
```bash
python3 scripts/check-github-secrets.py
```

### Step 3: Check Vercel Environment Variables

Go to: `https://vercel.com/dashboard` → Your Project → Settings → Environment Variables

**Required Variables:**
```
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
SECRET_KEY=your-secret-key-min-32-characters
JWT_SECRET_KEY=your-jwt-secret-min-32-characters
ENVIRONMENT=production
```

### Step 4: Redeploy

```bash
# Option 1: Trigger GitHub Actions
git commit --allow-empty -m "Redeploy"
git push origin main

# Option 2: Deploy with Vercel CLI
npm i -g vercel
vercel --prod
```

### Step 5: Verify Deployment

1. Go to https://vercel.com/dashboard
2. Click on your project
3. Check latest deployment shows "Ready"
4. Click on the deployment URL to test

## 🔧 Common Issues & Quick Fixes

### Issue 1: "VERCEL_TOKEN secret is not set"

**Fix:**
1. Go to https://vercel.com/account/tokens
2. Create new token
3. Copy token
4. Add to GitHub: Settings → Secrets → Actions → New secret
5. Name: `VERCEL_TOKEN`, Value: (paste token)

### Issue 2: Build Failed

**Fix:**
```bash
# Test build locally
cd frontend
npm ci
npm run build

# Should create dist/index.html
ls -la dist/index.html
```

If build fails locally, fix errors before pushing.

### Issue 3: "Cannot connect to database"

**Fix:**
1. Verify `DATABASE_URL` is set in Vercel
2. Check database is running (Railway/Render)
3. Verify connection string format:
   ```
   postgresql://user:pass@host:5432/db?sslmode=require
   ```

### Issue 4: Old deployment showing

**Fix:**
1. Vercel Dashboard → Project → Settings → General
2. Scroll to "Clear Cache"
3. Click "Clear Cache"
4. Redeploy

## 📚 Detailed Guides

**Choose your guide:**

1. **TROUBLESHOOTING_DEPLOYMENT_NOT_FOUND.md** ← Start here
   - Complete troubleshooting process
   - 6 common causes with solutions
   - Step-by-step instructions

2. **FIX_SIGN_IN_DEPLOYMENT_GUIDE.md**
   - Complete setup from scratch
   - Detailed configuration instructions

3. **VERCEL_DEPLOYMENT_404_FIX.md**
   - Technical details and background
   - Configuration conflicts

## ✅ Verification Checklist

Quick checklist to ensure everything is configured:

```bash
# 1. Configuration files
[ ] vercel.json exists in project root
[ ] No frontend/vercel.json (should be deleted)
[ ] api/index.py exists
[ ] api/requirements.txt includes mangum and fastapi

# 2. GitHub Secrets (Repository Settings)
[ ] VERCEL_TOKEN is set
[ ] VERCEL_ORG_ID is set
[ ] VERCEL_PROJECT_ID is set

# 3. Vercel Environment Variables (Project Settings)
[ ] DATABASE_URL is set
[ ] SECRET_KEY is set
[ ] JWT_SECRET_KEY is set
[ ] ENVIRONMENT=production is set

# 4. Build
[ ] Frontend builds locally: cd frontend && npm run build
[ ] dist/index.html exists after build

# 5. Deployment
[ ] GitHub Actions workflow completes successfully
[ ] Vercel shows deployment as "Ready"
[ ] Deployment URL loads correctly
```

## 🎯 Prevention

Prevent future issues:

1. **Before pushing:**
   ```bash
   python3 scripts/verify-vercel-deployment.py
   ```

2. **Use preview deployments:**
   - Create a PR first
   - Vercel auto-creates preview
   - Test preview before merging

3. **Monitor deployments:**
   - Check GitHub Actions after push
   - Review Vercel Dashboard regularly
   - Enable email notifications

## 🆘 Still Having Issues?

If you've followed all steps and still see the error:

1. **Check Vercel Status:** https://www.vercel-status.com/
2. **Review detailed guides:**
   - TROUBLESHOOTING_DEPLOYMENT_NOT_FOUND.md
   - FIX_SIGN_IN_DEPLOYMENT_GUIDE.md
3. **Check GitHub Actions logs**
4. **Review Vercel build logs**

## 📞 Getting Help

**Check these resources:**
- Repository Issues: https://github.com/cliffcho242/HireMeBahamas/issues
- Vercel Community: https://github.com/vercel/vercel/discussions
- Vercel Support: Available for Pro/Enterprise

---

**Last Updated:** 2025-12-05
**Status:** ✅ Tested and Working

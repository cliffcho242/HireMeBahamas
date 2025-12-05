# 🔍 Sign-In Troubleshooting Guide

## Quick Diagnostic

### Is the website loading?
- **No** → Check GitHub Actions deployment status
- **Yes** → Continue below

### Can you see the sign-in page?
- **No** → Check browser console for errors (F12)
- **Yes** → Continue below

### What happens when you click "Sign In"?

#### "Network Error"
**Cause:** Backend not accessible  
**Solution:** 
1. Test: `curl https://hiremebahamas.vercel.app/api/health`
2. If fails → Check Vercel Functions logs
3. Add DATABASE_URL to Vercel environment variables

#### "Invalid Credentials"
**Cause:** Database not connected  
**Solution:**
1. Test health: `curl https://hiremebahamas.vercel.app/api/health`
2. Check response for `"database": "connected"`
3. If not connected → Add DATABASE_URL to Vercel

#### "Internal Server Error"
**Cause:** Backend crash  
**Solution:**
1. Check Vercel Functions logs (Dashboard → Deployments → Functions)
2. Look for error messages
3. Common fix: Add missing environment variables

---

## Common Solutions

### 1. Deployment Failed
**Problem:** Website not accessible  
**Fix:** Add GitHub Secrets (VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID)  
**Guide:** [FIX_SIGN_IN_DEPLOYMENT_GUIDE.md](./FIX_SIGN_IN_DEPLOYMENT_GUIDE.md)

### 2. Database Not Connected  
**Problem:** "Invalid credentials" with correct password  
**Fix:** Add DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY to Vercel  
**Where:** Vercel Dashboard → Settings → Environment Variables

### 3. Backend Not Running
**Problem:** "Network Error"  
**Fix:** Check Vercel Functions logs for errors

---

## Validation Tools

**Check your configuration:**
```bash
python3 scripts/check-deployment-config.py
```

**Test backend directly:**
```bash
# Health check
curl https://hiremebahamas.vercel.app/api/health

# Should return JSON with database status
```

---

## Full Documentation

- **[Complete Fix Guide](./FIX_SIGN_IN_DEPLOYMENT_GUIDE.md)** - 11,000+ word guide
- **[Quick Reference](./DEPLOYMENT_QUICK_REFERENCE.md)** - One-page cheat sheet
- **[Check Script](./scripts/check-deployment-config.py)** - Configuration validator

---

**Still stuck?** Create a GitHub issue with:
1. Error message
2. Browser console output (F12)
3. Result of `curl https://hiremebahamas.vercel.app/api/health`
4. Vercel Functions logs (if accessible)

# 🚀 HireMeBahamas Deployment Quick Reference Card

## 📋 GitHub Secrets Checklist

Add these at: https://github.com/cliffcho242/HireMeBahamas/settings/secrets/actions

```
☐ VERCEL_TOKEN          → Get from: https://vercel.com/account/tokens
☐ VERCEL_ORG_ID         → Vercel → Settings → Team ID
☐ VERCEL_PROJECT_ID     → Project → Settings → Project ID
☐ DATABASE_URL          → Railway/Render PostgreSQL connection string
☐ SECRET_KEY            → Generate: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
☐ JWT_SECRET_KEY        → Generate: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Optional (for Railway backend):
```
☐ RAILWAY_TOKEN         → https://railway.app/account/tokens
☐ RAILWAY_PROJECT_ID    → Railway → Project Settings
```

## ⚙️ Vercel Environment Variables

Add these at: Vercel Dashboard → Project → Settings → Environment Variables

```
DATABASE_URL       = postgresql://user:pass@host:5432/db?sslmode=require
SECRET_KEY         = [same as GitHub secret]
JWT_SECRET_KEY     = [same as GitHub secret]  
ENVIRONMENT        = production
```

## 🔗 Important Links

| Resource | URL |
|----------|-----|
| GitHub Secrets | https://github.com/cliffcho242/HireMeBahamas/settings/secrets/actions |
| Vercel Dashboard | https://vercel.com/dashboard |
| Vercel Tokens | https://vercel.com/account/tokens |
| Railway Dashboard | https://railway.app/dashboard |
| Railway Tokens | https://railway.app/account/tokens |

## 🧪 Testing Commands

```bash
# Check configuration
python3 scripts/check-deployment-config.py

# Test health endpoint
curl https://hiremebahamas.vercel.app/api/health

# Test auth endpoint (should return 401)
curl https://hiremebahamas.vercel.app/api/auth/me

# Generate secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📝 Database URL Format

### Railway PostgreSQL
```
postgresql://postgres:PASSWORD@containers-us-west-XXX.railway.app:7432/railway?sslmode=require
```

### Render PostgreSQL
```
postgresql://user:PASSWORD@dpg-xxx-a.render.com/dbname?sslmode=require
```

**Important:** Always add `?sslmode=require` at the end!

## ✅ Deployment Verification

After deployment, verify:

1. ☐ GitHub Actions workflow completed successfully
2. ☐ Vercel deployment shows as "Ready"
3. ☐ https://hiremebahamas.vercel.app loads
4. ☐ https://hiremebahamas.vercel.app/api/health returns 200
5. ☐ Health check shows database: "connected"
6. ☐ Can sign in with: admin@hiremebahamas.com / AdminPass123!
7. ☐ After sign-in, redirected to homepage
8. ☐ User profile appears in top-right corner

## 🚨 Common Errors & Quick Fixes

| Error | Quick Fix |
|-------|-----------|
| "VERCEL_TOKEN not set" | Add token to GitHub Secrets |
| "Database connection failed" | Check DATABASE_URL in Vercel |
| "Invalid credentials" | Verify database is accessible |
| "Network Error" | Backend not deployed - check logs |
| "Token expired" | SECRET_KEY mismatch - must be same everywhere |

## 📖 Full Documentation

For detailed instructions, see: **[FIX_SIGN_IN_DEPLOYMENT_GUIDE.md](./FIX_SIGN_IN_DEPLOYMENT_GUIDE.md)**

## 🔄 Deployment Workflow

1. Configure GitHub Secrets (above) ✓
2. Configure Vercel Environment Variables (above) ✓
3. Push to main branch or re-run workflow ✓
4. Wait for GitHub Actions to complete (~3 min) ✓
5. Test sign-in at Vercel URL ✓
6. Done! 🎉

---

**Need Help?** Check the logs:
- GitHub Actions: https://github.com/cliffcho242/HireMeBahamas/actions
- Vercel Functions: Vercel Dashboard → Deployments → Functions
- Browser Console: Press F12 → Console tab

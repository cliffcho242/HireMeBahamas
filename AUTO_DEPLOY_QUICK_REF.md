# 🚀 Quick Auto-Deploy Reference

## 📦 Required GitHub Secrets

Add these secrets in: **GitHub Repository → Settings → Secrets and variables → Actions**

### For Vercel (Frontend):
```
VERCEL_TOKEN          → Get from: https://vercel.com/account/tokens
VERCEL_ORG_ID        → Get from: vercel link (in .vercel/project.json)
VERCEL_PROJECT_ID    → Get from: vercel link (in .vercel/project.json)
VITE_API_URL         → Your backend URL (optional, has default)
```

### For Railway (Backend):
```
RAILWAY_TOKEN        → Get from: https://railway.app/account (Tokens section)
RAILWAY_PROJECT_ID   → Get from: railway status (after railway link)
```

### For Render (Alternative Backend):
```
RENDER_DEPLOY_HOOK   → Get from: Render Dashboard → Service → Settings → Deploy Hook
```

## 🎯 Quick Setup Commands

### Get Vercel IDs:
```bash
cd frontend
npm i -g vercel
vercel link
cat .vercel/project.json
```

### Get Railway Project ID:
```bash
curl -fsSL https://railway.app/install.sh | sh
railway login
railway link
railway status
```

## 🔄 Deployment Workflows

| Workflow | Triggers | What it deploys |
|----------|----------|-----------------|
| `deploy-frontend.yml` | Push to main (frontend/ changes) | Frontend → Vercel |
| `deploy-backend.yml` | Push to main (backend changes) | Backend → Railway |
| `deploy-backend-render.yml` | Push to main (backend changes) | Backend → Render |
| `ci.yml` | Push/PR to main | Runs tests & builds |

## ⚡ Manual Deployment

Go to: **GitHub → Actions → Select Workflow → Run workflow**

## 📊 Check Deployment Status

- **GitHub**: Repository → Actions tab
- **Vercel**: https://vercel.com/dashboard
- **Railway**: https://railway.app/dashboard
- **Render**: https://dashboard.render.com

## 🔥 Quick Deploy

```bash
# Make changes
git add .
git commit -m "Your changes"
git push origin main

# Auto-deploy triggers automatically! 🎉
```

## 📝 Notes

- Frontend deploys only when `frontend/` files change
- Backend deploys only when backend files change
- CI runs on every push and pull request
- Manual triggers available via Actions tab
- Choose either Railway OR Render for backend (not both)

---

**For detailed setup instructions, see: [AUTO_DEPLOY_SETUP.md](./AUTO_DEPLOY_SETUP.md)**

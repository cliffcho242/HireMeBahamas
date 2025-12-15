# Deployment Checklist - FINAL SPEED ARCHITECTURE

Use this checklist to ensure a successful deployment of the FINAL SPEED ARCHITECTURE.

## Pre-Deployment Checklist

### 1. Repository Setup
- [ ] Code is pushed to GitHub main branch
- [ ] All tests pass locally
- [ ] No sensitive data in repository (check `.gitignore`)
- [ ] Dependencies are up to date (`package.json`, `requirements.txt`)

### 2. Accounts Created
- [ ] GitHub account with repository access
- [ ] Vercel account created and connected to GitHub
- [ ] Render account created
- [ ] Neon account created

### 3. Secrets Generated
- [ ] `SECRET_KEY` generated (32+ characters)
- [ ] `JWT_SECRET_KEY` generated (32+ characters)
- [ ] Both secrets stored securely (password manager)

Generate secrets:
```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

---

## Database Setup (Neon PostgreSQL)

### 1. Create Neon Project
- [ ] Logged into [neon.tech](https://neon.tech)
- [ ] Created new project named `hiremebahamas`
- [ ] Selected region: `US West` (or closest to Render Oregon)
- [ ] PostgreSQL version: 16 (latest)

### 2. Get Connection String
- [ ] Copied connection string from Neon dashboard
- [ ] Verified format includes:
  - [ ] Username
  - [ ] Password
  - [ ] Hostname (ep-xxxxx.us-west-2.aws.neon.tech)
  - [ ] Port (:5432)
  - [ ] Database name
  - [ ] SSL mode (?sslmode=require)

Example format:
```
postgresql://user:password@ep-xxxxx.us-west-2.aws.neon.tech:5432/hiremebahamas?sslmode=require
```

### 3. Verify Connection
- [ ] Test connection locally (optional):
```bash
export DATABASE_URL="<your-neon-connection-string>"
cd backend
python -c "from app.database import engine; print('✓ Connection successful')"
```

---

## Backend Deployment (Render)

### 1. Create Render Web Service
- [ ] Logged into [dashboard.render.com](https://dashboard.render.com)
- [ ] Clicked "New +" → "Web Service"
- [ ] Connected GitHub repository
- [ ] Selected `HireMeBahamas` repository

### 2. Configure Service Settings
- [ ] Name: `hiremebahamas-backend`
- [ ] Region: `Oregon`
- [ ] Branch: `main`
- [ ] Root Directory: (blank)
- [ ] Runtime: `Python 3`
- [ ] Build Command: `pip install -r backend/requirements.txt`
- [ ] Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`

### 3. Select Plan
- [ ] Plan: **Standard** ($25/month)
- [ ] ⚠️ Important: Standard plan required for Always On

### 4. Configure Environment Variables
Add these in Render Dashboard → Environment:

**Required Variables**:
- [ ] `ENVIRONMENT=production`
- [ ] `DATABASE_URL=<neon-connection-string>`
- [ ] `SECRET_KEY=<your-generated-secret>`
- [ ] `JWT_SECRET_KEY=<your-generated-jwt-secret>`
- [ ] `FRONTEND_URL=https://hiremebahamas.vercel.app` (update after Vercel deployment)
- [ ] `PYTHONUNBUFFERED=true`
- [ ] `PYTHON_VERSION=3.12.0`

**Database Configuration**:
- [ ] `DB_POOL_SIZE=5`
- [ ] `DB_MAX_OVERFLOW=10`
- [ ] `DB_POOL_TIMEOUT=30`
- [ ] `DB_POOL_RECYCLE=3600`
- [ ] `DB_ECHO=false`

**Performance Settings**:
- [ ] `WORKERS=1`
- [ ] `WORKER_CLASS=uvicorn.workers.UvicornWorker`
- [ ] `KEEPALIVE=5`
- [ ] `TIMEOUT=30`
- [ ] `FORWARDED_ALLOW_IPS=*`

### 5. Configure Health Check
In Render Dashboard → Settings → Health Check:

⚠️ **CRITICAL**: Path must match exactly (case-sensitive)

Choose ONE of these options:
- [ ] **Option 1 (Recommended)**: Health Check Path: `/health`
- [ ] **Option 2 (With API prefix)**: Health Check Path: `/api/health`

Additional settings:
- [ ] Grace Period: `60` seconds
- [ ] Health Check Timeout: `10` seconds
- [ ] Health Check Interval: `30` seconds

**Available endpoints:**
- `/health` - Instant health check (no database dependency)
- `/api/health` - Alternative with `/api` prefix
- `/ready` - Readiness check (includes database connectivity)
- `/live` - Liveness probe

### 6. Deploy
- [ ] Clicked "Create Web Service"
- [ ] Waited for deployment (5-10 minutes)
- [ ] Status shows "Live"

### 7. Verify Backend
Test the deployed backend:
- [ ] Health check: `curl https://hiremebahamas-backend.onrender.com/health`
  - Should return: `{"ok": true}`
- [ ] Alternative health check: `curl https://hiremebahamas-backend.onrender.com/api/health`
  - Should return: `{"status": "ok"}`
- [ ] Check Render logs for errors
- [ ] Verify Render dashboard shows service as "Live"

---

## Database Initialization

### 1. Create Tables
Choose one option:

**Option A: Using Render Shell**
- [ ] In Render Dashboard → Your service → "Shell" tab
- [ ] Run: `cd backend && python create_all_tables.py`
- [ ] Verify: Tables created successfully

**Option B: Locally**
- [ ] Set DATABASE_URL locally
- [ ] Run: `cd backend && python create_all_tables.py`
- [ ] Verify: Tables created successfully

### 2. Verify Tables (Optional)
- [ ] Connect to Neon via SQL editor
- [ ] Verify tables exist: `users`, `posts`, etc.

---

## Frontend Deployment (Vercel)

### 1. Import Project
- [ ] Logged into [vercel.com](https://vercel.com)
- [ ] Clicked "New Project"
- [ ] Imported `HireMeBahamas` from GitHub

### 2. Configure Build Settings
- [ ] Framework Preset: `Vite`
- [ ] Root Directory: `frontend`
- [ ] Build Command: `npm run build`
- [ ] Output Directory: `dist`
- [ ] Install Command: `npm install`

### 3. Configure Environment Variables
Add in Vercel Dashboard → Settings → Environment Variables:

**Option A: Separate Backend (Recommended)**
- [ ] `VITE_API_URL=https://hiremebahamas-backend.onrender.com`

**Option B: Same-Origin**
- [ ] No environment variables needed (uses relative paths)

### 4. Deploy
- [ ] Clicked "Deploy"
- [ ] Waited for deployment (2-3 minutes)
- [ ] Deployment successful
- [ ] Noted Vercel URL (e.g., `https://hiremebahamas-xxxx.vercel.app`)

### 5. Update Backend CORS
- [ ] Updated Render environment variable:
  - `FRONTEND_URL=<your-vercel-url>`
- [ ] Saved (triggers Render redeploy)
- [ ] Waited for Render to redeploy

---

## Post-Deployment Verification

### 1. Frontend Tests
Visit your Vercel URL and test:
- [ ] Homepage loads correctly
- [ ] Static assets load (images, CSS)
- [ ] No console errors (F12 → Console)
- [ ] No 404 errors in Network tab

### 2. Backend API Tests
Test API endpoints:
- [ ] Health: `curl https://hiremebahamas-backend.onrender.com/health`
- [ ] API docs (if enabled): `https://hiremebahamas-backend.onrender.com/docs`

### 3. Full Integration Tests
Test complete user flows:
- [ ] User registration works
- [ ] User login works
- [ ] Create a post
- [ ] Like/unlike a post
- [ ] Comment on a post
- [ ] Test on mobile device

### 4. Performance Tests
- [ ] Frontend load time <2s
- [ ] API response time <500ms
- [ ] No 502 errors
- [ ] No CORS errors

### 5. Security Verification
- [ ] HTTPS enabled on all domains
- [ ] Security headers present (check browser DevTools)
- [ ] No secrets exposed in frontend code
- [ ] Database uses SSL (`?sslmode=require` in DATABASE_URL)

---

## Monitoring Setup

### 1. Vercel Analytics
- [ ] Enabled Vercel Analytics in project settings
- [ ] Verify metrics are collecting

### 2. Render Monitoring
- [ ] Check Render Metrics tab
- [ ] Set up email alerts for downtime (optional)

### 3. Neon Monitoring
- [ ] Check Neon monitoring dashboard
- [ ] Verify connection counts are reasonable
- [ ] Monitor storage usage

---

## Optional Enhancements

### Custom Domain (Optional)
- [ ] Domain purchased
- [ ] Added to Vercel project
- [ ] DNS configured
- [ ] SSL certificate verified
- [ ] Updated `FRONTEND_URL` in Render

### Error Tracking (Recommended)
- [ ] Sentry account created
- [ ] Sentry DSN configured in environment variables
- [ ] Error tracking verified

### Backups (Important)
- [ ] Neon point-in-time recovery enabled
- [ ] Backup schedule documented
- [ ] Recovery procedure tested

---

## Troubleshooting

### Backend Not Starting
- [ ] Check Render logs for errors
- [ ] Verify all environment variables are set
- [ ] Verify DATABASE_URL format
- [ ] Check build command completed successfully

### Frontend Can't Connect to Backend
- [ ] Verify CORS settings (FRONTEND_URL in Render)
- [ ] Check browser console for CORS errors
- [ ] Verify VITE_API_URL in Vercel (if using Option A)
- [ ] Test backend health endpoint directly

### Database Connection Fails
- [ ] Verify Neon project is active
- [ ] Check DATABASE_URL format
- [ ] Ensure `?sslmode=require` is present
- [ ] Test connection from Render shell

### 502 Errors on Render
- [ ] Verify Standard plan is selected (not Starter)
- [ ] Check health check endpoint responds
- [ ] Verify start command is correct
- [ ] Check Render logs for startup errors

---

## Success Criteria

✅ **Deployment is successful when**:

1. **Frontend**:
   - Loads in <2 seconds globally
   - No console errors
   - All static assets load correctly

2. **Backend**:
   - Health check returns 200 OK
   - Always responds (no cold starts)
   - API responses in <500ms

3. **Database**:
   - Connections established successfully
   - Queries execute quickly (<50ms)
   - SSL/TLS encryption active

4. **Integration**:
   - Users can register and login
   - Posts can be created and viewed
   - Real-time features work
   - No CORS errors

5. **Security**:
   - HTTPS everywhere
   - Security headers active
   - Secrets not exposed
   - Database connections encrypted

---

## Post-Deployment Tasks

### Immediate (Day 1)
- [ ] Monitor for errors in logs
- [ ] Test all critical user flows
- [ ] Verify performance metrics
- [ ] Document any issues

### Short-term (Week 1)
- [ ] Review monitoring dashboards daily
- [ ] Collect user feedback
- [ ] Optimize slow queries
- [ ] Set up automated backups

### Long-term (Month 1)
- [ ] Review and optimize costs
- [ ] Scale resources if needed
- [ ] Implement additional monitoring
- [ ] Plan next features

---

## Support Resources

- **Architecture Guide**: [FINAL_SPEED_ARCHITECTURE.md](./FINAL_SPEED_ARCHITECTURE.md)
- **Quick Start**: [QUICK_START_FINAL_ARCHITECTURE.md](./QUICK_START_FINAL_ARCHITECTURE.md)
- **Vercel Docs**: https://vercel.com/docs
- **Render Docs**: https://render.com/docs
- **Neon Docs**: https://neon.tech/docs

---

**🎉 Congratulations on deploying the FINAL SPEED ARCHITECTURE!**

*Fast. Stable. Global. Scalable. Industry-Standard.*

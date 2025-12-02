# Vercel Deployment - Quick Reference

## 🚀 Deploy in 10 Minutes

### 1. Push to GitHub
```bash
git add .
git commit -m "Vercel migration complete"
git push origin main
```

### 2. Configure Vercel (One-Time Setup)

Go to https://vercel.com/dashboard and:

1. **Import Git Repository**
   - Click "Add New..." → "Project"
   - Select your GitHub repository
   - Click "Import"

2. **Configure Build Settings** (Auto-detected)
   - Framework Preset: Vite
   - Root Directory: `./`
   - Build Command: Auto-detected
   - Output Directory: Auto-detected

3. **Add Environment Variables**
   ```
   DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
   SECRET_KEY=your-secret-key
   JWT_SECRET=your-jwt-secret
   ENVIRONMENT=production
   ```

4. **Click "Deploy"**

### 3. Verify Deployment (< 2 Minutes)

```bash
# Health check
curl https://your-app.vercel.app/api/health
# Expected: {"status":"healthy","platform":"vercel-serverless",...}

# Test on phone
# Open: https://your-app.vercel.app
# Try login - should be fast (<200ms)
```

### 4. Delete Render Services

1. Go to https://dashboard.render.com
2. Services → [Your Backend Service] → Settings
3. Scroll down → "Delete Service"
4. Confirm deletion
5. ✅ $0 monthly bill

---

## 📱 Test Checklist

After deployment, verify:

- [ ] Frontend loads at https://your-app.vercel.app
- [ ] `/api/health` responds in <200ms
- [ ] Login works on phone
- [ ] Job listings load
- [ ] User profiles display
- [ ] Image uploads work
- [ ] Real-time messaging works

---

## 🔧 Key Files

| File | Purpose |
|------|---------|
| `vercel.json` | Root config - routes API to backend |
| `api/main.py` | Serverless backend entry point |
| `api/requirements.txt` | Python dependencies |
| `frontend/vercel.json` | Frontend config (security headers) |
| `frontend/.env.example` | Environment variable template |

---

## 🐛 Quick Troubleshooting

### Problem: API returns 500

**Fix**: Check logs
```bash
vercel logs [deployment-url]
```

### Problem: Database connection failed

**Fix**: Verify environment variables
```bash
vercel env ls
vercel env add DATABASE_URL production
```

### Problem: Cold start slow (>1s)

**Normal**: First request after idle period  
**Warm requests**: <200ms

### Problem: Module not found

**Fix**: Add to `api/requirements.txt`
```bash
echo "missing-package==1.0.0" >> api/requirements.txt
git commit -am "Add missing dependency"
git push
```

---

## 📊 Expected Performance

| Metric | Target | Typical |
|--------|--------|---------|
| Cold Start | <1s | 500ms |
| Warm Response | <200ms | 100-150ms |
| Database Query | <50ms | 20-30ms |
| Full Page Load | <2s | 1.2s |

---

## 🎯 Vercel URLs

After deployment:

- **Production**: `https://your-app.vercel.app`
- **API Health**: `https://your-app.vercel.app/api/health`
- **API Docs**: `https://your-app.vercel.app/docs`
- **Dashboard**: `https://vercel.com/dashboard`

---

## 💰 Cost Breakdown

| Resource | Cost |
|----------|------|
| Frontend Hosting | $0 (Free tier) |
| Backend Serverless | $0 (Free tier: 100GB, 100 invocations/day) |
| SSL/HTTPS | $0 (Included) |
| Global CDN | $0 (Included) |
| **Total** | **$0/month** |

*Free tier limits:*
- 100GB bandwidth
- 100 serverless function invocations per day
- Unlimited static requests
- 1000 build minutes/month

**For most apps, this is plenty!**

---

## 🔐 Environment Variables Reference

### Required
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname
```

### Recommended
```bash
SECRET_KEY=your-secret-key-32-chars-min
JWT_SECRET=your-jwt-secret-32-chars-min
ENVIRONMENT=production
```

### Optional
```bash
REDIS_URL=redis://...
SENTRY_DSN=https://...
CLOUDINARY_URL=cloudinary://...
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

---

## 📚 Resources

- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Full Migration Guide**: See `VERCEL_MIGRATION_GUIDE.md`
- **Support**: Open GitHub issue

---

## ✅ Success Criteria

Your migration is successful when:

1. ✅ Frontend loads on phone
2. ✅ Login works (<200ms)
3. ✅ Vercel logs show requests
4. ✅ Render services deleted
5. ✅ Monthly bill = $0

**Time to complete**: ~10 minutes  
**Status**: Ready to deploy! 🚀

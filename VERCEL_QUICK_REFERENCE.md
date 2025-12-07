# Vercel Configuration Quick Reference

## TL;DR - For Vercel Deployment

### If you're deploying to Vercel with serverless backend:

**DO THIS:**
```bash
# 1. Set these in Vercel Dashboard → Environment Variables
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
SECRET_KEY=your-random-32-char-secret
JWT_SECRET_KEY=your-random-32-char-jwt-secret

# 2. Do NOT set VITE_API_URL
# (Frontend automatically detects Vercel and uses same-origin)

# 3. Deploy
git push origin main
```

**VERIFY:**
```bash
# Check these URLs after deployment:
https://your-project.vercel.app/api/health
# Should return: {"status":"healthy","platform":"vercel-serverless"}

https://your-project.vercel.app
# Should load the frontend
```

That's it! ✅

---

## Environment Variables Setup

### Required Backend Variables

Set these in **Vercel Dashboard** → **Settings** → **Environment Variables**:

| Variable | Value | Example |
|----------|-------|---------|
| `DATABASE_URL` | PostgreSQL connection string with asyncpg | `postgresql+asyncpg://user:pass@host:5432/db` |
| `SECRET_KEY` | Random 32+ character string | `your-random-secret-key-here` |
| `JWT_SECRET_KEY` | Random 32+ character string | `your-random-jwt-secret-here` |

### Optional Backend Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `ENVIRONMENT` | Deployment environment | `production` |
| `CLOUDINARY_URL` | Image upload service | `cloudinary://...` |
| `SENDBIRD_APP_ID` | Messaging service | `your-app-id` |

### Frontend Variables (Optional)

| Variable | When to Set | Example |
|----------|-------------|---------|
| `VITE_API_URL` | **Only** if using separate backend | `https://your-backend.railway.app` |
| `VITE_CLOUDINARY_CLOUD_NAME` | If using Cloudinary | `your-cloud-name` |
| `VITE_SENDBIRD_APP_ID` | If using Sendbird | `your-app-id` |
| `VITE_GOOGLE_CLIENT_ID` | If using Google OAuth | `your-google-client-id` |
| `VITE_APPLE_CLIENT_ID` | If using Apple OAuth | `your-apple-client-id` |

---

## Common Scenarios

### Scenario 1: Vercel Serverless Backend (Recommended)

**Configuration:**
- ✅ Set `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET_KEY`
- ✅ Do NOT set `VITE_API_URL`
- ✅ Frontend and backend on same domain

**How it works:**
- Frontend detects `.vercel.app` domain
- Automatically uses `window.location.origin` for API calls
- API available at `/api/*` on same domain

### Scenario 2: Separate Backend (Railway, etc.)

**Configuration:**
- ✅ Set all backend variables on backend service
- ✅ Set `VITE_API_URL` in Vercel to point to backend
- ✅ Ensure backend CORS allows your Vercel domain

**Example:**
```bash
# In Vercel Dashboard
VITE_API_URL=https://hiremebahamas.up.railway.app

# In Railway/Backend
# Add Vercel domain to CORS settings
```

### Scenario 3: Local Development

**Configuration:**
```bash
# frontend/.env
VITE_API_URL=http://localhost:8000

# Start backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Start frontend
cd frontend
npm run dev
```

---

## Validation Checklist

Use this checklist to verify your configuration:

### Pre-Deployment
- [ ] `vercel.json` exists and is valid JSON
- [ ] API rewrite configured: `/api/(*)` → `/api/index.py`
- [ ] `api/index.py` exists
- [ ] `api/backend_app/` directory exists
- [ ] `frontend/src/services/api.ts` has Vercel detection

### Post-Deployment
- [ ] `/api/health` returns `{"status":"healthy"}`
- [ ] `/api/ready` shows database connected
- [ ] Frontend loads successfully
- [ ] Browser console shows correct API URL
- [ ] User can register/login

### Quick Validation Script
```bash
# Run from repository root
python3 validate_vercel_config.py

# Test deployed site
python3 validate_vercel_config.py https://your-project.vercel.app
```

---

## Troubleshooting

### Issue: 404 on API requests

**Check:**
1. Is `api/index.py` present?
2. Is `vercel.json` rewrite correct?
3. Are there Python errors in Vercel logs?

**Fix:**
```bash
# Verify files exist
ls -la api/index.py api/backend_app/

# Check Vercel logs
vercel logs --follow
```

### Issue: CORS errors

**For Vercel Serverless:**
- Should never happen (same-origin)
- If it does, check API is using correct origin

**For Separate Backend:**
```python
# Add to backend CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-project.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Environment variable not working

**Check:**
1. Variable name starts with `VITE_` for frontend
2. Set in correct environment (Production/Preview/Dev)
3. Redeploy after setting variable
4. Clear browser cache

### Issue: Database connection failed

**Check:**
1. `DATABASE_URL` format: `postgresql+asyncpg://...`
2. Database allows connections from Vercel IPs
3. Test with `/api/ready` endpoint

---

## File Structure

```
HireMeBahamas/
├── vercel.json                          # Vercel configuration
├── api/                                 # Serverless backend
│   ├── index.py                        # Main API handler
│   ├── backend_app/                    # Backend code
│   └── requirements.txt                # Python dependencies
└── frontend/                           # React frontend
    ├── .env.example                    # Example env vars
    ├── .env.production                 # Production documentation
    ├── src/
    │   ├── services/api.ts            # API client with auto-detection
    │   └── utils/backendRouter.ts     # Smart routing logic
    └── vite.config.ts                  # Vite configuration
```

---

## API Endpoints

After deployment, these endpoints are available:

| Endpoint | Purpose | Public |
|----------|---------|--------|
| `/api/health` | Health check | ✅ |
| `/api/ready` | Database connectivity | ✅ |
| `/api/auth/login` | User login | ✅ |
| `/api/auth/register` | User registration | ✅ |
| `/api/auth/profile` | Get user profile | 🔒 |
| `/api/jobs` | Job listings | 🔒 |
| `/api/posts` | Social posts | 🔒 |
| `/api/messages` | Messaging | 🔒 |

🔒 = Requires authentication (JWT token)

---

## Resources

### Documentation
- **[VERCEL_FRONTEND_BACKEND_SETUP.md](./VERCEL_FRONTEND_BACKEND_SETUP.md)** - Complete setup guide
- **[VERCEL_DEPLOYMENT_GUIDE.md](./VERCEL_DEPLOYMENT_GUIDE.md)** - Full deployment walkthrough
- **[VERCEL_MIGRATION_GUIDE.md](./VERCEL_MIGRATION_GUIDE.md)** - Migrating from other platforms
- **[VERCEL_POSTGRES_SETUP.md](./VERCEL_POSTGRES_SETUP.md)** - Database configuration

### Tools
- **[validate_vercel_config.py](./validate_vercel_config.py)** - Configuration validator

### External Resources
- [Vercel Dashboard](https://vercel.com/dashboard)
- [Vercel Documentation](https://vercel.com/docs)
- [Vercel CLI](https://vercel.com/docs/cli)

---

## Getting Help

1. **Check API Health:** Visit `/api/health` first
2. **Review Logs:** Use `vercel logs --follow`
3. **Browser Console:** Check for API URL detection
4. **Run Validator:** `python3 validate_vercel_config.py`
5. **Create Issue:** If problems persist, create GitHub issue

---

**Last Updated:** December 2025
**Status:** ✅ Production Ready

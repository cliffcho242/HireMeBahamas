# Backend Connection Troubleshooting Guide

## 🔍 Quick Diagnostic Tool

**NEW**: Use the automated diagnostic tool to quickly identify issues:

```bash
python diagnostic/check_vercel_connection.py --url https://your-app.vercel.app --verbose
```

This will test:
- ✅ Frontend accessibility
- ✅ Backend API endpoints
- ✅ Database connections
- ✅ Configuration
- ✅ Security settings

And provide specific troubleshooting suggestions. See [diagnostic/README.md](diagnostic/README.md) for details.

---

## Issue: "Backend connection: Load failed"

### Quick Fix Checklist

1. **Check Backend Status**
   ```bash
   curl https://your-app.vercel.app/api/status
   ```

2. **Look for `backend_loaded: false`**
   - If true: Backend is working normally
   - If false: Backend running in fallback mode (limited functionality)

3. **Check `backend_error` field for details**
   ```json
   {
     "backend_loaded": false,
     "backend_error": "No module named 'backend_app.api'",
     "recommendation": "Backend running in limited mode..."
   }
   ```

### Common Causes and Solutions

#### 1. Missing Dependencies in Deployment
**Symptom**: `backend_error: "No module named 'XXX'"`

**Solution**:
- Verify `api/requirements.txt` includes all dependencies
- Check that Vercel is installing from the correct requirements file
- Ensure `mangum`, `fastapi`, `sqlalchemy`, etc. are listed

**Verify locally**:
```bash
cd api
pip install -r requirements.txt
python -c "from backend_app.api import auth"
```

#### 2. Import Path Issues
**Symptom**: `backend_error: "cannot import name 'auth' from 'backend_app.api'"`

**Solution**:
- Check that `api/backend_app/api/` directory exists
- Verify `__init__.py` files are present in all directories
- Ensure router modules (auth.py, posts.py, etc.) exist

**Directory structure should be**:
```
api/
├── index.py
├── requirements.txt
└── backend_app/
    ├── __init__.py
    ├── api/
    │   ├── __init__.py
    │   ├── auth.py
    │   ├── posts.py
    │   ├── jobs.py
    │   ├── users.py
    │   ├── messages.py
    │   └── notifications.py
    ├── core/
    └── models.py
```

#### 3. Database Connection Issues
**Symptom**: Backend loads but database operations fail

**Solution**:
- Set `DATABASE_URL` environment variable in Vercel
- Format: `postgresql://user:pass@host:5432/db?sslmode=require`
- Check `/api/status` for `database_connected: false`

#### 4. Missing Environment Variables
**Symptom**: Backend loads but auth fails

**Check Required Variables**:
```bash
# In Vercel Dashboard → Settings → Environment Variables
DATABASE_URL=postgresql://...
SECRET_KEY=<generate-random-32-chars>
JWT_SECRET_KEY=<generate-random-32-chars>
ENVIRONMENT=production
```

### Diagnostic Endpoints

#### 1. `/api/status` - Detailed Backend Status
Returns comprehensive status including:
- Backend module load status
- Database connectivity
- Feature capabilities
- Error details if in fallback mode

```bash
curl https://your-app.vercel.app/api/status
```

#### 2. `/health` or `/api/health` - Quick Health Check
Returns basic health information:
```bash
curl https://your-app.vercel.app/health
```

#### 3. `/api/diagnostic` - Full Diagnostics
**Development/Debug Only** - Set `DEBUG=true` for full details
```bash
curl https://your-app.vercel.app/api/diagnostic
```

### Frontend Integration

Update your frontend to check backend status:

```javascript
// Check backend status on app load
async function checkBackendConnection() {
  try {
    const response = await fetch(`${API_URL}/api/status`);
    const status = await response.json();
    
    if (!status.backend_loaded) {
      console.error('Backend Error:', status.backend_error);
      
      // Show user-friendly message
      showNotification({
        type: 'warning',
        title: 'Limited Functionality',
        message: 'Some features may be unavailable. We are working to restore full service.',
        details: status.recommendation
      });
      
      // Disable features that require backend
      disableFeatures(status.capabilities);
    }
    
    return status;
  } catch (error) {
    console.error('Cannot reach backend:', error);
    showNotification({
      type: 'error',
      title: 'Connection Failed',
      message: 'Unable to connect to the backend. Please check your internet connection.'
    });
  }
}

// Disable features based on capabilities
function disableFeatures(capabilities) {
  if (!capabilities.auth) {
    disableLogin();
    showGuestMode();
  }
  if (!capabilities.posts) {
    disablePostCreation();
  }
  // etc.
}
```

### Vercel Deployment Logs

1. Go to Vercel Dashboard → Your Project → Deployments
2. Click on the latest deployment
3. Click "View Function Logs"
4. Look for:
   ```
   ⚠️  Backend modules not available: [error details]
   Running in FALLBACK MODE with limited API functionality
   ```

### Railway Deployment Logs

1. Go to Railway Dashboard → Your Project
2. Click "View Logs"
3. Look for:
   ```
   🚀 Starting Gunicorn
   ✅ Backend modules imported successfully
   ```
   
   Or errors:
   ```
   ModuleNotFoundError: No module named 'XXX'
   ImportError: cannot import name 'YYY'
   ```

### Manual Testing

Test backend module imports locally:
```bash
cd /home/runner/work/HireMeBahamas/HireMeBahamas
python3 << 'EOF'
import sys
sys.path.insert(0, 'api')
sys.path.insert(0, 'api/backend_app')

try:
    from backend_app.api import auth, posts, jobs
    print("✅ All backend modules loaded successfully")
except Exception as e:
    print(f"✗ Error loading backend: {e}")
    import traceback
    traceback.print_exc()
EOF
```

### Resolution Steps

1. **Immediate**: Check `/api/status` endpoint
2. **Identify**: Read `backend_error` message
3. **Fix**: Based on error type:
   - Missing module → Update requirements.txt
   - Import error → Fix file structure
   - Database error → Check DATABASE_URL
4. **Redeploy**: Push changes to trigger new deployment
5. **Verify**: Check `/api/status` again

### Support

If issue persists after following this guide:
1. Check deployment logs in Vercel/Railway
2. Review `DEPLOYMENT_FIX_SUMMARY.md` for configuration details
3. Verify all environment variables are set
4. Check that both `requirements.txt` and `api/requirements.txt` are current

### Related Documentation
- `DEPLOYMENT_FIX_SUMMARY.md` - Complete deployment configuration guide
- `.env.example` - Environment variable reference
- `api/requirements.txt` - Required Python packages for serverless
- `requirements.txt` - Required Python packages for Railway

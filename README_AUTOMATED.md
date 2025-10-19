# HireBahamas Platform - Automated Launch Guide

## 🚀 Quick Start

### Option 1: Fully Automated Launch (Recommended)
Double-click `AUTO_LAUNCH_HIREBAHAMAS.bat` to automatically:
- Start the React frontend on http://localhost:3000
- Start the Flask backend on http://127.0.0.1:8008
- Run health checks to verify everything works
- Open your browser to the platform

### Option 2: Manual Launch
If you prefer manual control:

1. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend will be available at http://localhost:3000

2. **Start Backend:**
   ```bash
   python ULTIMATE_BACKEND_FIXED.py
   ```
   Backend will be available at http://127.0.0.1:8008

## 🔑 Admin Credentials
- **Email:** admin@hirebahamas.com
- **Password:** AdminPass123!

## 🧪 Health Checks

### Automated Health Check
Run `python automated_backend_health.py` to:
- Kill any stuck processes
- Start fresh backend
- Test all endpoints
- Verify login and posts functionality

### Manual Health Check
```python
# Test health endpoint
curl http://127.0.0.1:8008/health

# Test login
curl -X POST http://127.0.0.1:8008/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hirebahamas.com","password":"AdminPass123!"}'

# Test posts
curl http://127.0.0.1:8008/api/posts
```

## 🛠️ Troubleshooting

### Frontend Issues
- Ensure you're in the `frontend` directory when running `npm run dev`
- If port 3000 is busy, Vite will automatically use the next available port

### Backend Issues
- Run `python automated_backend_health.py` to restart backend cleanly
- Check that port 8008 is not blocked by firewall/antivirus
- Ensure no other Python processes are using the port

### Network Errors
- Backend must be running on port 8008
- Frontend makes requests to `http://127.0.0.1:8008` (not localhost)
- CORS is configured to allow requests from localhost:3000

## 📁 Project Structure
```
HireBahamas/
├── frontend/           # React/TypeScript/Vite app
├── ULTIMATE_BACKEND_FIXED.py  # Flask backend server
├── hirebahamas.db      # SQLite database
├── AUTO_LAUNCH_HIREBAHAMAS.bat  # Automated launcher
├── automated_backend_health.py  # Backend health checker
└── README.md           # This file
```

## 🎯 What's Working
- ✅ Backend health checks
- ✅ User authentication (admin login)
- ✅ Posts API with sample data
- ✅ CORS configuration
- ✅ Automated startup scripts
- ✅ Database with users and posts tables

## 🔄 Recent Fixes
- Fixed npm directory issues (must run from frontend folder)
- Automated backend restart and health monitoring
- Resolved login endpoint authentication
- Added comprehensive health check automation
- Fixed batch script freezing issues

---

**Need help?** Run the automated launcher first - it handles 90% of common issues automatically!
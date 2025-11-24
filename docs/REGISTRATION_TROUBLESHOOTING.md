# Registration Issue Troubleshooting Guide

## Quick Fix for "Registration Failed" Errors

If users are experiencing registration errors, follow these steps:

### 1. Automatic Fix (Recommended)

Run the automated dependency installation script:

```bash
# For system-wide installation (requires sudo)
sudo ./scripts/install-dependencies.sh

# Or check and auto-install missing dependencies
python3 scripts/check-dependencies.py --install
```

### 2. Manual Verification

Check if all dependencies are installed:

```bash
python3 scripts/check-dependencies.py
```

### 3. Test Registration

Verify the registration system is working:

```bash
# Test Flask backend (legacy)
python -m pytest test_registration.py -v

# Test FastAPI backend (current)
python test_registration_fastapi.py
```

## Common Issues and Solutions

### Issue 1: "Module not found" errors

**Symptoms:**
- `ImportError: No module named 'fastapi'`
- `ImportError: No module named 'jose'`
- `ImportError: No module named 'passlib'`

**Solution:**
```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### Issue 2: OAuth authentication fails

**Symptoms:**
- Google Sign-In doesn't work
- Apple Sign-In doesn't work

**Solution:**

1. Check OAuth dependencies:
```bash
pip install google-auth google-auth-oauthlib PyJWT
```

2. Verify environment variables are set:
```bash
# Backend .env file
GOOGLE_CLIENT_ID=your_google_client_id

# Frontend .env file
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_APPLE_CLIENT_ID=your_apple_client_id
```

### Issue 3: Database connection errors

**Symptoms:**
- `sqlalchemy.exc.OperationalError`
- `no such table: users`

**Solution:**

1. Initialize the database:
```bash
cd backend
python -c "
from app.database import init_db
import asyncio
asyncio.run(init_db())
"
```

2. Or use the migration scripts:
```bash
cd backend
python create_all_tables.py
```

### Issue 4: "Password hashing failed"

**Symptoms:**
- Registration hangs or fails with cryptography errors

**Solution:**

1. Install/reinstall bcrypt:
```bash
pip uninstall bcrypt
pip install bcrypt==4.1.2
```

2. Install system dependencies (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install -y build-essential libffi-dev python3-dev
```

### Issue 5: Frontend build fails

**Symptoms:**
- `npm ERR! ERESOLVE unable to resolve dependency tree`
- Missing React OAuth packages

**Solution:**

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

Or force install:
```bash
npm install --legacy-peer-deps
```

### Issue 6: CORS errors in browser

**Symptoms:**
- Registration request blocked by CORS policy
- "Access-Control-Allow-Origin" error

**Solution:**

1. Verify backend CORS configuration in `backend/app/main.py`:
```python
allow_origins=[
    "http://localhost:3000",
    "http://localhost:5173",
    # Add your frontend URL
]
```

2. Ensure frontend is using correct API URL in `.env`:
```bash
VITE_API_URL=http://localhost:8005
```

## Testing After Fix

After applying fixes, run these tests:

### 1. Backend Tests
```bash
# All registration tests
python -m pytest test_registration.py -v

# FastAPI registration tests
python test_registration_fastapi.py

# Quick dependency check
python3 scripts/check-dependencies.py --backend-only
```

### 2. Frontend Tests
```bash
cd frontend

# Install dependencies
npm ci

# Build frontend
npm run build

# Check dependencies
cd .. && python3 scripts/check-dependencies.py --frontend-only
```

### 3. Integration Test

Start both backend and frontend to test end-to-end:

```bash
# Terminal 1: Start backend
cd backend
python -m app.main

# Terminal 2: Start frontend
cd frontend
npm run dev
```

Then open browser to `http://localhost:5173` and try to register.

## Preventive Measures

To avoid registration issues in the future:

### 1. Use the dependency check workflow

The repository includes a GitHub Actions workflow that automatically checks dependencies:
- Located at `.github/workflows/dependency-check.yml`
- Runs on push/PR to main branch
- Can be manually triggered

### 2. Keep dependencies updated

```bash
# Check for outdated packages
pip list --outdated
npm outdated

# Update carefully
pip install --upgrade [package]
npm update [package]
```

### 3. Use virtual environments

```bash
# Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies in isolated environment
pip install -r requirements.txt
```

## Getting Help

If issues persist after trying these solutions:

1. **Check the logs:** Look at browser console and backend logs for specific errors
2. **Review documentation:** See `docs/DEPENDENCY_MANAGEMENT.md` for detailed info
3. **Run diagnostics:** Use `python3 scripts/check-dependencies.py` for detailed report
4. **Test endpoints:** Use the API docs at `http://localhost:8005/docs` to test registration directly

## Technical Details

### Registration Endpoints

**Standard Registration (Email/Password):**
```
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "freelancer",
  "location": "Nassau, Bahamas",
  "phone": "+1-242-555-1234"  // optional
}
```

**Google OAuth:**
```
POST /api/auth/oauth/google
{
  "token": "google_oauth_token",
  "user_type": "freelancer"  // optional
}
```

**Apple OAuth:**
```
POST /api/auth/oauth/apple
{
  "token": "apple_oauth_token",
  "user_type": "freelancer"  // optional
}
```

### Required Dependencies

**Backend:**
- fastapi >= 0.109.0
- sqlalchemy >= 2.0.25
- psycopg2-binary >= 2.9.9
- python-jose[cryptography] >= 3.3.0
- passlib[bcrypt] >= 1.7.4
- google-auth >= 2.27.0
- PyJWT >= 2.8.0
- pydantic >= 2.7.0

**Frontend:**
- react >= 18.2.0
- react-router-dom >= 7.9.4
- axios >= 1.6.5
- react-hook-form >= 7.50.0
- @react-oauth/google >= 0.12.2
- react-apple-signin-auth >= 1.1.2

## Success Indicators

Registration is working correctly when:

✅ All dependency checks pass
✅ Backend tests pass (17 tests in test_registration.py)
✅ FastAPI tests pass (test_registration_fastapi.py)
✅ Frontend builds without errors
✅ You can register via UI and API
✅ OAuth endpoints respond (not 404)
✅ JWT tokens are generated
✅ User data is saved to database

Run the full test suite to verify:
```bash
python test_registration_fastapi.py
```

Expected output:
```
✓ ALL TESTS PASSED!
Registration system is working correctly.
Dependencies are properly installed.
OAuth endpoints are configured.
```

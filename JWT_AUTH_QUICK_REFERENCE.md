# JWT AUTH BULLETPROOF — QUICK REFERENCE

## 🚀 ONE COMMAND COPY-PASTE

For **NEW projects** starting from scratch:

```bash
# Install dependencies
cd backend
pip install -r requirements_bulletproof.txt

# Copy reference implementations
cp app/core/security_bulletproof.py app/core/security.py
cp app/api/auth_bulletproof.py app/api/auth.py  
cp app/main_bulletproof.py app/main.py

# Setup environment
cp .env.bulletproof.example .env
# Edit .env and set SECRET_KEY and DATABASE_URL

# Run the app
uvicorn app.main:app --reload
```

## 📍 KEY ENDPOINTS

```bash
# Register
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "user"
}
# Returns: { access_token, token_type: "bearer", user: {...} }

# Login  
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
# Returns: { access_token, token_type: "bearer", user: {...} }

# Get current user (requires token)
GET /api/auth/me
Authorization: Bearer <your_jwt_token>
# Returns: { id, email, first_name, ... }
```

## 🔑 ENVIRONMENT VARIABLES

Required in `.env`:

```env
# Generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-secret-key-here

# PostgreSQL connection
DATABASE_URL=postgresql://username:password@host:5432/database

# Optional
BCRYPT_ROUNDS=10
ENVIRONMENT=production
```

## 🛡️ PROTECTED ROUTES

```python
from app.core.dependencies import get_current_user, get_current_user_optional
from app.models import User
from typing import Optional

# Requires authentication (401 if no token)
@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.first_name}!"}

# Optional authentication (returns None if no token)
@router.get("/public")
async def public_route(user: Optional[User] = Depends(get_current_user_optional)):
    if user:
        return {"message": f"Hello {user.first_name}!", "authenticated": True}
    return {"message": "Hello guest!", "authenticated": False}
```

## 💻 FRONTEND INTEGRATION

```javascript
// Register
const registerResponse = await fetch('/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePass123!',
    first_name: 'John',
    last_name: 'Doe'
  })
});
const { access_token, user } = await registerResponse.json();
localStorage.setItem('token', access_token);

// Login
const loginResponse = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePass123!'
  })
});
const { access_token, user } = await loginResponse.json();
localStorage.setItem('token', access_token);

// Use protected endpoint
const token = localStorage.getItem('token');
const meResponse = await fetch('/api/auth/me', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const currentUser = await meResponse.json();
```

## 🗄️ DATABASE SETUP

PostgreSQL schema:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);
```

## 🚢 VERCEL DEPLOYMENT

**Step 1:** Add env vars in Vercel Dashboard
- `SECRET_KEY` - Generate random string
- `DATABASE_URL` - Vercel Postgres connection string
- `ENVIRONMENT` - Set to "production"

**Step 2:** Create `vercel.json`:
```json
{
  "builds": [{ "src": "api/main.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/api/(.*)", "dest": "api/main.py" }]
}
```

**Step 3:** Create `api/main.py` (Vercel entry point):
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")
```

**Step 4:** Deploy:
```bash
vercel --prod
```

## ✅ VERIFICATION

```bash
# Test health
curl https://your-api.vercel.app/health

# Test register
curl -X POST https://your-api.vercel.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","first_name":"Test","last_name":"User"}'

# Test login (save the access_token from response)
curl -X POST https://your-api.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Test /me (use token from login)
curl https://your-api.vercel.app/api/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📚 DOCUMENTATION

- **Complete Code:** `JWT_AUTH_BULLETPROOF_CODE_BLOCKS.md`
- **Deployment Guide:** `VERCEL_JWT_DEPLOYMENT_CHECKLIST.md`
- **Implementation Summary:** `JWT_AUTH_IMPLEMENTATION_SUMMARY.md`
- **Integration Notes:** `JWT_AUTH_INTEGRATION_NOTES.md`

## 🔧 TROUBLESHOOTING

**Issue:** "No module named 'jose'"
```bash
pip install python-jose[cryptography]
```

**Issue:** 401 Unauthorized on valid token
- Check SECRET_KEY is same everywhere
- Check token format: `Bearer <token>`
- Check token not expired (default 30 days)

**Issue:** CORS errors
- Add frontend domain to `allow_origins` in main.py
- Set `allow_credentials=True` for auth

**Issue:** Database connection failed
- Check DATABASE_URL format
- For Vercel Postgres: `postgresql://...?sslmode=require`
- Test connection: `psql $DATABASE_URL`

## ✨ JWT AUTH IS NOW IMMORTAL

**Requirements delivered:**
1. ✅ dependencies.py (get_current_user + optional auth)
2. ✅ auth.py (login + register + /me)  
3. ✅ models/user.py (Pydantic + bcrypt)
4. ✅ requirements.txt (exact versions)
5. ✅ main.py (CORS + router include)
6. ✅ .env + example
7. ✅ 4-step deploy checklist

**Features:**
- ✅ python-jose[cryptography] + passlib[bcrypt]
- ✅ Works on Vercel Serverless
- ✅ 401 on invalid/expired token
- ✅ Optional auth for public routes
- ✅ /api/auth/login → returns JWT
- ✅ /api/auth/me → returns user

**MAKE JWT AUTH IMMORTAL. ✅ EXECUTED.**

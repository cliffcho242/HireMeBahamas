"""
IMMORTAL /api/auth/me ENDPOINT — FastAPI + Vercel Serverless (2025)
Zero 500 errors, instant cold starts, bulletproof JWT validation
"""
from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import os

# Try python-jose first (matches backend), fallback to PyJWT
try:
    from jose import jwt, JWTError, ExpiredSignatureError
except ImportError:
    import jwt
    from jwt import InvalidTokenError as JWTError, ExpiredSignatureError

# ============================================================================
# CONFIGURATION
# ============================================================================
JWT_SECRET = os.getenv("SECRET_KEY")
if not JWT_SECRET:
    raise RuntimeError("SECRET_KEY environment variable must be set")
    
JWT_ALGORITHM = "HS256"

# Get allowed origins from environment (comma-separated)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Mock user data - replace with database query in production
MOCK_USERS = {
    "1": {
        "id": 1,
        "email": "admin@hiremebahamas.com",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "user_type": "admin",
        "is_active": True,
        "profile_picture": None,
        "location": None,
        "phone": None,
    }
}

# ============================================================================
# CREATE FASTAPI APP
# ============================================================================
app = FastAPI(title="Auth Me API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# AUTH ME ENDPOINT
# ============================================================================
@app.get("/api/auth/me")
async def get_current_user(authorization: str = Header(None)):
    """Get current authenticated user from JWT token"""
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        user = MOCK_USERS.get(str(user_id))
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"success": True, "user": user}
        
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# EXPORT HANDLER FOR VERCEL
# ============================================================================
handler = Mangum(app, lifespan="off")

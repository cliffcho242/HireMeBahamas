import json
import os
from http.server import BaseHTTPRequestHandler

# Try python-jose first (matches backend), fallback to PyJWT (already in api/requirements.txt)
try:
    from jose import jwt, JWTError, ExpiredSignatureError
    JWT_LIB = "jose"
except ImportError:
    import jwt
    from jwt import InvalidTokenError as JWTError, ExpiredSignatureError
    JWT_LIB = "pyjwt"

# JWT Secret - matches backend configuration
# SECURITY: Must be set via environment variable in production
JWT_SECRET = os.environ.get("SECRET_KEY")
if not JWT_SECRET:
    # For development/testing only - NEVER use in production
    if os.environ.get("VERCEL_ENV") == "production":
        raise RuntimeError("SECRET_KEY environment variable must be set in production")
    JWT_SECRET = "your-secret-key-change-in-production"
    
JWT_ALGORITHM = "HS256"

# CORS configuration
# TODO: In production, restrict to specific domains
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*")

# Mock user data for demo - in production, fetch from database
# TODO: Replace with actual database query using environment DATABASE_URL
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


class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        # SECURITY: Restrict CORS to specific origins in production
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGINS)
        self.send_header(
            "Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS"
        )
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()
        return

    def do_GET(self):
        """Handle GET /api/auth/me - Get current authenticated user"""
        
        # Extract Authorization header
        auth_header = self.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            self._set_headers(401)
            response = {
                "error": "Unauthorized",
                "detail": "Missing or invalid authorization header"
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Extract token
        token = auth_header.replace("Bearer ", "")
        
        try:
            # Decode JWT token (unified for both jose and PyJWT)
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                self._set_headers(401)
                response = {
                    "error": "Unauthorized",
                    "detail": "Invalid token payload"
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Get user from mock data (in production, fetch from database)
            # TODO: Replace with actual database query
            user = MOCK_USERS.get(str(user_id))
            
            if not user:
                self._set_headers(404)
                response = {
                    "error": "Not Found",
                    "detail": "User not found"
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Return user data
            self._set_headers(200)
            response = {
                "success": True,
                "user": user
            }
            self.wfile.write(json.dumps(response).encode())
            
        except ExpiredSignatureError:
            self._set_headers(401)
            response = {
                "error": "Unauthorized",
                "detail": "Token has expired"
            }
            self.wfile.write(json.dumps(response).encode())
            
        except JWTError:
            self._set_headers(401)
            response = {
                "error": "Unauthorized", 
                "detail": "Invalid token"
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            # Log the full error (in production, send to logging service)
            import sys
            print(f"Unexpected error in /api/auth/me: {type(e).__name__}: {e}", file=sys.stderr)
            
            # Return generic error to client (don't leak internal details)
            self._set_headers(500)
            response = {
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred. Please try again later."
            }
            self.wfile.write(json.dumps(response).encode())

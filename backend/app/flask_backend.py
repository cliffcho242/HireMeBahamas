from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
from datetime import datetime, timedelta
from pathlib import Path
import logging
import sys
import traceback

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# Database path
DB_PATH = Path(__file__).parent.parent / "hiremebahamas.db"
logger.info(f"Database path: {DB_PATH}")
logger.info(f"Database exists: {DB_PATH.exists()}")

# Test database connection on startup
try:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    logger.info(f"Available tables: {tables}")
    conn.close()
    logger.info("Database connection test successful")
except Exception as e:
    logger.error(f"Database connection failed: {e}")
    logger.error(traceback.format_exc())

@app.route('/health')
def health():
    logger.info("Health check endpoint called")
    return jsonify({
        "status": "healthy", 
        "message": "HireMeBahamas API is running"
    })


@app.route('/')
def root():
    logger.info("Root endpoint called")
    return jsonify({
        "message": "Welcome to HireMeBahamas API",
        "version": "1.0.0",
        "health": "/health"
    })


@app.route('/auth/register', methods=['POST'])
def register():
    logger.info("Register endpoint called")
    return jsonify({
        "message": "Registration endpoint - ready for implementation"
    })


@app.route('/auth/login', methods=['POST'])
def login():
    logger.info("Login endpoint called")
    try:
        # Get JSON data from request
        data = request.get_json()
        logger.info(f"Login attempt for: {data.get('email') if data else 'no data'}")
        
        if not data or not data.get('email') or not data.get('password'):
            logger.warning("Missing email or password in login request")
            return jsonify({
                "success": False,
                "message": "Email and password are required"
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        
        # Connect to database
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Get user from database
        cursor.execute("""
            SELECT id, email, hashed_password, first_name, last_name, 
                   is_admin, role FROM users WHERE email = ?
        """, (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401
        
        # Verify password
        user_id, user_email, hashed_password, first_name, last_name, is_admin, role = user
        
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            # Create JWT token
            payload = {
                'user_id': user_id,
                'email': user_email,
                'role': role,
                'is_admin': bool(is_admin),
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            
            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": user_id,
                    "email": user_email,
                    "name": f"{first_name} {last_name}",
                    "role": role,
                    "is_admin": bool(is_admin)
                },
                "token": token
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Login error: {str(e)}"
        }), 500

@app.route('/admin/dashboard')
def admin_dashboard():
    return jsonify({
        "message": "Admin Dashboard",
        "features": [
            "User Management",
            "Job Postings Management", 
            "Platform Analytics",
            "Content Moderation"
        ],
        "admin_user": {
            "email": "admin@hiremebahamas.com",
            "role": "admin",
            "permissions": ["read", "write", "delete", "moderate"]
        }
    })

if __name__ == '__main__':
    logger.info("Starting Flask backend server...")
    logger.info("Server will be available at http://127.0.0.1:8005")
    try:
        # Use Flask development server instead of Waitress for reliability
        app.run(host='127.0.0.1', port=8005, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
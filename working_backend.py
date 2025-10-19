from flask import Flask, jsonify, request
import sqlite3
import bcrypt
import jwt
from datetime import datetime, timedelta
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# Database path
DB_PATH = Path(__file__).parent.parent / "hirebahamas.db"

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "message": "HireBahamas API is running"})

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                "success": False,
                "message": "Email and password are required"
            }), 400
        
        email = data['email']
        password = data['password']
        
        # Connect to database
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Query user
        cursor.execute("""
            SELECT id, email, hashed_password, first_name, last_name, is_admin, role 
            FROM users WHERE email = ?
        """, (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401
        
        user_id, user_email, hashed_password, first_name, last_name, is_admin, role = user
        
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            # Create JWT token
            payload = {
                'user_id': user_id,
                'email': user_email,
                'is_admin': bool(is_admin),
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            
            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                "success": True,
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": user_id,
                    "email": user_email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_admin": bool(is_admin),
                    "role": role
                }
            })
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

if __name__ == '__main__':
    print("Starting HireBahamas backend on http://127.0.0.1:8005")
    app.run(host='127.0.0.1', port=8005, debug=False)
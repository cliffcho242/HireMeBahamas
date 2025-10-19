from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:3001"])

SECRET_KEY = 'your-secret-key-here-change-in-production'

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'hiremebahamas.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "HireMeBahamas API is running",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query user
        cursor.execute("""
            SELECT id, email, password_hash, first_name, last_name,
                   user_type, is_active
            FROM users WHERE email = ?
        """, (email,))

        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({"success": False, "message": "Invalid email or password"}), 401

        user_id, user_email, password_hash, first_name, last_name, user_type, is_active = user

        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            # Create JWT token
            payload = {
                'user_id': user_id,
                'email': user_email,
                'is_admin': user_type == 'admin',
                'exp': datetime.utcnow() + timedelta(hours=24)
            }

            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

            return jsonify({
                "success": True,
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": user_id,
                    "email": user_email,
                    "username": user_email.split('@')[0],
                    "full_name": f"{first_name or ''} {last_name or ''}".strip(),
                    "is_active": bool(is_active)
                }
            }), 200
        else:
            return jsonify({"success": False, "message": "Invalid email or password"}), 401

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"success": False, "message": f"Login error: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting HireMeBahamas API server...")
    print("Server will be available at http://127.0.0.1:8080")

    app.run(
        host='127.0.0.1',
        port=9999,
        debug=False,
        use_reloader=False,
        threaded=False
    )
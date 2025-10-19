#!/usr/bin/env python3
"""Working Flask Backend - Final Version"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hirebahamas-secret-key-2024'

# Enable CORS
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:3004"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

DATABASE_PATH = os.path.join(os.getcwd(), 'hirebahamas.db')

def init_database():
    """Initialize the database"""
    print("Initializing database...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            user_type TEXT DEFAULT 'client',
            location TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if admin exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('admin@hirebahamas.com',))
    if cursor.fetchone()[0] == 0:
        # Create admin user
        password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        cursor.execute('''
            INSERT INTO users (email, password_hash, first_name, last_name, user_type)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin@hirebahamas.com', password_hash, 'Admin', 'User', 'admin'))
        print("✅ Admin user created")
    else:
        print("✅ Admin user exists")
    
    conn.commit()
    conn.close()
    print("✅ Database ready")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "OK", "message": "Backend is running"})

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        print(f"🔑 Login attempt: {email}")
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        
        # Get user from database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, password_hash, first_name, last_name, user_type FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            print(f"❌ User not found: {email}")
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), user[2]):
            # Generate JWT token
            payload = {
                'user_id': user[0],
                'email': user[1],
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
            
            print(f"✅ Login successful: {email}")
            
            return jsonify({
                "token": token,
                "user": {
                    "id": user[0],
                    "email": user[1],
                    "first_name": user[3],
                    "last_name": user[4],
                    "user_type": user[5]
                }
            }), 200
        else:
            print(f"❌ Invalid password: {email}")
            return jsonify({"error": "Invalid credentials"}), 401
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    return jsonify({"message": "Registration endpoint"}), 200

@app.route('/profile', methods=['GET'])
def profile():
    return jsonify({"message": "Profile endpoint"}), 200

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 HIREBAHAMAS BACKEND STARTING")
    print("="*60)
    
    init_database()
    
    print(f"📍 Server URL: http://127.0.0.1:8008")
    print(f"🔑 Admin Login: admin@hirebahamas.com / admin123")
    print(f"🌐 Health Check: http://127.0.0.1:8008/health")
    print(f"🔐 Login Endpoint: http://127.0.0.1:8008/api/auth/login")
    print("="*60)
    
    try:
        app.run(
            host='127.0.0.1',
            port=8008,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        input("Press Enter to exit...")
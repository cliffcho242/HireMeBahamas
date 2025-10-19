#!/usr/bin/env python3
"""Ultra Simple Login Backend - Guaranteed to Work"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hirebahamas-secret-key-2024'

# Enable CORS for all origins during development
CORS(app, origins=["*"], supports_credentials=True)

DATABASE_PATH = 'hirebahamas.db'

def init_database():
    """Initialize the database with admin user"""
    print("Initializing database...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create users table
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
    admin_exists = cursor.fetchone()[0] > 0
    
    if not admin_exists:
        # Create admin user
        password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        cursor.execute('''
            INSERT INTO users (email, password_hash, first_name, last_name, user_type)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin@hirebahamas.com', password_hash, 'Admin', 'User', 'admin'))
        print("✅ Admin user created")
    else:
        print("✅ Admin user already exists")
    
    conn.commit()
    conn.close()
    print("✅ Database ready")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "OK", "message": "Backend is running"})

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        print(f"Login attempt for: {email}")
        
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
        stored_hash = user[2]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            # Generate JWT token
            payload = {
                'user_id': user[0],
                'email': user[1],
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
            
            print(f"✅ Login successful for: {email}")
            
            return jsonify({
                "token": token,
                "user": {
                    "id": user[0],
                    "email": user[1],
                    "first_name": user[3],
                    "last_name": user[4],
                    "user_type": user[5]
                }
            })
        else:
            print(f"❌ Invalid password for: {email}")
            return jsonify({"error": "Invalid credentials"}), 401
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({"error": "Login failed"}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register endpoint"""
    return jsonify({"message": "Registration endpoint"}), 200

@app.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    return jsonify({"message": "Profile endpoint"}), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Ultra Simple Backend Running",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

if __name__ == '__main__':
    print("=== ULTRA SIMPLE BACKEND ===")
    print("Starting backend...")
    
    # Initialize database
    init_database()
    
    print("\n🚀 Server starting...")
    print("📍 URL: http://127.0.0.1:8008")
    print("🔑 Admin: admin@hirebahamas.com / admin123")
    print("=" * 50)
    
    app.run(host='127.0.0.1', port=8008, debug=False, use_reloader=False)
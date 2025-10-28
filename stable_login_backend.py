#!/usr/bin/env python3
"""
Stable Login Backend - Focused on login functionality without AI monitoring
"""
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import bcrypt
import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS

# Simple, stable backend for login testing
app = Flask(__name__)
CORS(
    app,
    origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
        "http://localhost:3003",
        "http://127.0.0.1:3003",
    ],
)

app.config["SECRET_KEY"] = "hirebahamas-secret-key-2024"

# Database setup
DB_PATH = Path(__file__).parent / "backend" / "hirebahamas.db"


def init_database():
    """Initialize database with admin user"""
    print("Initializing database...")

    # Ensure directory exists
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Create users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            username TEXT,
            full_name TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Create admin user
    admin_email = "admin@hirebahamas.com"
    cursor.execute("SELECT id FROM users WHERE email = ?", (admin_email,))
    existing_admin = cursor.fetchone()

    if not existing_admin:
        print("Creating admin user...")
        password_hash = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt())

        cursor.execute(
            """
            INSERT INTO users (email, password_hash, username, full_name, is_active)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                admin_email,
                password_hash.decode("utf-8"),
                "admin",
                "Platform Administrator",
                True,
            ),
        )
        print("Admin user created successfully")
    else:
        print("Admin user already exists")

    conn.commit()
    conn.close()
    print("Database initialization complete")


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return (
        jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "HireBahamas Login API",
            }
        ),
        200,
    )


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Login endpoint"""
    try:
        data = request.get_json()

        if not data or not data.get("email") or not data.get("password"):
            return jsonify({"error": "Email and password are required"}), 400

        email = data["email"].lower().strip()
        password = data["password"]

        print(f"Login attempt for: {email}")

        # Get user from database
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, email, password_hash, username, full_name, is_active
            FROM users WHERE email = ?
        """,
            (email,),
        )

        user = cursor.fetchone()
        conn.close()

        if not user:
            print(f"User not found: {email}")
            return jsonify({"error": "Invalid credentials"}), 401

        user_id, user_email, password_hash, username, full_name, is_active = user

        if not is_active:
            print(f"User account inactive: {email}")
            return jsonify({"error": "Account inactive"}), 401

        # Verify password
        try:
            password_valid = bcrypt.checkpw(
                password.encode("utf-8"), password_hash.encode("utf-8")
            )
        except Exception as e:
            print(f"Password verification error: {e}")
            return jsonify({"error": "Authentication error"}), 500

        if not password_valid:
            print(f"Invalid password for: {email}")
            return jsonify({"error": "Invalid credentials"}), 401

        # Generate JWT token
        try:
            token_payload = {
                "user_id": user_id,
                "email": user_email,
                "exp": datetime.utcnow() + timedelta(days=30),
            }

            token = jwt.encode(
                token_payload, app.config["SECRET_KEY"], algorithm="HS256"
            )

            print(f"Login successful for: {email}")

            return (
                jsonify(
                    {
                        "token": token,
                        "user": {
                            "id": user_id,
                            "email": user_email,
                            "username": username,
                            "full_name": full_name,
                        },
                        "message": "Login successful",
                    }
                ),
                200,
            )

        except Exception as e:
            print(f"Token generation error: {e}")
            return jsonify({"error": "Authentication error"}), 500

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/auth/verify", methods=["POST"])
def verify_token():
    """Verify JWT token"""
    try:
        data = request.get_json()
        token = data.get("token")

        if not token:
            return jsonify({"error": "Token required"}), 400

        payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])

        return (
            jsonify(
                {
                    "valid": True,
                    "user_id": payload["user_id"],
                    "email": payload["email"],
                }
            ),
            200,
        )

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        print(f"Token verification error: {e}")
        return jsonify({"error": "Token verification failed"}), 500


@app.route("/api/posts", methods=["GET"])
def get_posts():
    """Get posts endpoint - placeholder"""
    return jsonify([]), 200


@app.route("/api/posts", methods=["POST"])
def create_post():
    """Create post endpoint - placeholder"""
    return jsonify({"message": "Post created successfully"}), 201


@app.route("/api/auth/profile", methods=["GET"])
def get_profile():
    """Get user profile"""
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization token required"}), 401

        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])

        # Get user from database
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, email, username, full_name, is_active
            FROM users WHERE id = ?
        """,
            (payload["user_id"],),
        )

        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_id, email, username, full_name, is_active = user

        return (
            jsonify(
                {
                    "id": user_id,
                    "email": email,
                    "username": username,
                    "full_name": full_name,
                    "is_active": is_active,
                }
            ),
            200,
        )

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        print(f"Profile error: {e}")
        return jsonify({"error": "Profile fetch failed"}), 500


if __name__ == "__main__":
    print("Starting stable login backend...")
    print("Initializing database...")

    try:
        init_database()
        print("Database ready")

        print("Starting Flask server...")
        print("Server: http://127.0.0.1:8008")
        print("Health: http://127.0.0.1:8008/health")
        print("Login: http://127.0.0.1:8008/api/auth/login")
        print("Admin credentials: admin@hirebahamas.com / admin123")
        print("-" * 50)

        app.run(host="127.0.0.1", port=8008, debug=True, threaded=True)

    except Exception as e:
        print(f"Startup error: {e}")
        exit(1)

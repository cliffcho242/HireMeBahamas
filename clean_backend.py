#!/usr/bin/env python3
"""Clean Working Backend - No Unicode Issues"""

import os
import sqlite3
from datetime import datetime, timedelta

import bcrypt
import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
app.config["SECRET_KEY"] = "hirebahamas-secret-key-2024"

# Enable CORS
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://localhost:3002",
                "http://localhost:3003",
                "http://localhost:3004",
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    },
)

DATABASE_PATH = "hirebahamas.db"


def init_database():
    """Initialize the database"""
    print("Initializing database...")

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
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
    """
    )

    # Create posts table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """
    )

    # Create likes table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS post_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
            UNIQUE(user_id, post_id)
        )
    """
    )

    # Check if admin exists
    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE email = ?", ("admin@hirebahamas.com",)
    )
    if cursor.fetchone()[0] == 0:
        # Create admin user
        password_hash = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt())
        cursor.execute(
            """
            INSERT INTO users (email, password_hash, first_name, last_name, user_type)
            VALUES (?, ?, ?, ?, ?)
        """,
            ("admin@hirebahamas.com", password_hash, "Admin", "User", "admin"),
        )
        print("Admin user created")
    else:
        print("Admin user exists")

    conn.commit()
    conn.close()
    print("Database ready")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "OK", "message": "Backend is running"})


@app.route("/api/auth/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        email = data.get("email")
        password = data.get("password")

        print(f"Login attempt: {email}")

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        # Get user from database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, password_hash, first_name, last_name, user_type FROM users WHERE email = ?",
            (email,),
        )
        user = cursor.fetchone()
        conn.close()

        if not user:
            print(f"User not found: {email}")
            return jsonify({"error": "Invalid credentials"}), 401

        # Check password
        if bcrypt.checkpw(password.encode("utf-8"), user[2]):
            # Generate JWT token
            payload = {
                "user_id": user[0],
                "email": user[1],
                "exp": datetime.utcnow() + timedelta(hours=24),
            }
            token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")

            print(f"Login successful: {email}")

            return (
                jsonify(
                    {
                        "token": token,
                        "user": {
                            "id": user[0],
                            "email": user[1],
                            "first_name": user[3],
                            "last_name": user[4],
                            "user_type": user[5],
                        },
                    }
                ),
                200,
            )
        else:
            print(f"Invalid password: {email}")
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@app.route("/api/auth/register", methods=["POST"])
def register():
    return jsonify({"message": "Registration endpoint"}), 200


@app.route("/api/posts", methods=["GET"])
def get_posts():
    """Get all posts with user information"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Get posts with user info and like counts
        cursor.execute(
            """
            SELECT 
                p.id, p.content, p.image_url, p.created_at,
                u.id as user_id, u.first_name, u.last_name, u.email,
                COUNT(pl.id) as likes_count
            FROM posts p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN post_likes pl ON p.id = pl.post_id
            GROUP BY p.id
            ORDER BY p.created_at DESC
            LIMIT 50
        """
        )

        posts = []
        for row in cursor.fetchall():
            posts.append(
                {
                    "id": row[0],
                    "content": row[1],
                    "image_url": row[2],
                    "created_at": row[3],
                    "user": {
                        "id": row[4],
                        "first_name": row[5],
                        "last_name": row[6],
                        "email": row[7],
                    },
                    "likes_count": row[8],
                }
            )

        conn.close()
        return jsonify(posts), 200

    except Exception as e:
        print(f"Get posts error: {e}")
        return jsonify({"error": f"Failed to get posts: {str(e)}"}), 500


@app.route("/api/posts", methods=["POST"])
def create_post():
    """Create a new post"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "No token provided"}), 401

        token = auth_header.split(" ")[1]

        # Decode token
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        data = request.get_json()
        if not data or not data.get("content"):
            return jsonify({"error": "Content is required"}), 400

        content = data.get("content")
        image_url = data.get("image_url")

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO posts (user_id, content, image_url)
            VALUES (?, ?, ?)
        """,
            (user_id, content, image_url),
        )

        post_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return (
            jsonify({"message": "Post created successfully", "post_id": post_id}),
            201,
        )

    except Exception as e:
        print(f"Create post error: {e}")
        return jsonify({"error": f"Failed to create post: {str(e)}"}), 500


@app.route("/api/posts/<int:post_id>/like", methods=["POST"])
def like_post(post_id):
    """Like or unlike a post"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "No token provided"}), 401

        token = auth_header.split(" ")[1]

        # Decode token
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Check if like already exists
        cursor.execute(
            """
            SELECT id FROM post_likes WHERE user_id = ? AND post_id = ?
        """,
            (user_id, post_id),
        )

        existing_like = cursor.fetchone()

        if existing_like:
            # Unlike - remove the like
            cursor.execute(
                """
                DELETE FROM post_likes WHERE user_id = ? AND post_id = ?
            """,
                (user_id, post_id),
            )
            action = "unliked"
        else:
            # Like - add the like
            cursor.execute(
                """
                INSERT INTO post_likes (user_id, post_id)
                VALUES (?, ?)
            """,
                (user_id, post_id),
            )
            action = "liked"

        conn.commit()
        conn.close()

        return jsonify({"message": f"Post {action} successfully"}), 200

    except Exception as e:
        print(f"Like post error: {e}")
        return jsonify({"error": f"Failed to like post: {str(e)}"}), 500


@app.route("/profile", methods=["GET"])
def profile():
    return jsonify({"message": "Profile endpoint"}), 200


if __name__ == "__main__":
    print("HIREBAHAMAS BACKEND STARTING")
    print("=" * 50)

    init_database()

    print(f"Server URL: http://127.0.0.1:8008")
    print(f"Admin Login: admin@hirebahamas.com / admin123")
    print(f"Health Check: http://127.0.0.1:8008/health")
    print(f"Login Endpoint: http://127.0.0.1:8008/api/auth/login")
    print("=" * 50)

    try:
        app.run(
            host="127.0.0.1", port=8008, debug=False, use_reloader=False, threaded=True
        )
    except Exception as e:
        print(f"Server failed to start: {e}")
        input("Press Enter to exit...")

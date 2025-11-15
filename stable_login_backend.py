import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
import bcrypt
import jwt

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hirebahamas.db")
# IMPORTANT: Use a more secure, environment-variable-based secret in production
SECRET_KEY = "your-very-secret-and-secure-key" 

# --- Flask App Initialization ---
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},  # Be more restrictive in production
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# --- Database Initialization ---
def init_database():
    """Initializes the database and creates tables if they don't exist."""
    print("Initializing database...")
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Create users table with all necessary fields
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            user_type TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    print("Users table checked/created.")

    # Check for admin user and create if not present
    cursor.execute("SELECT * FROM users WHERE email = ?", ("admin@hiremebahamas.com",))
    if not cursor.fetchone():
        print("Creating admin user...")
        password = "AdminPass123!"
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        cursor.execute(
            """
            INSERT INTO users (email, password_hash, first_name, last_name, user_type, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "admin@hiremebahamas.com",
                hashed_password.decode("utf-8"),
                "Admin",
                "User",
                "admin",
                True,
            ),
        )
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")

    conn.commit()
    conn.close()
    print("Database initialization complete.")

# --- API Endpoints ---
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

@app.route("/api/auth/login", methods=["POST"])
def login():
    """Login endpoint."""
    try:
        data = request.get_json()
        if not data or not data.get("email") or not data.get("password"):
            return jsonify({"message": "Email and password are required"}), 400

        email = data["email"].lower().strip()
        password = data["password"]

        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_data = cursor.fetchone()
        conn.close()

        if not user_data:
            return jsonify({"message": "Invalid credentials"}), 401
        
        user_dict = dict(user_data)

        if not user_dict.get("is_active"):
            return jsonify({"message": "Account is not active"}), 401

        if not bcrypt.checkpw(password.encode("utf-8"), user_dict["password_hash"].encode("utf-8")):
            return jsonify({"message": "Invalid credentials"}), 401

        token_payload = {
            "user_id": user_dict["id"],
            "email": user_dict["email"],
            "exp": datetime.utcnow() + timedelta(days=30),
        }
        token = jwt.encode(token_payload, app.config["SECRET_KEY"], algorithm="HS256")

        return jsonify({
            "access_token": token,  # Fixed: Changed 'token' to 'access_token'
            "user": {
                "id": user_dict["id"],
                "email": user_dict["email"],
                "first_name": user_dict["first_name"],
                "last_name": user_dict["last_name"],
                "user_type": user_dict["user_type"],
            },
            "message": "Login successful",
        }), 200
        
    except Exception as e:
        print(f"[Login Error] {e}")
        return jsonify({"message": "Internal server error"}), 500

@app.route("/api/auth/register", methods=["POST"])
def register():
    """User registration endpoint."""
    try:
        data = request.get_json()
        required = ["email", "password", "first_name", "last_name", "user_type"]
        if not data or not all(field in data for field in required):
            return jsonify({"message": "Missing required fields"}), 400

        email = data["email"].lower().strip()
        
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"message": "An account with this email already exists"}), 409

        hashed_password = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        cursor.execute(
            "INSERT INTO users (email, password_hash, first_name, last_name, user_type) VALUES (?, ?, ?, ?, ?)",
            (email, hashed_password, data["first_name"], data["last_name"], data["user_type"]),
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        token_payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.utcnow() + timedelta(days=30),
        }
        token = jwt.encode(token_payload, app.config["SECRET_KEY"], algorithm="HS256")

        return jsonify({
            "access_token": token, # Send token for auto-login
            "user": {
                "id": user_id,
                "email": email,
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "user_type": data["user_type"],
            },
            "message": "Registration successful",
        }), 201

    except Exception as e:
        print(f"[Registration Error] {e}")
        return jsonify({"message": "Could not process your request"}), 500

# --- Main Execution ---
if __name__ == "__main__":
    init_database()
    print("Starting Flask server on http://0.0.0.0:8008")
    app.run(host="0.0.0.0", port=8008, debug=True)
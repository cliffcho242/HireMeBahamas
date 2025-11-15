import os
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

import bcrypt
import jwt
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_caching import Cache
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load environment variables from .env file
load_dotenv()

# Force Railway redeploy to activate DATABASE_URL - 2025-11-04
print("Initializing Flask app with PostgreSQL support...")
app = Flask(__name__)

# Production configuration
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "your-secret-key-here-change-in-production"
)
app.config["JSON_SORT_KEYS"] = False
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max file size

# Rate limiting configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Caching configuration
cache = Cache(
    app,
    config={
        "CACHE_TYPE": "simple",
        "CACHE_DEFAULT_TIMEOUT": 300,
    },
)

# Enhanced CORS configuration
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=False,
    max_age=3600,
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-Retry-Count",
    ],
    expose_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
STORIES_FOLDER = os.path.join(UPLOAD_FOLDER, "stories")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["STORIES_FOLDER"] = STORIES_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mov", "avi", "webm"}

# Ensure upload directories exist
os.makedirs(STORIES_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Serve uploaded files with caching
@app.route("/uploads/<path:filename>")
@cache.cached(timeout=3600)
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ==========================================
# DATABASE CONNECTION MANAGEMENT
# ==========================================

# Check if running on Railway with PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
USE_POSTGRESQL = DATABASE_URL is not None

print(
    f"🗄️ Database Mode: {'PostgreSQL (Production)' if USE_POSTGRESQL else 'SQLite (Development)'}"
)

if USE_POSTGRESQL:
    print(f"✅ PostgreSQL URL detected: {DATABASE_URL[:30]}...")

    # Parse DATABASE_URL
    parsed = urlparse(DATABASE_URL)
    DB_CONFIG = {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "database": parsed.path[1:],  # Remove leading '/'
        "user": parsed.username,
        "password": parsed.password,
        "sslmode": "require",
    }
else:
    # SQLite for local development
    DB_PATH = Path(__file__).parent / "hiremebahamas.db"
    print(f"📁 SQLite database path: {DB_PATH}")


def get_db_connection():
    """Get database connection (PostgreSQL on Railway, SQLite locally)"""
    if USE_POSTGRESQL:
        conn = psycopg2.connect(
            DATABASE_URL, sslmode="require", cursor_factory=RealDictCursor
        )
        return conn
    else:
        conn = sqlite3.connect(str(DB_PATH), timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn


def execute_query(query, params=None, fetch=False, fetchone=False, commit=False):
    """
    Universal query executor for both PostgreSQL and SQLite
    """
    conn = get_db_connection()

    try:
        if USE_POSTGRESQL:
            cursor = conn.cursor()
            # Convert SQLite ? placeholders to PostgreSQL %s
            query = query.replace("?", "%s")
        else:
            cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetch:
            result = cursor.fetchall()

        if commit:
            conn.commit()
            if USE_POSTGRESQL:
                # Get last inserted ID for PostgreSQL
                if "INSERT" in query.upper() and "RETURNING" not in query.upper():
                    result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result

    except Exception as e:
        conn.rollback()
        conn.close()
        raise e


def init_database():
    """Initialize database with all required tables"""
    print("🚀 Initializing database...")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Detect if we need to create tables
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                )
            """
            )
            table_exists = cursor.fetchone()[0]
        else:
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='users'
            """
            )
            table_exists = cursor.fetchone() is not None

        if not table_exists:
            print("📦 Creating database tables...")

            # Adjust syntax for PostgreSQL vs SQLite
            if USE_POSTGRESQL:
                # PostgreSQL uses SERIAL instead of AUTOINCREMENT
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        first_name VARCHAR(100),
                        last_name VARCHAR(100),
                        user_type VARCHAR(50) DEFAULT 'user',
                        location TEXT,
                        phone VARCHAR(20),
                        bio TEXT,
                        avatar_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        is_available_for_hire BOOLEAN DEFAULT FALSE,
                        trade VARCHAR(100) DEFAULT '',
                        username VARCHAR(100),
                        occupation VARCHAR(100),
                        company_name VARCHAR(200)
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS posts (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        image_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS jobs (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        company VARCHAR(255) NOT NULL,
                        location VARCHAR(255) NOT NULL,
                        description TEXT NOT NULL,
                        requirements TEXT,
                        salary_range VARCHAR(100),
                        job_type VARCHAR(50) DEFAULT 'full-time',
                        category VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS comments (
                        id SERIAL PRIMARY KEY,
                        post_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS likes (
                        id SERIAL PRIMARY KEY,
                        post_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(post_id, user_id),
                        FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS stories (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        media_url TEXT NOT NULL,
                        media_type VARCHAR(20) NOT NULL,
                        caption TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        views INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversations (
                        id SERIAL PRIMARY KEY,
                        participant_1_id INTEGER NOT NULL,
                        participant_2_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (participant_1_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (participant_2_id) REFERENCES users (id) ON DELETE CASCADE,
                        UNIQUE(participant_1_id, participant_2_id)
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        conversation_id INTEGER NOT NULL,
                        sender_id INTEGER NOT NULL,
                        receiver_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        is_read BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE,
                        FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

            else:
                # SQLite syntax (original)
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        first_name TEXT,
                        last_name TEXT,
                        user_type TEXT DEFAULT 'user',
                        location TEXT,
                        phone TEXT,
                        bio TEXT,
                        avatar_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        is_available_for_hire BOOLEAN DEFAULT 0,
                        trade TEXT DEFAULT '',
                        username TEXT,
                        occupation TEXT,
                        company_name TEXT
                    )
                """
                )

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

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS jobs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        company TEXT NOT NULL,
                        location TEXT NOT NULL,
                        description TEXT NOT NULL,
                        requirements TEXT,
                        salary_range TEXT,
                        job_type TEXT DEFAULT 'full-time',
                        category TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS comments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS likes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(post_id, user_id),
                        FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS stories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        media_url TEXT NOT NULL,
                        media_type TEXT NOT NULL,
                        caption TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        views INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        participant_1_id INTEGER NOT NULL,
                        participant_2_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (participant_1_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (participant_2_id) REFERENCES users (id) ON DELETE CASCADE,
                        UNIQUE(participant_1_id, participant_2_id)
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id INTEGER NOT NULL,
                        sender_id INTEGER NOT NULL,
                        receiver_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        is_read BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE,
                        FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

            conn.commit()
            print("✅ Database tables created successfully!")

        else:
            print("✅ Database tables already exist")

            # Run migrations to add missing columns
            migrate_user_columns(cursor, conn)

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        raise


def migrate_user_columns(cursor, conn):
    """Add missing columns to users table if they don't exist"""
    try:
        columns_to_add = [
            ("username", "VARCHAR(100)" if USE_POSTGRESQL else "TEXT"),
            ("occupation", "VARCHAR(100)" if USE_POSTGRESQL else "TEXT"),
            ("company_name", "VARCHAR(200)" if USE_POSTGRESQL else "TEXT"),
        ]

        for column_name, column_type in columns_to_add:
            try:
                if USE_POSTGRESQL:
                    cursor.execute(
                        f"""
                        ALTER TABLE users 
                        ADD COLUMN IF NOT EXISTS {column_name} {column_type}
                    """
                    )
                else:
                    # Check if column exists in SQLite
                    cursor.execute("PRAGMA table_info(users)")
                    columns = [row[1] for row in cursor.fetchall()]
                    if column_name not in columns:
                        cursor.execute(
                            f"""
                            ALTER TABLE users 
                            ADD COLUMN {column_name} {column_type}
                        """
                        )
                        print(f"✅ Added {column_name} column to users table")

                conn.commit()
            except Exception as e:
                if (
                    "duplicate column" not in str(e).lower()
                    and "already exists" not in str(e).lower()
                ):
                    print(f"⚠️ Migration warning for {column_name}: {e}")

    except Exception as e:
        print(f"⚠️ Migration warning: {e}")


# Initialize database on startup
init_database()


# ==========================================
# AUTHENTICATION HELPER FUNCTIONS
# ==========================================


def get_current_user():
    """Get current user from JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth():
    """Decorator to require authentication"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Authentication required"}), 401
    return None


# ==========================================
# HEALTH CHECK ENDPOINT
# ==========================================


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for Railway"""
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        if USE_POSTGRESQL:
            cursor.execute("SELECT 1")
        else:
            cursor.execute("SELECT 1")

        cursor.close()
        conn.close()

        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return (
        jsonify(
            {
                "status": "healthy",
                "message": "HireMeBahamas API is running",
                "database": db_status,
                "db_type": "PostgreSQL" if USE_POSTGRESQL else "SQLite",
            }
        ),
        200,
    )


# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================


@app.route("/api/auth/register", methods=["POST", "OPTIONS"])
def register():
    """Register a new user"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()

        required_fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "user_type",
            "location",
        ]
        for field in required_fields:
            if field not in data or not data[field].strip():
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": f"{field.replace('_', ' ').title()} is required",
                        }
                    ),
                    400,
                )

        email = data["email"].strip().lower()
        password = data["password"]

        # Validate password strength
        if (
            len(password) < 8
            or not any(c.isdigit() for c in password)
            or not any(c.isalpha() for c in password)
        ):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Password must be at least 8 characters with at least one letter and one number",
                    }
                ),
                400,
            )

        # Check if user already exists
        conn = get_db_connection()
        cursor = conn.cursor()

        if USE_POSTGRESQL:
            cursor.execute("SELECT id FROM users WHERE LOWER(email) = %s", (email,))
        else:
            cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email,))

        if cursor.fetchone():
            cursor.close()
            conn.close()
            return (
                jsonify(
                    {"success": False, "message": "User with this email already exists"}
                ),
                409,
            )

        # Hash password
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Insert new user
        now = datetime.now(timezone.utc)

        if USE_POSTGRESQL:
            cursor.execute(
                """
                INSERT INTO users (email, password_hash, first_name, last_name, user_type, location, phone, bio, is_active, created_at, last_login, is_available_for_hire)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s, %s, FALSE)
                RETURNING id
                """,
                (
                    email,
                    password_hash,
                    data["first_name"].strip(),
                    data["last_name"].strip(),
                    data["user_type"],
                    data["location"].strip(),
                    data.get("phone", "").strip(),
                    data.get("bio", "").strip(),
                    now,
                    now,
                ),
            )
            user_id = cursor.fetchone()["id"]
        else:
            cursor.execute(
                """
                INSERT INTO users (email, password_hash, first_name, last_name, user_type, location, phone, bio, is_active, created_at, last_login, is_available_for_hire)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, 0)
                """,
                (
                    email,
                    password_hash,
                    data["first_name"].strip(),
                    data["last_name"].strip(),
                    data["user_type"],
                    data["location"].strip(),
                    data.get("phone", "").strip(),
                    data.get("bio", "").strip(),
                    now,
                    now,
                ),
            )
            user_id = cursor.lastrowid

        conn.commit()
        cursor.close()
        conn.close()

        # Get the created user
        conn = get_db_connection()
        cursor = conn.cursor()

        if USE_POSTGRESQL:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        else:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        # Create JWT token
        token_payload = {
            "user_id": user["id"],
            "email": user["email"],
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
        }

        token = jwt.encode(token_payload, app.config["SECRET_KEY"], algorithm="HS256")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Registration successful",
                    "access_token": token,
                    "token_type": "bearer",
                    "user": {
                        "id": user["id"],
                        "email": user["email"],
                        "first_name": user["first_name"] or "",
                        "last_name": user["last_name"] or "",
                        "user_type": user["user_type"] or "user",
                        "location": user["location"] or "",
                        "phone": user["phone"] or "",
                        "bio": user["bio"] or "",
                        "avatar_url": user["avatar_url"] or "",
                        "is_available_for_hire": bool(user["is_available_for_hire"]),
                    },
                }
            ),
            201,
        )

    except Exception as e:
        print(f"Registration error: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Registration failed: {str(e)}",
                }
            ),
            500,
        )


@app.route("/api/auth/login", methods=["POST", "OPTIONS"])
def login():
    """Login user"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()

        if not data.get("email") or not data.get("password"):
            return (
                jsonify(
                    {"success": False, "message": "Email and password are required"}
                ),
                400,
            )

        email = data["email"].strip().lower()
        password = data["password"]

        # Get user from database
        conn = get_db_connection()
        cursor = conn.cursor()

        if USE_POSTGRESQL:
            cursor.execute("SELECT * FROM users WHERE LOWER(email) = %s", (email,))
        else:
            cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email,))

        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            return (
                jsonify({"success": False, "message": "Invalid email or password"}),
                401,
            )

        # Verify password
        if not bcrypt.checkpw(
            password.encode("utf-8"), user["password_hash"].encode("utf-8")
        ):
            cursor.close()
            conn.close()
            return (
                jsonify({"success": False, "message": "Invalid email or password"}),
                401,
            )

        # Update last login
        now = datetime.now(timezone.utc)
        if USE_POSTGRESQL:
            cursor.execute(
                "UPDATE users SET last_login = %s WHERE id = %s", (now, user["id"])
            )
        else:
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?", (now, user["id"])
            )

        conn.commit()
        cursor.close()
        conn.close()

        # Create JWT token
        token_payload = {
            "user_id": user["id"],
            "email": user["email"],
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
        }

        token = jwt.encode(token_payload, app.config["SECRET_KEY"], algorithm="HS256")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Login successful",
                    "access_token": token,
                    "token_type": "bearer",
                    "user": {
                        "id": user["id"],
                        "email": user["email"],
                        "first_name": user["first_name"] or "",
                        "last_name": user["last_name"] or "",
                        "user_type": user["user_type"] or "user",
                        "location": user["location"] or "",
                        "phone": user["phone"] or "",
                        "bio": user["bio"] or "",
                        "avatar_url": user["avatar_url"] or "",
                        "is_available_for_hire": bool(user["is_available_for_hire"]),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Login error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Login failed: {str(e)}"}),
            500,
        )


# ==========================================
# MESSAGES ENDPOINTS
# ==========================================


@app.route("/api/messages/conversations", methods=["GET", "OPTIONS"])
def get_conversations():
    """Get all conversations for the current user"""
    if request.method == "OPTIONS":
        return "", 200

    # Check authentication
    auth_error = require_auth()
    if auth_error:
        return auth_error

    try:
        current_user = get_current_user()
        user_id = current_user["user_id"]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all conversations where user is a participant
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT c.*, 
                       u1.id as p1_id, u1.first_name as p1_first, u1.last_name as p1_last,
                       u2.id as p2_id, u2.first_name as p2_first, u2.last_name as p2_last
                FROM conversations c
                JOIN users u1 ON c.participant_1_id = u1.id
                JOIN users u2 ON c.participant_2_id = u2.id
                WHERE c.participant_1_id = %s OR c.participant_2_id = %s
                ORDER BY c.updated_at DESC
            """,
                (user_id, user_id),
            )
        else:
            cursor.execute(
                """
                SELECT c.*, 
                       u1.id as p1_id, u1.first_name as p1_first, u1.last_name as p1_last,
                       u2.id as p2_id, u2.first_name as p2_first, u2.last_name as p2_last
                FROM conversations c
                JOIN users u1 ON c.participant_1_id = u1.id
                JOIN users u2 ON c.participant_2_id = u2.id
                WHERE c.participant_1_id = ? OR c.participant_2_id = ?
                ORDER BY c.updated_at DESC
            """,
                (user_id, user_id),
            )

        conversations = cursor.fetchall()

        result = []
        for conv in conversations:
            # Get messages for this conversation
            if USE_POSTGRESQL:
                cursor.execute(
                    """
                    SELECT m.*, 
                           u.id as sender_id, u.first_name as sender_first, u.last_name as sender_last
                    FROM messages m
                    JOIN users u ON m.sender_id = u.id
                    WHERE m.conversation_id = %s
                    ORDER BY m.created_at ASC
                """,
                    (conv["id"],),
                )
            else:
                cursor.execute(
                    """
                    SELECT m.*, 
                           u.id as sender_id, u.first_name as sender_first, u.last_name as sender_last
                    FROM messages m
                    JOIN users u ON m.sender_id = u.id
                    WHERE m.conversation_id = ?
                    ORDER BY m.created_at ASC
                """,
                    (conv["id"],),
                )

            messages = cursor.fetchall()
            messages_list = [
                {
                    "id": msg["id"],
                    "content": msg["content"],
                    "sender_id": msg["sender_id"],
                    "conversation_id": msg["conversation_id"],
                    "created_at": msg["created_at"],
                    "sender": {
                        "first_name": msg["sender_first"],
                        "last_name": msg["sender_last"],
                    },
                }
                for msg in messages
            ]

            result.append(
                {
                    "id": conv["id"],
                    "participant_1_id": conv["p1_id"],
                    "participant_2_id": conv["p2_id"],
                    "created_at": conv["created_at"],
                    "updated_at": conv["updated_at"],
                    "participant_1": {
                        "first_name": conv["p1_first"],
                        "last_name": conv["p1_last"],
                    },
                    "participant_2": {
                        "first_name": conv["p2_first"],
                        "last_name": conv["p2_last"],
                    },
                    "messages": messages_list,
                }
            )

        cursor.close()
        conn.close()

        return jsonify(result), 200

    except Exception as e:
        print(f"Error fetching conversations: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Error fetching conversations: {str(e)}",
                }
            ),
            500,
        )


@app.route("/api/messages/", methods=["POST", "OPTIONS"])
def send_message():
    """Send a message in a conversation"""
    if request.method == "OPTIONS":
        return "", 200

    # Check authentication
    auth_error = require_auth()
    if auth_error:
        return auth_error

    try:
        current_user = get_current_user()
        user_id = current_user["user_id"]

        data = request.get_json()
        conversation_id = data.get("conversation_id")
        content = data.get("content", "").strip()

        if not conversation_id or not content:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "conversation_id and content are required",
                    }
                ),
                400,
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify user is participant in this conversation
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT participant_1_id, participant_2_id 
                FROM conversations 
                WHERE id = %s
            """,
                (conversation_id,),
            )
        else:
            cursor.execute(
                """
                SELECT participant_1_id, participant_2_id 
                FROM conversations 
                WHERE id = ?
            """,
                (conversation_id,),
            )

        conversation = cursor.fetchone()

        if not conversation:
            cursor.close()
            conn.close()
            return (
                jsonify({"success": False, "message": "Conversation not found"}),
                404,
            )

        # Check if current user is a participant
        if (
            conversation["participant_1_id"] != user_id
            and conversation["participant_2_id"] != user_id
        ):
            cursor.close()
            conn.close()
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "You are not a participant in this conversation",
                    }
                ),
                403,
            )

        # Determine receiver
        receiver_id = (
            conversation["participant_2_id"]
            if conversation["participant_1_id"] == user_id
            else conversation["participant_1_id"]
        )

        # Insert message
        now = datetime.now(timezone.utc)
        if USE_POSTGRESQL:
            cursor.execute(
                """
                INSERT INTO messages (conversation_id, sender_id, receiver_id, content, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """,
                (conversation_id, user_id, receiver_id, content, now),
            )
            message_id = cursor.fetchone()["id"]

            # Update conversation updated_at
            cursor.execute(
                """
                UPDATE conversations 
                SET updated_at = %s 
                WHERE id = %s
            """,
                (now, conversation_id),
            )
        else:
            cursor.execute(
                """
                INSERT INTO messages (conversation_id, sender_id, receiver_id, content, created_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (conversation_id, user_id, receiver_id, content, now),
            )
            message_id = cursor.lastrowid

            # Update conversation updated_at
            cursor.execute(
                """
                UPDATE conversations 
                SET updated_at = ? 
                WHERE id = ?
            """,
                (now, conversation_id),
            )

        conn.commit()

        # Fetch the created message with sender info
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT m.*, u.first_name, u.last_name
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.id = %s
            """,
                (message_id,),
            )
        else:
            cursor.execute(
                """
                SELECT m.*, u.first_name, u.last_name
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.id = ?
            """,
                (message_id,),
            )

        message = cursor.fetchone()
        cursor.close()
        conn.close()

        return (
            jsonify(
                {
                    "id": message["id"],
                    "content": message["content"],
                    "sender_id": message["sender_id"],
                    "conversation_id": message["conversation_id"],
                    "created_at": message["created_at"],
                    "sender": {
                        "first_name": message["first_name"],
                        "last_name": message["last_name"],
                    },
                }
            ),
            201,
        )

    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Error sending message: {str(e)}"}),
            500,
        )


@app.route("/api/messages/conversations", methods=["POST", "OPTIONS"])
def create_conversation():
    """Create or get existing conversation with another user"""
    if request.method == "OPTIONS":
        return "", 200

    # Check authentication
    auth_error = require_auth()
    if auth_error:
        return auth_error

    try:
        current_user = get_current_user()
        user_id = current_user["user_id"]

        data = request.get_json()
        other_user_id = data.get("participant_id")

        if not other_user_id:
            return (
                jsonify({"success": False, "message": "participant_id is required"}),
                400,
            )

        if other_user_id == user_id:
            return (
                jsonify(
                    {"success": False, "message": "Cannot create conversation with self"}
                ),
                400,
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if conversation already exists (in either direction)
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT id FROM conversations
                WHERE (participant_1_id = %s AND participant_2_id = %s)
                   OR (participant_1_id = %s AND participant_2_id = %s)
            """,
                (user_id, other_user_id, other_user_id, user_id),
            )
        else:
            cursor.execute(
                """
                SELECT id FROM conversations
                WHERE (participant_1_id = ? AND participant_2_id = ?)
                   OR (participant_1_id = ? AND participant_2_id = ?)
            """,
                (user_id, other_user_id, other_user_id, user_id),
            )

        existing = cursor.fetchone()

        if existing:
            conversation_id = existing["id"]
        else:
            # Atomically create new conversation, or get existing one if already present
            now = datetime.now(timezone.utc)
            if USE_POSTGRESQL:
                cursor.execute(
                    """
                    INSERT INTO conversations (participant_1_id, participant_2_id, created_at, updated_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (participant_1_id, participant_2_id) DO NOTHING
                    RETURNING id
                """,
                    (user_id, other_user_id, now, now),
                )
                result = cursor.fetchone()
                if result and result.get("id"):
                    conversation_id = result["id"]
                else:
                    # Insert did not happen due to conflict, fetch existing id
                    cursor.execute(
                        """
                        SELECT id FROM conversations
                        WHERE (participant_1_id = %s AND participant_2_id = %s)
                           OR (participant_1_id = %s AND participant_2_id = %s)
                        """,
                        (user_id, other_user_id, other_user_id, user_id),
                    )
                    conversation_id = cursor.fetchone()["id"]
            else:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO conversations (participant_1_id, participant_2_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (user_id, other_user_id, now, now),
                )
                if cursor.lastrowid:
                    conversation_id = cursor.lastrowid
                else:
                    # Insert was ignored due to conflict, fetch existing id
                    cursor.execute(
                        """
                        SELECT id FROM conversations
                        WHERE (participant_1_id = ? AND participant_2_id = ?)
                           OR (participant_1_id = ? AND participant_2_id = ?)
                    """,
                        (user_id, other_user_id, other_user_id, user_id),
                    )
                    conversation_id = cursor.fetchone()["id"]

            conn.commit()
        # Fetch the conversation with participant details
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT c.*, 
                       u1.id as p1_id, u1.first_name as p1_first, u1.last_name as p1_last,
                       u2.id as p2_id, u2.first_name as p2_first, u2.last_name as p2_last
                FROM conversations c
                JOIN users u1 ON c.participant_1_id = u1.id
                JOIN users u2 ON c.participant_2_id = u2.id
                WHERE c.id = %s
            """,
                (conversation_id,),
            )
        else:
            cursor.execute(
                """
                SELECT c.*, 
                       u1.id as p1_id, u1.first_name as p1_first, u1.last_name as p1_last,
                       u2.id as p2_id, u2.first_name as p2_first, u2.last_name as p2_last
                FROM conversations c
                JOIN users u1 ON c.participant_1_id = u1.id
                JOIN users u2 ON c.participant_2_id = u2.id
                WHERE c.id = ?
            """,
                (conversation_id,),
            )

        conv = cursor.fetchone()
        cursor.close()
        conn.close()

        return (
            jsonify(
                {
                    "id": conv["id"],
                    "participant_1_id": conv["p1_id"],
                    "participant_2_id": conv["p2_id"],
                    "created_at": conv["created_at"],
                    "updated_at": conv["updated_at"],
                    "participant_1": {
                        "first_name": conv["p1_first"],
                        "last_name": conv["p1_last"],
                    },
                    "participant_2": {
                        "first_name": conv["p2_first"],
                        "last_name": conv["p2_last"],
                    },
                    "messages": [],
                }
            ),
            201,
        )

    except Exception as e:
        print(f"Error creating conversation: {str(e)}")
        return (
            jsonify(
                {"success": False, "message": f"Error creating conversation: {str(e)}"}
            ),
            500,
        )


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

# Export application for gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting HireMeBahamas backend on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)

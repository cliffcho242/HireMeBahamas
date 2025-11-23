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


# Initialize database on startup (wrapped in try-except to not block app startup)
try:
    init_database()
except Exception as e:
    print(f"⚠️ Database initialization deferred due to error: {e}")
    print("Database will be initialized on first request if needed.")



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


@app.route("/api/users/<user_id>", methods=["GET", "OPTIONS"])
def get_user_profile(user_id):
    """Get user profile by user ID"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Validate user_id is a valid integer
        try:
            user_id_int = int(user_id)
            if user_id_int <= 0:
                return (
                    jsonify({"success": False, "message": "Invalid user ID"}),
                    400,
                )
        except ValueError:
            return (
                jsonify({"success": False, "message": "Invalid user ID format"}),
                400,
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        # Query user by ID
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT id, email, first_name, last_name, username, user_type,
                       location, phone, bio, avatar_url, created_at,
                       is_available_for_hire, occupation, company_name
                FROM users 
                WHERE id = %s AND is_active = TRUE
                """,
                (user_id_int,)
            )
        else:
            cursor.execute(
                """
                SELECT id, email, first_name, last_name, username, user_type,
                       location, phone, bio, avatar_url, created_at,
                       is_available_for_hire, occupation, company_name
                FROM users 
                WHERE id = ? AND is_active = 1
                """,
                (user_id_int,)
            )

        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            return (
                jsonify({"success": False, "message": "User not found"}),
                404,
            )

        # Count user's posts
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT COUNT(*) FROM posts WHERE user_id = %s",
                (user_id_int,)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) FROM posts WHERE user_id = ?",
                (user_id_int,)
            )
        
        count_result = cursor.fetchone()
        posts_count = count_result[0] if count_result else 0

        cursor.close()
        conn.close()

        # Handle created_at field - could be string or datetime
        created_at_value = user["created_at"]
        if created_at_value:
            if isinstance(created_at_value, str):
                created_at_str = created_at_value
            else:
                created_at_str = created_at_value.isoformat()
        else:
            created_at_str = ""

        return (
            jsonify(
                {
                    "success": True,
                    "id": user["id"],
                    "email": user["email"],
                    "first_name": user["first_name"] or "",
                    "last_name": user["last_name"] or "",
                    "username": user["username"] or "",
                    "user_type": user["user_type"] or "user",
                    "location": user["location"] or "",
                    "phone": user["phone"] or "",
                    "bio": user["bio"] or "",
                    "avatar_url": user["avatar_url"] or "",
                    "created_at": created_at_str,
                    "is_available_for_hire": bool(user["is_available_for_hire"]),
                    "occupation": user["occupation"] or "",
                    "company_name": user["company_name"] or "",
                    "posts_count": posts_count,
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Get user profile error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Failed to get user profile: {str(e)}"}),
            500,
        )


# ==========================================
# AUTH PROFILE ENDPOINTS
# ==========================================


@app.route("/api/auth/profile", methods=["GET", "PUT", "OPTIONS"])
def auth_profile():
    """Get or update authenticated user profile"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get user ID from JWT token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.replace("Bearer ", "")
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == "GET":
            # Get user profile
            if USE_POSTGRESQL:
                cursor.execute(
                    """
                    SELECT id, email, first_name, last_name, username, user_type,
                           location, phone, bio, avatar_url, created_at,
                           is_available_for_hire, occupation, company_name
                    FROM users WHERE id = %s
                    """,
                    (user_id,)
                )
            else:
                cursor.execute(
                    """
                    SELECT id, email, first_name, last_name, username, user_type,
                           location, phone, bio, avatar_url, created_at,
                           is_available_for_hire, occupation, company_name
                    FROM users WHERE id = ?
                    """,
                    (user_id,)
                )

            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if not user:
                return jsonify({"success": False, "message": "User not found"}), 404

            # Handle datetime
            created_at_value = user["created_at"]
            if created_at_value:
                if isinstance(created_at_value, str):
                    created_at_str = created_at_value
                else:
                    created_at_str = created_at_value.isoformat()
            else:
                created_at_str = ""

            return jsonify({
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"] or "",
                "last_name": user["last_name"] or "",
                "username": user["username"] or "",
                "user_type": user["user_type"] or "user",
                "location": user["location"] or "",
                "phone": user["phone"] or "",
                "bio": user["bio"] or "",
                "avatar_url": user["avatar_url"] or "",
                "created_at": created_at_str,
                "is_available_for_hire": bool(user["is_available_for_hire"]),
                "occupation": user["occupation"] or "",
                "company_name": user["company_name"] or "",
            }), 200

        elif request.method == "PUT":
            # Update user profile
            data = request.get_json()
            
            # Build update query dynamically
            allowed_fields = [
                'first_name', 'last_name', 'username', 'location', 'phone',
                'bio', 'occupation', 'company_name'
            ]
            
            updates = []
            values = []
            for field in allowed_fields:
                if field in data:
                    updates.append(f"{field} = %s" if USE_POSTGRESQL else f"{field} = ?")
                    values.append(data[field])
            
            if not updates:
                return jsonify({"success": False, "message": "No fields to update"}), 400
            
            values.append(user_id)
            update_query = f"UPDATE users SET {', '.join(updates)} WHERE id = {'%s' if USE_POSTGRESQL else '?'}"
            
            cursor.execute(update_query, tuple(values))
            conn.commit()
            
            # Fetch updated user
            if USE_POSTGRESQL:
                cursor.execute(
                    "SELECT * FROM users WHERE id = %s",
                    (user_id,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM users WHERE id = ?",
                    (user_id,)
                )
            
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return jsonify({
                "success": True,
                "message": "Profile updated successfully",
                "user": dict(user)
            }), 200

    except Exception as e:
        print(f"Profile error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ==========================================
# POSTS ENDPOINTS
# ==========================================


@app.route("/api/posts", methods=["GET", "OPTIONS"])
def get_posts():
    """Get all posts with likes and comments"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get current user ID from token (if provided)
        current_user_id = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            try:
                payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
                current_user_id = payload["user_id"]
            except:
                pass  # Guest user

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get posts with user info
        cursor.execute(
            """
            SELECT
                p.id, p.user_id, p.content, p.image_url, p.created_at,
                u.first_name, u.last_name, u.email, u.user_type, u.avatar_url
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            """
        )

        posts_data = cursor.fetchall()
        posts = []

        for row in posts_data:
            post_id = row["id"]

            # Get likes count
            if USE_POSTGRESQL:
                cursor.execute(
                    "SELECT COUNT(*) FROM likes WHERE post_id = %s", (post_id,)
                )
            else:
                cursor.execute(
                    "SELECT COUNT(*) FROM likes WHERE post_id = ?", (post_id,)
                )
            likes_count = cursor.fetchone()[0]

            # Get comments count
            if USE_POSTGRESQL:
                cursor.execute(
                    "SELECT COUNT(*) FROM comments WHERE post_id = %s", (post_id,)
                )
            else:
                cursor.execute(
                    "SELECT COUNT(*) FROM comments WHERE post_id = ?", (post_id,)
                )
            comments_count = cursor.fetchone()[0]

            # Check if current user liked this post
            is_liked = False
            if current_user_id:
                if USE_POSTGRESQL:
                    cursor.execute(
                        "SELECT id FROM likes WHERE user_id = %s AND post_id = %s",
                        (current_user_id, post_id),
                    )
                else:
                    cursor.execute(
                        "SELECT id FROM likes WHERE user_id = ? AND post_id = ?",
                        (current_user_id, post_id),
                    )
                is_liked = cursor.fetchone() is not None

            # Handle datetime
            created_at = row["created_at"]
            if isinstance(created_at, str):
                created_at_str = created_at
            else:
                created_at_str = created_at.isoformat() if created_at else ""

            posts.append({
                "id": post_id,
                "content": row["content"],
                "image_url": row["image_url"],
                "created_at": created_at_str,
                "user_id": row["user_id"],
                "user": {
                    "id": row["user_id"],
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "email": row["email"],
                    "user_type": row["user_type"],
                    "avatar_url": row["avatar_url"],
                },
                "likes_count": likes_count,
                "comments_count": comments_count,
                "is_liked": is_liked,
            })

        conn.close()

        return jsonify({
            "success": True,
            "posts": posts
        }), 200

    except Exception as e:
        print(f"Get posts error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/posts", methods=["POST"])
def create_post():
    """Create a new post"""
    try:
        # Get user ID from JWT token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.replace("Bearer ", "")
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        data = request.get_json()
        content = data.get("content", "").strip()

        if not content:
            return jsonify({"success": False, "message": "Content is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert post
        now = datetime.now(timezone.utc)
        if USE_POSTGRESQL:
            cursor.execute(
                "INSERT INTO posts (user_id, content, image_url, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
                (user_id, content, data.get("image_url"), now)
            )
            post_id = cursor.fetchone()[0]
        else:
            cursor.execute(
                "INSERT INTO posts (user_id, content, image_url, created_at) VALUES (?, ?, ?, ?)",
                (user_id, content, data.get("image_url"), now)
            )
            post_id = cursor.lastrowid

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Post created successfully",
            "post_id": post_id
        }), 201

    except Exception as e:
        print(f"Create post error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/posts/<int:post_id>/like", methods=["POST", "OPTIONS"])
def like_post(post_id):
    """Like or unlike a post"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get user ID from JWT token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.replace("Bearer ", "")
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if already liked
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT id FROM likes WHERE user_id = %s AND post_id = %s",
                (user_id, post_id)
            )
        else:
            cursor.execute(
                "SELECT id FROM likes WHERE user_id = ? AND post_id = ?",
                (user_id, post_id)
            )

        existing_like = cursor.fetchone()

        if existing_like:
            # Unlike
            if USE_POSTGRESQL:
                cursor.execute(
                    "DELETE FROM likes WHERE user_id = %s AND post_id = %s",
                    (user_id, post_id)
                )
            else:
                cursor.execute(
                    "DELETE FROM likes WHERE user_id = ? AND post_id = ?",
                    (user_id, post_id)
                )
            message = "Post unliked"
            is_liked = False
        else:
            # Like
            now = datetime.now(timezone.utc)
            if USE_POSTGRESQL:
                cursor.execute(
                    "INSERT INTO likes (user_id, post_id, created_at) VALUES (%s, %s, %s)",
                    (user_id, post_id, now)
                )
            else:
                cursor.execute(
                    "INSERT INTO likes (user_id, post_id, created_at) VALUES (?, ?, ?)",
                    (user_id, post_id, now)
                )
            message = "Post liked"
            is_liked = True

        conn.commit()

        # Get updated likes count
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT COUNT(*) FROM likes WHERE post_id = %s", (post_id,)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) FROM likes WHERE post_id = ?", (post_id,)
            )
        likes_count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": message,
            "is_liked": is_liked,
            "likes_count": likes_count
        }), 200

    except Exception as e:
        print(f"Like post error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/posts/<int:post_id>/comments", methods=["GET", "POST", "OPTIONS"])
def post_comments(post_id):
    """Get or create comments on a post"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == "GET":
            # Get comments
            if USE_POSTGRESQL:
                cursor.execute(
                    """
                    SELECT c.id, c.content, c.created_at, c.user_id,
                           u.first_name, u.last_name, u.avatar_url
                    FROM comments c
                    JOIN users u ON c.user_id = u.id
                    WHERE c.post_id = %s
                    ORDER BY c.created_at ASC
                    """,
                    (post_id,)
                )
            else:
                cursor.execute(
                    """
                    SELECT c.id, c.content, c.created_at, c.user_id,
                           u.first_name, u.last_name, u.avatar_url
                    FROM comments c
                    JOIN users u ON c.user_id = u.id
                    WHERE c.post_id = ?
                    ORDER BY c.created_at ASC
                    """,
                    (post_id,)
                )

            comments_data = cursor.fetchall()
            comments = []

            for row in comments_data:
                created_at = row["created_at"]
                if isinstance(created_at, str):
                    created_at_str = created_at
                else:
                    created_at_str = created_at.isoformat() if created_at else ""

                comments.append({
                    "id": row["id"],
                    "content": row["content"],
                    "created_at": created_at_str,
                    "user": {
                        "id": row["user_id"],
                        "first_name": row["first_name"],
                        "last_name": row["last_name"],
                        "avatar_url": row["avatar_url"],
                    }
                })

            cursor.close()
            conn.close()

            return jsonify({
                "success": True,
                "comments": comments
            }), 200

        elif request.method == "POST":
            # Create comment
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"success": False, "message": "Authentication required"}), 401

            token = auth_header.replace("Bearer ", "")
            try:
                payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
                user_id = payload["user_id"]
            except:
                return jsonify({"success": False, "message": "Invalid token"}), 401

            data = request.get_json()
            content = data.get("content", "").strip()

            if not content:
                return jsonify({"success": False, "message": "Content is required"}), 400

            now = datetime.now(timezone.utc)
            if USE_POSTGRESQL:
                cursor.execute(
                    "INSERT INTO comments (post_id, user_id, content, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
                    (post_id, user_id, content, now)
                )
                comment_id = cursor.fetchone()[0]
            else:
                cursor.execute(
                    "INSERT INTO comments (post_id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
                    (post_id, user_id, content, now)
                )
                comment_id = cursor.lastrowid

            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({
                "success": True,
                "message": "Comment created successfully",
                "comment_id": comment_id
            }), 201

    except Exception as e:
        print(f"Comments error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/posts/<int:post_id>", methods=["DELETE", "OPTIONS"])
def delete_post(post_id):
    """Delete a post"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get user ID from JWT token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.replace("Bearer ", "")
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if post belongs to user
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT user_id FROM posts WHERE id = %s", (post_id,)
            )
        else:
            cursor.execute(
                "SELECT user_id FROM posts WHERE id = ?", (post_id,)
            )

        post = cursor.fetchone()

        if not post:
            return jsonify({"success": False, "message": "Post not found"}), 404

        if post["user_id"] != user_id:
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        # Delete post (cascades to likes and comments)
        if USE_POSTGRESQL:
            cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        else:
            cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Post deleted successfully"
        }), 200

    except Exception as e:
        print(f"Delete post error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/posts/<int:post_id>/comments/<int:comment_id>", methods=["DELETE", "OPTIONS"])
def delete_comment(post_id, comment_id):
    """Delete a comment"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get user ID from JWT token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.replace("Bearer ", "")
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if comment belongs to user
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT user_id FROM comments WHERE id = %s AND post_id = %s",
                (comment_id, post_id)
            )
        else:
            cursor.execute(
                "SELECT user_id FROM comments WHERE id = ? AND post_id = ?",
                (comment_id, post_id)
            )

        comment = cursor.fetchone()

        if not comment:
            return jsonify({"success": False, "message": "Comment not found"}), 404

        if comment["user_id"] != user_id:
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        # Delete comment
        if USE_POSTGRESQL:
            cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        else:
            cursor.execute("DELETE FROM comments WHERE id = ?", (comment_id,))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Comment deleted successfully"
        }), 200

    except Exception as e:
        print(f"Delete comment error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ==========================================
# HIREME ENDPOINTS
# ==========================================


@app.route("/api/hireme/available", methods=["GET", "OPTIONS"])
def get_available_users():
    """Get users available for hire"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        search = request.args.get("search", "").strip()

        if search:
            search_pattern = f"%{search}%"
            if USE_POSTGRESQL:
                cursor.execute(
                    """
                    SELECT id, email, first_name, last_name, username, location,
                           bio, occupation, company_name, avatar_url
                    FROM users
                    WHERE is_available_for_hire = TRUE
                      AND is_active = TRUE
                      AND (first_name ILIKE %s OR last_name ILIKE %s OR occupation ILIKE %s)
                    ORDER BY created_at DESC
                    """,
                    (search_pattern, search_pattern, search_pattern)
                )
            else:
                cursor.execute(
                    """
                    SELECT id, email, first_name, last_name, username, location,
                           bio, occupation, company_name, avatar_url
                    FROM users
                    WHERE is_available_for_hire = 1
                      AND is_active = 1
                      AND (first_name LIKE ? OR last_name LIKE ? OR occupation LIKE ?)
                    ORDER BY created_at DESC
                    """,
                    (search_pattern, search_pattern, search_pattern)
                )
        else:
            if USE_POSTGRESQL:
                cursor.execute(
                    """
                    SELECT id, email, first_name, last_name, username, location,
                           bio, occupation, company_name, avatar_url
                    FROM users
                    WHERE is_available_for_hire = TRUE AND is_active = TRUE
                    ORDER BY created_at DESC
                    """
                )
            else:
                cursor.execute(
                    """
                    SELECT id, email, first_name, last_name, username, location,
                           bio, occupation, company_name, avatar_url
                    FROM users
                    WHERE is_available_for_hire = 1 AND is_active = 1
                    ORDER BY created_at DESC
                    """
                )

        users_data = cursor.fetchall()
        users = [dict(row) for row in users_data]

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "users": users
        }), 200

    except Exception as e:
        print(f"Get available users error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/hireme/toggle", methods=["POST", "OPTIONS"])
def toggle_availability():
    """Toggle user's availability for hire"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get user ID from JWT token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.replace("Bearer ", "")
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get current status
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT is_available_for_hire FROM users WHERE id = %s", (user_id,)
            )
        else:
            cursor.execute(
                "SELECT is_available_for_hire FROM users WHERE id = ?", (user_id,)
            )

        user = cursor.fetchone()
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Toggle status
        new_status = not bool(user["is_available_for_hire"])

        if USE_POSTGRESQL:
            cursor.execute(
                "UPDATE users SET is_available_for_hire = %s WHERE id = %s",
                (new_status, user_id)
            )
        else:
            cursor.execute(
                "UPDATE users SET is_available_for_hire = ? WHERE id = ?",
                (1 if new_status else 0, user_id)
            )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "is_available": new_status,
            "message": f"Availability {'enabled' if new_status else 'disabled'}"
        }), 200

    except Exception as e:
        print(f"Toggle availability error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

# Export application for gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting HireMeBahamas backend on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)

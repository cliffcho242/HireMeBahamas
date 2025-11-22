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

# JWT token expiration configuration (in days)
TOKEN_EXPIRATION_DAYS = int(os.getenv("TOKEN_EXPIRATION_DAYS", "7"))

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

# Track database initialization status
_db_initialized = False
_db_init_lock = threading.Lock()

# Error message length limit for health checks
MAX_ERROR_MESSAGE_LENGTH = 500

if USE_POSTGRESQL:
    print(f"✅ PostgreSQL URL detected: {DATABASE_URL[:30]}...")

    # Parse DATABASE_URL with defensive error handling
    parsed = urlparse(DATABASE_URL)

    # Safely parse port with error handling
    try:
        port = int(parsed.port) if parsed.port else 5432
    except (ValueError, TypeError):
        port = 5432
        print(f"⚠️  Invalid port '{parsed.port}' in DATABASE_URL, using default 5432")

    # Safely parse database name
    try:
        database = parsed.path[1:] if parsed.path and len(parsed.path) > 1 else None
        if not database:
            raise ValueError("Database name is missing from DATABASE_URL")
    except (ValueError, IndexError) as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        print(
            f"DATABASE_URL format should be: postgresql://username:password@hostname:5432/database"
        )
        raise

    DB_CONFIG = {
        "host": parsed.hostname,
        "port": port,
        "database": database,
        "user": parsed.username,
        "password": parsed.password,
        "sslmode": "require",
    }

    # Validate all required fields are present
    required_fields = ["host", "database", "user", "password"]
    missing_fields = [field for field in required_fields if not DB_CONFIG.get(field)]
    if missing_fields:
        print(
            f"❌ Missing required DATABASE_URL components: {', '.join(missing_fields)}"
        )
        print(
            f"DATABASE_URL format should be: postgresql://username:password@hostname:5432/database"
        )
        raise ValueError(f"Invalid DATABASE_URL: missing {', '.join(missing_fields)}")

    print(
        f"✅ Database config parsed: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
else:
    # SQLite for local development
    DB_PATH = Path(__file__).parent / "hiremebahamas.db"
    print(f"📁 SQLite database path: {DB_PATH}")


def get_db_connection():
    """Get database connection (PostgreSQL on Railway, SQLite locally)"""
    if USE_POSTGRESQL:
        conn = psycopg2.connect(
            DATABASE_URL,
            sslmode="require",
            cursor_factory=RealDictCursor,
            connect_timeout=10,  # 10 second timeout for connection
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
    global _db_initialized

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

        # Mark database as successfully initialized
        _db_initialized = True
        print("✅ Database initialization completed successfully")

    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        try:
            conn.rollback()
            cursor.close()
            conn.close()
        except Exception:
            pass  # Connection might already be closed
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


def ensure_database_initialized():
    """
    Ensure database is initialized.
    If initialization failed on startup, retry it here.
    This is thread-safe and will only initialize once.
    """
    global _db_initialized

    if not _db_initialized:
        with _db_init_lock:
            # Double-check inside the lock
            if not _db_initialized:
                try:
                    print("🔧 Retrying database initialization...")
                    init_database()
                    print("✅ Database initialization successful on retry")
                except Exception as e:
                    print(f"⚠️ Database initialization retry failed: {e}")
                    # Don't raise - let the endpoint handle it

    return _db_initialized


# Initialize database on startup with error handling
try:
    print("🔧 Attempting database initialization...")
    init_database()
    print("✅ Database initialization completed successfully")
except Exception as e:
    print(f"⚠️ Database initialization warning: {e}")
    print("⚠️ Application will continue - database will be initialized on first request")
    # Don't exit - allow the app to start and try again later


# ==========================================
# HEALTH CHECK ENDPOINT
# ==========================================


@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for Railway
    Returns 200 OK immediately to ensure Railway healthcheck passes
    The app is healthy if this endpoint responds - database initialization
    happens asynchronously and doesn't need to block the healthcheck
    """
    return (
        jsonify(
            {
                "status": "healthy",
                "message": "HireMeBahamas API is running",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ),
        200,
    )


@app.route("/api/health", methods=["GET"])
def api_health_check():
    """
    Detailed health check endpoint with database status
    This can be used for monitoring but won't block Railway healthcheck
    Attempts to retry database initialization if it failed on startup
    """
    response = {
        "status": "healthy",
        "message": "HireMeBahamas API is running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "db_initialized": _db_initialized,
    }

    # Try to ensure database is initialized
    if not _db_initialized:
        ensure_database_initialized()
        response["db_initialized"] = _db_initialized

    # Try to check database connection
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        response["database"] = "connected"
        response["db_type"] = "PostgreSQL" if USE_POSTGRESQL else "SQLite"
    except Exception as e:
        response["database"] = "error"
        # Keep meaningful error information up to MAX_ERROR_MESSAGE_LENGTH
        error_msg = str(e)
        if len(error_msg) <= MAX_ERROR_MESSAGE_LENGTH:
            response["error"] = error_msg
        else:
            # Truncate with ellipsis
            response["error"] = error_msg[: (MAX_ERROR_MESSAGE_LENGTH - 3)] + "..."

    return jsonify(response), 200


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
            "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRATION_DAYS),
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
            "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRATION_DAYS),
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


@app.route("/api/auth/refresh", methods=["POST", "OPTIONS"])
def refresh_token():
    """Refresh authentication token"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "No token provided"}),
                401,
            )

        token = auth_header.split(" ")[1]

        # Decode token to get user info
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload.get("user_id")
        except jwt.ExpiredSignatureError:
            return (
                jsonify({"success": False, "message": "Token has expired"}),
                401,
            )
        except jwt.InvalidTokenError:
            return (
                jsonify({"success": False, "message": "Invalid token"}),
                401,
            )

        # Get user from database
        conn = get_db_connection()
        cursor = conn.cursor()

        if USE_POSTGRESQL:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        else:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return (
                jsonify({"success": False, "message": "User not found"}),
                404,
            )

        # Create new JWT token with extended expiration
        new_token_payload = {
            "user_id": user["id"],
            "email": user["email"],
            "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRATION_DAYS),
        }

        new_token = jwt.encode(
            new_token_payload, app.config["SECRET_KEY"], algorithm="HS256"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Token refreshed successfully",
                    "access_token": new_token,
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
        print(f"Token refresh error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Token refresh failed: {str(e)}"}),
            500,
        )


@app.route("/api/auth/verify", methods=["GET", "OPTIONS"])
def verify_session():
    """Verify if the current session is valid"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "No token provided"}),
                401,
            )

        token = auth_header.split(" ")[1]

        # Decode token to verify validity
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload.get("user_id")

            # Check if user exists
            conn = get_db_connection()
            cursor = conn.cursor()

            if USE_POSTGRESQL:
                cursor.execute("SELECT id, email FROM users WHERE id = %s", (user_id,))
            else:
                cursor.execute("SELECT id, email FROM users WHERE id = ?", (user_id,))

            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if not user:
                return (
                    jsonify({"success": False, "message": "User not found"}),
                    404,
                )

            return (
                jsonify(
                    {
                        "success": True,
                        "valid": True,
                        "message": "Session is valid",
                        "user_id": user["id"],
                        "email": user["email"],
                    }
                ),
                200,
            )

        except jwt.ExpiredSignatureError:
            return (
                jsonify(
                    {"success": False, "valid": False, "message": "Token has expired"}
                ),
                401,
            )
        except jwt.InvalidTokenError:
            return (
                jsonify({"success": False, "valid": False, "message": "Invalid token"}),
                401,
            )

    except Exception as e:
        print(f"Session verification error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Verification failed: {str(e)}"}),
            500,
        )


@app.route("/api/auth/profile", methods=["GET", "OPTIONS"])
def get_profile():
    """Get user profile"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "No token provided"}),
                401,
            )

        token = auth_header.split(" ")[1]

        # Decode token
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload.get("user_id")
        except jwt.ExpiredSignatureError:
            return (
                jsonify({"success": False, "message": "Token has expired"}),
                401,
            )
        except jwt.InvalidTokenError:
            return (
                jsonify({"success": False, "message": "Invalid token"}),
                401,
            )

        # Get user from database
        conn = get_db_connection()
        cursor = conn.cursor()

        if USE_POSTGRESQL:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        else:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return (
                jsonify({"success": False, "message": "User not found"}),
                404,
            )

        return (
            jsonify(
                {
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
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Profile fetch error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Profile fetch failed: {str(e)}"}),
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

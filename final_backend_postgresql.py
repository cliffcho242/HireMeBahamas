import os
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse, parse_qs

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
# Set to 365 days (1 year) to prevent frequent re-login
# Users stay logged in for a full year unless they manually log out
TOKEN_EXPIRATION_DAYS = int(os.getenv("TOKEN_EXPIRATION_DAYS", "365"))

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

# Check if this is a production environment
# Detect Railway environment using Railway-specific variables:
# - RAILWAY_ENVIRONMENT: Set by Railway to indicate the environment (e.g., "production")
# - RAILWAY_PROJECT_ID: Always present in Railway deployments, used as fallback detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
RAILWAY_ENVIRONMENT = os.getenv("RAILWAY_ENVIRONMENT", "").lower()
IS_RAILWAY = os.getenv("RAILWAY_PROJECT_ID") is not None

# Production is determined by:
# 1. Explicit ENVIRONMENT=production setting, OR
# 2. Railway deployment with explicit production environment setting
# Note: If RAILWAY_ENVIRONMENT is not set or empty, we don't assume production
# to avoid unexpected behavior - require explicit configuration
IS_PRODUCTION = (
    ENVIRONMENT in ["production", "prod"] or 
    (IS_RAILWAY and RAILWAY_ENVIRONMENT in ["production", "prod"])
)

# Track if database configuration is valid for production
# Don't crash at startup - allow health check to report issues
DATABASE_CONFIG_WARNING = None

# For production, PostgreSQL is REQUIRED - but don't crash, just warn
if IS_PRODUCTION and not USE_POSTGRESQL:
    DATABASE_CONFIG_WARNING = (
        "DATABASE_URL must be set in production. "
        "PostgreSQL is required for data persistence."
    )
    print("⚠️" * 50)
    print("⚠️  WARNING: Production environment REQUIRES PostgreSQL!")
    print("⚠️  DATABASE_URL environment variable is not set.")
    print("⚠️")
    print("⚠️  SQLite is NOT suitable for production use because:")
    print("⚠️  - No data persistence in containerized environments (Railway, Docker)")
    print("⚠️  - Users and data will be lost on every deployment/restart")
    print("⚠️  - No concurrent access support at scale")
    print("⚠️")
    print("⚠️  Please set DATABASE_URL to a PostgreSQL connection string:")
    print("⚠️  DATABASE_URL=postgresql://username:password@hostname:5432/database")
    print("⚠️" * 50)
    # Don't raise an exception - allow the app to start so health check can report the issue
    # This prevents Gunicorn worker boot failures while still warning about the misconfiguration

print(
    f"🗄️ Database Mode: {'PostgreSQL (Production)' if USE_POSTGRESQL else 'SQLite (Development Only)'}"
)
if IS_PRODUCTION:
    print(f"🌍 Environment: PRODUCTION")
else:
    print(f"💻 Environment: Development")

if not USE_POSTGRESQL:
    print("⚠️  Note: Using SQLite for local development only.")
    print("⚠️  Set DATABASE_URL to use PostgreSQL.")

# Track database initialization status
_db_initialized = False
_db_init_lock = threading.Lock()

# Error message length limit for health checks
MAX_ERROR_MESSAGE_LENGTH = 500

if USE_POSTGRESQL:
    print(f"✅ PostgreSQL URL detected: {DATABASE_URL[:30]}...")

    # Expected DATABASE_URL format message
    DATABASE_URL_FORMAT = "postgresql://username:password@hostname:5432/database"

    # Parse DATABASE_URL with defensive error handling
    parsed = urlparse(DATABASE_URL)

    # Safely parse port with error handling
    try:
        port = int(parsed.port) if parsed.port else 5432
    except (ValueError, TypeError):
        port = 5432
        print(f"⚠️  Invalid port '{parsed.port}' in DATABASE_URL, using default 5432")

    # Safely parse database name (remove leading '/' from path)
    try:
        database = parsed.path[1:] if parsed.path and len(parsed.path) > 1 else None
        if not database:
            raise ValueError("Database name is missing from DATABASE_URL")
    except (ValueError, IndexError) as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        print(f"DATABASE_URL format should be: {DATABASE_URL_FORMAT}")
        raise

    # Parse query string for SSL mode and other options
    query_params = parse_qs(parsed.query)
    # Get sslmode from URL if present, otherwise default to "require"
    # Handles empty values like ?sslmode= by checking if the list is non-empty
    sslmode_list = query_params.get("sslmode", [])
    sslmode = sslmode_list[0] if sslmode_list and sslmode_list[0] else "require"
    
    DB_CONFIG = {
        "host": parsed.hostname,
        "port": port,
        "database": database,
        "user": parsed.username,
        "password": parsed.password,
        "sslmode": sslmode,
    }

    # Validate all required fields are present
    required_fields = ["host", "database", "user", "password"]
    missing_fields = [field for field in required_fields if not DB_CONFIG.get(field)]
    if missing_fields:
        print(
            f"❌ Missing required DATABASE_URL components: {', '.join(missing_fields)}"
        )
        print(f"DATABASE_URL format should be: {DATABASE_URL_FORMAT}")
        raise ValueError(f"Invalid DATABASE_URL: missing {', '.join(missing_fields)}")

    print(
        f"✅ Database config parsed: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']} (sslmode={sslmode})"
    )
else:
    # SQLite for local development
    DB_PATH = Path(__file__).parent / "hiremebahamas.db"
    print(f"📁 SQLite database path: {DB_PATH}")


def get_db_connection():
    """Get database connection (PostgreSQL on Railway, SQLite locally)"""
    if USE_POSTGRESQL:
        # Use connection parameters from parsed URL to avoid conflicts
        # This prevents issues when DATABASE_URL already contains sslmode
        try:
            conn = psycopg2.connect(
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                database=DB_CONFIG["database"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                sslmode=DB_CONFIG["sslmode"],
                cursor_factory=RealDictCursor,
                connect_timeout=10,  # 10 second timeout for connection
            )
            return conn
        except psycopg2.OperationalError as e:
            error_msg = str(e).lower()
            # Handle SSL-related errors by trying with sslmode=prefer
            if "ssl" in error_msg or "certificate" in error_msg:
                print(f"⚠️ SSL connection failed, attempting with sslmode=prefer...")
                try:
                    conn = psycopg2.connect(
                        host=DB_CONFIG["host"],
                        port=DB_CONFIG["port"],
                        database=DB_CONFIG["database"],
                        user=DB_CONFIG["user"],
                        password=DB_CONFIG["password"],
                        sslmode="prefer",
                        cursor_factory=RealDictCursor,
                        connect_timeout=10,
                    )
                    return conn
                except Exception as fallback_error:
                    print(f"❌ Fallback connection also failed: {fallback_error}")
                    raise
            raise
    else:
        conn = sqlite3.connect(str(DB_PATH), timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        
        # Enable WAL mode for better concurrent access and crash recovery
        result = conn.execute("PRAGMA journal_mode=WAL").fetchone()
        if result[0].lower() != 'wal':
            print(f"⚠️  Warning: Failed to enable WAL mode, got: {result[0]}")
        
        # Set synchronous to NORMAL for better performance while maintaining safety
        conn.execute("PRAGMA synchronous=NORMAL")
        
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys=ON")
        result = conn.execute("PRAGMA foreign_keys").fetchone()
        if not result or not result[0]:
            print(f"⚠️  Warning: Failed to enable foreign keys, got: {result[0] if result else 'None'}")
        
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
                        video_url TEXT,
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
                    CREATE TABLE IF NOT EXISTS follows (
                        id SERIAL PRIMARY KEY,
                        follower_id INTEGER NOT NULL,
                        followed_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(follower_id, followed_id),
                        FOREIGN KEY (follower_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (followed_id) REFERENCES users (id) ON DELETE CASCADE
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
                        video_url TEXT,
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
                    CREATE TABLE IF NOT EXISTS follows (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        follower_id INTEGER NOT NULL,
                        followed_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(follower_id, followed_id),
                        FOREIGN KEY (follower_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (followed_id) REFERENCES users (id) ON DELETE CASCADE
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


# Initialize database in background thread to avoid blocking healthcheck
def init_database_background():
    """Initialize database in background thread to allow app to start quickly"""
    global _db_initialized

    with _db_init_lock:
        # Check if already initialized by another thread
        if _db_initialized:
            print("✅ Database already initialized")
            return

        try:
            print("🔧 Attempting database initialization in background thread...")
            init_database()
        except Exception as e:
            print(f"⚠️ Database initialization warning: {e}")
            print("⚠️ Database will be initialized on first request")

# Start database initialization in background thread
_db_init_thread = None
try:
    _db_init_thread = threading.Thread(target=init_database_background, daemon=True, name="db-init")
    _db_init_thread.start()
    print("🚀 Database initialization started in background thread")
except Exception as e:
    print(f"⚠️ Failed to start database initialization thread: {e}")
    print("⚠️ Database will be initialized on first request")

print("✅ Application ready to serve requests")


# ==========================================
# HEALTH CHECK ENDPOINT
# ==========================================


@app.route("/", methods=["GET"])
def root():
    """
    Root endpoint - returns API information
    Provides a welcome message and basic API status for monitoring tools
    """
    return (
        jsonify(
            {
                "name": "HireMeBahamas API",
                "status": "running",
                "version": "1.0.0",
                "message": "Welcome to the HireMeBahamas API",
                "endpoints": {
                    "health": "/health",
                    "health_detailed": "/api/health",
                },
            }
        ),
        200,
    )


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
    # Determine HTTP status code based on service availability
    # 200: Service is healthy or degraded but functional
    # 503: Service is unavailable (cannot connect to database)
    http_status = 200
    
    response = {
        "status": "healthy",
        "message": "HireMeBahamas API is running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "db_initialized": _db_initialized,
        "environment": ENVIRONMENT,
        "is_production": IS_PRODUCTION,
        "is_railway": IS_RAILWAY,
        "database_url_configured": USE_POSTGRESQL,
    }

    # Report database configuration warning if present
    # Use 200 status with 'degraded' state - the service is still functional
    if DATABASE_CONFIG_WARNING:
        response["status"] = "degraded"
        response["config_warning"] = DATABASE_CONFIG_WARNING
        # Keep http_status = 200 since the service is still functional

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
        response["status"] = "unhealthy"
        http_status = 503  # Service Unavailable - actual database connection failure
        # Keep meaningful error information up to MAX_ERROR_MESSAGE_LENGTH
        error_msg = str(e)
        if len(error_msg) <= MAX_ERROR_MESSAGE_LENGTH:
            response["error"] = error_msg
        else:
            # Truncate with ellipsis
            response["error"] = error_msg[: (MAX_ERROR_MESSAGE_LENGTH - 3)] + "..."

    return jsonify(response), http_status


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
# POSTS ENDPOINTS
# ==========================================


@app.route("/api/posts", methods=["GET", "OPTIONS"])
def get_posts():
    """
    Get posts with user information
    
    Posts are PERMANENTLY stored - never automatically deleted.
    Supports pagination for handling millions of posts efficiently.
    
    Query Parameters:
    - page: Page number (default: 1)
    - per_page: Posts per page (default: 20, max: 100)
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Validate pagination
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 20
        if per_page > 100:
            per_page = 100  # Max 100 posts per page
        
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as total FROM posts")
        total_posts = cursor.fetchone()["total"]

        # Get paginated posts with user information
        if USE_POSTGRESQL:
            # PostgreSQL requires all non-aggregate columns in GROUP BY
            cursor.execute(
                """
                SELECT 
                    p.id, p.content, p.image_url, p.video_url, p.created_at,
                    u.id as user_id, u.email, u.first_name, u.last_name, u.avatar_url,
                    u.username, u.occupation, u.company_name,
                    COUNT(DISTINCT l.id) as likes_count,
                    COUNT(DISTINCT c.id) as comments_count
                FROM posts p
                JOIN users u ON p.user_id = u.id
                LEFT JOIN likes l ON p.id = l.post_id
                LEFT JOIN comments c ON p.id = c.post_id
                GROUP BY p.id, p.content, p.image_url, p.video_url, p.created_at, 
                         u.id, u.email, u.first_name, u.last_name, u.avatar_url,
                         u.username, u.occupation, u.company_name
                ORDER BY p.created_at DESC
                LIMIT %s OFFSET %s
            """,
                (per_page, offset)
            )
        else:
            # SQLite allows grouping by primary key only (functionally dependent columns)
            cursor.execute(
                """
                SELECT 
                    p.id, p.content, p.image_url, p.video_url, p.created_at,
                    u.id as user_id, u.email, u.first_name, u.last_name, u.avatar_url,
                    u.username, u.occupation, u.company_name,
                    COUNT(DISTINCT l.id) as likes_count,
                    COUNT(DISTINCT c.id) as comments_count
                FROM posts p
                JOIN users u ON p.user_id = u.id
                LEFT JOIN likes l ON p.id = l.post_id
                LEFT JOIN comments c ON p.id = c.post_id
                GROUP BY p.id
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            """,
                (per_page, offset)
            )

        posts_data = cursor.fetchall()
        cursor.close()
        conn.close()

        # Format posts for response
        posts = []
        for post in posts_data:
            posts.append(
                {
                    "id": post["id"],
                    "content": post["content"],
                    "image_url": post["image_url"],
                    "video_url": post["video_url"],
                    "created_at": post["created_at"],
                    "likes_count": post["likes_count"],
                    "comments_count": post["comments_count"],
                    "user": {
                        "id": post["user_id"],
                        "email": post["email"],
                        "first_name": post["first_name"] or "",
                        "last_name": post["last_name"] or "",
                        "avatar_url": post["avatar_url"] or "",
                        "username": post["username"],
                        "occupation": post["occupation"],
                        "company_name": post["company_name"],
                    },
                }
            )
        
        # Calculate pagination info
        total_pages = (total_posts + per_page - 1) // per_page  # Ceiling division

        return jsonify({
            "success": True, 
            "posts": posts,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_posts": total_posts,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }), 200

    except Exception as e:
        print(f"Get posts error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Failed to fetch posts: {str(e)}"}),
            500,
        )


@app.route("/api/posts", methods=["POST"])
def create_post():
    """Create a new post"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "No token provided"}),
                401,
            )

        parts = auth_header.split(" ")
        if len(parts) != 2:
            return (
                jsonify({"success": False, "message": "Invalid authorization header format"}),
                401,
            )
        
        token = parts[1]

        # Decode token to get user_id
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

        # Get post data
        data = request.get_json()
        content = data.get("content", "").strip()
        image_url = data.get("image_url", "")
        video_url = data.get("video_url", "")

        if not content:
            return (
                jsonify({"success": False, "message": "Post content is required"}),
                400,
            )

        # Create post in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify user exists before creating post
        if USE_POSTGRESQL:
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        else:
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return (
                jsonify({"success": False, "message": "User not found. Please log in again."}),
                401,
            )

        if USE_POSTGRESQL:
            cursor.execute(
                """
                INSERT INTO posts (user_id, content, image_url, video_url, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, created_at
            """,
                (user_id, content, image_url, video_url, datetime.now(timezone.utc)),
            )
        else:
            cursor.execute(
                """
                INSERT INTO posts (user_id, content, image_url, video_url, created_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (user_id, content, image_url, video_url, datetime.now(timezone.utc)),
            )

        if USE_POSTGRESQL:
            result = cursor.fetchone()
            post_id = result["id"]
            created_at = result["created_at"]
        else:
            post_id = cursor.lastrowid
            created_at = datetime.now(timezone.utc)

        # Get user information for response
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT id, email, first_name, last_name, avatar_url FROM users WHERE id = %s",
                (user_id,),
            )
        else:
            cursor.execute(
                "SELECT id, email, first_name, last_name, avatar_url FROM users WHERE id = ?",
                (user_id,),
            )

        user = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Post created successfully",
                    "post": {
                        "id": post_id,
                        "content": content,
                        "image_url": image_url,
                        "video_url": video_url,
                        "created_at": created_at,
                        "likes_count": 0,
                        "user": {
                            "id": user["id"],
                            "email": user["email"],
                            "first_name": user["first_name"] or "",
                            "last_name": user["last_name"] or "",
                            "avatar_url": user["avatar_url"] or "",
                        },
                    },
                }
            ),
            201,
        )

    except Exception as e:
        print(f"Create post error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Failed to create post: {str(e)}"}),
            500,
        )


@app.route("/api/posts/<int:post_id>/like", methods=["POST", "OPTIONS"])
def like_post(post_id):
    """Like or unlike a post"""
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

        parts = auth_header.split(" ")
        if len(parts) != 2:
            return (
                jsonify({"success": False, "message": "Invalid authorization header format"}),
                401,
            )
        
        token = parts[1]

        # Decode token to get user_id
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

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user already liked the post
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT id FROM likes WHERE post_id = %s AND user_id = %s",
                (post_id, user_id),
            )
        else:
            cursor.execute(
                "SELECT id FROM likes WHERE post_id = ? AND user_id = ?",
                (post_id, user_id),
            )

        existing_like = cursor.fetchone()

        if existing_like:
            # Unlike - remove the like
            if USE_POSTGRESQL:
                cursor.execute(
                    "DELETE FROM likes WHERE post_id = %s AND user_id = %s",
                    (post_id, user_id),
                )
            else:
                cursor.execute(
                    "DELETE FROM likes WHERE post_id = ? AND user_id = ?",
                    (post_id, user_id),
                )
            message = "Post unliked"
            liked = False
        else:
            # Like - add a new like
            if USE_POSTGRESQL:
                cursor.execute(
                    "INSERT INTO likes (post_id, user_id, created_at) VALUES (%s, %s, %s)",
                    (post_id, user_id, datetime.now(timezone.utc)),
                )
            else:
                cursor.execute(
                    "INSERT INTO likes (post_id, user_id, created_at) VALUES (?, ?, ?)",
                    (post_id, user_id, datetime.now(timezone.utc)),
                )
            message = "Post liked"
            liked = True

        # Get updated likes count
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT COUNT(*) as count FROM likes WHERE post_id = %s", (post_id,)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) as count FROM likes WHERE post_id = ?", (post_id,)
            )

        likes_count = cursor.fetchone()["count"]

        conn.commit()
        cursor.close()
        conn.close()

        return (
            jsonify(
                {
                    "success": True,
                    "message": message,
                    "liked": liked,
                    "likes_count": likes_count,
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Like post error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Failed to like post: {str(e)}"}),
            500,
        )


@app.route("/api/posts/<int:post_id>", methods=["DELETE", "OPTIONS"])
def delete_post(post_id):
    """
    Delete a post - MANUAL DELETION ONLY
    
    Posts are permanently stored and should NEVER be automatically deleted.
    This endpoint only allows:
    1. User to manually delete their own posts
    2. No automatic deletion based on age, pagination, or number of posts
    
    Even with millions of posts, they remain in database.
    Use pagination on GET /api/posts to handle large datasets.
    """
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

        parts = auth_header.split(" ")
        if len(parts) != 2:
            return (
                jsonify({"success": False, "message": "Invalid authorization header format"}),
                401,
            )
        
        token = parts[1]

        # Decode token to get user_id
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

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if post exists and belongs to user
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
            cursor.close()
            conn.close()
            return (
                jsonify({"success": False, "message": "Post not found"}),
                404,
            )

        if post["user_id"] != user_id:
            cursor.close()
            conn.close()
            return (
                jsonify(
                    {"success": False, "message": "You can only delete your own posts"}
                ),
                403,
            )

        # Delete the post (likes and comments will be cascade deleted)
        if USE_POSTGRESQL:
            cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        else:
            cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))

        conn.commit()
        cursor.close()
        conn.close()

        return (
            jsonify({"success": True, "message": "Post deleted successfully"}),
            200,
        )

    except Exception as e:
        print(f"Delete post error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Failed to delete post: {str(e)}"}),
            500,
        )


# ==========================================
# USER ENDPOINTS
# ==========================================

@app.route("/api/users/<int:user_id>", methods=["GET", "OPTIONS"])
def get_user(user_id):
    """
    Get a specific user's profile by ID
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get user details
        cursor.execute(
            """
            SELECT id, email, first_name, last_name, username, avatar_url, bio,
                   occupation, company_name, location, phone, user_type, 
                   is_available_for_hire, created_at
            FROM users
            WHERE id = %s AND is_active = TRUE
            """ if USE_POSTGRESQL else """
            SELECT id, email, first_name, last_name, username, avatar_url, bio,
                   occupation, company_name, location, phone, user_type, 
                   is_available_for_hire, created_at
            FROM users
            WHERE id = ? AND is_active = 1
            """,
            (user_id,)
        )
        
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "User not found"}), 404

        # Check if current user follows this user
        cursor.execute(
            """
            SELECT id FROM follows
            WHERE follower_id = %s AND followed_id = %s
            """ if USE_POSTGRESQL else """
            SELECT id FROM follows
            WHERE follower_id = ? AND followed_id = ?
            """,
            (current_user_id, user_id)
        )
        is_following = cursor.fetchone() is not None

        # Get follower count
        cursor.execute(
            """
            SELECT COUNT(*) as count FROM follows
            WHERE followed_id = %s
            """ if USE_POSTGRESQL else """
            SELECT COUNT(*) as count FROM follows
            WHERE followed_id = ?
            """,
            (user_id,)
        )
        followers_count = cursor.fetchone()["count"]

        # Get following count
        cursor.execute(
            """
            SELECT COUNT(*) as count FROM follows
            WHERE follower_id = %s
            """ if USE_POSTGRESQL else """
            SELECT COUNT(*) as count FROM follows
            WHERE follower_id = ?
            """,
            (user_id,)
        )
        following_count = cursor.fetchone()["count"]

        # Get posts count
        cursor.execute(
            """
            SELECT COUNT(*) as count FROM posts
            WHERE user_id = %s
            """ if USE_POSTGRESQL else """
            SELECT COUNT(*) as count FROM posts
            WHERE user_id = ?
            """,
            (user_id,)
        )
        posts_count = cursor.fetchone()["count"]

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"] or "",
                "last_name": user["last_name"] or "",
                "username": user["username"],
                "avatar_url": user["avatar_url"],
                "bio": user["bio"],
                "occupation": user["occupation"],
                "company_name": user["company_name"],
                "location": user["location"],
                "phone": user["phone"],
                "user_type": user["user_type"] or "user",
                "is_available_for_hire": user["is_available_for_hire"] or False,
                "created_at": user["created_at"],
                "posts_count": posts_count,
                "is_following": is_following,
                "followers_count": followers_count,
                "following_count": following_count,
            }
        }), 200

    except Exception as e:
        print(f"Get user error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to fetch user: {str(e)}"}), 500


@app.route("/api/users/list", methods=["GET", "OPTIONS"])
def get_users_list():
    """
    Get list of users with optional search
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        # Get search parameter and sanitize it
        search = request.args.get("search", "").strip()
        
        # Validate search input (max 100 chars, no SQL special chars that aren't escaped by parameterization)
        if search and len(search) > 100:
            return jsonify({"success": False, "message": "Search query too long"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query based on search
        if search:
            # Escape wildcards in search pattern to prevent injection
            # The % and _ are already safely parameterized, but we sanitize for clarity
            search_pattern = f"%{search}%"
            cursor.execute(
                """
                SELECT id, email, first_name, last_name, username, avatar_url, bio,
                       occupation, location
                FROM users
                WHERE is_active = TRUE AND id != %s
                AND (first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s 
                     OR occupation ILIKE %s OR location ILIKE %s)
                LIMIT 50
                """ if USE_POSTGRESQL else """
                SELECT id, email, first_name, last_name, username, avatar_url, bio,
                       occupation, location
                FROM users
                WHERE is_active = 1 AND id != ?
                AND (first_name LIKE ? OR last_name LIKE ? OR email LIKE ? 
                     OR occupation LIKE ? OR location LIKE ?)
                LIMIT 50
                """,
                (current_user_id, search_pattern, search_pattern, search_pattern, 
                 search_pattern, search_pattern)
            )
        else:
            cursor.execute(
                """
                SELECT id, email, first_name, last_name, username, avatar_url, bio,
                       occupation, location
                FROM users
                WHERE is_active = TRUE AND id != %s
                LIMIT 50
                """ if USE_POSTGRESQL else """
                SELECT id, email, first_name, last_name, username, avatar_url, bio,
                       occupation, location
                FROM users
                WHERE is_active = 1 AND id != ?
                LIMIT 50
                """,
                (current_user_id,)
            )

        users = cursor.fetchall()

        # Get follow status for each user (batch query)
        user_ids = [u["id"] for u in users]
        following_ids = set()
        
        if user_ids:
            placeholders = ",".join(["%s" if USE_POSTGRESQL else "?" for _ in user_ids])
            cursor.execute(
                """
                SELECT followed_id FROM follows
                WHERE follower_id = %s AND followed_id IN ({})
                """.format(placeholders) if USE_POSTGRESQL else """
                SELECT followed_id FROM follows
                WHERE follower_id = ? AND followed_id IN ({})
                """.format(placeholders),
                [current_user_id] + user_ids
            )
            following_ids = {row["followed_id"] for row in cursor.fetchall()}
            
            # Get follower counts for all users in one query
            cursor.execute(
                """
                SELECT followed_id, COUNT(*) as count
                FROM follows
                WHERE followed_id IN ({})
                GROUP BY followed_id
                """.format(placeholders) if USE_POSTGRESQL else """
                SELECT followed_id, COUNT(*) as count
                FROM follows
                WHERE followed_id IN ({})
                GROUP BY followed_id
                """.format(placeholders),
                user_ids
            )
            followers_counts = {row["followed_id"]: row["count"] for row in cursor.fetchall()}
            
            # Get following counts for all users in one query
            cursor.execute(
                """
                SELECT follower_id, COUNT(*) as count
                FROM follows
                WHERE follower_id IN ({})
                GROUP BY follower_id
                """.format(placeholders) if USE_POSTGRESQL else """
                SELECT follower_id, COUNT(*) as count
                FROM follows
                WHERE follower_id IN ({})
                GROUP BY follower_id
                """.format(placeholders),
                user_ids
            )
            following_counts = {row["follower_id"]: row["count"] for row in cursor.fetchall()}
        else:
            followers_counts = {}
            following_counts = {}

        # Build user list with follow status and counts
        users_data = []
        for user in users:
            followers_count = followers_counts.get(user["id"], 0)
            following_count = following_counts.get(user["id"], 0)

            users_data.append({
                "id": user["id"],
                "first_name": user["first_name"] or "",
                "last_name": user["last_name"] or "",
                "email": user["email"],
                "username": user["username"],
                "avatar_url": user["avatar_url"],
                "bio": user["bio"],
                "occupation": user["occupation"],
                "location": user["location"],
                "is_following": user["id"] in following_ids,
                "followers_count": followers_count,
                "following_count": following_count,
            })

        cursor.close()
        conn.close()

        return jsonify({"success": True, "users": users_data, "total": len(users_data)}), 200

    except Exception as e:
        print(f"Get users list error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to fetch users: {str(e)}"}), 500


@app.route("/api/users/follow/<int:user_id>", methods=["POST", "OPTIONS"])
def follow_user(user_id):
    """
    Follow a user
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        if current_user_id == user_id:
            return jsonify({"success": False, "message": "Cannot follow yourself"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute(
            """
            SELECT id FROM users WHERE id = %s
            """ if USE_POSTGRESQL else """
            SELECT id FROM users WHERE id = ?
            """,
            (user_id,)
        )
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "User not found"}), 404

        # Check if already following
        cursor.execute(
            """
            SELECT id FROM follows
            WHERE follower_id = %s AND followed_id = %s
            """ if USE_POSTGRESQL else """
            SELECT id FROM follows
            WHERE follower_id = ? AND followed_id = ?
            """,
            (current_user_id, user_id)
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Already following this user"}), 400

        # Create follow relationship
        cursor.execute(
            """
            INSERT INTO follows (follower_id, followed_id)
            VALUES (%s, %s)
            """ if USE_POSTGRESQL else """
            INSERT INTO follows (follower_id, followed_id)
            VALUES (?, ?)
            """,
            (current_user_id, user_id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "User followed successfully"}), 200

    except Exception as e:
        print(f"Follow user error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to follow user: {str(e)}"}), 500


@app.route("/api/users/unfollow/<int:user_id>", methods=["POST", "OPTIONS"])
def unfollow_user(user_id):
    """
    Unfollow a user
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if following
        cursor.execute(
            """
            SELECT id FROM follows
            WHERE follower_id = %s AND followed_id = %s
            """ if USE_POSTGRESQL else """
            SELECT id FROM follows
            WHERE follower_id = ? AND followed_id = ?
            """,
            (current_user_id, user_id)
        )
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Not following this user"}), 400

        # Delete follow relationship
        cursor.execute(
            """
            DELETE FROM follows
            WHERE follower_id = %s AND followed_id = %s
            """ if USE_POSTGRESQL else """
            DELETE FROM follows
            WHERE follower_id = ? AND followed_id = ?
            """,
            (current_user_id, user_id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "User unfollowed successfully"}), 200

    except Exception as e:
        print(f"Unfollow user error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to unfollow user: {str(e)}"}), 500


@app.route("/api/users/following/list", methods=["GET", "OPTIONS"])
def get_following_list():
    """
    Get list of users that current user is following
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get users that current user is following
        cursor.execute(
            """
            SELECT u.id, u.email, u.first_name, u.last_name, u.username, 
                   u.avatar_url, u.bio, u.occupation, u.location
            FROM users u
            INNER JOIN follows f ON u.id = f.followed_id
            WHERE f.follower_id = %s
            """ if USE_POSTGRESQL else """
            SELECT u.id, u.email, u.first_name, u.last_name, u.username, 
                   u.avatar_url, u.bio, u.occupation, u.location
            FROM users u
            INNER JOIN follows f ON u.id = f.followed_id
            WHERE f.follower_id = ?
            """,
            (current_user_id,)
        )

        following_users = cursor.fetchall()
        
        following_data = [
            {
                "id": user["id"],
                "first_name": user["first_name"] or "",
                "last_name": user["last_name"] or "",
                "email": user["email"],
                "username": user["username"],
                "avatar_url": user["avatar_url"],
                "bio": user["bio"],
                "occupation": user["occupation"],
                "location": user["location"],
            }
            for user in following_users
        ]

        cursor.close()
        conn.close()

        return jsonify({"success": True, "following": following_data}), 200

    except Exception as e:
        print(f"Get following list error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to fetch following list: {str(e)}"}), 500


@app.route("/api/users/followers/list", methods=["GET", "OPTIONS"])
def get_followers_list():
    """
    Get list of users that follow current user
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get users that follow current user
        cursor.execute(
            """
            SELECT u.id, u.email, u.first_name, u.last_name, u.username, 
                   u.avatar_url, u.bio, u.occupation, u.location
            FROM users u
            INNER JOIN follows f ON u.id = f.follower_id
            WHERE f.followed_id = %s
            """ if USE_POSTGRESQL else """
            SELECT u.id, u.email, u.first_name, u.last_name, u.username, 
                   u.avatar_url, u.bio, u.occupation, u.location
            FROM users u
            INNER JOIN follows f ON u.id = f.follower_id
            WHERE f.followed_id = ?
            """,
            (current_user_id,)
        )

        followers = cursor.fetchall()
        
        followers_data = [
            {
                "id": user["id"],
                "first_name": user["first_name"] or "",
                "last_name": user["last_name"] or "",
                "email": user["email"],
                "username": user["username"],
                "avatar_url": user["avatar_url"],
                "bio": user["bio"],
                "occupation": user["occupation"],
                "location": user["location"],
            }
            for user in followers
        ]

        cursor.close()
        conn.close()

        return jsonify({"success": True, "followers": followers_data}), 200

    except Exception as e:
        print(f"Get followers list error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to fetch followers list: {str(e)}"}), 500


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

# Export application for gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting HireMeBahamas backend on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)

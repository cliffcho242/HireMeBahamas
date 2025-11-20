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

# ==========================================
# STARTUP INITIALIZATION
# ==========================================
print("=" * 60)
print("🚀 HireMeBahamas Backend Initialization")
print("=" * 60)

# Quick dependency check on startup
try:
    critical_deps = ["flask", "flask_cors", "flask_limiter", "jwt", "bcrypt"]
    missing_deps = []
    
    for dep in critical_deps:
        try:
            __import__(dep)
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"❌ Missing critical dependencies: {', '.join(missing_deps)}")
        print("💡 Run: python scripts/activate_all_dependencies.py")
        raise ImportError(f"Critical dependencies missing: {missing_deps}")
    
    print("✅ All critical dependencies loaded")
except Exception as e:
    print(f"⚠️  Startup check warning: {str(e)}")

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


# Serve admin dashboard
@app.route("/admin/dependencies")
def admin_dependencies():
    """Serve the dependency dashboard HTML"""
    admin_panel_path = os.path.join(os.path.dirname(__file__), "admin_panel")
    return send_from_directory(admin_panel_path, "dependencies.html")


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


# Initialize database on startup
init_database()


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


@app.route("/api/health/dependencies", methods=["GET"])
def dependencies_health():
    """Comprehensive dependency health check endpoint"""
    import importlib
    from datetime import datetime
    
    def check_package(package_name, import_name=None):
        """Check if a package is installed"""
        if import_name is None:
            import_name = package_name.lower().replace("-", "_")
        try:
            module = importlib.import_module(import_name)
            version = getattr(module, "__version__", "unknown")
            return {"active": True, "version": version}
        except ImportError:
            return {"active": False, "version": "not installed"}
    
    def check_redis():
        """Check Redis status"""
        try:
            import redis
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            try:
                r = redis.from_url(redis_url, socket_connect_timeout=2)
                start = datetime.now(timezone.utc)
                r.ping()
                latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000
                return {
                    "active": True,
                    "connected": True,
                    "latency_ms": round(latency, 2)
                }
            except Exception:
                return {"active": False, "connected": False}
        except ImportError:
            return {"active": False, "connected": False, "note": "redis-py not installed"}
    
    def check_database():
        """Check database status"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return {
                "active": True,
                "connected": True,
                "type": "postgresql" if USE_POSTGRESQL else "sqlite"
            }
        except Exception as e:
            return {
                "active": False,
                "connected": False,
                "error": str(e)
            }
    
    # Check backend dependencies
    backend_deps = {
        "flask": check_package("Flask", "flask"),
        "redis": check_redis(),
        "database": check_database(),
        "flask_cors": check_package("Flask-CORS", "flask_cors"),
        "flask_limiter": check_package("Flask-Limiter", "flask_limiter"),
        "flask_caching": check_package("Flask-Caching", "flask_caching"),
        "jwt": check_package("PyJWT", "jwt"),
        "bcrypt": check_package("bcrypt", "bcrypt"),
    }
    
    # Determine status
    missing = []
    for name, info in backend_deps.items():
        if isinstance(info, dict) and not info.get("active", False):
            if info.get("version") == "not installed":
                missing.append(name)
    
    critical_active = backend_deps["flask"]["active"] and backend_deps["database"]["active"]
    status = "healthy" if critical_active else "unhealthy"
    
    return jsonify({
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dependencies": {
            "backend": backend_deps
        },
        "missing_dependencies": missing,
        "inactive_services": []
    })


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
# APPLICATION ENTRY POINT
# ==========================================

# Export application for gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting HireMeBahamas backend on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)

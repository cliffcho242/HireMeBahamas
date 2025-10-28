"""
Admin Control Panel Backend - Flask API
Separate admin routes with role-based access control
"""

import os
import sqlite3
from datetime import datetime, timedelta
from functools import wraps

import bcrypt
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = os.getenv(
    "ADMIN_SECRET_KEY", "admin-secret-key-change-in-production"
)
app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY", "jwt-secret-key-change-in-production"
)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)

# Initialize extensions
jwt = JWTManager(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://",
)

# CORS for admin panel
CORS(
    app,
    resources={
        r"/admin/*": {
            "origins": [
                "http://localhost:3001",
                "http://localhost:5173",
                "https://admin.hiremebahamas.com",
            ]
        }
    },
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)

DATABASE = "hireme_bahamas.db"


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_admin_tables():
    """Initialize admin-specific tables"""
    conn = get_db()
    cursor = conn.cursor()

    # Add is_admin column to users table if it doesn't exist
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        conn.commit()
        print("✅ Added is_admin column to users table")
    except sqlite3.OperationalError:
        print("✓ is_admin column already exists")

    # Create admin_logs table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id INTEGER,
            details TEXT,
            ip_address TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES users (id)
        )
    """
    )

    # Create admin_settings table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_by INTEGER,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (updated_by) REFERENCES users (id)
        )
    """
    )

    conn.commit()
    conn.close()
    print("✅ Admin tables initialized")


def admin_required(fn):
    """Decorator to require admin role"""

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = int(get_jwt_identity())

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (current_user_id,))
        user = cursor.fetchone()
        conn.close()

        if not user or not user["is_admin"]:
            return jsonify({"error": "Admin access required", "success": False}), 403

        return fn(*args, **kwargs)

    return wrapper


def log_admin_action(admin_id, action, target_type=None, target_id=None, details=None):
    """Log admin actions"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO admin_logs (admin_id, action, target_type, target_id, details, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (admin_id, action, target_type, target_id, details, request.remote_addr),
    )
    conn.commit()
    conn.close()


# ============================================================================
# ADMIN AUTHENTICATION ROUTES
# ============================================================================


@app.route("/admin/auth/login", methods=["POST", "OPTIONS"])
@limiter.limit("10 per minute")
def admin_login():
    """Admin-only login endpoint"""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json()
    email = data.get("email", "").lower().strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password required", "success": False}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? AND is_admin = 1", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Invalid admin credentials", "success": False}), 401

    # Verify password
    if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({"error": "Invalid admin credentials", "success": False}), 401

    # Create access token
    access_token = create_access_token(
        identity=str(user["id"]), additional_claims={"is_admin": True}
    )

    log_admin_action(user["id"], "login", details="Admin logged in")

    return (
        jsonify(
            {
                "success": True,
                "access_token": access_token,
                "admin": {
                    "id": user["id"],
                    "email": user["email"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                },
            }
        ),
        200,
    )


@app.route("/admin/auth/me", methods=["GET"])
@jwt_required()
def admin_me():
    """Get current admin user info"""
    current_user_id = int(get_jwt_identity())

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE id = ? AND is_admin = 1", (current_user_id,)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Not authorized", "success": False}), 403

    return (
        jsonify(
            {
                "success": True,
                "admin": {
                    "id": user["id"],
                    "email": user["email"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                },
            }
        ),
        200,
    )


# ============================================================================
# USER MANAGEMENT ROUTES
# ============================================================================


@app.route("/admin/users", methods=["GET"])
@admin_required
def get_all_users():
    """Get all users with pagination and filters"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search = request.args.get("search", "")
    user_type = request.args.get("user_type", "")

    conn = get_db()
    cursor = conn.cursor()

    # Build query
    query = "SELECT id, email, first_name, last_name, user_type, location, created_at, is_admin FROM users WHERE 1=1"
    params = []

    if search:
        query += " AND (email LIKE ? OR first_name LIKE ? OR last_name LIKE ?)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])

    if user_type:
        query += " AND user_type = ?"
        params.append(user_type)

    # Get total count
    count_query = query.replace(
        "SELECT id, email, first_name, last_name, user_type, location, created_at, is_admin",
        "SELECT COUNT(*)",
    )
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]

    # Get paginated results
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])

    cursor.execute(query, params)
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return (
        jsonify(
            {
                "success": True,
                "users": users,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page,
            }
        ),
        200,
    )


@app.route("/admin/users/<int:user_id>", methods=["GET"])
@admin_required
def get_user_detail(user_id):
    """Get detailed user information"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "User not found", "success": False}), 404

    user_dict = dict(user)
    user_dict.pop("password", None)  # Remove password

    return jsonify({"success": True, "user": user_dict}), 200


@app.route("/admin/users/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    """Update user information"""
    data = request.get_json()
    admin_id = int(get_jwt_identity())

    conn = get_db()
    cursor = conn.cursor()

    # Build update query
    updates = []
    params = []

    allowed_fields = [
        "email",
        "first_name",
        "last_name",
        "user_type",
        "location",
        "bio",
        "is_admin",
    ]
    for field in allowed_fields:
        if field in data:
            updates.append(f"{field} = ?")
            params.append(data[field])

    if not updates:
        return jsonify({"error": "No valid fields to update", "success": False}), 400

    params.append(user_id)
    query = f'UPDATE users SET {", ".join(updates)} WHERE id = ?'

    cursor.execute(query, params)
    conn.commit()
    conn.close()

    log_admin_action(
        admin_id,
        "update_user",
        "user",
        user_id,
        f'Updated fields: {", ".join(data.keys())}',
    )

    return jsonify({"success": True, "message": "User updated successfully"}), 200


@app.route("/admin/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """Delete a user"""
    admin_id = int(get_jwt_identity())

    # Prevent admin from deleting themselves
    if user_id == admin_id:
        return (
            jsonify({"error": "Cannot delete your own account", "success": False}),
            400,
        )

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    log_admin_action(admin_id, "delete_user", "user", user_id)

    return jsonify({"success": True, "message": "User deleted successfully"}), 200


# ============================================================================
# STATISTICS & DASHBOARD ROUTES
# ============================================================================


@app.route("/admin/dashboard/stats", methods=["GET"])
@admin_required
def get_dashboard_stats():
    """Get dashboard statistics"""
    conn = get_db()
    cursor = conn.cursor()

    # Total users
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 0")
    total_users = cursor.fetchone()[0]

    # Users by type
    cursor.execute(
        "SELECT user_type, COUNT(*) as count FROM users WHERE is_admin = 0 GROUP BY user_type"
    )
    users_by_type = {row[0]: row[1] for row in cursor.fetchall()}

    # New users this month
    cursor.execute(
        """
        SELECT COUNT(*) FROM users 
        WHERE is_admin = 0 AND created_at >= date('now', 'start of month')
    """
    )
    new_users_month = cursor.fetchone()[0]

    # Users by location
    cursor.execute(
        """
        SELECT location, COUNT(*) as count FROM users 
        WHERE is_admin = 0 AND location IS NOT NULL 
        GROUP BY location 
        ORDER BY count DESC 
        LIMIT 10
    """
    )
    users_by_location = [
        {"location": row[0], "count": row[1]} for row in cursor.fetchall()
    ]

    conn.close()

    return (
        jsonify(
            {
                "success": True,
                "stats": {
                    "total_users": total_users,
                    "users_by_type": users_by_type,
                    "new_users_month": new_users_month,
                    "users_by_location": users_by_location,
                },
            }
        ),
        200,
    )


@app.route("/admin/dashboard/activity", methods=["GET"])
@admin_required
def get_recent_activity():
    """Get recent user activity"""
    limit = request.args.get("limit", 50, type=int)

    conn = get_db()
    cursor = conn.cursor()

    # Recent registrations
    cursor.execute(
        """
        SELECT id, email, first_name, last_name, user_type, created_at 
        FROM users 
        WHERE is_admin = 0 
        ORDER BY created_at DESC 
        LIMIT ?
    """,
        (limit,),
    )
    recent_users = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify({"success": True, "recent_users": recent_users}), 200


# ============================================================================
# ADMIN LOGS ROUTES
# ============================================================================


@app.route("/admin/logs", methods=["GET"])
@admin_required
def get_admin_logs():
    """Get admin activity logs"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    conn = get_db()
    cursor = conn.cursor()

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM admin_logs")
    total = cursor.fetchone()[0]

    # Get logs with admin info
    cursor.execute(
        """
        SELECT al.*, u.email as admin_email, u.first_name, u.last_name
        FROM admin_logs al
        JOIN users u ON al.admin_id = u.id
        ORDER BY al.timestamp DESC
        LIMIT ? OFFSET ?
    """,
        (per_page, (page - 1) * per_page),
    )

    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return (
        jsonify(
            {
                "success": True,
                "logs": logs,
                "total": total,
                "page": page,
                "per_page": per_page,
            }
        ),
        200,
    )


# ============================================================================
# SYSTEM SETTINGS ROUTES
# ============================================================================


@app.route("/admin/settings", methods=["GET"])
@admin_required
def get_settings():
    """Get all system settings"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin_settings")
    settings = {row["key"]: row["value"] for row in cursor.fetchall()}
    conn.close()

    return jsonify({"success": True, "settings": settings}), 200


@app.route("/admin/settings", methods=["PUT"])
@admin_required
def update_settings():
    """Update system settings"""
    data = request.get_json()
    admin_id = int(get_jwt_identity())

    conn = get_db()
    cursor = conn.cursor()

    for key, value in data.items():
        cursor.execute(
            """
            INSERT INTO admin_settings (key, value, updated_by)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET 
                value = excluded.value,
                updated_by = excluded.updated_by,
                updated_at = CURRENT_TIMESTAMP
        """,
            (key, str(value), admin_id),
        )

    conn.commit()
    conn.close()

    log_admin_action(
        admin_id, "update_settings", details=f"Updated {len(data)} settings"
    )

    return jsonify({"success": True, "message": "Settings updated successfully"}), 200


# ============================================================================
# HEALTH CHECK
# ============================================================================


@app.route("/admin/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return (
        jsonify({"status": "healthy", "service": "admin-api", "version": "1.0.0"}),
        200,
    )


if __name__ == "__main__":
    print("Initializing Admin Control Panel API...")
    init_admin_tables()
    print("✅ Admin API ready on port 8000")
    app.run(host="0.0.0.0", port=8000, debug=True)

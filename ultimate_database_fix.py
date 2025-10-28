"""
Complete Database Fix - Handle Multiple Database Files
Fix all database files and ensure backend uses correct one
"""

import os
import sqlite3
from pathlib import Path

import bcrypt


def fix_all_databases():
    """Fix all database files in the workspace"""

    workspace = Path("C:/Users/Dell/OneDrive/Desktop/HireBahamas")

    # List of all possible database locations
    db_paths = [workspace / "hirebahamas.db", workspace / "backend" / "hirebahamas.db"]

    print("🔧 Fixing all database files...")

    for db_path in db_paths:
        if db_path.exists():
            print(f"\n📂 Processing: {db_path}")
            fix_database(db_path)
        else:
            print(f"\n📂 Creating: {db_path}")
            create_database(db_path)


def fix_database(db_path):
    """Fix a specific database file"""

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Check current structure
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns] if columns else []

    print(f"   Current columns: {column_names}")

    # Check if password_hash column exists
    if "password_hash" not in column_names:
        print("   ❌ Missing password_hash column - rebuilding table...")
        rebuild_table(cursor, conn)
        return

    print("   ✅ Table structure correct")

    # Delete existing admin user if exists
    cursor.execute("DELETE FROM users WHERE email = ?", ("admin@hirebahamas.com",))

    # Create admin user with proper structure
    password = "AdminPass123!"
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # Use the columns that actually exist in the database
    if "first_name" in column_names and "last_name" in column_names:
        # Database uses first_name/last_name structure
        print("   ℹ️ Using first_name/last_name structure")

        # Check what columns are available for INSERT
        available_columns = []
        if "user_type" in column_names:
            available_columns.append("user_type")
        if "is_active" in column_names:
            available_columns.append("is_active")

        # Build INSERT statement dynamically
        insert_columns = [
            "email",
            "password_hash",
            "first_name",
            "last_name",
        ] + available_columns
        placeholders = ["?"] * len(insert_columns)
        values = [
            "admin@hirebahamas.com",
            password_hash.decode("utf-8"),
            "Platform",
            "Administrator",
        ]

        if "user_type" in column_names:
            values.append("admin")
        if "is_active" in column_names:
            values.append(1)

        insert_sql = f"""
            INSERT INTO users ({', '.join(insert_columns)})
            VALUES ({', '.join(placeholders)})
        """

        cursor.execute(insert_sql, values)
    elif "username" in column_names and "full_name" in column_names:
        # Database uses username/full_name structure
        print("   ℹ️ Using username/full_name structure")
        cursor.execute(
            """
            INSERT INTO users (email, password_hash, username, full_name, bio, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                "admin@hirebahamas.com",
                password_hash.decode("utf-8"),
                "admin",
                "Platform Administrator",
                "Welcome to HireBahamas - Your AI-Powered Social Platform! 🚀",
                1,
            ),
        )
    else:
        print("   ❌ Unknown table structure - rebuilding...")
        rebuild_table(cursor, conn)
        return

    conn.commit()

    # Verify admin user was created
    cursor.execute(
        "SELECT id, email FROM users WHERE email = ?", ("admin@hirebahamas.com",)
    )
    admin_user = cursor.fetchone()

    if admin_user:
        print(f"   ✅ Admin created: ID={admin_user[0]}")

        # Test password verification
        cursor.execute(
            "SELECT password_hash FROM users WHERE email = ?",
            ("admin@hirebahamas.com",),
        )
        stored_hash = cursor.fetchone()[0]

        if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
            print("   ✅ Password verification: OK")
        else:
            print("   ❌ Password verification: FAILED")
    else:
        print("   ❌ Admin creation failed")

    conn.close()


def rebuild_table(cursor, conn):
    """Rebuild the users table with correct structure"""

    # Backup existing data
    try:
        cursor.execute("SELECT * FROM users")
        existing_users = cursor.fetchall()
        print(f"   📦 Backing up {len(existing_users)} existing users")
    except:
        existing_users = []

    # Drop and recreate table
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute(
        """
        CREATE TABLE users (
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
            is_active BOOLEAN DEFAULT 1
        )
    """
    )

    print("   ✅ Table recreated with first_name/last_name structure")

    # Create admin user
    password = "AdminPass123!"
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    cursor.execute(
        """
        INSERT INTO users (email, password_hash, first_name, last_name, user_type, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            "admin@hirebahamas.com",
            password_hash.decode("utf-8"),
            "Platform",
            "Administrator",
            "admin",
            1,
        ),
    )

    conn.commit()
    print("   ✅ Admin user created")


def create_database(db_path):
    """Create a new database file"""

    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create users table with first_name/last_name structure
    cursor.execute(
        """
        CREATE TABLE users (
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
            is_active BOOLEAN DEFAULT 1
        )
    """
    )

    # Create admin user
    password = "AdminPass123!"
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    cursor.execute(
        """
        INSERT INTO users (email, password_hash, first_name, last_name, user_type, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            "admin@hirebahamas.com",
            password_hash.decode("utf-8"),
            "Platform",
            "Administrator",
            "admin",
            1,
        ),
    )

    conn.commit()
    conn.close()

    print(f"   ✅ Created new database with admin user")


def test_backend_connection():
    """Test which database the backend is actually using"""

    import time

    import requests

    print("\n🧪 Testing backend database connection...")

    # Try to hit health endpoint first
    try:
        health_response = requests.get("http://127.0.0.1:8008/health", timeout=5)
        if health_response.status_code == 200:
            print("   ✅ Backend is running")
        else:
            print("   ❌ Backend health check failed")
            return False
    except:
        print("   ❌ Backend not responding")
        print("   💡 Please start the backend server first")
        return False

    # Test login
    login_data = {"email": "admin@hirebahamas.com", "password": "AdminPass123!"}

    try:
        response = requests.post(
            "http://127.0.0.1:8008/api/auth/login", json=login_data, timeout=10
        )
        if response.status_code == 200:
            print("   ✅ Login working!")
            print(f"   ✅ Response: {response.json()}")
            return True
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            try:
                print(f"   Error: {response.json()}")
            except:
                print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {str(e)[:100]}")
        return False


def main():
    print("=" * 60)
    print("🔧 Complete Database Fix - All Locations")
    print("=" * 60)

    # Fix all databases
    fix_all_databases()

    print("\n✅ Database fix complete!")
    print("\n📋 ADMIN CREDENTIALS:")
    print("   Email: admin@hirebahamas.com")
    print("   Password: AdminPass123!")

    # Test if backend is running
    print("\n🔄 Testing backend connection...")

    if test_backend_connection():
        print("\n🎉 SUCCESS! Everything is working!")
        print("\n🌐 Access your platform:")
        print("   Frontend: http://localhost:3000")
        print("   Backend: http://127.0.0.1:8008")
    else:
        print("\n⚠️ Backend needs to be started/restarted:")
        print("\n📝 Next steps:")
        print("   1. Stop the backend if running (Ctrl+C)")
        print("   2. Run: python ULTIMATE_BACKEND_FIXED.py")
        print("   3. Or double-click: COMPLETE_RESTART.bat")
        print("\n   Then try logging in at http://localhost:3000")


if __name__ == "__main__":
    main()

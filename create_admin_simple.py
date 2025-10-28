#!/usr/bin/env python3
"""
Simple Admin User Creation Script
Creates admin user using direct SQLite operations
"""

import sqlite3
from datetime import datetime
from pathlib import Path

import bcrypt


def create_admin_user():
    """Create admin user directly in SQLite database"""

    # Admin user details
    admin_email = "admin@hiremebahamas.com"
    admin_password = "Admin123!"

    # Database path
    db_path = Path(__file__).parent / "backend" / "hiremebahamas.db"

    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        return False

    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check if admin user already exists
        cursor.execute(
            "SELECT id, email, first_name, last_name FROM users WHERE email = ?",
            (admin_email,),
        )
        existing_user = cursor.fetchone()

        if existing_user:
            print(f"❌ Admin user already exists:")
            print(f"   ID: {existing_user[0]}")
            print(f"   Email: {existing_user[1]}")
            print(f"   Name: {existing_user[2]} {existing_user[3]}")
            conn.close()
            return False

        # Hash password
        password_bytes = admin_password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode("utf-8")

        # Create admin user
        now = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO users (
                email, hashed_password, first_name, last_name, phone, location, 
                bio, skills, experience, education, is_active, is_admin, role, 
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                admin_email,
                hashed_password,
                "Admin",
                "User",
                "+1-242-555-0100",
                "Nassau, Bahamas",
                "Platform Administrator for HireMeBahamas",
                "Platform Management, User Support, Content Moderation",
                "Platform Administration, Community Management",
                "Administrative Experience",
                1,  # is_active
                1,  # is_admin
                "admin",  # role
                now,
                now,
            ),
        )

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        print("✅ Admin user created successfully!")
        print("=" * 50)
        print("📧 ADMIN LOGIN CREDENTIALS")
        print("=" * 50)
        print(f"📧 Email:    {admin_email}")
        print(f"🔑 Password: {admin_password}")
        print(f"👤 Name:     Admin User")
        print(f"📱 Phone:    +1-242-555-0100")
        print(f"📍 Location: Nassau, Bahamas")
        print(f"🎯 Role:     ADMIN")
        print(f"🆔 User ID:  {user_id}")
        print("=" * 50)
        print("⚠️  IMPORTANT SECURITY NOTES:")
        print("   1. Change the default password after first login")
        print("   2. Use a strong, unique password")
        print("   3. Keep admin credentials secure")
        print("=" * 50)

        return True

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("🎯 HireMeBahamas Simple Admin Creation")
    print("=" * 40)

    success = create_admin_user()
    if success:
        print("\n🎉 Admin account setup complete!")
        print("💻 You can now log in with these credentials")
    else:
        print("\n❌ Admin account setup failed")

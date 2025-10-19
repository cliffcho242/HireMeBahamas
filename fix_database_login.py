"""
Database Fix and Admin Account Creation
Fixes the database schema and creates proper admin account
"""

import sqlite3
import bcrypt
import os
from pathlib import Path

def fix_database_and_create_admin():
    """Fix database schema and create admin account"""
    
    workspace = Path("C:/Users/Dell/OneDrive/Desktop/HireBahamas")
    db_path = workspace / "hirebahamas.db"
    
    print(f"🔧 Fixing database: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check current users table structure
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    
    print("📊 Current users table structure:")
    for col in columns:
        print(f"   {col[1]} ({col[2]})")
    
    # Check if password_hash column exists
    column_names = [col[1] for col in columns]
    
    if 'password_hash' not in column_names:
        print("❌ password_hash column missing! Rebuilding users table...")
        
        # Backup existing data if any
        cursor.execute("SELECT * FROM users")
        existing_users = cursor.fetchall()
        
        # Drop existing table
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Create new table with correct structure
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                bio TEXT,
                avatar_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        print("✅ Users table recreated with correct structure")
        
        # Restore any existing users (excluding admin which we'll recreate)
        for user in existing_users:
            if len(user) >= 4 and user[1] != "admin@hirebahamas.com":  # Skip admin, we'll recreate
                try:
                    cursor.execute('''
                        INSERT INTO users (email, username, full_name, bio)
                        VALUES (?, ?, ?, ?)
                    ''', (user[1], user[2] if len(user) > 2 else f"user_{user[0]}", 
                         user[3] if len(user) > 3 else "User", 
                         user[4] if len(user) > 4 else ""))
                except:
                    pass  # Skip if there are conflicts
        
        conn.commit()
    else:
        print("✅ password_hash column exists")
    
    # Create/recreate admin user
    print("🔧 Creating admin user...")
    
    # Delete existing admin if any
    cursor.execute("DELETE FROM users WHERE email = ?", ("admin@hirebahamas.com",))
    
    # Create new admin user
    password = "AdminPass123!"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    cursor.execute('''
        INSERT INTO users (email, password_hash, username, full_name, bio, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        "admin@hirebahamas.com",
        password_hash.decode('utf-8'),
        "admin",
        "Platform Administrator",
        "Welcome to HireBahamas - Your AI-Powered Social Platform! 🚀",
        1
    ))
    
    conn.commit()
    
    # Verify admin user creation
    cursor.execute("SELECT id, email, username FROM users WHERE email = ?", ("admin@hirebahamas.com",))
    admin_user = cursor.fetchone()
    
    if admin_user:
        print(f"✅ Admin user created: ID={admin_user[0]}, Email={admin_user[1]}")
        
        # Test password verification
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", ("admin@hirebahamas.com",))
        stored_hash = cursor.fetchone()[0]
        
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            print("✅ Password verification test passed")
        else:
            print("❌ Password verification test failed")
    else:
        print("❌ Failed to create admin user")
    
    # Show final table structure
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    
    print("\n📊 Final users table structure:")
    for col in columns:
        print(f"   {col[1]} ({col[2]})")
    
    # Show all users
    cursor.execute("SELECT id, email, username, full_name FROM users")
    all_users = cursor.fetchall()
    
    print(f"\n👥 Users in database ({len(all_users)}):")
    for user in all_users:
        print(f"   ID: {user[0]}, Email: {user[1]}, Username: {user[2]}")
    
    conn.close()
    
    return True

def test_login_direct():
    """Test login directly with database"""
    print("\n🧪 Testing direct database login...")
    
    workspace = Path("C:/Users/Dell/OneDrive/Desktop/HireBahamas")
    db_path = workspace / "hirebahamas.db"
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    email = "admin@hirebahamas.com"
    password = "AdminPass123!"
    
    cursor.execute("SELECT id, password_hash, username FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if user:
        print(f"✅ User found: ID={user[0]}, Username={user[2]}")
        
        if bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            print("✅ Password verification: SUCCESS")
            return True
        else:
            print("❌ Password verification: FAILED")
            return False
    else:
        print("❌ User not found in database")
        return False
    
    conn.close()

def main():
    print("=" * 60)
    print("🔧 HireBahamas Database Fix & Admin Creation")
    print("=" * 60)
    
    # Fix database and create admin
    success = fix_database_and_create_admin()
    
    if success:
        # Test login
        login_success = test_login_direct()
        
        if login_success:
            print("\n🎉 SUCCESS! Database and admin account are working!")
            print("\n📋 ADMIN LOGIN CREDENTIALS:")
            print("=" * 40)
            print("Email: admin@hirebahamas.com")
            print("Password: AdminPass123!")
            print("Platform: http://localhost:3000")
            print("Backend: http://127.0.0.1:8008")
            print("=" * 40)
            print("\n💡 You can now login to your Facebook-like AI platform!")
        else:
            print("\n❌ Login test failed - please check the logs")
    else:
        print("\n❌ Database fix failed")

if __name__ == "__main__":
    main()
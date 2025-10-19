#!/usr/bin/env python3
"""
Simple test of the login functionality
"""

import sqlite3
import bcrypt
from pathlib import Path

def test_login():
    """Test login functionality"""
    
    # Database path
    db_path = Path(__file__).parent / "backend" / "hirebahamas.db"
    
    print(f"Database path: {db_path}")
    print(f"Database exists: {db_path.exists()}")
    
    if not db_path.exists():
        print("❌ Database not found!")
        return
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get admin user
    cursor.execute("""
        SELECT id, email, hashed_password, first_name, last_name, 
               is_admin, role FROM users WHERE email = ?
    """, ("admin@hirebahamas.com",))
    
    user = cursor.fetchone()
    
    if not user:
        print("❌ Admin user not found!")
        conn.close()
        return
    
    print(f"✅ Found user: {user[1]} ({user[3]} {user[4]})")
    
    # Test password verification
    test_password = "Admin123!"
    hashed_password = user[2]
    
    print(f"Testing password: {test_password}")
    print(f"Stored hash: {hashed_password[:50]}...")
    
    try:
        result = bcrypt.checkpw(test_password.encode('utf-8'), hashed_password.encode('utf-8'))
        print(f"Password verification: {'✅ SUCCESS' if result else '❌ FAILED'}")
    except Exception as e:
        print(f"❌ Password verification error: {e}")
    
    conn.close()

if __name__ == "__main__":
    test_login()
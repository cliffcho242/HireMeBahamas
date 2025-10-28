#!/usr/bin/env python3
"""
Debug password hashing issue
"""
import sqlite3

import bcrypt


def test_password_verification():
    """Test password verification with current database"""

    # Connect to backend database
    conn = sqlite3.connect("backend/hirebahamas.db")
    cursor = conn.cursor()

    # Get admin user
    cursor.execute(
        "SELECT id, email, password_hash FROM users WHERE email = ?",
        ("admin@hirebahamas.com",),
    )
    user = cursor.fetchone()

    if not user:
        print("❌ No admin user found!")
        return

    user_id, email, stored_hash = user
    print(f"👤 Found user: {email} (ID: {user_id})")
    print(f"🔑 Stored hash: {stored_hash}")
    print(f"🔑 Hash type: {type(stored_hash)}")
    print(f"🔑 Hash length: {len(stored_hash)}")

    # Test password
    test_password = "admin123"
    print(f"\n🧪 Testing password: '{test_password}'")

    # Convert to bytes if needed
    if isinstance(stored_hash, str):
        stored_hash_bytes = stored_hash.encode("utf-8")
    else:
        stored_hash_bytes = stored_hash

    password_bytes = test_password.encode("utf-8")

    print(f"🔑 Password bytes: {password_bytes}")
    print(f"🔑 Hash bytes length: {len(stored_hash_bytes)}")

    # Try verification
    try:
        result = bcrypt.checkpw(password_bytes, stored_hash_bytes)
        print(f"✅ Verification result: {result}")

        if not result:
            # Let's create a new hash and compare
            print("\n🔧 Creating new hash for comparison...")
            new_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
            print(f"🔑 New hash: {new_hash.decode('utf-8')}")

            # Test new hash
            new_result = bcrypt.checkpw(password_bytes, new_hash)
            print(f"✅ New hash verification: {new_result}")

            # Update database with working hash
            if new_result:
                print("\n🔧 Updating database with working hash...")
                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE email = ?",
                    (new_hash.decode("utf-8"), email),
                )
                conn.commit()
                print("✅ Database updated!")

    except Exception as e:
        print(f"❌ Error during verification: {e}")

    conn.close()


if __name__ == "__main__":
    test_password_verification()

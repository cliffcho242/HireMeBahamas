import sqlite3

import bcrypt

conn = sqlite3.connect("hiremebahamas.db")
cursor = conn.cursor()

cursor.execute(
    "SELECT password_hash FROM users WHERE email = ?", ("admin@hiremebahamas.com",)
)
user = cursor.fetchone()

if user:
    stored_hash = user[0]
    test_password = "AdminPass123!"

    if bcrypt.checkpw(test_password.encode("utf-8"), stored_hash.encode("utf-8")):
        print("✅ Password 'AdminPass123!' matches!")
    else:
        print("❌ Password 'AdminPass123!' does not match")
        print(f"Stored hash: {stored_hash[:50]}...")
else:
    print("❌ Admin user not found")

conn.close()

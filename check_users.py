import sqlite3

conn = sqlite3.connect("hiremebahamas.db")
cursor = conn.cursor()

try:
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print(f"Found {len(users)} users in database:")
    for user in users:
        print(f"ID: {user[0]}, Email: {user[1]}, Name: {user[3]}")
except Exception as e:
    print(f"Error: {e}")

conn.close()

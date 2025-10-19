import sqlite3

conn = sqlite3.connect('hirebahamas.db')
cursor = conn.cursor()

print("Checking users table...")
cursor.execute('SELECT id, email, username, full_name, is_active FROM users')
users = cursor.fetchall()

print(f"Found {len(users)} users:")
for user in users:
    print(f"ID: {user[0]}, Email: {user[1]}, Username: {user[2]}, Name: {user[3]}, Active: {user[4]}")

print("\nChecking posts table...")
cursor.execute('SELECT COUNT(*) FROM posts')
post_count = cursor.fetchone()[0]
print(f"Found {post_count} posts")

conn.close()
print("Database check complete.")
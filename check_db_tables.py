import sqlite3

conn = sqlite3.connect('hirebahamas.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

print("Tables in database:")
for table in tables:
    print(f"  - {table}")

# Check posts table specifically
if 'posts' in tables:
    cursor.execute("SELECT COUNT(*) FROM posts")
    count = cursor.fetchone()[0]
    print(f"\nPosts table exists with {count} posts")

    # Check schema
    cursor.execute("PRAGMA table_info(posts)")
    columns = cursor.fetchall()
    print("Posts table columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
else:
    print("\nPosts table does NOT exist!")

conn.close()
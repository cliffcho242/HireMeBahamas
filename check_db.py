import sqlite3

conn = sqlite3.connect("hiremebahamas.db")
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Get columns for each table
for table in tables:
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    print(f"\n{table[0]} columns:")
    for col in columns:
        print(f"  {col[1]} - {col[2]}")

conn.close()

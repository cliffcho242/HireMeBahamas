import sqlite3

# Connect to local database
conn = sqlite3.connect('hiremebahamas.db')
cursor = conn.cursor()

# Get all table schemas
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
schemas = cursor.fetchall()

print("="*60)
print("DATABASE SCHEMA")
print("="*60 + "\n")

for schema in schemas:
    if schema[0]:
        print(schema[0] + ";")
        print()

conn.close()

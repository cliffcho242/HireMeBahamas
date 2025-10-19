#!/usr/bin/env python3
"""Check database schema"""

import sqlite3

conn = sqlite3.connect('hirebahamas.db')
cursor = conn.cursor()

print('Posts table schema:')
cursor.execute('PRAGMA table_info(posts)')
for row in cursor.fetchall():
    print(row)

print('\nUsers table schema:')
cursor.execute('PRAGMA table_info(users)')
for row in cursor.fetchall():
    print(row)

print('\nSample posts query:')
cursor.execute('SELECT p.id, p.content, p.created_at, u.id as user_id, u.first_name, u.last_name, u.email, u.user_type FROM posts p JOIN users u ON p.user_id = u.id LIMIT 1')
result = cursor.fetchone()
if result:
    print('Query works:', result)
else:
    print('Query returned no results')

conn.close()
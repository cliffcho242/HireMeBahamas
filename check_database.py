#!/usr/bin/env python3
"""Check database tables and posts"""

import sqlite3


def check_database():
    conn = sqlite3.connect('hirebahamas.db')
    cursor = conn.cursor()

    # Check tables
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = cursor.fetchall()
    table_names = [t[0] for t in tables]
    print(f'Tables: {table_names}')

    if 'posts' in table_names:
        # Check posts count
        cursor.execute('SELECT COUNT(*) FROM posts')
        count = cursor.fetchone()[0]
        print(f'Posts count: {count}')

        # Show sample posts
        cursor.execute('SELECT id, content, user_id FROM posts LIMIT 3')
        posts = cursor.fetchall()
        print('Sample posts:')
        for post in posts:
            print(f'  ID {post[0]}: {post[1][:50]}... (User: {post[2]})')
    else:
        print('Posts table does not exist!')

    conn.close()


if __name__ == '__main__':
    check_database()

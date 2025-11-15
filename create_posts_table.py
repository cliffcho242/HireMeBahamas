#!/usr/bin/env python3
"""
Create posts table in the database.

⚠️  NOTE: This script no longer adds sample data by default.
To add sample data for development, use: python add_sample_posts.py --dev
"""

import sqlite3


def create_posts_table():
    conn = sqlite3.connect("hirebahamas.db")
    cursor = conn.cursor()

    # Create posts table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """
    )

    # Create likes table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS post_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
            UNIQUE(user_id, post_id)
        )
    """
    )

    conn.commit()

    # Check tables
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = cursor.fetchall()
    table_names = [t[0] for t in tables]
    print(f"Tables: {table_names}")

    if "posts" in table_names:
        print("✅ Posts table created successfully!")
        
        # Check count
        cursor.execute("SELECT COUNT(*) FROM posts")
        count = cursor.fetchone()[0]
        print(f"ℹ️  Total posts in database: {count}")
        
        if count == 0:
            print()
            print("⚠️  No posts in database yet.")
            print("   To add sample data for development, run:")
            print("   python add_sample_posts.py --dev")
    else:
        print("❌ Posts table creation failed")

    conn.close()


if __name__ == "__main__":
    create_posts_table()

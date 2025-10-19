#!/usr/bin/env python3
"""Test the posts functionality directly"""

import sqlite3
from pathlib import Path

def get_db_connection():
    """Get database connection"""
    DB_PATH = Path(__file__).parent / "hirebahamas.db"
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def test_posts_api():
    """Test the posts API logic"""
    try:
        print("Testing posts API logic...")

        # Query posts from database with user information
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                p.id as id, p.content as content, p.image_url as image_url, p.created_at as created_at,
                u.id as user_id, u.first_name as first_name, u.last_name as last_name, u.email as email, u.user_type as user_type
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
        ''')

        posts_data = cursor.fetchall()
        conn.close()

        print(f"Found {len(posts_data)} posts in database")

        # Format posts for frontend
        posts = []
        for row in posts_data:
            posts.append({
                'id': row['id'],
                'content': row['content'],
                'image_url': row['image_url'],
                'created_at': row['created_at'],
                'user': {
                    'id': row['user_id'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'email': row['email'],
                    'user_type': row['user_type']
                },
                'likes_count': 0,  # We'll implement this later
                'comments_count': 0  # We'll implement this later
            })

        print(f"Successfully formatted {len(posts)} posts")
        print("Sample post:", posts[0] if posts else "No posts")

        return {
            "success": True,
            "posts": posts,
            "recommendations": [],  # For SocialFeed compatibility
            "ai_insights": {  # For SocialFeed compatibility
                "user_type": "professional",
                "engagement_score": 85,
                "activity_trend": "increasing"
            }
        }

    except Exception as e:
        print(f"Error in posts API: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": "Failed to get posts",
            "posts": []  # Always return posts array even on error
        }

if __name__ == '__main__':
    result = test_posts_api()
    print("Test result:", result)
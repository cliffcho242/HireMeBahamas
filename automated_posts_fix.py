#!/usr/bin/env python3
"""
Automated Fix for Posts Loading Error
HireBahamas Platform - Posts API Fix
"""

import sqlite3
import subprocess
import sys
import os
from pathlib import Path

def check_database():
    """Check database and posts"""
    print("🔍 Checking database and posts...")

    try:
        conn = sqlite3.connect('hirebahamas.db')
        cursor = conn.cursor()

        # Check tables
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]

        if 'posts' not in table_names:
            print("❌ Posts table missing!")
            return False

        if 'users' not in table_names:
            print("❌ Users table missing!")
            return False

        # Check posts count
        cursor.execute('SELECT COUNT(*) FROM posts')
        count = cursor.fetchone()[0]
        print(f"✅ Found {count} posts in database")

        if count == 0:
            print("⚠️ No posts found, creating sample posts...")
            create_sample_posts(cursor)
            conn.commit()

        # Test posts query
        cursor.execute('''
            SELECT p.id, p.content, u.first_name, u.last_name
            FROM posts p JOIN users u ON p.user_id = u.id
            LIMIT 1
        ''')
        sample = cursor.fetchone()
        if sample:
            print(f"✅ Sample post: '{sample[1][:50]}...' by {sample[2]} {sample[3]}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def create_sample_posts(cursor):
    """Create sample posts if none exist"""
    sample_posts = [
        (1, 'Welcome to HireBahamas! 🌴 The premier platform for connecting talent with opportunities in the beautiful Bahamas.'),
        (1, 'Just launched our new job board. Looking for talented developers, designers, and professionals across all industries! #HireBahamas'),
        (1, 'Beautiful day in Nassau! The perfect environment for innovation and creativity. Join our growing community! ☀️')
    ]

    for user_id, content in sample_posts:
        cursor.execute('INSERT INTO posts (user_id, content) VALUES (?, ?)', (user_id, content))

    print("✅ Created sample posts")

def check_backend_code():
    """Check if backend has posts endpoints"""
    print("🔍 Checking backend code...")

    backend_file = Path('final_backend.py')
    if not backend_file.exists():
        print("❌ final_backend.py not found!")
        return False

    try:
        with open(backend_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if '@app.route(\'/api/posts\'' not in content:
            print("❌ Posts API endpoints missing from backend!")
            return False

        print("✅ Posts API endpoints found in backend")
        return True
    except Exception as e:
        print(f"❌ Error reading backend file: {e}")
        # Try a simpler check - just check if the file contains the route
        try:
            with open(backend_file, 'rb') as f:
                raw_content = f.read()
                if b'@app.route(\'/api/posts\'' in raw_content:
                    print("✅ Posts API endpoints found in backend")
                    return True
                else:
                    print("❌ Posts API endpoints missing from backend!")
                    return False
        except Exception as e2:
            print(f"❌ Error checking backend file: {e2}")
            return False

def test_posts_logic():
    """Test the posts API logic directly"""
    print("🔍 Testing posts API logic...")

    try:
        # Run the test script directly
        result = subprocess.run([sys.executable, 'test_posts.py'],
                              capture_output=True, text=True, timeout=30)

        if result.returncode == 0 and 'Successfully formatted' in result.stdout:
            print("✅ Posts API logic works!")
            return True
        else:
            print("❌ Posts API logic failed")
            print("Output:", result.stdout[-200:])  # Last 200 chars
            return False

    except Exception as e:
        print(f"❌ Error testing posts logic: {e}")
        return False

def provide_instructions():
    """Provide instructions for running the system"""
    print("\n" + "="*50)
    print("🎉 POSTS LOADING ERROR - AUTOMATED FIX COMPLETE!")
    print("="*50)
    print()
    print("✅ Database: Posts table exists with data")
    print("✅ Backend: Posts API endpoints implemented")
    print("✅ Logic: Posts retrieval logic verified")
    print()
    print("🚀 To run the system:")
    print("1. Set up API keys (optional for posts):")
    print("   python configure_api_keys.py --auto")
    print()
    print("2. Start the platform:")
    print("   python advanced_ai_launcher.py")
    print()
    print("3. Or use the automated launcher:")
    print("   .\\AUTO_LAUNCH_HIREBAHAMAS.bat")
    print()
    print("4. Open browser to: http://localhost:3000")
    print()
    print("📝 The posts should now load correctly!")
    print("   If you still see errors, check the browser console")
    print("   and ensure the backend is running on port 8008")
    print()

def main():
    """Main automated fix function"""
    print("🤖 AUTOMATED FIX: Posts Loading Error")
    print("="*40)

    success = True

    # Check database
    if not check_database():
        success = False

    # Check backend code
    if not check_backend_code():
        success = False

    # Test posts logic
    if not test_posts_logic():
        success = False

    if success:
        provide_instructions()
        return 0
    else:
        print("\n❌ Automated fix failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
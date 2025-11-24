#!/usr/bin/env python3
"""
Diagnostic tool to investigate if posts from admin accounts are being deleted after inactivity.

This script checks:
1. Database structure for posts and users
2. Posts from admin accounts
3. Foreign key constraints and cascade rules
4. Scheduled tasks or cleanup jobs
5. Session expiration and user inactivity handling
6. Post filtering logic in queries

Usage:
    python diagnose_admin_post_deletion.py
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


def check_database_connection():
    """Check if database exists and is accessible"""
    print("=" * 80)
    print("1. DATABASE CONNECTION CHECK")
    print("=" * 80)
    
    db_url = os.environ.get("DATABASE_URL")
    
    if db_url and db_url.startswith("postgresql"):
        print("✓ Using PostgreSQL database")
        print(f"  Database URL: {db_url.split('@')[1] if '@' in db_url else 'configured'}")
        return "postgresql", db_url
    else:
        db_path = "hiremebahamas.db"
        if os.path.exists(db_path):
            print(f"✓ Using SQLite database: {db_path}")
            print(f"  File size: {os.path.getsize(db_path)} bytes")
            return "sqlite", db_path
        else:
            print(f"❌ Database file not found: {db_path}")
            return None, None


def connect_db(db_type, db_path_or_url):
    """Connect to the database"""
    if db_type == "sqlite":
        return sqlite3.connect(db_path_or_url)
    elif db_type == "postgresql":
        try:
            import psycopg2
            from urllib.parse import urlparse
            
            result = urlparse(db_path_or_url)
            conn = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port,
            )
            return conn
        except ImportError:
            print("Error: psycopg2 not installed. Run: pip install psycopg2-binary")
            sys.exit(1)
    return None


def check_admin_users(conn, db_type):
    """Check for admin users in the system"""
    print("\n" + "=" * 80)
    print("2. ADMIN USERS CHECK")
    print("=" * 80)
    
    cursor = conn.cursor()
    
    try:
        # Get all admin users
        cursor.execute("""
            SELECT id, email, first_name, last_name, is_admin, is_active, 
                   created_at, role
            FROM users 
            WHERE is_admin = TRUE OR role = 'admin'
        """)
        admin_users = cursor.fetchall()
        
        if not admin_users:
            print("⚠️  No admin users found in the database")
            return []
        
        print(f"✓ Found {len(admin_users)} admin user(s):\n")
        
        admin_ids = []
        for user in admin_users:
            user_id, email, first_name, last_name, is_admin, is_active, created_at, role = user
            admin_ids.append(user_id)
            
            print(f"  User ID: {user_id}")
            print(f"  Email: {email}")
            print(f"  Name: {first_name} {last_name}")
            print(f"  Is Admin: {is_admin}")
            print(f"  Is Active: {is_active}")
            print(f"  Role: {role}")
            print(f"  Created: {created_at}")
            print()
        
        return admin_ids
        
    except Exception as e:
        print(f"❌ Error checking admin users: {e}")
        return []


def check_admin_posts(conn, admin_ids):
    """Check posts from admin accounts"""
    print("\n" + "=" * 80)
    print("3. ADMIN POSTS CHECK")
    print("=" * 80)
    
    if not admin_ids:
        print("⚠️  No admin users to check posts for")
        return
    
    cursor = conn.cursor()
    
    try:
        # Get posts from admin users
        placeholders = ','.join(['?' if 'sqlite' in str(type(conn)) else '%s'] * len(admin_ids))
        query = f"""
            SELECT p.id, p.user_id, p.content, p.created_at, p.updated_at,
                   u.email, u.first_name, u.last_name
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.user_id IN ({placeholders})
            ORDER BY p.created_at DESC
        """
        cursor.execute(query, admin_ids)
        admin_posts = cursor.fetchall()
        
        if not admin_posts:
            print("⚠️  No posts found from admin accounts")
            print("   This could mean:")
            print("   - Admin users have not created any posts")
            print("   - Posts have been deleted (investigating why...)")
        else:
            print(f"✓ Found {len(admin_posts)} post(s) from admin accounts:\n")
            
            for post in admin_posts[:10]:  # Show first 10
                post_id, user_id, content, created_at, updated_at, email, first_name, last_name = post
                preview = content[:50] + "..." if len(content) > 50 else content
                
                print(f"  Post ID: {post_id}")
                print(f"  Author: {first_name} {last_name} ({email})")
                print(f"  Content: {preview}")
                print(f"  Created: {created_at}")
                print(f"  Updated: {updated_at}")
                print()
        
        # Count total posts by admin vs non-admin
        cursor.execute(f"""
            SELECT 
                COUNT(CASE WHEN p.user_id IN ({placeholders}) THEN 1 END) as admin_posts,
                COUNT(CASE WHEN p.user_id NOT IN ({placeholders}) THEN 1 END) as non_admin_posts
            FROM posts p
        """, admin_ids + admin_ids)
        admin_count, non_admin_count = cursor.fetchone()
        
        print(f"📊 Post Statistics:")
        print(f"   Admin posts: {admin_count}")
        print(f"   Non-admin posts: {non_admin_count}")
        print(f"   Total posts: {admin_count + non_admin_count}")
        
    except Exception as e:
        print(f"❌ Error checking admin posts: {e}")


def check_foreign_key_constraints(conn):
    """Check for foreign key constraints that might cause cascading deletes"""
    print("\n" + "=" * 80)
    print("4. FOREIGN KEY CONSTRAINTS CHECK")
    print("=" * 80)
    
    cursor = conn.cursor()
    
    try:
        # For SQLite
        if 'sqlite' in str(type(conn)).lower():
            cursor.execute("PRAGMA foreign_key_list('posts')")
            constraints = cursor.fetchall()
            
            if constraints:
                print("✓ Foreign key constraints on 'posts' table:\n")
                for constraint in constraints:
                    print(f"  Column: {constraint[3]}")
                    print(f"  References: {constraint[2]}.{constraint[4]}")
                    print(f"  On Delete: {constraint[5] if len(constraint) > 5 else 'NO ACTION'}")
                    print(f"  On Update: {constraint[6] if len(constraint) > 6 else 'NO ACTION'}")
                    print()
            else:
                print("⚠️  No foreign key constraints found on 'posts' table")
        
        # Check if there are any CASCADE rules that might delete posts
        print("\n🔍 Potential cascading delete scenarios:")
        print("   - If user is deleted, posts might cascade delete (check models.py)")
        print("   - If user.is_active is set to False, posts should remain")
        print("   - Check backend/app/models.py for cascade rules")
        
    except Exception as e:
        print(f"❌ Error checking foreign key constraints: {e}")


def check_post_query_filters():
    """Check if posts API applies filters that might exclude admin posts"""
    print("\n" + "=" * 80)
    print("5. POST QUERY FILTERS CHECK")
    print("=" * 80)
    
    posts_api_path = "backend/app/api/posts.py"
    
    if not os.path.exists(posts_api_path):
        print(f"⚠️  Posts API file not found: {posts_api_path}")
        return
    
    print(f"✓ Checking {posts_api_path} for filters...\n")
    
    with open(posts_api_path, 'r') as f:
        content = f.read()
    
    # Check for common filter patterns
    filters_found = []
    
    if "is_active" in content and "User.is_active" in content:
        filters_found.append("User.is_active filter detected")
    
    if "is_admin" in content:
        filters_found.append("is_admin filter detected")
    
    if ".where(" in content:
        # Count where clauses
        where_count = content.count(".where(")
        filters_found.append(f"Found {where_count} WHERE clause(s) in post queries")
    
    if filters_found:
        print("🔍 Filters detected in posts API:")
        for filter_msg in filters_found:
            print(f"   - {filter_msg}")
    else:
        print("✓ No suspicious filters detected in posts API")
    
    # Check if posts query joins users and filters by is_active
    if "User.is_active" in content and "select(Post)" in content:
        print("\n⚠️  POTENTIAL ISSUE FOUND:")
        print("   The posts query might be filtering by User.is_active")
        print("   If admin accounts become inactive, their posts might not appear")


def check_inactivity_handling():
    """Check for session expiration or inactivity handling"""
    print("\n" + "=" * 80)
    print("6. INACTIVITY & SESSION HANDLING CHECK")
    print("=" * 80)
    
    # Check environment variables
    token_exp = os.getenv("TOKEN_EXPIRATION_DAYS", "7")
    print(f"Token expiration: {token_exp} days")
    
    # Check for cleanup scripts
    cleanup_files = [
        "remove_fake_posts.py",
        "clean_backend.py",
        "automated_posts_fix.py"
    ]
    
    found_scripts = []
    for script in cleanup_files:
        if os.path.exists(script):
            found_scripts.append(script)
    
    if found_scripts:
        print(f"\n⚠️  Found cleanup scripts:")
        for script in found_scripts:
            print(f"   - {script}")
            # Check if they're scheduled
            print(f"     (Check if this runs automatically)")
    
    # Check models for any automatic deletion logic
    models_path = "backend/app/models.py"
    if os.path.exists(models_path):
        with open(models_path, 'r') as f:
            models_content = f.read()
        
        if "cascade" in models_content.lower():
            print("\n🔍 Cascade rules found in models.py")
            print("   Posts table might have cascade delete rules")


def check_recent_deletions(conn, admin_ids):
    """Check for signs of recent post deletions"""
    print("\n" + "=" * 80)
    print("7. RECENT DELETION ANALYSIS")
    print("=" * 80)
    
    cursor = conn.cursor()
    
    try:
        # Check if there are any posts at all
        cursor.execute("SELECT COUNT(*) FROM posts")
        total_posts = cursor.fetchone()[0]
        
        # Check post creation dates
        cursor.execute("""
            SELECT MIN(created_at), MAX(created_at), COUNT(*)
            FROM posts
        """)
        min_date, max_date, count = cursor.fetchone()
        
        print(f"📊 Post Timeline:")
        print(f"   Total posts: {total_posts}")
        if min_date and max_date:
            print(f"   Oldest post: {min_date}")
            print(f"   Newest post: {max_date}")
        
        # Check if there are gaps in post IDs (indication of deletions)
        cursor.execute("SELECT id FROM posts ORDER BY id")
        post_ids = [row[0] for row in cursor.fetchall()]
        
        if post_ids:
            missing_ids = []
            for i in range(min(post_ids), max(post_ids)):
                if i not in post_ids:
                    missing_ids.append(i)
            
            if missing_ids:
                print(f"\n⚠️  Found {len(missing_ids)} missing post ID(s) between {min(post_ids)} and {max(post_ids)}")
                print(f"   This suggests posts have been deleted")
                print(f"   Missing IDs (first 10): {missing_ids[:10]}")
        
    except Exception as e:
        print(f"❌ Error analyzing deletions: {e}")


def provide_recommendations():
    """Provide recommendations based on findings"""
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    print("\nTo investigate why posts from admin accounts might be disappearing:\n")
    
    print("1. CHECK USER INACTIVITY HANDLING:")
    print("   - Review if admin accounts are being set to is_active=False")
    print("   - Check if posts query filters by User.is_active")
    print("   - Modify query to include posts from inactive users if needed")
    
    print("\n2. REVIEW CASCADE DELETE RULES:")
    print("   - Check backend/app/models.py for cascade='all, delete-orphan'")
    print("   - Ensure posts don't cascade delete when users are deactivated")
    print("   - Posts should only delete if explicitly requested")
    
    print("\n3. CHECK AUTOMATED CLEANUP SCRIPTS:")
    print("   - Review remove_fake_posts.py")
    print("   - Check if any cron jobs or scheduled tasks delete posts")
    print("   - Verify admin posts are not being targeted by cleanup")
    
    print("\n4. VERIFY FRONTEND POST FILTERING:")
    print("   - Check frontend/src/components/PostFeed.tsx")
    print("   - Ensure no client-side filtering of admin posts")
    print("   - Verify posts from all users are displayed")
    
    print("\n5. SOLUTION: Modify posts query to NOT filter by user activity:")
    print("   - In backend/app/api/posts.py, remove User.is_active filter")
    print("   - Posts should be visible regardless of user account status")
    print("   - Only hide posts if explicitly deleted")
    
    print()


def main():
    """Main diagnostic function"""
    print("\n" + "=" * 80)
    print("ADMIN POST DELETION DIAGNOSTIC TOOL")
    print("=" * 80)
    print()
    
    # Check database connection
    db_type, db_path_or_url = check_database_connection()
    
    if not db_type:
        print("\n❌ Cannot proceed without database connection")
        sys.exit(1)
    
    # Connect to database
    conn = connect_db(db_type, db_path_or_url)
    
    if not conn:
        print("\n❌ Failed to connect to database")
        sys.exit(1)
    
    try:
        # Run diagnostic checks
        admin_ids = check_admin_users(conn, db_type)
        check_admin_posts(conn, admin_ids)
        check_foreign_key_constraints(conn)
        check_post_query_filters()
        check_inactivity_handling()
        check_recent_deletions(conn, admin_ids)
        
        # Provide recommendations
        provide_recommendations()
        
    finally:
        conn.close()
    
    print("=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()

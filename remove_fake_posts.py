#!/usr/bin/env python3
"""
Remove fake/sample/test posts from the HireMeBahamas database.

This script removes:
1. Posts from test users (IDs 1-5)
2. Posts containing test/sample keywords
3. Posts from fake email addresses (john@, sarah@, mike@, lisa@hirebahamas.com)

Usage:
    python remove_fake_posts.py [--dry-run]

Options:
    --dry-run    Show what would be deleted without actually deleting
"""

import argparse
import os
import sqlite3
import sys


def is_sqlite_db():
    """Check if using SQLite database"""
    db_url = os.environ.get("DATABASE_URL", "sqlite:///./hiremebahamas.db")
    return db_url.startswith("sqlite") or not db_url.startswith("postgresql")


def connect_db():
    """Connect to the database"""
    if is_sqlite_db():
        # SQLite database
        return sqlite3.connect("hiremebahamas.db")
    else:
        # PostgreSQL database
        try:
            import psycopg2
            from urllib.parse import urlparse

            db_url = os.environ.get("DATABASE_URL")
            result = urlparse(db_url)
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


def remove_fake_posts(dry_run=False):
    """Remove all fake/sample/test posts from the database"""
    conn = connect_db()
    cursor = conn.cursor()

    print("=" * 60)
    print("REMOVING FAKE/SAMPLE/TEST POSTS FROM HIREBAHAMAS DATABASE")
    print("=" * 60)
    print()

    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()

    # Count total posts before cleanup
    cursor.execute("SELECT COUNT(*) FROM posts")
    total_before = cursor.fetchone()[0]
    print(f"📊 Total posts before cleanup: {total_before}")
    print()

    deleted_count = 0

    # 1. Delete posts from test users (IDs 1-5)
    print("🗑️  Step 1: Removing posts from test users (IDs 1-5)...")
    cursor.execute("SELECT COUNT(*) FROM posts WHERE user_id BETWEEN 1 AND 5")
    count = cursor.fetchone()[0]
    print(f"   Found {count} posts from test users")

    if not dry_run and count > 0:
        cursor.execute("DELETE FROM posts WHERE user_id BETWEEN 1 AND 5")
        deleted_count += count
        print(f"   ✅ Deleted {count} posts")
    print()

    # 2. Delete posts from fake email addresses
    print("🗑️  Step 2: Removing posts from fake email addresses...")
    fake_emails = [
        "john@hirebahamas.com",
        "sarah@hirebahamas.com",
        "mike@hirebahamas.com",
        "lisa@hirebahamas.com",
    ]

    for email in fake_emails:
        cursor.execute(
            """
            SELECT COUNT(*) FROM posts 
            WHERE user_id IN (SELECT id FROM users WHERE email = ?)
        """,
            (email,),
        )
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"   Found {count} posts from {email}")
            if not dry_run:
                cursor.execute(
                    """
                    DELETE FROM posts 
                    WHERE user_id IN (SELECT id FROM users WHERE email = ?)
                """,
                    (email,),
                )
                deleted_count += count
                print(f"   ✅ Deleted {count} posts")

    print()

    # 3. Delete posts containing test/sample keywords
    print("🗑️  Step 3: Removing posts with test/sample keywords...")
    keywords = [
        "%test%",
        "%sample%",
        "%demo%",
        "%fake%",
        "%Welcome to HireBahamas%",
        "%Just launched our new job board%",
    ]

    for keyword in keywords:
        cursor.execute(
            "SELECT COUNT(*) FROM posts WHERE content LIKE ?", (keyword,)
        )
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"   Found {count} posts matching '{keyword}'")
            if not dry_run:
                cursor.execute("DELETE FROM posts WHERE content LIKE ?", (keyword,))
                deleted_count += count
                print(f"   ✅ Deleted {count} posts")

    print()

    # Commit changes if not dry run
    if not dry_run:
        conn.commit()

    # Count total posts after cleanup
    cursor.execute("SELECT COUNT(*) FROM posts")
    total_after = cursor.fetchone()[0]

    print("=" * 60)
    print("CLEANUP SUMMARY")
    print("=" * 60)
    print(f"Posts before cleanup:  {total_before}")
    print(f"Posts after cleanup:   {total_after}")
    print(f"Total posts deleted:   {deleted_count}")
    print()

    if dry_run:
        print("⚠️  This was a dry run - no changes were made")
    else:
        print("✅ Cleanup completed successfully!")

    print()

    # Verify deletion - show remaining posts
    print("📋 Remaining posts:")
    cursor.execute(
        """
        SELECT p.id, u.email, u.first_name, u.last_name, 
               SUBSTR(p.content, 1, 50) as preview
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
        LIMIT 10
    """
    )
    rows = cursor.fetchall()

    if rows:
        for row in rows:
            post_id, email, first_name, last_name, preview = row
            print(f"   Post #{post_id} by {first_name} {last_name} ({email})")
            print(f"   Preview: {preview}...")
            print()
    else:
        print("   No posts remaining in database")

    conn.close()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Remove fake/sample/test posts from HireMeBahamas database"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    args = parser.parse_args()

    try:
        remove_fake_posts(dry_run=args.dry_run)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

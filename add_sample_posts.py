#!/usr/bin/env python3
"""
Add sample posts to the database.

⚠️  WARNING: This script is for DEVELOPMENT ONLY!
This script creates fake/sample data for testing purposes.

Usage:
    python add_sample_posts.py --dev    # Explicitly run in development mode

To prevent accidental use in production, this script requires the --dev flag.
"""

import sqlite3
import sys

import bcrypt

from production_utils import check_dev_flag, is_production, print_environment_info


def add_sample_data():
    """Add sample users and posts to the database (DEVELOPMENT ONLY)"""
    print("=" * 60)
    print("ADD SAMPLE POSTS TO DATABASE")
    print("=" * 60)
    print()
    print("⚠️  This script creates FAKE/SAMPLE data for development only!")
    print()

    # Check if running in production
    if is_production():
        print("❌ ERROR: Cannot run in PRODUCTION mode!")
        print("   This script creates fake/sample data and should only be used in development.")
        print()
        print("   If you really need to run this (NOT recommended):")
        print("   1. Set PRODUCTION=false in your environment")
        print("   2. Use the --dev flag: python add_sample_posts.py --dev")
        print()
        return False

    # Connect to database
    conn = sqlite3.connect("hirebahamas.db")
    cursor = conn.cursor()
    
    print("ℹ️  Running in DEVELOPMENT mode - creating sample data...")
    print()

    # Create sample users if they don't exist
    sample_users = [
        ("john@hirebahamas.com", "John", "Doe", "freelancer"),
        ("sarah@hirebahamas.com", "Sarah", "Smith", "employer"),
        ("mike@hirebahamas.com", "Mike", "Johnson", "freelancer"),
        ("lisa@hirebahamas.com", "Lisa", "Brown", "recruiter"),
    ]

    for email, first_name, last_name, user_type in sample_users:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if not cursor.fetchone():
            password_hash = bcrypt.hashpw(
                "password123".encode("utf-8"), bcrypt.gensalt()
            )
            cursor.execute(
                """
                INSERT INTO users (email, password_hash, first_name, last_name, user_type)
                VALUES (?, ?, ?, ?, ?)
            """,
                (email, password_hash, first_name, last_name, user_type),
            )
            print(f"Created user: {first_name} {last_name}")

    # Create sample posts
    sample_posts = [
        (
            1,
            "Just finished an amazing web development project in Nassau! The Bahamas tech scene is growing fast. Looking for more opportunities! #BahamasTech #WebDev",
        ),
        (
            2,
            "Hiring React developers for our new e-commerce platform. Remote work available. DM for details! #HireBahamas #ReactJS",
        ),
        (
            3,
            "Completed my first freelance gig through HireBahamas. Such a great platform for connecting talent with opportunities in paradise! 🌴",
        ),
        (
            4,
            "Looking for talented graphic designers for branding projects. Nassau-based preferred but open to remote. #GraphicDesign #Bahamas",
        ),
        (
            1,
            "Beautiful day in Freeport! Working on some exciting mobile app projects. The Caribbean lifestyle really inspires creativity. ☀️",
        ),
        (
            3,
            "Just landed a new contract for mobile app development. Thanks to the HireBahamas community for the support! #MobileDev #Success",
        ),
        (
            2,
            "Our company is expanding and we need more talented developers. Join our team in Grand Bahama! Great benefits and work-life balance.",
        ),
        (
            4,
            "Excited to announce new job openings for marketing specialists. Perfect for those who love the island lifestyle! #Marketing #BahamasJobs",
        ),
    ]

    for user_id, content in sample_posts:
        cursor.execute(
            "INSERT INTO posts (user_id, content) VALUES (?, ?)", (user_id, content)
        )
        print(f"Created post by user {user_id}")

    conn.commit()
    conn.close()
    print("✅ Sample data created successfully!")
    print()
    return True


if __name__ == "__main__":
    print_environment_info()

    # Check for --dev flag
    if not check_dev_flag():
        print("❌ ERROR: --dev flag required!")
        print()
        print("This script creates fake/sample data for DEVELOPMENT only.")
        print("To run this script, use:")
        print("   python add_sample_posts.py --dev")
        print()
        sys.exit(1)

    success = add_sample_data()
    sys.exit(0 if success else 1)

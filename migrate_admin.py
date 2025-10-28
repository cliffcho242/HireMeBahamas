#!/usr/bin/env python3
"""
Migration script to add admin fields to existing users table
"""

import os
import sqlite3
from pathlib import Path


def migrate_database():
    """Add admin fields to the users table"""

    # Database path
    db_path = Path(__file__).parent / "backend" / "hirebahamas.db"

    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        return False

    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        print("🔧 Migrating database to add admin fields...")

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        # Add is_admin column if it doesn't exist
        if "is_admin" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            print("✅ Added is_admin column")
        else:
            print("ℹ️  is_admin column already exists")

        # Add role column if it doesn't exist
        if "role" not in columns:
            cursor.execute(
                "ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user'"
            )
            print("✅ Added role column")
        else:
            print("ℹ️  role column already exists")

        # Commit changes
        conn.commit()
        conn.close()

        print("✅ Database migration completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    print("🎯 HireBahamas Database Migration")
    print("=" * 40)

    success = migrate_database()
    if success:
        print("\n🎉 Ready to create admin user!")
    else:
        print("\n❌ Migration failed")

#!/usr/bin/env python3
"""
Database Initialization Script for HireMeBahamas
This script ensures the database is properly initialized before the app starts.
It should be run during deployment to prevent data loss and user deletion issues.
"""

import os
import sys
from pathlib import Path


def ensure_database_initialized():
    """
    Ensure database is initialized before starting the application.
    This prevents users from being deleted due to missing database.
    """
    print("=" * 60)
    print("HireMeBahamas Database Initialization")
    print("=" * 60)
    print()
    
    # Check if DATABASE_URL is set (indicates PostgreSQL for production)
    database_url = os.getenv("DATABASE_URL")
    environment = os.getenv("ENVIRONMENT", "development").lower()
    is_production = environment in ["production", "prod"]
    
    print(f"Environment: {environment}")
    print(f"Database URL set: {'Yes' if database_url else 'No (using SQLite)'}")
    print()
    
    # For production, PostgreSQL is REQUIRED
    if is_production and not database_url:
        print("❌" * 30)
        print("❌  CRITICAL ERROR: Production requires PostgreSQL!")
        print("❌")
        print("❌  DATABASE_URL environment variable is NOT set.")
        print("❌")
        print("❌  Why this matters:")
        print("❌  - SQLite files are ephemeral in containers (Railway, Docker)")
        print("❌  - Users and posts will be DELETED on every restart/deploy")
        print("❌  - Data persistence requires PostgreSQL")
        print("❌")
        print("❌  ACTION REQUIRED:")
        print("❌  1. Create a PostgreSQL database (Railway has this built-in)")
        print("❌  2. Set DATABASE_URL environment variable:")
        print("❌     DATABASE_URL=postgresql://user:pass@host:5432/database")
        print("❌  3. Redeploy the application")
        print("❌" * 30)
        sys.exit(1)
    
    # Check if database file exists (for SQLite)
    if not database_url:
        db_path = Path(__file__).parent / "hiremebahamas.db"
        if db_path.exists():
            print(f"✅ SQLite database found: {db_path}")
            print("⚠️  WARNING: SQLite is for development only!")
            print("⚠️  Data will be lost on production deployments.")
        else:
            print(f"📦 SQLite database will be created: {db_path}")
            print("⚠️  WARNING: SQLite is for development only!")
    else:
        print("✅ PostgreSQL configured for production")
        print("✅ Data will persist across deployments")
    
    print()
    print("Database initialization check complete.")
    print("=" * 60)
    print()
    
    return True


if __name__ == "__main__":
    try:
        ensure_database_initialized()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error during database initialization check: {e}")
        sys.exit(1)

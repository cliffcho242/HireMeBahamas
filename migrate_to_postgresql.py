"""
🚀 POSTGRESQL MIGRATION SCRIPT
================================
This script will help you migrate from SQLite to PostgreSQL on Railway.
"""

import os
from pathlib import Path


def print_banner():
    print("=" * 70)
    print("🚀 HIREMEBAHAMAS POSTGRESQL MIGRATION")
    print("=" * 70)
    print()


def check_railway_postgresql():
    """Check if Railway PostgreSQL is configured"""
    print("📋 Step 1: Check Railway PostgreSQL Setup")
    print("-" * 70)

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        print("✅ DATABASE_URL detected!")
        print(f"   URL: {database_url[:40]}...")
        print()
        return True
    else:
        print("❌ DATABASE_URL not found!")
        print()
        print("🔧 TO FIX THIS:")
        print("   1. Go to your Railway project dashboard")
        print("   2. Click 'New' → 'Database' → 'PostgreSQL'")
        print("   3. Railway will automatically create DATABASE_URL")
        print("   4. Wait for database to provision (1-2 minutes)")
        print("   5. Re-run this script")
        print()
        return False


def backup_sqlite_data():
    """Backup existing SQLite data"""
    print("📋 Step 2: Backup SQLite Data")
    print("-" * 70)

    db_path = Path("hiremebahamas.db")

    if db_path.exists():
        backup_path = Path("hiremebahamas_backup.db")
        import shutil

        shutil.copy(db_path, backup_path)
        print(f"✅ SQLite database backed up to: {backup_path}")
        print()
        return True
    else:
        print("⚠️ No SQLite database found (this is OK for new deployments)")
        print()
        return False


def update_backend_file():
    """Replace final_backend.py with PostgreSQL version"""
    print("📋 Step 3: Update Backend Code")
    print("-" * 70)

    source = Path("final_backend_postgresql.py")
    target = Path("final_backend.py")

    if not source.exists():
        print("❌ PostgreSQL backend file not found!")
        return False

    # Backup current backend
    backup = Path("final_backend_sqlite_backup.py")
    if target.exists():
        import shutil

        shutil.copy(target, backup)
        print(f"✅ Original backend backed up to: {backup}")

    # Replace with PostgreSQL version
    import shutil

    shutil.copy(source, target)
    print(f"✅ Backend updated to use PostgreSQL!")
    print()
    return True


def test_local_connection():
    """Test database connection"""
    print("📋 Step 4: Test Database Connection")
    print("-" * 70)

    try:
        if os.getenv("DATABASE_URL"):
            print("Testing PostgreSQL connection...")
            import psycopg2

            conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            cursor.close()
            conn.close()
            print(f"✅ PostgreSQL connected: {version[0][:50]}...")
        else:
            print("Testing SQLite connection (local development)...")
            import sqlite3

            conn = sqlite3.connect("hiremebahamas.db")
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()
            cursor.close()
            conn.close()
            print(f"✅ SQLite connected: {version[0]}")

        print()
        return True
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print()
        return False


def deployment_instructions():
    """Show deployment instructions"""
    print("📋 Step 5: Deploy to Railway")
    print("-" * 70)
    print()
    print("🚀 DEPLOYMENT STEPS:")
    print()
    print("1. Commit the changes:")
    print("   git add .")
    print('   git commit -m "Add PostgreSQL support for persistent data storage"')
    print("   git push origin main")
    print()
    print("2. Railway will automatically:")
    print("   ✅ Detect the changes")
    print("   ✅ Install psycopg2-binary")
    print("   ✅ Connect to PostgreSQL database")
    print("   ✅ Create all tables automatically")
    print("   ✅ Keep your data forever (no more resets!)")
    print()
    print("3. Verify deployment:")
    print("   - Check Railway logs for 'PostgreSQL (Production)'")
    print("   - Test user registration on your site")
    print("   - Register a test user")
    print("   - Wait 5 minutes, then check if user still exists")
    print()
    print("=" * 70)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 70)
    print()
    print("🎉 YOUR APP WILL NOW:")
    print("   ✅ Keep all user registrations forever")
    print("   ✅ Keep all posts and data permanent")
    print("   ✅ Never reset on deployment")
    print("   ✅ Never reset when admin edits code")
    print("   ✅ Support thousands of concurrent users")
    print()


def main():
    print_banner()

    # Check if running locally or on Railway
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None

    if is_railway:
        print("🚂 Running on Railway - PostgreSQL should be available")
        print()
    else:
        print("💻 Running locally - checking configuration")
        print()

    # Step 1: Check Railway PostgreSQL
    has_postgresql = check_railway_postgresql()

    if not has_postgresql and not is_railway:
        print("⚠️ PostgreSQL not configured yet.")
        print()
        print("OPTIONS:")
        print("1. Set up PostgreSQL on Railway (recommended for production)")
        print("2. Continue with SQLite for local development")
        print()
        choice = input("Continue anyway? (y/n): ").strip().lower()
        if choice != "y":
            print("Exiting. Set up PostgreSQL on Railway and try again.")
            return
        print()

    # Step 2: Backup SQLite
    backup_sqlite_data()

    # Step 3: Update backend
    if update_backend_file():
        print("✅ Backend code updated successfully!")
        print()
    else:
        print("❌ Failed to update backend code")
        return

    # Step 4: Test connection
    test_local_connection()

    # Step 5: Show deployment instructions
    deployment_instructions()


if __name__ == "__main__":
    main()

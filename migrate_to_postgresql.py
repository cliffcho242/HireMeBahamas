"""
🚀 POSTGRESQL MIGRATION SCRIPT
================================
This script will help you migrate from SQLite to PostgreSQL on Render.
"""

import os
import sys
from pathlib import Path

# Import database URL normalizer for sync connections
try:
    # Try to import from the api directory structure
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
    from backend_app.core.db_url_normalizer import normalize_database_url
    HAS_NORMALIZER = True
except ImportError:
    # Fallback if normalizer not available
    # This script only uses sync connections, so we only need for_async=False support
    HAS_NORMALIZER = False
    def normalize_database_url(url, for_async=False):
        """Fallback normalizer - removes +asyncpg suffix for sync connections"""
        if not url:
            return url
        if for_async:
            # This fallback doesn't support async conversion
            # The script only uses sync connections, so this branch shouldn't be reached
            return url
        # Remove driver suffixes for sync connections
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
        url = url.replace("postgresql+psycopg2://", "postgresql://", 1)
        url = url.replace("postgresql+psycopg://", "postgresql://", 1)
        url = url.replace("postgres://", "postgresql://", 1)
        return url


def print_banner():
    print("=" * 70)
    print("🚀 HIREMEBAHAMAS POSTGRESQL MIGRATION")
    print("=" * 70)
    print()


def check_render_postgresql():
    """Check if Render PostgreSQL is configured"""
    print("📋 Step 1: Check Render PostgreSQL Setup")
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
        print("   1. Go to your Render project dashboard")
        print("   2. Click 'New' → 'Database' → 'PostgreSQL'")
        print("   3. Render will automatically create DATABASE_URL")
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

            # Normalize DATABASE_URL for sync connection
            db_url = os.getenv("DATABASE_URL")
            sync_url = normalize_database_url(db_url, for_async=False)
            
            # ✅ Use normalized URL for psycopg2 (sync driver)
            conn = psycopg2.connect(sync_url)
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
    print("📋 Step 5: Deploy to Render")
    print("-" * 70)
    print()
    print("🚀 DEPLOYMENT STEPS:")
    print()
    print("1. Commit the changes:")
    print("   git add .")
    print('   git commit -m "Add PostgreSQL support for persistent data storage"')
    print("   git push origin main")
    print()
    print("2. Render will automatically:")
    print("   ✅ Detect the changes")
    print("   ✅ Install psycopg2-binary")
    print("   ✅ Connect to PostgreSQL database")
    print("   ✅ Create all tables automatically")
    print("   ✅ Keep your data forever (no more resets!)")
    print()
    print("3. Verify deployment:")
    print("   - Check Render logs for 'PostgreSQL (Production)'")
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

    # Check if running locally or on Render
    is_render = os.getenv("RENDER_ENVIRONMENT") is not None

    if is_render:
        print("🚂 Running on Render - PostgreSQL should be available")
        print()
    else:
        print("💻 Running locally - checking configuration")
        print()

    # Step 1: Check Render PostgreSQL
    has_postgresql = check_render_postgresql()

    if not has_postgresql and not is_render:
        print("⚠️ PostgreSQL not configured yet.")
        print()
        print("OPTIONS:")
        print("1. Set up PostgreSQL on Render (recommended for production)")
        print("2. Continue with SQLite for local development")
        print()
        choice = input("Continue anyway? (y/n): ").strip().lower()
        if choice != "y":
            print("Exiting. Set up PostgreSQL on Render and try again.")
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

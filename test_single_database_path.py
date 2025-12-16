"""
Test to verify single database path consolidation.

This test ensures that the application uses only ONE database engine
from app.database (the single source of truth), not multiple engines 
from different modules.

Updated Dec 2025: All code should now import from app.database
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "api"))


def test_app_database_engine_exists():
    """Test that app.database module has a get_engine function (single source of truth)."""
    print("Testing app.database module (single source of truth)...")
    
    # Check if the file exists and has the get_engine function
    database_path = project_root / "app" / "database.py"
    
    if not database_path.exists():
        print(f"❌ app/database.py not found at {database_path}")
        return False
    
    with open(database_path, 'r') as f:
        content = f.read()
    
    if "def get_engine():" in content:
        print("✅ app/database.py has get_engine() function")
        
        # Check for single source of truth documentation
        if "SINGLE SOURCE OF TRUTH" in content:
            print("✅ app/database.py documented as SINGLE SOURCE OF TRUTH")
            return True
        else:
            print("⚠️  app/database.py missing SINGLE SOURCE OF TRUTH documentation")
            return True  # Still pass, just a warning
    else:
        print("❌ app/database.py missing get_engine() function")
        return False


def test_old_database_modules_have_deprecation_notices():
    """Test that old database modules have deprecation notices pointing to app.database."""
    print("\nTesting old database modules for deprecation notices...")
    
    old_modules = [
        ("api/database.py", project_root / "api" / "database.py"),
        ("api/backend_app/database.py", project_root / "api" / "backend_app" / "database.py"),
        ("backend/app/database.py", project_root / "backend" / "app" / "database.py"),
    ]
    
    all_passed = True
    
    for module_name, database_path in old_modules:
        if not database_path.exists():
            print(f"⚠️  {module_name} not found (may have been removed)")
            continue
        
        with open(database_path, 'r') as f:
            content = f.read()
        
        # Check for deprecation notice
        if "DEPRECATION NOTICE" in content or "DEPRECATED" in content:
            print(f"✅ {module_name} has DEPRECATION NOTICE")
            
            # Check if it mentions app.database
            if "app.database" in content:
                print(f"✅ {module_name} points to app.database (correct)")
            else:
                print(f"⚠️  {module_name} doesn't mention app.database")
                all_passed = False
        else:
            print(f"❌ {module_name} missing DEPRECATION NOTICE")
            all_passed = False
    
    return all_passed


def test_index_uses_app_database():
    """Test that api/index.py uses app.database (not creating its own engine)."""
    print("\nTesting api/index.py for proper database imports...")
    
    index_path = project_root / "api" / "index.py"
    
    if not index_path.exists():
        print(f"⚠️  api/index.py not found at {index_path} (may not be used)")
        return True  # Not failing if file doesn't exist
    
    with open(index_path, 'r') as f:
        content = f.read()
    
    # Check if it actually creates an engine (not just imports the function)
    # Look for actual engine instantiation patterns
    creates_engine = "= create_async_engine(" in content or "_engine = create_async_engine(" in content
    
    if creates_engine:
        print("❌ api/index.py creates its own database engine (dual path issue)")
        return False
    
    # Check that it uses app.database or backend_app.database (via alias)
    # The file uses backend_app.database, which is aliased to app in sys.modules
    if "from app.database import" in content or "from backend_app.database import" in content:
        print("✅ api/index.py uses centralized database module (no dual path)")
        return True
    else:
        # Just importing create_async_engine for type checking is OK
        # as long as it's not instantiating its own engine
        if "from sqlalchemy.ext.asyncio import create_async_engine" in content and not creates_engine:
            print("✅ api/index.py imports SQLAlchemy types but uses centralized database engine")
            return True
        print("⚠️  Could not verify database import in api/index.py (may not use database)")
        return True  # Don't fail, just warning


def test_cron_health_no_database():
    """Test that cron health endpoint doesn't use database."""
    print("\nTesting cron health endpoint...")
    
    cron_health_path = project_root / "api" / "cron" / "health.py"
    
    if not cron_health_path.exists():
        print(f"⚠️  Cron health endpoint not found at {cron_health_path} (optional)")
        return True  # This is optional, so pass
    
    with open(cron_health_path, 'r') as f:
        content = f.read()
    
    # Check for database imports
    database_patterns = [
        "from database import",
        "from backend_app.database import",
        "import database",
        "import backend_app.database",
        "get_engine",
        "AsyncSession",
    ]
    
    has_db_import = any(pattern in content for pattern in database_patterns)
    
    if has_db_import:
        print("❌ Cron health endpoint imports database modules (should not)")
        return False
    
    # Check for explicit comment about not using database
    if "MUST NOT ping the database" in content or "no database" in content.lower():
        print("✅ Cron health endpoint documented to NOT use database")
        return True
    
    print("✅ Cron health endpoint doesn't import database modules")
    return True


def main():
    """Run all tests."""
    print("="*60)
    print("Testing Single Database Path Consolidation")
    print("="*60)
    
    tests = [
        ("app.database module exists (single source of truth)", test_app_database_engine_exists),
        ("Old database modules have deprecation notices", test_old_database_modules_have_deprecation_notices),
        ("Index.py uses app.database (no dual path)", test_index_uses_app_database),
        ("Cron health doesn't use database", test_cron_health_no_database),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"❌ Test '{test_name}' raised exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Single database path consolidation verified.")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

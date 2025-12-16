"""
Test to verify single database path consolidation.

This test ensures that the application uses only ONE database engine
from backend_app.database, not multiple engines from different modules.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "api"))


def test_backend_database_engine_exists():
    """Test that backend_app.database module has a get_engine function."""
    print("Testing backend_app.database module...")
    
    # Check if the file exists and has the get_engine function
    database_path = project_root / "api" / "backend_app" / "database.py"
    
    if not database_path.exists():
        print(f"❌ backend_app/database.py not found at {database_path}")
        return False
    
    with open(database_path, 'r') as f:
        content = f.read()
    
    if "def get_engine():" in content:
        print("✅ backend_app/database.py has get_engine() function")
        return True
    else:
        print("❌ backend_app/database.py missing get_engine() function")
        return False


def test_api_database_has_deprecation_notice():
    """Test that api/database.py has deprecation notice."""
    print("\nTesting api/database.py deprecation notice...")
    
    database_path = project_root / "api" / "database.py"
    
    if not database_path.exists():
        print(f"❌ api/database.py not found at {database_path}")
        return False
    
    with open(database_path, 'r') as f:
        content = f.read()
    
    # Check for deprecation notice
    if "DEPRECATION NOTICE" in content:
        print("✅ api/database.py has DEPRECATION NOTICE")
        
        # Check if it mentions backend_app
        if "backend_app.database" in content:
            print("✅ Deprecation notice recommends backend_app.database")
            return True
        else:
            print("⚠️  Deprecation notice doesn't mention backend_app.database")
            return False
    else:
        print("❌ api/database.py missing DEPRECATION NOTICE")
        return False


def test_index_no_fallback_engine():
    """Test that api/index.py doesn't create a fallback database engine."""
    print("\nTesting api/index.py for fallback engine creation...")
    
    index_path = project_root / "api" / "index.py"
    
    if not index_path.exists():
        print(f"❌ api/index.py not found at {index_path}")
        return False
    
    with open(index_path, 'r') as f:
        content = f.read()
    
    # Check that there's no fallback engine creation
    problematic_patterns = [
        "create_async_engine",  # Should not create its own engine
        "Creating fallback database engine",  # Old message
    ]
    
    # Find the get_db_engine function
    if "def get_db_engine():" not in content:
        print("❌ get_db_engine() function not found in index.py")
        return False
    
    # Check the entire file for problematic patterns
    # We don't need to extract just the function - if create_async_engine
    # appears anywhere in get_db_engine's context, that's a problem
    func_content = content
    
    # Primary check: Look for engine creation in get_db_engine function context
    # Split into sections to check the relevant function
    func_sections = content.split('def get_db_engine():')
    
    if len(func_sections) < 2:
        print("❌ Could not find get_db_engine function")
        return False
    
    # Get the function body (everything after the function definition until the next function or end)
    func_body = func_sections[1].split('\ndef ')[0]  # Get until next function def
    
    # Check for problematic patterns in the function body
    has_create_engine = "create_async_engine" in func_body
    
    if has_create_engine:
        print("❌ api/index.py still creates its own database engine (dual path issue)")
        return False
    
    # Check that it uses backend_app.database
    if "from backend_app.database import" in func_body:
        print("✅ api/index.py uses backend_app.database (no dual path)")
        return True
    else:
        print("⚠️  Could not find backend_app.database import in get_db_engine")
        return False


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
        ("Backend database module exists", test_backend_database_engine_exists),
        ("API database has deprecation notice", test_api_database_has_deprecation_notice),
        ("Index.py has no fallback engine", test_index_no_fallback_engine),
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

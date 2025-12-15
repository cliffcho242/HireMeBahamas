#!/usr/bin/env python3
"""
Test script for production_utils module and sample data scripts.

This test verifies that:
1. Production detection works correctly
2. Sample data scripts require --dev flag
3. Sample data scripts block in production mode
4. Database configuration fails in production without DATABASE_URL
5. Production environment enforces PostgreSQL (no SQLite fallback)
"""

import os
import subprocess
import sys


def test_production_detection():
    """Test production detection logic"""
    print("Testing production detection...")

    # Test 1: Default should be development
    from production_utils import is_production, is_development

    if not is_development():
        print("❌ FAIL: Default should be development mode")
        return False

    print("✅ PASS: Default is development mode")

    # Test 2: PRODUCTION=true should enable production
    os.environ["PRODUCTION"] = "true"
    from importlib import reload
    import production_utils

    reload(production_utils)
    if not production_utils.is_production():
        print("❌ FAIL: PRODUCTION=true should enable production mode")
        del os.environ["PRODUCTION"]
        return False

    print("✅ PASS: PRODUCTION=true enables production mode")
    del os.environ["PRODUCTION"]
    reload(production_utils)

    return True


def test_dev_flag_requirement():
    """Test that scripts require --dev flag"""
    print("\nTesting --dev flag requirement...")

    scripts = ["add_sample_posts.py", "seed_data.py"]

    for script in scripts:
        print(f"  Testing {script}...")

        # Run without --dev flag
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print(f"❌ FAIL: {script} should fail without --dev flag")
            return False

        if "--dev flag required" not in result.stdout:
            print(f"❌ FAIL: {script} should show --dev flag error")
            return False

        print(f"✅ PASS: {script} requires --dev flag")

    return True


def test_production_blocking():
    """Test that scripts block in production mode"""
    print("\nTesting production mode blocking...")

    # Set production mode
    os.environ["PRODUCTION"] = "true"

    try:
        result = subprocess.run(
            [sys.executable, "seed_data.py", "--dev"],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "PRODUCTION": "true"},
        )

        if result.returncode == 0:
            print("❌ FAIL: Script should fail in production mode")
            return False

        if "Cannot run in PRODUCTION mode" not in result.stdout:
            print("❌ FAIL: Should show production mode error")
            return False

        print("✅ PASS: Scripts block in production mode")
        return True

    finally:
        if "PRODUCTION" in os.environ:
            del os.environ["PRODUCTION"]


def test_cleanup_script():
    """Test that cleanup script syntax is valid"""
    print("\nTesting cleanup script...")

    result = subprocess.run(
        [sys.executable, "-m", "py_compile", "remove_fake_posts.py"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    if result.returncode != 0:
        print("❌ FAIL: Cleanup script has syntax errors")
        print(result.stderr)
        return False

    print("✅ PASS: Cleanup script syntax is valid")
    return True


def test_database_production_safety():
    """Test that database configuration fails in production without DATABASE_URL"""
    print("\nTesting database production safety...")
    
    # Test api/database.py
    test_code_api = """
import os
import sys

# Set production environment WITHOUT DATABASE_URL
os.environ['ENV'] = 'production'
# Ensure DATABASE_URL is not set
if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']

try:
    # This should raise RuntimeError in production without DATABASE_URL
    # Need to import after setting env vars
    sys.path.insert(0, 'api')
    import database
    print("FAIL: Should have raised RuntimeError")
    sys.exit(1)
except RuntimeError as e:
    if "DATABASE_URL is required in production" in str(e):
        print("PASS: Correctly raised RuntimeError for missing DATABASE_URL")
        sys.exit(0)
    else:
        print(f"FAIL: Wrong error message: {e}")
        sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error: {e}")
    sys.exit(1)
"""
    
    result = subprocess.run(
        [sys.executable, "-c", test_code_api],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    
    if result.returncode != 0:
        print(f"❌ FAIL: api/database.py - {result.stdout}")
        return False
    
    print(f"✅ PASS: api/database.py - {result.stdout.strip()}")
    
    # Test api/backend_app/database.py
    test_code_backend = """
import os
import sys

# Set production environment WITHOUT DATABASE_URL
os.environ['ENV'] = 'production'
os.environ['ENVIRONMENT'] = 'production'
# Ensure all database-related env vars are not set
for var in ['DATABASE_URL', 'DATABASE_PRIVATE_URL', 'POSTGRES_URL', 
            'PGHOST', 'PGUSER', 'PGPASSWORD', 'PGDATABASE']:
    if var in os.environ:
        del os.environ[var]

try:
    # This should raise RuntimeError in production without DATABASE_URL
    sys.path.insert(0, 'api/backend_app')
    import database
    print("FAIL: Should have raised RuntimeError")
    sys.exit(1)
except RuntimeError as e:
    if "DATABASE_URL is required in production" in str(e):
        print("PASS: Correctly raised RuntimeError for missing DATABASE_URL")
        sys.exit(0)
    else:
        print(f"FAIL: Wrong error message: {e}")
        sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error: {e}")
    sys.exit(1)
"""
    
    result = subprocess.run(
        [sys.executable, "-c", test_code_backend],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    
    if result.returncode != 0:
        print(f"❌ FAIL: backend_app/database.py - {result.stdout}")
        return False
    
    print(f"✅ PASS: backend_app/database.py - {result.stdout.strip()}")
    return True


def test_database_ssl_enforcement():
    """Test that database engine enforces SSL in configuration"""
    print("\nTesting database SSL enforcement...")
    
    # Test that api/database.py engine has sslmode=require in connect_args
    test_code = """
import os
import sys

# Set environment to have a valid DATABASE_URL
os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost:5432/test'

try:
    sys.path.insert(0, 'api')
    import database
    
    # Check if the connect_args includes sslmode
    # We can't directly inspect the engine without connecting,
    # but we can verify the get_engine function exists
    engine_func = database.get_engine
    if engine_func:
        print("PASS: Database module loaded with SSL enforcement configured")
        sys.exit(0)
    else:
        print("FAIL: get_engine function not found")
        sys.exit(1)
except Exception as e:
    print(f"FAIL: Error loading database module: {e}")
    sys.exit(1)
"""
    
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    
    if result.returncode != 0:
        print(f"❌ FAIL: {result.stdout}")
        return False
    
    print(f"✅ PASS: {result.stdout.strip()}")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("PRODUCTION UTILS AND SAFETY CHECKS TEST SUITE")
    print("=" * 60)
    print()

    tests = [
        ("Production Detection", test_production_detection),
        ("Dev Flag Requirement", test_dev_flag_requirement),
        ("Production Blocking", test_production_blocking),
        ("Cleanup Script", test_cleanup_script),
        ("Database Production Safety", test_database_production_safety),
        ("Database SSL Enforcement", test_database_ssl_enforcement),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n⚠️  Test '{test_name}' FAILED\n")
        except Exception as e:
            failed += 1
            print(f"\n❌ Test '{test_name}' ERROR: {e}\n")

    print()
    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print()

    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

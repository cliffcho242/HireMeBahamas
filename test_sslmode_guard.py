#!/usr/bin/env python3
"""
Test script for sslmode guard in DATABASE_URL.

This test verifies that:
1. App refuses to boot when sslmode is present in DATABASE_URL
2. RuntimeError is raised with the correct message
3. All three database modules enforce the guard
"""

import os
import sys
import subprocess
from pathlib import Path


def test_sslmode_guard_api_database():
    """Test that api/database.py blocks sslmode in DATABASE_URL"""
    print("Test 1: Testing api/database.py sslmode guard...")
    
    test_code = """
import os
import sys
import logging

# Suppress logging output for cleaner test results
logging.basicConfig(level=logging.CRITICAL)

# Set DATABASE_URL with sslmode
os.environ['DATABASE_URL'] = 'postgresql://user:pass@host:5432/db?sslmode=require'

try:
    # This should raise RuntimeError
    # Import from api.database (package import instead of modifying sys.path)
    from api import database
    print("FAIL: Should have raised RuntimeError")
    sys.exit(1)
except RuntimeError as e:
    if "sslmode is not allowed" in str(e):
        print("PASS: Correctly raised RuntimeError for sslmode in DATABASE_URL")
        sys.exit(0)
    else:
        print(f"FAIL: Wrong error message: {e}")
        sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error: {type(e).__name__}: {e}")
    sys.exit(1)
"""
    
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=Path(__file__).parent,
    )
    
    if result.returncode != 0:
        print(f"❌ FAIL: api/database.py - {result.stdout}")
        print(f"stderr: {result.stderr}")
        return False
    
    print(f"✅ PASS: api/database.py - {result.stdout.strip()}")
    return True


def test_sslmode_guard_backend_app_database():
    """Test that api/backend_app/database.py blocks sslmode in DATABASE_URL"""
    print("\nTest 2: Testing api/backend_app/database.py sslmode guard...")
    
    test_code = """
import os
import sys
import logging

# Suppress logging output for cleaner test results
logging.basicConfig(level=logging.CRITICAL)

# Set DATABASE_URL with sslmode
os.environ['DATABASE_URL'] = 'postgresql://user:pass@host:5432/db?sslmode=require'

try:
    # This should raise RuntimeError
    sys.path.insert(0, 'api/backend_app')
    import database
    print("FAIL: Should have raised RuntimeError")
    sys.exit(1)
except RuntimeError as e:
    if "sslmode is not allowed" in str(e):
        print("PASS: Correctly raised RuntimeError for sslmode in DATABASE_URL")
        sys.exit(0)
    else:
        print(f"FAIL: Wrong error message: {e}")
        sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error: {type(e).__name__}: {e}")
    sys.exit(1)
"""
    
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=Path(__file__).parent,
    )
    
    if result.returncode != 0:
        print(f"❌ FAIL: api/backend_app/database.py - {result.stdout}")
        print(f"stderr: {result.stderr}")
        return False
    
    print(f"✅ PASS: api/backend_app/database.py - {result.stdout.strip()}")
    return True


def test_sslmode_guard_app_database():
    """Test that app/database.py blocks sslmode in DATABASE_URL"""
    print("\nTest 3: Testing app/database.py sslmode guard...")
    
    test_code = """
import os
import sys
import logging

# Suppress logging output for cleaner test results
logging.basicConfig(level=logging.CRITICAL)

# Set DATABASE_URL with sslmode
os.environ['DATABASE_URL'] = 'postgresql://user:pass@host:5432/db?sslmode=require'

try:
    # This should raise RuntimeError
    sys.path.insert(0, '.')
    from app import database
    print("FAIL: Should have raised RuntimeError")
    sys.exit(1)
except RuntimeError as e:
    if "sslmode is not allowed" in str(e):
        print("PASS: Correctly raised RuntimeError for sslmode in DATABASE_URL")
        sys.exit(0)
    else:
        print(f"FAIL: Wrong error message: {e}")
        sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error: {type(e).__name__}: {e}")
    sys.exit(1)
"""
    
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=Path(__file__).parent,
    )
    
    if result.returncode != 0:
        print(f"❌ FAIL: app/database.py - {result.stdout}")
        print(f"stderr: {result.stderr}")
        return False
    
    print(f"✅ PASS: app/database.py - {result.stdout.strip()}")
    return True


def test_sslmode_guard_backend_core_database():
    """Test that backend/app/core/database.py strips sslmode for asyncpg"""
    print("\nTest 4: Testing backend/app/core/database.py sslmode stripping...")
    
    test_code = """
import os
import sys
import logging
import importlib

logging.basicConfig(level=logging.CRITICAL)

# Set DATABASE_URL with sslmode for asyncpg
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://user:pass@host:5432/db?sslmode=require&connect_timeout=10'

try:
    sys.path.insert(0, '.')
    module = importlib.import_module('backend.app.core.database')
    if 'sslmode=' in module.DATABASE_URL:
        print("FAIL: sslmode parameter still present in DATABASE_URL")
        sys.exit(1)
    print("PASS: sslmode stripped from asyncpg DATABASE_URL")
    sys.exit(0)
except Exception as e:
    print(f"FAIL: Unexpected error: {type(e).__name__}: {e}")
    sys.exit(1)
"""
    
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=Path(__file__).parent,
    )
    
    if result.returncode != 0:
        print(f"❌ FAIL: backend/app/core/database.py - {result.stdout}")
        print(f"stderr: {result.stderr}")
        return False
    
    print(f"✅ PASS: backend/app/core/database.py - {result.stdout.strip()}")
    return True


def test_sslmode_guard_allows_urls_without_sslmode():
    """Test that URLs without sslmode are allowed"""
    print("\nTest 5: Testing that URLs without sslmode are allowed...")
    
    test_code = """
import os
import sys
import logging

# Suppress logging output for cleaner test results
logging.basicConfig(level=logging.CRITICAL)

# Set DATABASE_URL WITHOUT sslmode
os.environ['DATABASE_URL'] = 'postgresql://user:pass@host:5432/db'

try:
    # This should NOT raise RuntimeError
    sys.path.insert(0, '.')
    from app import database
    print("PASS: URL without sslmode is allowed")
    sys.exit(0)
except RuntimeError as e:
    if "sslmode is not allowed" in str(e):
        print(f"FAIL: Should NOT block URLs without sslmode")
        sys.exit(1)
    else:
        # Some other RuntimeError (e.g., connection failure) is OK
        print("PASS: URL without sslmode is allowed (connection error is OK)")
        sys.exit(0)
except Exception as e:
    # Other exceptions (e.g., import errors, connection failures) are OK
    # We only care that the sslmode guard doesn't trigger
    print("PASS: URL without sslmode is allowed (other error is OK)")
    sys.exit(0)
"""
    
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=Path(__file__).parent,
    )
    
    if result.returncode != 0:
        print(f"❌ FAIL: {result.stdout}")
        print(f"stderr: {result.stderr}")
        return False
    
    print(f"✅ PASS: {result.stdout.strip()}")
    return True


def test_sslmode_guard_variations():
    """Test that sslmode is detected in various URL formats"""
    print("\nTest 6: Testing sslmode detection in various URL formats...")
    
    test_cases = [
        "postgresql://user:pass@host:5432/db?sslmode=require",
        "postgresql://user:pass@host:5432/db?param1=value1&sslmode=prefer",
        "postgresql://user:pass@host:5432/db?sslmode=disable",
        "postgresql+asyncpg://user:pass@host:5432/db?sslmode=require",
    ]
    
    all_passed = True
    
    for i, url in enumerate(test_cases, 1):
        test_code = f"""
import os
import sys
import logging

logging.basicConfig(level=logging.CRITICAL)

os.environ['DATABASE_URL'] = '{url}'

try:
    sys.path.insert(0, '.')
    from app import database
    print("FAIL: Should have raised RuntimeError")
    sys.exit(1)
except RuntimeError as e:
    if "sslmode is not allowed" in str(e):
        print("PASS: Detected sslmode in URL")
        sys.exit(0)
    else:
        print(f"FAIL: Wrong error: {{e}}")
        sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error: {{type(e).__name__}}: {{e}}")
    sys.exit(1)
"""
        
        result = subprocess.run(
            [sys.executable, "-c", test_code],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=Path(__file__).parent,
        )
        
        if result.returncode != 0:
            print(f"  ❌ FAIL: Case {i} ({url[:50]}...): {result.stdout}")
            all_passed = False
        else:
            print(f"  ✅ PASS: Case {i} - {result.stdout.strip()}")
    
    return all_passed


def main():
    """Run all tests"""
    print("=" * 70)
    print("SSLMODE GUARD TEST SUITE")
    print("=" * 70)
    print()

    tests = [
        ("api/database.py sslmode guard", test_sslmode_guard_api_database),
        ("api/backend_app/database.py sslmode guard", test_sslmode_guard_backend_app_database),
        ("app/database.py sslmode guard", test_sslmode_guard_app_database),
        ("backend/app/core/database.py sslmode stripping", test_sslmode_guard_backend_core_database),
        ("URLs without sslmode allowed", test_sslmode_guard_allows_urls_without_sslmode),
        ("sslmode detection variations", test_sslmode_guard_variations),
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
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
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

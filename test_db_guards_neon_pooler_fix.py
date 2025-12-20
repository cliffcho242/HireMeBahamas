#!/usr/bin/env python3
"""
Test script for database guards fix for Neon pooled connections.

This test verifies that:
1. Neon pooled connections are allowed without sslmode
2. asyncpg driver connections are allowed without sslmode
3. Direct PostgreSQL connections still require sslmode
4. Local development URLs are allowed without sslmode
"""

import os
import sys
from pathlib import Path

# Suppress logging for cleaner output
os.environ['PYTHONPATH'] = str(Path(__file__).parent)


def clear_modules(*patterns):
    """Clear modules from cache that match any of the given patterns."""
    modules_to_remove = []
    for k in sys.modules:
        if any(pattern in k for pattern in patterns):
            if k.startswith('backend.') or k == 'backend':
                modules_to_remove.append(k)
    
    for mod in modules_to_remove:
        del sys.modules[mod]


def test_neon_pooled_connection_without_sslmode():
    """Test that Neon pooled connections work without sslmode"""
    print("Test 1: Neon pooled connection without sslmode...")
    
    # Set DATABASE_URL to Neon pooled connection format (no sslmode)
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://user:pass@ep-xxx-pooler.us-east-1.aws.neon.tech:5432/dbname'
    
    try:
        clear_modules('backend', 'db_guards')
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.app.core.db_guards import check_sslmode_in_database_url
        
        valid, error = check_sslmode_in_database_url()
        if not valid:
            print(f"❌ FAIL: Neon pooled connection rejected: {error}")
            return False
        
        print("✅ PASS: Neon pooled connection allowed without sslmode")
        return True
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_asyncpg_connection_without_sslmode():
    """Test that asyncpg connections work without sslmode"""
    print("\nTest 2: asyncpg connection without sslmode...")
    
    # Set DATABASE_URL with asyncpg driver (no sslmode)
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://user:pass@db.example.com:5432/dbname'
    
    try:
        clear_modules('backend', 'db_guards')
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.app.core.db_guards import check_sslmode_in_database_url
        
        valid, error = check_sslmode_in_database_url()
        if not valid:
            print(f"❌ FAIL: asyncpg connection rejected: {error}")
            return False
        
        print("✅ PASS: asyncpg connection allowed without sslmode")
        return True
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_direct_postgres_requires_sslmode():
    """Test that direct PostgreSQL connections still require sslmode"""
    print("\nTest 3: Direct PostgreSQL connection requires sslmode...")
    
    # Set DATABASE_URL to direct PostgreSQL (psycopg2) without sslmode
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@db.example.com:5432/dbname'
    
    try:
        clear_modules('backend', 'db_guards')
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.app.core.db_guards import check_sslmode_in_database_url
        
        valid, error = check_sslmode_in_database_url()
        if valid:
            print("❌ FAIL: Direct PostgreSQL connection should require sslmode")
            return False
        
        if "missing sslmode parameter" not in str(error):
            print(f"❌ FAIL: Wrong error message: {error}")
            return False
        
        print("✅ PASS: Direct PostgreSQL connection requires sslmode")
        return True
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_direct_postgres_with_sslmode():
    """Test that direct PostgreSQL connections with sslmode are allowed"""
    print("\nTest 4: Direct PostgreSQL connection with sslmode...")
    
    # Set DATABASE_URL to direct PostgreSQL with sslmode
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@db.example.com:5432/dbname?sslmode=require'
    
    try:
        clear_modules('backend', 'db_guards')
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.app.core.db_guards import check_sslmode_in_database_url
        
        valid, error = check_sslmode_in_database_url()
        if not valid:
            print(f"❌ FAIL: PostgreSQL with sslmode rejected: {error}")
            return False
        
        print("✅ PASS: Direct PostgreSQL connection with sslmode allowed")
        return True
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_localhost_without_sslmode():
    """Test that localhost connections work without sslmode"""
    print("\nTest 5: Localhost connection without sslmode...")
    
    # Set DATABASE_URL to localhost
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost:5432/dbname'
    
    try:
        clear_modules('backend', 'db_guards')
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.app.core.db_guards import check_sslmode_in_database_url
        
        valid, error = check_sslmode_in_database_url()
        if not valid:
            print(f"❌ FAIL: Localhost connection rejected: {error}")
            return False
        
        print("✅ PASS: Localhost connection allowed without sslmode")
        return True
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_neon_non_pooled_with_asyncpg():
    """Test that Neon non-pooled connections with asyncpg work without sslmode"""
    print("\nTest 6: Neon non-pooled connection with asyncpg...")
    
    # Set DATABASE_URL to Neon direct connection (no -pooler)
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://user:pass@ep-xxx.us-east-1.aws.neon.tech:5432/dbname'
    
    try:
        clear_modules('backend', 'db_guards')
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.app.core.db_guards import check_sslmode_in_database_url
        
        valid, error = check_sslmode_in_database_url()
        if not valid:
            print(f"❌ FAIL: Neon non-pooled asyncpg connection rejected: {error}")
            return False
        
        print("✅ PASS: Neon non-pooled asyncpg connection allowed (asyncpg driver exemption)")
        return True
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("DATABASE GUARDS FIX - NEON POOLED CONNECTION TESTS")
    print("=" * 70)
    print()

    tests = [
        test_neon_pooled_connection_without_sslmode,
        test_asyncpg_connection_without_sslmode,
        test_direct_postgres_requires_sslmode,
        test_direct_postgres_with_sslmode,
        test_localhost_without_sslmode,
        test_neon_non_pooled_with_asyncpg,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            print(f"\n❌ Test ERROR: {e}\n")
            import traceback
            traceback.print_exc()

    print()
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print()

    if failed == 0:
        print("✅ All tests passed!")
        print()
        print("Summary:")
        print("  ✅ Neon pooled connections work without sslmode")
        print("  ✅ asyncpg driver connections work without sslmode")
        print("  ✅ Direct PostgreSQL connections still require sslmode")
        print("  ✅ Localhost connections work without sslmode")
        print("  ✅ Validation is consistent and correct")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

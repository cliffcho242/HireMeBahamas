#!/usr/bin/env python3
"""
Test for SQLAlchemy URL parsing error with whitespace-only DATABASE_URL.

This test validates that:
1. Empty/whitespace DATABASE_URL is handled gracefully in all database modules
2. No ArgumentError is raised when creating database engines
3. Proper fallback URLs are used in development vs production
"""

import os
import sys
import importlib

# Track test results
test_results = []


def test_config_module_whitespace_handling():
    """Test backend/app/core/config.py handles whitespace-only DATABASE_URL."""
    print("\nTest 1: backend/app/core/config.py whitespace handling")
    
    # Save original environment
    original_database_url = os.environ.get('DATABASE_URL')
    original_postgres_url = os.environ.get('POSTGRES_URL')
    original_database_private_url = os.environ.get('DATABASE_PRIVATE_URL')
    
    try:
        # Test Case 1: Whitespace-only DATABASE_URL in development
        os.environ['ENVIRONMENT'] = 'development'
        os.environ['DATABASE_URL'] = '   '  # Whitespace-only string
        if 'POSTGRES_URL' in os.environ:
            del os.environ['POSTGRES_URL']
        if 'DATABASE_PRIVATE_URL' in os.environ:
            del os.environ['DATABASE_PRIVATE_URL']
        
        # Remove cached modules to force reload
        if 'backend.app.core.config' in sys.modules:
            del sys.modules['backend.app.core.config']
        
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from app.core.config import settings, Settings
        
        db_url = settings.get_database_url()
        
        # Verify URL is not empty
        assert db_url, "DATABASE_URL should not be empty after processing whitespace-only string"
        
        # Verify URL starts with postgresql
        assert db_url.startswith('postgresql'), f"Expected URL to start with 'postgresql', got: {db_url}"
        
        print("  ✓ Whitespace-only DATABASE_URL handled correctly in development")
        test_results.append(('config_whitespace_dev', True, None))
        
        # Test Case 2: Empty string DATABASE_URL in development
        os.environ['DATABASE_URL'] = ''
        
        # Force settings to re-read (update class attribute, not instance attribute)
        Settings.DATABASE_URL = None
        db_url = settings.get_database_url()
        
        assert db_url, "DATABASE_URL should not be empty after processing empty string"
        assert db_url.startswith('postgresql'), f"Expected URL to start with 'postgresql', got: {db_url}"
        
        print("  ✓ Empty DATABASE_URL handled correctly in development")
        test_results.append(('config_empty_dev', True, None))
        
        # Test Case 3: Whitespace-only in production should raise ValueError
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['DATABASE_URL'] = '   '
        
        # Update class attributes, not instance attributes (since get_database_url is a classmethod)
        Settings.ENVIRONMENT = 'production'
        Settings.DATABASE_URL = '   '
        
        try:
            db_url = settings.get_database_url()
            print(f"  ✗ Production should raise ValueError for whitespace-only URL, but got: {db_url}")
            test_results.append(('config_whitespace_prod', False, "Expected ValueError not raised"))
        except ValueError as e:
            if "DATABASE_URL must be set in production" in str(e):
                print("  ✓ Production correctly raises ValueError for whitespace-only DATABASE_URL")
                test_results.append(('config_whitespace_prod', True, None))
            else:
                print(f"  ✗ Wrong ValueError message: {e}")
                test_results.append(('config_whitespace_prod', False, f"Wrong error message: {e}"))
        
    except Exception as e:
        print(f"  ✗ Unexpected exception: {type(e).__name__}: {e}")
        test_results.append(('config_whitespace', False, str(e)))
        import traceback
        traceback.print_exc()
    finally:
        # Restore original environment
        if original_database_url:
            os.environ['DATABASE_URL'] = original_database_url
        elif 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']
        
        if original_postgres_url:
            os.environ['POSTGRES_URL'] = original_postgres_url
        elif 'POSTGRES_URL' in os.environ:
            del os.environ['POSTGRES_URL']
        
        if original_database_private_url:
            os.environ['DATABASE_PRIVATE_URL'] = original_database_private_url
        elif 'DATABASE_PRIVATE_URL' in os.environ:
            del os.environ['DATABASE_PRIVATE_URL']
        
        os.environ['ENVIRONMENT'] = 'development'


def test_backend_database_whitespace_handling():
    """Test backend/app/database.py handles whitespace-only DATABASE_URL."""
    print("\nTest 2: backend/app/database.py whitespace handling")
    
    # Save original environment
    original_database_url = os.environ.get('DATABASE_URL')
    original_environment = os.environ.get('ENVIRONMENT')
    
    try:
        # Test Case 1: Whitespace-only DATABASE_URL
        os.environ['ENVIRONMENT'] = 'development'
        os.environ['DATABASE_URL'] = '   '
        
        # Remove cached modules to force reload
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from app import database
        
        # Check that DATABASE_URL was converted to a valid URL
        assert database.DATABASE_URL, "DATABASE_URL should not be empty"
        assert database.DATABASE_URL.startswith('postgresql'), \
            f"Expected URL to start with 'postgresql', got: {database.DATABASE_URL}"
        
        print("  ✓ backend/app/database.py handles whitespace-only DATABASE_URL correctly")
        test_results.append(('backend_database_whitespace', True, None))
        
    except Exception as e:
        print(f"  ✗ Unexpected exception: {type(e).__name__}: {e}")
        test_results.append(('backend_database_whitespace', False, str(e)))
        import traceback
        traceback.print_exc()
    finally:
        # Restore original environment
        if original_database_url:
            os.environ['DATABASE_URL'] = original_database_url
        elif 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']
        
        if original_environment:
            os.environ['ENVIRONMENT'] = original_environment
        else:
            os.environ['ENVIRONMENT'] = 'development'


def test_api_database_whitespace_handling():
    """Test api/database.py handles whitespace-only DATABASE_URL."""
    print("\nTest 3: api/database.py whitespace handling")
    
    # Save original environment
    original_database_url = os.environ.get('DATABASE_URL')
    original_env = os.environ.get('ENV')
    
    try:
        # Test Case 1: Whitespace-only DATABASE_URL
        os.environ['ENV'] = 'development'
        os.environ['DATABASE_URL'] = '   '
        
        # Remove cached modules to force reload
        if 'api.database' in sys.modules:
            del sys.modules['api.database']
        
        sys.path.insert(0, os.path.dirname(__file__))
        from api import database
        
        # get_database_url() should return None for invalid URLs (production-safe)
        db_url = database.get_database_url()
        
        # In api/database.py, whitespace-only URL returns None (warning logged)
        # This is the expected behavior for this module (production-safe)
        if db_url is None:
            print("  ✓ api/database.py returns None for whitespace-only DATABASE_URL (production-safe)")
            test_results.append(('api_database_whitespace', True, None))
        else:
            print(f"  ✗ Expected None, got: {db_url}")
            test_results.append(('api_database_whitespace', False, f"Expected None, got {db_url}"))
        
    except Exception as e:
        print(f"  ✗ Unexpected exception: {type(e).__name__}: {e}")
        test_results.append(('api_database_whitespace', False, str(e)))
        import traceback
        traceback.print_exc()
    finally:
        # Restore original environment
        if original_database_url:
            os.environ['DATABASE_URL'] = original_database_url
        elif 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']
        
        if original_env:
            os.environ['ENV'] = original_env
        else:
            os.environ['ENV'] = 'development'


def main():
    """Run all tests."""
    print("=" * 70)
    print("SQLAlchemy URL Parsing Error Fix - Whitespace Handling Tests")
    print("=" * 70)
    
    test_config_module_whitespace_handling()
    test_backend_database_whitespace_handling()
    test_api_database_whitespace_handling()
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, success, _ in test_results if success)
    failed = sum(1 for _, success, _ in test_results if not success)
    
    for test_name, success, error in test_results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
        if error:
            print(f"  Error: {error}")
    
    print(f"\nTotal: {len(test_results)} tests, {passed} passed, {failed} failed")
    
    if failed > 0:
        print("\n❌ SOME TESTS FAILED")
        return 1
    else:
        print("\n✅ ALL TESTS PASSED")
        return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

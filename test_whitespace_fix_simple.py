#!/usr/bin/env python3
"""
Simple test to validate whitespace DATABASE_URL handling without requiring SQLAlchemy.
This test verifies the fix for SQLAlchemy URL parsing error with whitespace-only DATABASE_URL.
"""

import os
import sys


def test_whitespace_handling():
    """Test that whitespace-only DATABASE_URL is handled correctly."""
    print("=" * 70)
    print("Testing Whitespace DATABASE_URL Handling")
    print("=" * 70)
    
    results = []
    
    # Save original environment variables
    original_env = os.environ.get('ENVIRONMENT')
    original_db_url = os.environ.get('DATABASE_URL')
    
    # Test 1: Development mode with whitespace-only URL
    print("\n[Test 1] Development mode with whitespace-only DATABASE_URL")
    os.environ['ENVIRONMENT'] = 'development'
    os.environ['DATABASE_URL'] = '   '
    
    # Remove cached modules
    for module in list(sys.modules.keys()):
        if 'backend.app.core.config' in module:
            del sys.modules[module]
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    
    try:
        from app.core.config import settings, Settings
        
        # Verify Settings reads the whitespace URL
        assert Settings.DATABASE_URL == '   ', f"Expected '   ', got {repr(Settings.DATABASE_URL)}"
        
        # Call get_database_url()
        url = settings.get_database_url()
        
        # Should return a fallback URL, not empty
        assert url, "URL should not be empty in development"
        assert url.startswith('postgresql'), f"Expected postgresql URL, got: {url}"
        
        print(f"  ✓ PASS: Returned fallback URL: {url[:50]}...")
        results.append(('dev_whitespace', True, None))
        
    except Exception as e:
        print(f"  ✗ FAIL: {type(e).__name__}: {e}")
        results.append(('dev_whitespace', False, str(e)))
    
    # Test 2: Production mode with whitespace-only URL
    print("\n[Test 2] Production mode with whitespace-only DATABASE_URL")
    
    # Save original class attributes
    orig_environment = Settings.ENVIRONMENT
    orig_database_url = Settings.DATABASE_URL
    
    try:
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['DATABASE_URL'] = '   '
        
        # Update class attributes
        Settings.ENVIRONMENT = 'production'
        Settings.DATABASE_URL = '   '
        
        try:
            url = settings.get_database_url()
            print(f"  ✗ FAIL: Should have raised ValueError, but got: {url}")
            results.append(('prod_whitespace', False, "ValueError not raised"))
            
        except ValueError as e:
            if "DATABASE_URL must be set in production" in str(e):
                print(f"  ✓ PASS: Correctly raised ValueError: {e}")
                results.append(('prod_whitespace', True, None))
            else:
                print(f"  ✗ FAIL: Wrong error message: {e}")
                results.append(('prod_whitespace', False, f"Wrong error: {e}"))
        
        except Exception as e:
            print(f"  ✗ FAIL: Unexpected {type(e).__name__}: {e}")
            results.append(('prod_whitespace', False, str(e)))
    
    finally:
        # Restore original class attributes
        Settings.ENVIRONMENT = orig_environment
        Settings.DATABASE_URL = orig_database_url
    
    # Test 3: Empty string DATABASE_URL in development
    print("\n[Test 3] Development mode with empty DATABASE_URL")
    
    # Save original class attributes
    orig_environment = Settings.ENVIRONMENT
    orig_database_url = Settings.DATABASE_URL
    
    try:
        os.environ['ENVIRONMENT'] = 'development'
        os.environ['DATABASE_URL'] = ''
        
        Settings.ENVIRONMENT = 'development'
        Settings.DATABASE_URL = ''
        
        try:
            url = settings.get_database_url()
            
            assert url, "URL should not be empty in development"
            assert url.startswith('postgresql'), f"Expected postgresql URL, got: {url}"
            
            print(f"  ✓ PASS: Returned fallback URL: {url[:50]}...")
            results.append(('dev_empty', True, None))
            
        except Exception as e:
            print(f"  ✗ FAIL: {type(e).__name__}: {e}")
            results.append(('dev_empty', False, str(e)))
    
    finally:
        # Restore original class attributes
        Settings.ENVIRONMENT = orig_environment
        Settings.DATABASE_URL = orig_database_url
    
    # Test 4: Production mode with empty DATABASE_URL
    print("\n[Test 4] Production mode with empty DATABASE_URL")
    
    # Save original class attributes
    orig_environment = Settings.ENVIRONMENT
    orig_database_url = Settings.DATABASE_URL
    
    try:
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['DATABASE_URL'] = ''
        
        Settings.ENVIRONMENT = 'production'
        Settings.DATABASE_URL = ''
        
        try:
            url = settings.get_database_url()
            print(f"  ✗ FAIL: Should have raised ValueError, but got: {url}")
            results.append(('prod_empty', False, "ValueError not raised"))
            
        except ValueError as e:
            if "DATABASE_URL must be set in production" in str(e):
                print(f"  ✓ PASS: Correctly raised ValueError: {e}")
                results.append(('prod_empty', True, None))
            else:
                print(f"  ✗ FAIL: Wrong error message: {e}")
                results.append(('prod_empty', False, f"Wrong error: {e}"))
        
        except Exception as e:
            print(f"  ✗ FAIL: Unexpected {type(e).__name__}: {e}")
            results.append(('prod_empty', False, str(e)))
    
    finally:
        # Restore original class attributes
        Settings.ENVIRONMENT = orig_environment
        Settings.DATABASE_URL = orig_database_url
        
        # Restore original environment variables
        if original_env is not None:
            os.environ['ENVIRONMENT'] = original_env
        elif 'ENVIRONMENT' in os.environ:
            del os.environ['ENVIRONMENT']
        
        if original_db_url is not None:
            os.environ['DATABASE_URL'] = original_db_url
        elif 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, error in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
        if error:
            print(f"  Error: {error}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(test_whitespace_handling())

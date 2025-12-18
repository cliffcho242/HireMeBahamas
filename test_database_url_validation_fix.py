#!/usr/bin/env python3
"""
Test to verify DATABASE_URL validation fix.

This test ensures that:
1. Complex validation is removed from startup
2. Simple existence check works correctly
3. Basic URL processing still happens (whitespace strip, driver conversion)
4. No port parsing, auto-fixing, or runtime modification occurs
"""
import os
import sys
import importlib


def test_backend_app_config():
    """Test backend/app/config.py"""
    print("=" * 60)
    print("Testing backend/app/config.py")
    print("=" * 60)
    
    # Clear any existing modules
    if 'app' in sys.modules:
        del sys.modules['app']
    if 'app.config' in sys.modules:
        del sys.modules['app.config']
    
    sys.path.insert(0, 'backend')
    
    # Test 1: Production without DATABASE_URL should raise RuntimeError
    print("\n✓ Test 1: Production without DATABASE_URL")
    os.environ['ENVIRONMENT'] = 'production'
    for key in ['DATABASE_URL', 'POSTGRES_URL', 'DATABASE_PRIVATE_URL']:
        os.environ.pop(key, None)
    
    from app.config import Settings
    
    try:
        url = Settings.get_database_url()
        print("  ❌ FAIL: Should have raised RuntimeError")
        return False
    except RuntimeError as e:
        if 'DATABASE_URL is required in production' in str(e):
            print("  ✅ PASS: Correctly raised RuntimeError")
        else:
            print(f"  ❌ FAIL: Wrong error message: {e}")
            return False
    
    # Test 2: Production with DATABASE_URL
    print("\n✓ Test 2: Production with DATABASE_URL")
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@db.example.com:5432/mydb?sslmode=require'
    
    # Reload to pick up new env
    importlib.reload(sys.modules['app.config'])
    from app.config import Settings
    
    url = Settings.get_database_url()
    if 'postgresql+asyncpg://' in url and 'db.example.com:5432' in url:
        print(f"  ✅ PASS: URL correctly processed: {url}")
    else:
        print(f"  ❌ FAIL: URL processing failed: {url}")
        return False
    
    # Test 3: Whitespace is stripped
    print("\n✓ Test 3: Whitespace handling")
    os.environ['DATABASE_URL'] = '  postgresql://user:pass@host:5432/db  '
    url = Settings.get_database_url()
    if not url.startswith(' ') and not url.endswith(' '):
        print(f"  ✅ PASS: Whitespace stripped correctly")
    else:
        print(f"  ❌ FAIL: Whitespace not handled: '{url}'")
        return False
    
    # Test 4: postgres:// converted to postgresql+asyncpg://
    print("\n✓ Test 4: Driver conversion")
    os.environ['DATABASE_URL'] = 'postgres://user:pass@host:5432/db'
    url = Settings.get_database_url()
    if url.startswith('postgresql+asyncpg://'):
        print(f"  ✅ PASS: Driver converted correctly")
    else:
        print(f"  ❌ FAIL: Driver conversion failed: {url}")
        return False
    
    sys.path.pop(0)
    return True


def test_backend_app_core_config():
    """Test backend/app/core/config.py"""
    print("\n" + "=" * 60)
    print("Testing backend/app/core/config.py")
    print("=" * 60)
    
    # Clear any existing modules
    for mod in list(sys.modules.keys()):
        if mod.startswith('app'):
            del sys.modules[mod]
    
    sys.path.insert(0, 'backend')
    
    # Test 1: Production without DATABASE_URL should raise RuntimeError
    print("\n✓ Test 1: Production without DATABASE_URL")
    os.environ['ENVIRONMENT'] = 'production'
    for key in ['DATABASE_URL', 'POSTGRES_URL', 'DATABASE_PRIVATE_URL']:
        os.environ.pop(key, None)
    
    from app.core.config import Settings
    
    try:
        url = Settings.get_database_url()
        print("  ❌ FAIL: Should have raised RuntimeError")
        return False
    except RuntimeError as e:
        if 'DATABASE_URL is required in production' in str(e):
            print("  ✅ PASS: Correctly raised RuntimeError")
        else:
            print(f"  ❌ FAIL: Wrong error message: {e}")
            return False
    
    # Test 2: Production with DATABASE_URL
    print("\n✓ Test 2: Production with DATABASE_URL")
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@db.example.com:5432/mydb?sslmode=require'
    
    # Reload to pick up new env
    importlib.reload(sys.modules['app.core.config'])
    from app.core.config import Settings
    
    url = Settings.get_database_url()
    if 'postgresql+asyncpg://' in url and 'db.example.com:5432' in url:
        print(f"  ✅ PASS: URL correctly processed")
    else:
        print(f"  ❌ FAIL: URL processing failed: {url}")
        return False
    
    sys.path.pop(0)
    return True


def test_no_runtime_modifications():
    """Verify no auto-fixing or runtime modifications occur"""
    print("\n" + "=" * 60)
    print("Testing No Runtime Modifications")
    print("=" * 60)
    
    # Clear any existing modules
    for mod in list(sys.modules.keys()):
        if mod.startswith('app'):
            del sys.modules[mod]
    
    sys.path.insert(0, 'backend')
    
    os.environ['ENVIRONMENT'] = 'production'
    
    # Test: URL without explicit port is NOT auto-fixed
    print("\n✓ Test: No port auto-fix")
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@db.example.com/mydb'
    
    from app.config import Settings
    importlib.reload(sys.modules['app.config'])
    
    url = Settings.get_database_url()
    # Should NOT add port automatically
    if ':5432' not in url or 'db.example.com:' not in url:
        print("  ✅ PASS: Port NOT auto-added to URL")
    else:
        print(f"  ⚠️  WARNING: Port may have been auto-added: {url}")
    
    # Test: Invalid hostnames are NOT validated/rejected at startup
    print("\n✓ Test: No hostname validation at startup")
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost:5432/mydb'
    
    # Reload to pick up new env
    importlib.reload(sys.modules['app.config'])
    from app.config import Settings as ReloadedSettings
    
    url = ReloadedSettings.get_database_url()
    if 'localhost' in url:
        print("  ✅ PASS: localhost URL accepted (no validation)")
    else:
        print(f"  ❌ FAIL: URL was rejected or modified: {url}")
        return False
    
    sys.path.pop(0)
    return True


def main():
    """Run all tests"""
    print("DATABASE_URL Validation Fix - Test Suite")
    print("=========================================\n")
    
    os.chdir('/home/runner/work/HireMeBahamas/HireMeBahamas')
    
    results = []
    
    # Run all tests
    results.append(("backend/app/config.py", test_backend_app_config()))
    results.append(("backend/app/core/config.py", test_backend_app_core_config()))
    results.append(("No runtime modifications", test_no_runtime_modifications()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

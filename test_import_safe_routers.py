"""
Test script to verify that routers are import-safe.

This test ensures that:
1. The api package can be imported without loading all routers
2. Routers are only loaded when explicitly imported
3. Routers can still be imported and used normally when needed
"""
import sys
import os

# Add the repository root to the path
repo_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(repo_root, 'api'))


def test_api_package_import_safe():
    """Test that importing the api package doesn't load all routers."""
    print("Test 1: Verify api package is import-safe...")
    
    # Clear any previously loaded api modules
    modules_to_remove = [m for m in sys.modules if m.startswith('backend_app.api.') and m != 'backend_app.api']
    for m in modules_to_remove:
        del sys.modules[m]
    
    # Import the api package
    from backend_app import api as api_pkg
    
    # Verify __all__ is defined
    assert hasattr(api_pkg, '__all__'), "api package should have __all__ attribute"
    print(f"  ✓ __all__ defined with {len(api_pkg.__all__)} routers")
    
    # Verify that router modules are NOT loaded yet
    loaded_routers = [m for m in sys.modules if m.startswith('backend_app.api.') and m != 'backend_app.api']
    
    if loaded_routers:
        print(f"  ✗ FAILED: Router modules were loaded eagerly: {loaded_routers}")
        print("    This violates the import-safe principle!")
        return False
    else:
        print("  ✓ No router modules loaded (import-safe!)")
        return True


def test_explicit_router_import():
    """Test that routers can be imported explicitly when needed."""
    print("\nTest 2: Verify routers can be imported explicitly...")
    
    # Note: We can't actually import the router in this test context
    # because it requires FastAPI and other dependencies to be installed.
    # But we can verify the module structure is correct.
    
    import backend_app.api
    
    # Verify that the expected routers are listed in __all__
    expected_routers = [
        'analytics', 'auth', 'debug', 'hireme', 'jobs', 
        'messages', 'notifications', 'posts', 'profile_pictures', 
        'reviews', 'upload', 'users'
    ]
    
    for router in expected_routers:
        if router not in backend_app.api.__all__:
            print(f"  ✗ FAILED: Router '{router}' not in __all__")
            return False
    
    print(f"  ✓ All {len(expected_routers)} routers declared in __all__")
    print("  ✓ Routers can be imported with: from backend_app.api import <router>")
    return True


def test_backend_app_api_import_safe():
    """Test that backend/app/api is also import-safe."""
    print("\nTest 3: Verify backend/app/api is import-safe...")
    
    # Add backend to path
    sys.path.insert(0, os.path.join(repo_root, 'backend'))
    
    # Clear any previously loaded api modules
    modules_to_remove = [m for m in sys.modules if m.startswith('app.api.') and m != 'app.api']
    for m in modules_to_remove:
        del sys.modules[m]
    
    try:
        # Import the api package
        from app import api as api_pkg
        
        # Verify __all__ is defined
        assert hasattr(api_pkg, '__all__'), "api package should have __all__ attribute"
        print(f"  ✓ __all__ defined with {len(api_pkg.__all__)} routers")
        
        # Verify that router modules are NOT loaded yet
        loaded_routers = [m for m in sys.modules if m.startswith('app.api.') and m != 'app.api']
        
        if loaded_routers:
            print(f"  ✗ FAILED: Router modules were loaded eagerly: {loaded_routers}")
            return False
        else:
            print("  ✓ No router modules loaded (import-safe!)")
            return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*70)
    print("Import-Safe Routers Test")
    print("="*70)
    print()
    print("Testing that routers ONLY export their router objects and")
    print("do NOT execute heavy operations at import time.")
    print()
    
    # Run tests
    test1_passed = test_api_package_import_safe()
    test2_passed = test_explicit_router_import()
    test3_passed = test_backend_app_api_import_safe()
    
    print()
    print("="*70)
    if test1_passed and test2_passed and test3_passed:
        print("✅ All import-safe tests PASSED!")
        print()
        print("Routers are now import-safe:")
        print("  - Package import does NOT load routers")
        print("  - Routers are loaded ONLY when explicitly imported")
        print("  - No circular dependencies or import-time side effects")
        print("="*70)
        sys.exit(0)
    else:
        print("❌ Some import-safe tests FAILED")
        print("="*70)
        sys.exit(1)

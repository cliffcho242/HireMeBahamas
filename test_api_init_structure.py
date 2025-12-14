"""
Test script to verify that API __init__.py files have the correct structure.

This test checks the content of __init__.py files without actually importing
the modules, which avoids dependency issues.
"""
import os


def test_backend_app_api_init():
    """Test that backend/app/api/__init__.py has the correct structure."""
    print("Testing backend/app/api/__init__.py structure...")
    
    init_file = "/home/runner/work/HireMeBahamas/HireMeBahamas/backend/app/api/__init__.py"
    
    with open(init_file, 'r') as f:
        content = f.read()
    
    # Expected modules in the import statement
    expected_modules = [
        'auth', 'hireme', 'jobs', 'messages', 'notifications',
        'posts', 'profile_pictures', 'reviews', 'upload', 'users'
    ]
    
    # Check that import statement exists
    assert 'from . import' in content, "Missing 'from . import' statement"
    
    # Check that __all__ exists
    assert '__all__' in content, "Missing __all__ definition"
    
    # Check that all expected modules are present
    for module in expected_modules:
        assert module in content, f"Missing module '{module}' in __init__.py"
    
    print("✓ backend/app/api/__init__.py structure is correct")
    print(f"  - Contains import statement with {len(expected_modules)} modules")
    print(f"  - Contains __all__ definition")
    return True


def test_api_backend_app_api_init():
    """Test that api/backend_app/api/__init__.py has the correct structure."""
    print("\nTesting api/backend_app/api/__init__.py structure...")
    
    init_file = "/home/runner/work/HireMeBahamas/HireMeBahamas/api/backend_app/api/__init__.py"
    
    with open(init_file, 'r') as f:
        content = f.read()
    
    # Expected modules in the import statement (includes analytics and debug)
    expected_modules = [
        'analytics', 'auth', 'debug', 'hireme', 'jobs', 'messages',
        'notifications', 'posts', 'profile_pictures', 'reviews', 'upload', 'users'
    ]
    
    # Check that import statement exists
    assert 'from . import' in content, "Missing 'from . import' statement"
    
    # Check that __all__ exists
    assert '__all__' in content, "Missing __all__ definition"
    
    # Check that all expected modules are present
    for module in expected_modules:
        assert module in content, f"Missing module '{module}' in __init__.py"
    
    print("✓ api/backend_app/api/__init__.py structure is correct")
    print(f"  - Contains import statement with {len(expected_modules)} modules")
    print(f"  - Contains __all__ definition")
    return True


def test_import_statement_format():
    """Test that the import statements follow the expected format."""
    print("\nTesting import statement format...")
    
    backend_init = "/home/runner/work/HireMeBahamas/HireMeBahamas/backend/app/api/__init__.py"
    api_init = "/home/runner/work/HireMeBahamas/HireMeBahamas/api/backend_app/api/__init__.py"
    
    with open(backend_init, 'r') as f:
        backend_content = f.read()
    
    with open(api_init, 'r') as f:
        api_content = f.read()
    
    # Check that both use relative imports
    assert 'from . import' in backend_content, "backend/app/api should use relative import 'from . import'"
    assert 'from . import' in api_content, "api/backend_app/api should use relative import 'from . import'"
    
    # Check that neither uses 'from .api import' (which would be wrong in __init__.py)
    assert 'from .api import' not in backend_content, \
        "backend/app/api/__init__.py should not use 'from .api import'"
    assert 'from .api import' not in api_content, \
        "api/backend_app/api/__init__.py should not use 'from .api import'"
    
    print("✓ Import statement format is correct")
    print("  - Uses 'from . import' pattern")
    print("  - Does not use incorrect 'from .api import' pattern")
    return True


if __name__ == "__main__":
    print("="*60)
    print("API __init__.py Structure Test")
    print("="*60)
    
    try:
        # Run tests
        test1_passed = test_backend_app_api_init()
        test2_passed = test_api_backend_app_api_init()
        test3_passed = test_import_statement_format()
        
        print("\n" + "="*60)
        if test1_passed and test2_passed and test3_passed:
            print("✓ All API __init__.py structure tests passed!")
            print("="*60)
            exit(0)
        else:
            print("✗ Some API __init__.py structure tests failed")
            print("="*60)
            exit(1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

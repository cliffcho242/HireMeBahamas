"""
Test script to verify that API module imports work correctly.

This test ensures that the __init__.py files in the api directories
properly expose the API modules for import.
"""
import sys
import os

# Add the repository root to the path
repo_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, repo_root)


def test_backend_app_api_imports():
    """Test that backend/app/api modules can be imported."""
    print("Testing backend/app/api imports...")
    
    try:
        # Test importing the api package
        from backend.app import api
        
        # Test importing individual modules
        from backend.app.api import auth
        from backend.app.api import hireme
        from backend.app.api import jobs
        from backend.app.api import messages
        from backend.app.api import notifications
        from backend.app.api import posts
        from backend.app.api import profile_pictures
        from backend.app.api import reviews
        from backend.app.api import upload
        from backend.app.api import users
        
        # Verify __all__ is properly defined
        expected_modules = [
            'auth', 'hireme', 'jobs', 'messages', 'notifications',
            'posts', 'profile_pictures', 'reviews', 'upload', 'users'
        ]
        
        assert hasattr(api, '__all__'), "api package should have __all__ attribute"
        assert set(expected_modules).issubset(set(api.__all__)), \
            f"Missing modules in __all__. Expected: {expected_modules}, Got: {api.__all__}"
        
        print("✓ backend/app/api imports successful")
        return True
        
    except Exception as e:
        print(f"✗ backend/app/api imports failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_backend_app_api_imports():
    """Test that api/backend_app/api modules can be imported."""
    print("\nTesting api/backend_app/api imports...")
    
    try:
        # Test importing the api package
        from api.backend_app import api
        
        # Test importing individual modules (including analytics and debug which are extra)
        from api.backend_app.api import analytics
        from api.backend_app.api import auth
        from api.backend_app.api import debug
        from api.backend_app.api import hireme
        from api.backend_app.api import jobs
        from api.backend_app.api import messages
        from api.backend_app.api import notifications
        from api.backend_app.api import posts
        from api.backend_app.api import profile_pictures
        from api.backend_app.api import reviews
        from api.backend_app.api import upload
        from api.backend_app.api import users
        
        # Verify __all__ is properly defined
        expected_modules = [
            'analytics', 'auth', 'debug', 'hireme', 'jobs', 'messages',
            'notifications', 'posts', 'profile_pictures', 'reviews', 'upload', 'users'
        ]
        
        assert hasattr(api, '__all__'), "api package should have __all__ attribute"
        assert set(expected_modules).issubset(set(api.__all__)), \
            f"Missing modules in __all__. Expected: {expected_modules}, Got: {api.__all__}"
        
        print("✓ api/backend_app/api imports successful")
        return True
        
    except Exception as e:
        print(f"✗ api/backend_app/api imports failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*60)
    print("API Module Import Test")
    print("="*60)
    
    # Run tests
    test1_passed = test_backend_app_api_imports()
    test2_passed = test_api_backend_app_api_imports()
    
    print("\n" + "="*60)
    if test1_passed and test2_passed:
        print("✓ All API import tests passed!")
        print("="*60)
        sys.exit(0)
    else:
        print("✗ Some API import tests failed")
        print("="*60)
        sys.exit(1)

#!/usr/bin/env python3
"""
Test script to verify profile pictures feature is working correctly
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        from app.models import ProfilePicture, User
        from app.api import profile_pictures
        from app.database import Base
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_model_structure():
    """Test that ProfilePicture model has correct structure"""
    print("\nTesting model structure...")
    try:
        from app.models import ProfilePicture
        
        expected_columns = ['id', 'user_id', 'file_url', 'filename', 'file_size', 'is_current', 'created_at']
        actual_columns = ProfilePicture.__table__.columns.keys()
        
        missing = set(expected_columns) - set(actual_columns)
        if missing:
            print(f"❌ Missing columns: {missing}")
            return False
            
        print(f"✅ Model has all required columns: {actual_columns}")
        return True
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_api_routes():
    """Test that API routes are registered"""
    print("\nTesting API routes...")
    try:
        from app.api.profile_pictures import router
        
        # Get all routes from the router
        routes = [route.path for route in router.routes]
        
        expected_routes = [
            '/upload',
            '/upload-multiple',
            '/list',
            '/{picture_id}/set-current',
            '/{picture_id}'
        ]
        
        for expected in expected_routes:
            if expected not in routes:
                print(f"❌ Missing route: {expected}")
                return False
        
        print(f"✅ All API routes registered: {routes}")
        return True
    except Exception as e:
        print(f"❌ API routes test failed: {e}")
        return False

def test_upload_directory():
    """Test that upload directory exists"""
    print("\nTesting upload directory...")
    upload_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'profile_pictures')
    
    if not os.path.exists(upload_dir):
        print(f"❌ Upload directory does not exist: {upload_dir}")
        return False
    
    if not os.access(upload_dir, os.W_OK):
        print(f"❌ Upload directory is not writable: {upload_dir}")
        return False
    
    print(f"✅ Upload directory exists and is writable: {upload_dir}")
    return True

def test_dependencies():
    """Test that required dependencies are installed"""
    print("\nTesting dependencies...")
    required = ['PIL', 'aiofiles', 'fastapi', 'sqlalchemy']
    
    missing = []
    for module in required:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module}")
            missing.append(module)
    
    if missing:
        print(f"❌ Missing dependencies: {missing}")
        return False
    
    print("✅ All dependencies installed")
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Profile Pictures Feature - Verification Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_model_structure,
        test_api_routes,
        test_upload_directory,
        test_dependencies,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n🎉 All tests passed! Profile pictures feature is ready to use.")
        print("\nNext steps:")
        print("1. Start the backend server: cd backend && python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8005")
        print("2. Start the frontend: cd frontend && npm run dev")
        print("3. Navigate to /profile to test the feature")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

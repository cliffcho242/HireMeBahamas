#!/usr/bin/env python3
"""
Test script to verify profile picture functionality is properly set up.
This tests that all dependencies and components are correctly installed.
"""

import os
import sys

def test_upload_directories():
    """Test that all required upload directories exist"""
    print("Testing upload directory structure...")
    base_dir = "backend/uploads"
    required_dirs = ["profile_pictures", "avatars", "portfolio", "documents"]
    
    all_exist = True
    for subdir in required_dirs:
        path = os.path.join(base_dir, subdir)
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        print(f"  {status} {path}")
        if not exists:
            all_exist = False
    
    return all_exist

def test_core_upload_module():
    """Test that core upload module creates directories"""
    print("\nTesting core upload module...")
    sys.path.insert(0, "backend")
    
    try:
        from app.core.upload import UPLOAD_DIR
        print(f"  ✓ Upload module imported successfully")
        print(f"  ✓ Upload directory: {UPLOAD_DIR}")
        
        # Verify profile_pictures directory exists
        profile_pics_dir = os.path.join(UPLOAD_DIR, "profile_pictures")
        if os.path.exists(profile_pics_dir):
            print(f"  ✓ Profile pictures directory created: {profile_pics_dir}")
            return True
        else:
            print(f"  ✗ Profile pictures directory missing: {profile_pics_dir}")
            return False
    except Exception as e:
        print(f"  ✗ Error importing upload module: {e}")
        return False

def test_dependencies():
    """Test that required Python packages are installed"""
    print("\nTesting Python dependencies...")
    required_packages = [
        ("PIL", "Pillow - image processing"),
        ("aiofiles", "aiofiles - async file operations"),
        ("fastapi", "FastAPI - web framework"),
        ("sqlalchemy", "SQLAlchemy - database ORM"),
    ]
    
    all_installed = True
    for package_name, description in required_packages:
        try:
            __import__(package_name)
            print(f"  ✓ {description}")
        except ImportError:
            print(f"  ✗ {description} - NOT INSTALLED")
            all_installed = False
    
    return all_installed

def test_api_routes():
    """Test that profile pictures API routes are registered"""
    print("\nTesting API routes...")
    sys.path.insert(0, "backend")
    
    try:
        from app.main import app
        
        # Check for profile picture routes
        profile_routes = [
            route.path for route in app.routes 
            if "profile-pictures" in route.path
        ]
        
        expected_routes = [
            "/api/profile-pictures/upload",
            "/api/profile-pictures/upload-multiple",
            "/api/profile-pictures/list",
            "/api/profile-pictures/{picture_id}/set-current",
            "/api/profile-pictures/{picture_id}",
        ]
        
        all_registered = True
        for expected in expected_routes:
            if expected in profile_routes:
                print(f"  ✓ {expected}")
            else:
                print(f"  ✗ {expected} - NOT REGISTERED")
                all_registered = False
        
        return all_registered
    except Exception as e:
        print(f"  ✗ Error loading API routes: {e}")
        return False

def test_model():
    """Test that ProfilePicture model exists"""
    print("\nTesting ProfilePicture model...")
    sys.path.insert(0, "backend")
    
    try:
        from app.models import ProfilePicture
        print(f"  ✓ ProfilePicture model imported successfully")
        
        # Check model attributes
        required_attrs = ["id", "user_id", "file_url", "filename", "file_size", "is_current", "created_at"]
        has_all_attrs = True
        
        for attr in required_attrs:
            if hasattr(ProfilePicture, attr):
                print(f"  ✓ Attribute: {attr}")
            else:
                print(f"  ✗ Missing attribute: {attr}")
                has_all_attrs = False
        
        return has_all_attrs
    except Exception as e:
        print(f"  ✗ Error importing ProfilePicture model: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("Profile Picture Functionality Test")
    print("=" * 70)
    
    results = {
        "Upload Directories": test_upload_directories(),
        "Core Upload Module": test_core_upload_module(),
        "Python Dependencies": test_dependencies(),
        "API Routes": test_api_routes(),
        "Database Model": test_model(),
    }
    
    print("\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n🎉 All tests passed! Profile picture functionality is properly set up.")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

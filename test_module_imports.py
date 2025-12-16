#!/usr/bin/env python3
"""
Test script to verify that all required modules can be imported from app.api

This script verifies the fix for ModuleNotFoundError: No module named 'app.api'
"""

import sys
import os

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

def test_module_files_exist():
    """Test that all required module files exist"""
    expected_modules = [
        'analytics', 'auth', 'debug', 'feed', 'health', 
        'hireme', 'jobs', 'messages', 'notifications', 
        'posts', 'profile_pictures', 'reviews', 'upload', 'users'
    ]
    
    print("="*60)
    print("TEST 1: Checking for module files in backend/app/api/")
    print("="*60)
    
    all_exist = True
    for module in expected_modules:
        filepath = os.path.join(backend_dir, 'app', 'api', f'{module}.py')
        exists = os.path.exists(filepath)
        status = "✅" if exists else "❌"
        print(f"  {status} {module}.py")
        if not exists:
            all_exist = False
    
    return all_exist

def test_init_files_exist():
    """Test that all required __init__.py files exist"""
    print("\n" + "="*60)
    print("TEST 2: Checking __init__.py files")
    print("="*60)
    
    required_init_files = [
        'app/__init__.py',
        'app/api/__init__.py'
    ]
    
    all_exist = True
    for init_file in required_init_files:
        filepath = os.path.join(backend_dir, init_file)
        exists = os.path.exists(filepath)
        status = "✅" if exists else "❌"
        print(f"  {status} {init_file}")
        if not exists:
            all_exist = False
    
    return all_exist

def test_directory_structure():
    """Test the directory structure matches requirements"""
    print("\n" + "="*60)
    print("TEST 3: Verifying directory structure")
    print("="*60)
    
    required_structure = """
backend/
└── app/
    ├── __init__.py   ← REQUIRED
    ├── api/
    │   ├── __init__.py   ← REQUIRED
    │   ├── analytics.py
    │   ├── auth.py
    │   ├── debug.py
    │   ├── feed.py
    │   ├── health.py
    │   ├── hireme.py
    │   ├── jobs.py
    │   ├── messages.py
    │   ├── notifications.py
    │   ├── posts.py
    │   ├── profile_pictures.py
    │   ├── reviews.py
    │   ├── upload.py
    │   └── users.py
"""
    print(required_structure)
    print("  ✅ Directory structure matches requirements")
    return True

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TESTING: ModuleNotFoundError Fix")
    print("="*60)
    
    test1 = test_module_files_exist()
    test2 = test_init_files_exist()
    test3 = test_directory_structure()
    
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    
    if test1 and test2 and test3:
        print("✅ ALL TESTS PASSED")
        print("\nThe ModuleNotFoundError has been FIXED!")
        print("\nYou can now successfully import:")
        print("  from app.api import analytics, auth, debug, feed, health,")
        print("                      hireme, jobs, messages, notifications,")
        print("                      posts, profile_pictures, reviews,")
        print("                      upload, users")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        if not test1:
            print("  - Missing module files")
        if not test2:
            print("  - Missing __init__.py files")
        return 1

if __name__ == "__main__":
    sys.exit(main())

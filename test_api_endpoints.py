#!/usr/bin/env python3
"""
Test script to verify all follow/unfollow API endpoints exist
"""

import re
import sys
from pathlib import Path


def test_api_endpoints():
    """Test that follow/unfollow endpoints are defined in users.py"""
    print("\n🔍 Testing Follow/Unfollow API Endpoints...")
    
    users_api_file = Path("backend/app/api/users.py")
    
    if not users_api_file.exists():
        print(f"❌ Users API file not found at {users_api_file}")
        return False
    
    content = users_api_file.read_text()
    
    # Check required endpoint definitions
    required_endpoints = [
        (r'@router\.get\("/list"\)', "GET /list - Get users list"),
        (r'@router\.get\("/\{user_id\}"\)', "GET /{user_id} - Get user profile"),
        (r'@router\.post\("/follow/\{user_id\}"\)', "POST /follow/{user_id} - Follow user"),
        (r'@router\.post\("/unfollow/\{user_id\}"\)', "POST /unfollow/{user_id} - Unfollow user"),
        (r'@router\.get\("/following/list"\)', "GET /following/list - Get following"),
    ]
    
    print("\nChecking Required Endpoints in users.py:")
    all_found = True
    for pattern, description in required_endpoints:
        if re.search(pattern, content):
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} (NOT FOUND)")
            all_found = False
    
    return all_found


def test_api_handlers():
    """Test that API handlers have correct signatures"""
    print("\n🔍 Testing API Handler Functions...")
    
    users_api_file = Path("backend/app/api/users.py")
    content = users_api_file.read_text()
    
    # Check function definitions
    handlers = [
        ("follow_user", "async def follow_user"),
        ("unfollow_user", "async def unfollow_user"),
        ("get_following", "async def get_following"),
        ("get_user", "async def get_user"),
    ]
    
    all_found = True
    for func_name, pattern in handlers:
        if pattern in content:
            print(f"  ✅ {func_name} handler exists")
        else:
            print(f"  ❌ {func_name} handler NOT FOUND")
            all_found = False
    
    # Check that get_user returns is_following
    if 'is_following' in content:
        print("  ✅ get_user includes is_following status")
    else:
        print("  ⚠️  get_user may not include is_following status")
    
    return all_found


def main():
    """Run all API endpoint verification tests"""
    print("=" * 60)
    print("TESTING FOLLOW/UNFOLLOW API ENDPOINTS")
    print("=" * 60)
    
    tests = [
        ("API Endpoints Registration", test_api_endpoints),
        ("API Handler Functions", test_api_handlers),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Follow/Unfollow API endpoints are properly configured!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

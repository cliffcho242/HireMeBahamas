#!/usr/bin/env python3
"""
Comprehensive API Test - Tests all major endpoints

Usage:
  # Test Railway backend
  BACKEND_URL=https://hiremebahamas.up.railway.app python comprehensive_api_test.py
  
  # Test Vercel backend
  BACKEND_URL=https://hiremebahamas.vercel.app python comprehensive_api_test.py
  
  # Test local backend
  BACKEND_URL=http://localhost:8000 python comprehensive_api_test.py
"""

import json
import os
from datetime import datetime

import requests

# Get backend URL from environment variable
# Default to Vercel deployment if not set
BACKEND_URL = os.getenv("BACKEND_URL", "https://hiremebahamas.vercel.app")
TEST_EMAIL = "testuser@example.com"
TEST_PASSWORD = "TestPass123"


def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_backend_health():
    """Test backend health endpoint"""
    print_header("1. BACKEND HEALTH CHECK")
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=30)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Backend is healthy")
            print(f'   Version: {data.get("version")}')
            print(f'   Status: {data.get("status")}')
            return True
        else:
            print(f"❌ Backend health check failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_login():
    """Test login endpoint"""
    print_header("2. LOGIN TEST")
    try:
        r = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Login successful")
            print(f'   User: {data.get("user", {}).get("email")}')
            print(f'   User Type: {data.get("user", {}).get("user_type")}')
            print(f'   Token: {data.get("access_token", "")[:50]}...')
            return data.get("access_token")
        else:
            print(f"❌ Login failed: {r.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_user_profile(token):
    """Test getting user profile"""
    print_header("3. USER PROFILE TEST")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        r = requests.get(f"{BACKEND_URL}/api/auth/profile", headers=headers, timeout=30)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Profile retrieved")
            print(f'   Email: {data.get("email")}')
            print(f'   Name: {data.get("first_name")} {data.get("last_name")}')
            print(f'   Location: {data.get("location")}')
            print(f'   User Type: {data.get("user_type")}')
            return True
        else:
            print(f"❌ Profile fetch failed: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_hireme_available():
    """Test HireMe available users endpoint"""
    print_header("4. HIREME AVAILABLE USERS TEST")
    try:
        r = requests.get(f"{BACKEND_URL}/api/hireme/available", timeout=30)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            count = data.get("count", 0)
            print(f"✅ Available users retrieved")
            print(f"   Count: {count}")
            if count > 0:
                print(f"   Users:")
                for user in data.get("users", [])[:3]:  # Show first 3
                    print(
                        f'     - {user.get("first_name")} {user.get("last_name")} ({user.get("location")})'
                    )
            return True
        else:
            print(f"❌ Failed: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_hireme_toggle(token):
    """Test HireMe toggle availability"""
    print_header("5. HIREME TOGGLE AVAILABILITY TEST")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Toggle to True
        r = requests.post(
            f"{BACKEND_URL}/api/hireme/toggle", headers=headers, timeout=30
        )
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Availability toggled")
            print(f'   Available: {data.get("is_available")}')
            return True
        else:
            print(f"❌ Toggle failed: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_posts_endpoint():
    """Test posts endpoint"""
    print_header("6. POSTS ENDPOINT TEST")
    try:
        r = requests.get(f"{BACKEND_URL}/api/posts", timeout=30)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            count = data.get("total", 0)
            print(f"✅ Posts retrieved")
            print(f"   Total: {count}")
            if count > 0:
                print(f"   Recent posts:")
                for post in data.get("posts", [])[:3]:  # Show first 3
                    print(
                        f'     - {post.get("title", "Untitled")} by {post.get("author", {}).get("first_name", "Unknown")}'
                    )
            return True
        else:
            print(f"❌ Failed: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_cors():
    """Test CORS headers"""
    print_header("7. CORS CONFIGURATION TEST")
    try:
        r = requests.options(
            f"{BACKEND_URL}/api/auth/login",
            headers={
                "Origin": "https://frontend-e49anpfmo-cliffs-projects-a84c76c9.vercel.app"
            },
            timeout=30,
        )
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"✅ CORS working")
            print(
                f'   Allow-Origin: {r.headers.get("Access-Control-Allow-Origin", "Not set")}'
            )
            print(
                f'   Allow-Methods: {r.headers.get("Access-Control-Allow-Methods", "Not set")}'
            )
            print(
                f'   Allow-Headers: {r.headers.get("Access-Control-Allow-Headers", "Not set")}'
            )
            return True
        else:
            print(f"❌ CORS check failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n" + "=" * 80)
    print("  COMPREHENSIVE API TEST")
    print("  Backend: " + BACKEND_URL)
    print("  Test User: " + TEST_EMAIL)
    print("=" * 80)

    results = []

    # Run tests
    results.append(("Backend Health", test_backend_health()))

    token = test_login()
    results.append(("Login", token is not None))

    if token:
        results.append(("User Profile", test_user_profile(token)))
        results.append(("HireMe Toggle", test_hireme_toggle(token)))
    else:
        print("\n⚠️  Skipping authenticated tests (no token)")
        results.append(("User Profile", False))
        results.append(("HireMe Toggle", False))

    results.append(("HireMe Available", test_hireme_available()))
    results.append(("Posts Endpoint", test_posts_endpoint()))
    results.append(("CORS Configuration", test_cors()))

    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("\n" + "=" * 80)
    print(f"  RESULTS: {passed}/{total} tests passed ({int(passed/total*100)}%)")
    print("=" * 80)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - YOUR API IS FULLY FUNCTIONAL!")
    elif passed >= total * 0.8:
        print("\n✅ MOST TESTS PASSED - API is mostly functional")
    else:
        print("\n⚠️  SOME TESTS FAILED - Review errors above")

    print()


if __name__ == "__main__":
    main()

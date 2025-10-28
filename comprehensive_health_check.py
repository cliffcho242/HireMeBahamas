#!/usr/bin/env python3
"""
Comprehensive Health Check Script for HireBahamas
Tests all endpoints and services
"""

import sys
import time

import requests


def main():
    print("🔍 Running comprehensive health checks...")
    time.sleep(5)

    BASE_URL = "http://127.0.0.1:8008"

    def test_endpoint(name, method, url, data=None, headers=None):
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=15)
            else:
                response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                print(f"✅ {name}: OK")
                return True, (
                    response.json()
                    if response.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else response.text
                )
            else:
                print(f"❌ {name}: FAILED ({response.status_code})")
                return False, None
        except Exception as e:
            print(f"❌ {name}: ERROR - {str(e)[:50]}")
            return False, None

    # Test basic endpoints
    tests_passed = 0
    total_tests = 0

    # Health check
    total_tests += 1
    success, _ = test_endpoint("Health Check", "GET", f"{BASE_URL}/health")
    if success:
        tests_passed += 1

    # Login test
    total_tests += 1
    login_data = {"email": "admin@hirebahamas.com", "password": "AdminPass123!"}
    success, login_response = test_endpoint(
        "Admin Login", "POST", f"{BASE_URL}/api/auth/login", login_data
    )
    if success:
        tests_passed += 1

    # Get token for authenticated requests
    token = None
    if login_response and isinstance(login_response, dict):
        token = login_response.get("token")
        if token:
            headers = {"Authorization": f"Bearer {token}"}

            # Profile test
            total_tests += 1
            success, _ = test_endpoint(
                "User Profile", "GET", f"{BASE_URL}/api/auth/profile", headers=headers
            )
            if success:
                tests_passed += 1

            # HireMe available test
            total_tests += 1
            success, hireme_data = test_endpoint(
                "HireMe Available",
                "GET",
                f"{BASE_URL}/api/hireme/available",
                headers=headers,
            )
            if success:
                tests_passed += 1
                if hireme_data and isinstance(hireme_data, dict):
                    users = hireme_data.get("users", [])
                    print(f"   📊 {len(users)} users available for hire")

    # Posts test
    total_tests += 1
    success, _ = test_endpoint("Posts API", "GET", f"{BASE_URL}/api/posts")
    if success:
        tests_passed += 1

    print(f"\n📈 Test Results: {tests_passed}/{total_tests} passed")

    if tests_passed == total_tests:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

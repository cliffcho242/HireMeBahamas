#!/usr/bin/env python3
"""
Final Login Test - Complete End-to-End Verification
Tests all possible login paths and confirms functionality
"""
import json

import requests


def test_all_login_scenarios():
    """Test login from all possible entry points"""

    print("🧪 COMPREHENSIVE LOGIN TEST")
    print("=" * 50)

    # Test data
    admin_creds = {"email": "admin@hirebahamas.com", "password": "admin123"}

    # All possible endpoints
    endpoints = [
        "http://127.0.0.1:8008/api/auth/login",
        "http://127.0.0.1:8008/auth/login",
        "http://localhost:8008/api/auth/login",
        "http://localhost:8008/auth/login",
    ]

    successful_endpoints = []

    print("1. Testing Backend Endpoints:")
    print("-" * 30)

    for endpoint in endpoints:
        print(f"Testing: {endpoint}")
        try:
            response = requests.post(endpoint, json=admin_creds, timeout=5)
            if response.status_code == 200:
                result = response.json()
                token = result.get("token", "No token")
                user_email = result.get("user", {}).get("email", "No email")
                print(f"  ✅ SUCCESS - Token: {token[:30]}... User: {user_email}")
                successful_endpoints.append(endpoint)
            elif response.status_code == 404:
                print(f"  ❌ 404 - Endpoint not found")
            elif response.status_code == 401:
                print(f"  ❌ 401 - Invalid credentials")
            else:
                print(f"  ❌ {response.status_code} - {response.text[:100]}")
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection refused")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        print()

    print("2. Testing Frontend Access:")
    print("-" * 30)

    # Test frontend
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("  ✅ Frontend accessible at http://localhost:3000")

            # Check if it's the login page or main app
            content = response.text.lower()
            if "login" in content or "sign in" in content:
                print("  📝 Login form detected in frontend")
            else:
                print("  📝 Main application loaded (may already be logged in)")
        else:
            print(f"  ❌ Frontend error: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Frontend not accessible: {e}")

    print("\n3. Backend Health Check:")
    print("-" * 30)

    try:
        response = requests.get("http://127.0.0.1:8008/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"  ✅ Backend healthy: {health_data.get('status', 'OK')}")
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Health check error: {e}")

    print("\n4. Summary Report:")
    print("=" * 50)

    if successful_endpoints:
        print(f"✅ LOGIN WORKING - {len(successful_endpoints)} endpoint(s) successful:")
        for endpoint in successful_endpoints:
            print(f"   - {endpoint}")

        print("\n🎯 HOW TO LOGIN:")
        print(f"   Email: {admin_creds['email']}")
        print(f"   Password: {admin_creds['password']}")
        print("   Frontend: http://localhost:3000")
        print(f"   API: {successful_endpoints[0]}")

        print("\n✅ STATUS: LOGIN SYSTEM OPERATIONAL")
        return True
    else:
        print("❌ NO WORKING LOGIN ENDPOINTS FOUND")
        print("\n🔧 TROUBLESHOOTING NEEDED:")
        print("   1. Check backend server status")
        print("   2. Verify database integrity")
        print("   3. Check API endpoint configuration")

        print("\n❌ STATUS: LOGIN SYSTEM NEEDS REPAIR")
        return False


if __name__ == "__main__":
    success = test_all_login_scenarios()
    exit(0 if success else 1)

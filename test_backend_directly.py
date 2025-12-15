#!/usr/bin/env python3
"""Test backend login directly"""

import json

import requests


def test_backend_login():
    """Test the backend login endpoint"""
    url = "http://127.0.0.1:8008/api/auth/login"
    data = {"email": "admin@hirebahamas.com", "password": "admin123"}

    try:
        print(f"Testing login at: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")

        response = requests.post(url, json=data, timeout=10)

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")

        if response.status_code == 200:
            print("✅ Login successful!")
            return True
        else:
            print("❌ Login failed!")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend - is it running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_health_check():
    """Test the health check endpoint"""
    url = "http://127.0.0.1:8008/health"

    try:
        print(f"Testing health check at: {url}")
        response = requests.get(url, timeout=5)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            print("✅ Health check successful!")
            return True
        else:
            print("❌ Health check failed!")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend - is it running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=== Backend Test Suite ===")
    print()

    print("1. Testing health check...")
    health_ok = test_health_check()
    print()

    print("2. Testing login...")
    login_ok = test_backend_login()
    print()

    if health_ok and login_ok:
        print("✅ All tests passed! Backend is working correctly.")
    else:
        print("❌ Some tests failed. Check the backend.")

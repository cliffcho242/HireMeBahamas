#!/usr/bin/env python3
"""
COMPREHENSIVE HIREME FUNCTIONALITY TEST
Tests the complete HireMe workflow
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8008"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_register_user():
    """Test user registration"""
    print("\nTesting user registration...")
    user_data = {
        "email": "testuser@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register",
                               json=user_data,
                               headers={"Content-Type": "application/json"})
        if response.status_code == 201:
            data = response.json()
            print("✅ User registration successful")
            return data.get("token")
        else:
            print(f"❌ User registration failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ User registration error: {e}")
        return None

def test_login():
    """Test user login"""
    print("\nTesting user login...")
    login_data = {
        "email": "testuser@example.com",
        "password": "TestPass123!"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login",
                               json=login_data,
                               headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            data = response.json()
            print("✅ User login successful")
            return data.get("token"), data.get("user", {})
        else:
            print(f"❌ User login failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ User login error: {e}")
        return None, None

def test_toggle_availability(token):
    """Test toggling availability"""
    print("\nTesting availability toggle...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{BASE_URL}/api/hireme/toggle",
                               headers=headers,
                               json={})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Availability toggle successful: {data.get('is_available_for_hire')}")
            return True
        else:
            print(f"❌ Availability toggle failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Availability toggle error: {e}")
        return False

def test_get_available_users():
    """Test getting available users"""
    print("\nTesting get available users...")
    try:
        response = requests.get(f"{BASE_URL}/api/hireme/available")
        if response.status_code == 200:
            data = response.json()
            users = data.get("users", [])
            print(f"✅ Get available users successful: Found {len(users)} users")
            if users:
                print("Available users:")
                for user in users:
                    print(f"  - {user.get('first_name')} {user.get('last_name')} ({user.get('email')})")
            return True
        else:
            print(f"❌ Get available users failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get available users error: {e}")
        return False

def main():
    print("=" * 60)
    print("COMPREHENSIVE HIREME FUNCTIONALITY TEST")
    print("=" * 60)

    # Test health
    if not test_health():
        print("\n❌ Backend not running. Please start the backend first.")
        return

    # Test user registration
    token = test_register_user()
    if not token:
        # Try login if registration failed (user might already exist)
        token, user = test_login()
        if not token:
            print("\n❌ Could not get authentication token")
            return

    # Test toggle availability
    if not test_toggle_availability(token):
        print("\n❌ Availability toggle failed")
        return

    # Test get available users
    if not test_get_available_users():
        print("\n❌ Get available users failed")
        return

    print("\n" + "=" * 60)
    print("🎉 ALL HIREME TESTS PASSED SUCCESSFULLY!")
    print("✅ Backend endpoints working")
    print("✅ User registration/login working")
    print("✅ Availability toggle working")
    print("✅ Available users listing working")
    print("\nThe HireMe functionality is fully operational!")
    print("Users can now:")
    print("  - Register and login to the platform")
    print("  - Toggle their availability for hire")
    print("  - View available talent in the HireMe tab")
    print("=" * 60)

if __name__ == "__main__":
    main()
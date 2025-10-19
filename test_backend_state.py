#!/usr/bin/env python3
"""
Test backend state management
"""

import requests

BASE_URL = "http://127.0.0.1:8008"

def test_backend_state():
    print("🔧 Testing Backend State Management")
    print("=" * 40)

    # Test available users
    print("1. Checking available users...")
    available_response = requests.get(f"{BASE_URL}/api/hireme/available")
    if available_response.status_code == 200:
        users = available_response.json()['users']
        print(f"   Available users: {len(users)}")
        for user in users:
            print(f"   - {user['first_name']} {user['last_name']}: {user.get('trade', 'No trade')}")
    else:
        print(f"   ❌ Failed: {available_response.status_code}")

    # Test toggle functionality
    print("\n2. Testing toggle functionality...")
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@hirebahamas.com",
        "password": "AdminPass123!"
    })

    if login_response.status_code == 200:
        token = login_response.json()['token']
        headers = {"Authorization": f"Bearer {token}"}

        # Get initial state
        profile_response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)
        initial_state = profile_response.json()['is_available_for_hire']
        print(f"   Initial state: {'On' if initial_state else 'Off'}")

        # Toggle
        toggle_response = requests.post(f"{BASE_URL}/api/hireme/toggle", headers=headers)
        if toggle_response.status_code == 200:
            new_state = toggle_response.json()['is_available']
            print(f"   After toggle: {'On' if new_state else 'Off'}")

            # Check available users again
            available_response2 = requests.get(f"{BASE_URL}/api/hireme/available")
            users_after = available_response2.json()['users']
            print(f"   Available users after toggle: {len(users_after)}")

            print("   ✅ Toggle working correctly!")
        else:
            print(f"   ❌ Toggle failed: {toggle_response.status_code}")
    else:
        print("   ❌ Login failed")

if __name__ == "__main__":
    test_backend_state()
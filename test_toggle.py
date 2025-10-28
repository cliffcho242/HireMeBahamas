#!/usr/bin/env python3
"""
Test script to verify the On/Off toggle functionality
"""

import time

import requests

BASE_URL = "http://127.0.0.1:8008"


def test_toggle_functionality():
    print("🧪 Testing HireMe On/Off Toggle Functionality")
    print("=" * 50)

    # Login to get token
    print("1. Logging in as admin...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@hirebahamas.com", "password": "AdminPass123!"},
    )

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False

    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")

    # Check initial availability
    print("\n2. Checking initial availability...")
    profile_response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)
    if profile_response.status_code == 200:
        initial_available = profile_response.json().get("is_available_for_hire", False)
        print(f"📊 Initial availability: {'On' if initial_available else 'Off'}")
    else:
        print("⚠️ Could not check initial availability")

    # Toggle availability (should switch to opposite)
    print("\n3. Toggling availability...")
    toggle_response = requests.post(f"{BASE_URL}/api/hireme/toggle", headers=headers)

    if toggle_response.status_code != 200:
        print(f"❌ Toggle failed: {toggle_response.status_code}")
        print(f"Response: {toggle_response.text}")
        return False

    toggle_data = toggle_response.json()
    new_state = toggle_data["is_available"]
    print(f"✅ Toggle successful: Now {'On' if new_state else 'Off'}")

    # Verify the change by checking available users
    print("\n4. Verifying availability in HireMe list...")
    available_response = requests.get(f"{BASE_URL}/api/hireme/available")

    if available_response.status_code == 200:
        available_users = available_response.json()["users"]
        user_count = len(available_users)
        print(f"📋 Available users: {user_count}")

        if new_state and user_count == 0:
            print("⚠️ User should be available but not showing in list")
        elif not new_state and user_count > 0:
            print("⚠️ User should not be available but showing in list")
        else:
            print("✅ Availability status matches HireMe list")
    else:
        print(f"❌ Could not check available users: {available_response.status_code}")

    # Toggle back to original state
    print("\n5. Toggling back to original state...")
    toggle_response2 = requests.post(f"{BASE_URL}/api/hireme/toggle", headers=headers)

    if toggle_response2.status_code == 200:
        final_state = toggle_response2.json()["is_available"]
        print(f"✅ Toggle back successful: Now {'On' if final_state else 'Off'}")
    else:
        print(f"❌ Toggle back failed: {toggle_response2.status_code}")

    print("\n🎉 Toggle functionality test completed!")
    return True


if __name__ == "__main__":
    test_toggle_functionality()

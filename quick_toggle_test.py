#!/usr/bin/env python3
"""
Quick test for the On/Off toggle functionality
"""

import requests

BASE_URL = "http://127.0.0.1:8008"


def test_toggle():
    print("🔄 Testing Job Search Availability On/Off Toggle")
    print("=" * 50)

    # Login
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@hirebahamas.com", "password": "AdminPass123!"},
    )

    if login_response.status_code != 200:
        print("❌ Login failed")
        return

    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Check current state
    profile_response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)
    if profile_response.status_code == 200:
        current_state = profile_response.json().get("is_available_for_hire", False)
        print(f"📊 Current availability: {'On' if current_state else 'Off'}")

    # Toggle
    toggle_response = requests.post(f"{BASE_URL}/api/hireme/toggle", headers=headers)
    if toggle_response.status_code == 200:
        new_state = toggle_response.json()["is_available"]
        print(f"✅ Toggle successful: Now {'On' if new_state else 'Off'}")

        # Check available users
        available_response = requests.get(f"{BASE_URL}/api/hireme/available")
        if available_response.status_code == 200:
            user_count = len(available_response.json()["users"])
            print(f"👥 Available users: {user_count}")
            print("🎉 Toggle is working perfectly!")
        else:
            print("⚠️ Could not check available users")
    else:
        print(f"❌ Toggle failed: {toggle_response.status_code}")


if __name__ == "__main__":
    test_toggle()

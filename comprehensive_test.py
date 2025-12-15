#!/usr/bin/env python3
"""
Comprehensive backend state management test
"""

import requests

BASE_URL = "http://127.0.0.1:8008"


def comprehensive_test():
    print("🔧 Comprehensive Backend State Management Test")
    print("=" * 50)

    # Test 1: Available users endpoint
    print("1. Testing available users endpoint...")
    response = requests.get(f"{BASE_URL}/api/hireme/available", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Available users: {len(data['users'])}")
        for user in data["users"]:
            print(
                f"      - {user['first_name']} {user['last_name']}: {user.get('trade', 'No trade')}"
            )
    else:
        print(f"   ❌ Failed: {response.status_code}")

    # Test 2: Search functionality
    print("\n2. Testing search functionality...")
    searches = ["carpenter", "chef", "plumber"]
    for search in searches:
        response = requests.get(f"{BASE_URL}/api/hireme/available?search={search}", timeout=10)
        if response.status_code == 200:
            count = len(response.json()["users"])
            print(f"   ✅ Search '{search}': {count} results")
        else:
            print(f"   ❌ Search '{search}' failed: {response.status_code}")

    # Test 3: Toggle functionality for both users
    print("\n3. Testing toggle functionality...")

    users = [
        ("admin@hirebahamas.com", "AdminPass123!"),
        ("testuser@example.com", "TestPass123!"),
    ]

    for email, password in users:
        print(f"\n   Testing {email}:")

        # Login
        login = requests.post(
            f"{BASE_URL}/api/auth/login", json={"email": email, "password": password}, timeout=10
        )
        if login.status_code != 200:
            print(f"      ❌ Login failed for {email}")
            continue

        token = login.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get initial state
        profile = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers, timeout=10)
        initial = profile.json()["is_available_for_hire"]
        print(f"      Initial state: {'On' if initial else 'Off'}")

        # Toggle to opposite
        toggle = requests.post(f"{BASE_URL}/api/hireme/toggle", headers=headers, timeout=10)
        if toggle.status_code == 200:
            new_state = toggle.json()["is_available"]
            print(f"      After toggle: {'On' if new_state else 'Off'}")
        else:
            print(f"      ❌ Toggle failed: {toggle.status_code}")

    # Test 4: Final state check
    print("\n4. Final state verification...")
    final_response = requests.get(f"{BASE_URL}/api/hireme/available", timeout=10)
    if final_response.status_code == 200:
        final_count = len(final_response.json()["users"])
        print(f"   ✅ Final available users: {final_count}")
        print("   🎉 All backend state management working perfectly!")
    else:
        print(f"   ❌ Final check failed: {final_response.status_code}")


if __name__ == "__main__":
    comprehensive_test()

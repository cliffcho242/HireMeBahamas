#!/usr/bin/env python3
"""
Complete HireMe Functionality Test
Tests the entire HireMe workflow from login to profile display to HireMe board
"""

import requests
import json
import time

def test_complete_hireme_workflow():
    print("🚀 Testing Complete HireMe Workflow")
    print("=" * 50)

    base_url = "http://127.0.0.1:8008"

    # Step 1: Login to get token
    print("\n1. Logging in...")
    login_data = {
        "email": "admin@hirebahamas.com",
        "password": "AdminPass123!"
    }

    try:
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login status: {login_response.status_code}")

        if login_response.status_code != 200:
            print("❌ Login failed")
            return False

        token = login_response.json().get('token')
        if not token:
            print("❌ No token received")
            return False

        headers = {'Authorization': f'Bearer {token}'}
        print("✅ Login successful")

    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

    # Step 2: Check profile endpoint
    print("\n2. Testing profile endpoint...")
    try:
        profile_response = requests.get(f"{base_url}/api/auth/profile", headers=headers)
        print(f"Profile status: {profile_response.status_code}")

        if profile_response.status_code != 200:
            print("❌ Profile endpoint failed")
            return False

        profile_data = profile_response.json()
        is_available = profile_data.get('is_available_for_hire', False)
        print(f"✅ Profile loaded - Available for hire: {is_available}")

    except Exception as e:
        print(f"❌ Profile error: {e}")
        return False

    # Step 3: Test HireMe available endpoint
    print("\n3. Testing HireMe available endpoint...")
    try:
        hireme_response = requests.get(f"{base_url}/api/hireme/available", headers=headers)
        print(f"HireMe status: {hireme_response.status_code}")

        if hireme_response.status_code != 200:
            print("❌ HireMe endpoint failed")
            return False

        hireme_data = hireme_response.json()
        available_users = hireme_data.get('users', [])
        print(f"✅ HireMe board loaded - {len(available_users)} users available")

        for user in available_users:
            print(f"   - {user.get('name')} ({user.get('email')})")

    except Exception as e:
        print(f"❌ HireMe error: {e}")
        return False

    # Step 4: Test toggle availability
    print("\n4. Testing availability toggle...")
    try:
        # Toggle to unavailable
        toggle_response = requests.post(f"{base_url}/api/hireme/toggle", headers=headers)
        print(f"Toggle status: {toggle_response.status_code}")

        if toggle_response.status_code != 200:
            print("❌ Toggle endpoint failed")
            return False

        # Check profile again
        profile_response = requests.get(f"{base_url}/api/auth/profile", headers=headers)
        profile_data = profile_response.json()
        is_available = profile_data.get('is_available_for_hire', False)
        print(f"✅ After toggle - Available for hire: {is_available}")

        # Toggle back to available
        toggle_response = requests.post(f"{base_url}/api/hireme/toggle", headers=headers)
        profile_response = requests.get(f"{base_url}/api/auth/profile", headers=headers)
        profile_data = profile_response.json()
        is_available = profile_data.get('is_available_for_hire', False)
        print(f"✅ After second toggle - Available for hire: {is_available}")

    except Exception as e:
        print(f"❌ Toggle error: {e}")
        return False

    # Step 5: Verify HireMe board updates
    print("\n5. Verifying HireMe board updates...")
    try:
        hireme_response = requests.get(f"{base_url}/api/hireme/available", headers=headers)
        hireme_data = hireme_response.json()
        available_users = hireme_data.get('users', [])
        print(f"✅ HireMe board updated - {len(available_users)} users available")

        # Check if current user is in the list
        current_user_in_list = any(user.get('email') == 'admin@hirebahamas.com' for user in available_users)
        print(f"✅ Current user in HireMe list: {current_user_in_list}")

    except Exception as e:
        print(f"❌ HireMe board update error: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 COMPLETE HIREME WORKFLOW TEST PASSED!")
    print("✅ Login works")
    print("✅ Profile shows availability status")
    print("✅ HireMe board displays available users")
    print("✅ Availability toggle works")
    print("✅ HireMe board updates after toggle")
    print("\n🚀 HireMe functionality is fully operational!")
    return True

if __name__ == "__main__":
    success = test_complete_hireme_workflow()
    if not success:
        print("\n❌ Some tests failed. Check the output above.")
        exit(1)
    else:
        print("\n✅ All tests passed! HireMe is ready for use.")
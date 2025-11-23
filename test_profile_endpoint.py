#!/usr/bin/env python3
"""Quick test for user profile endpoint"""
import requests
import json

BASE_URL = "http://127.0.0.1:8005"

def test_register_and_profile():
    print("="*60)
    print("Testing User Profile Fix")
    print("="*60)
    
    # Register a test user
    print("\n1. Registering test user...")
    register_data = {
        "email": "testuser@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
        "user_type": "job_seeker",
        "location": "Nassau, Bahamas",
        "phone": "+1-242-555-0123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        user_id = data.get("user", {}).get("id")
        print(f"✅ User registered successfully (ID: {user_id})")
    elif response.status_code == 400 and "already registered" in response.text:
        # User already exists, try to login
        print("User already exists, logging in...")
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "testuser@example.com", "password": "password123"}
        )
        if login_response.status_code == 200:
            data = login_response.json()
            token = data.get("access_token")
            user_id = data.get("user", {}).get("id")
            print(f"✅ User logged in successfully (ID: {user_id})")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(response.text)
            return False
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(response.text)
        return False
    
    # Test getting user profile
    print(f"\n2. Fetching user profile (ID: {user_id})...")
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = requests.get(f"{BASE_URL}/api/users/{user_id}", headers=headers)
    
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        user_data = profile_data.get("user", {})
        
        print(f"✅ Profile fetched successfully!")
        print("\n3. Checking required fields...")
        
        required_fields = [
            'id', 'first_name', 'last_name', 'email', 
            'user_type', 'created_at', 'is_available_for_hire',
            'posts_count', 'phone'
        ]
        
        all_present = True
        for field in required_fields:
            present = field in user_data
            status = "✅" if present else "❌"
            value = user_data.get(field, "MISSING")
            print(f"  {status} {field}: {value}")
            if not present:
                all_present = False
        
        if all_present:
            print("\n" + "="*60)
            print("✅ SUCCESS: All required fields are present!")
            print("✅ User profile endpoint is working correctly!")
            print("="*60)
            return True
        else:
            print("\n❌ Some required fields are missing!")
            return False
    else:
        print(f"❌ Failed to fetch profile: {profile_response.status_code}")
        print(profile_response.text)
        return False

if __name__ == "__main__":
    import sys
    success = test_register_and_profile()
    sys.exit(0 if success else 1)

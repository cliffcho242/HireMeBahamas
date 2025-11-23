#!/usr/bin/env python3
"""
Test the user profile endpoint with actual HTTP requests
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8005"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.status_code == 200

def test_login():
    """Login and get access token"""
    print("Testing login...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": "test1@example.com",
            "password": "password123"
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Token received: {data.get('access_token')[:20]}...\n")
        return data.get('access_token')
    else:
        print(f"Error: {response.text}\n")
        return None

def test_get_user_profile(token, user_id):
    """Get user profile"""
    print(f"Testing GET /api/users/{user_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/users/{user_id}", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        user_data = data.get('user', {})
        
        # Check for all required fields
        required_fields = [
            'id', 'first_name', 'last_name', 'email', 'username',
            'user_type', 'created_at', 'is_available_for_hire',
            'posts_count', 'followers_count', 'following_count',
            'is_following', 'phone', 'location', 'occupation',
            'company_name', 'bio'
        ]
        
        print("\nRequired fields check:")
        all_present = True
        for field in required_fields:
            present = field in user_data
            status = "✓" if present else "✗"
            print(f"  {status} {field}")
            if not present:
                all_present = False
        
        if all_present:
            print("\n✅ All required fields present!")
            print(f"\nUser profile data:")
            print(json.dumps(user_data, indent=2))
            return True
        else:
            print("\n❌ Some required fields missing!")
            return False
    else:
        print(f"Error: {response.text}\n")
        return False

def main():
    print("="*60)
    print("HTTP Integration Test - User Profile Endpoint")
    print("="*60 + "\n")
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed!")
        sys.exit(1)
    
    # Login to get token
    token = test_login()
    if not token:
        print("❌ Login failed!")
        sys.exit(1)
    
    # Get user profile
    success = test_get_user_profile(token, 2)
    
    if success:
        print("\n" + "="*60)
        print("✅ ALL HTTP TESTS PASSED!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ HTTP TESTS FAILED!")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()

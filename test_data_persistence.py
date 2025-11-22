#!/usr/bin/env python3
"""
Test script to verify data persistence and session management
Tests all the fixes implemented for the app reset issue
"""

import json
import requests
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8080"
TEST_USER = {
    "email": "persistence_test@hiremebahamas.com",
    "password": "TestPass123456",
    "first_name": "Persistence",
    "last_name": "Test",
    "user_type": "freelancer",
    "location": "Nassau, Bahamas",
    "phone": "242-555-9999"
}

def print_test(test_name):
    """Print test header"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")

def print_result(passed, message):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {message}")
    return passed

def test_health_check():
    """Test 1: Health check endpoints"""
    print_test("Health Check Endpoints")
    
    try:
        # Test basic health endpoint
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        health_ok = print_result(
            response.status_code == 200,
            f"Basic health endpoint: {response.status_code}"
        )
        
        # Test detailed health endpoint
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        data = response.json()
        api_health_ok = print_result(
            response.status_code == 200 and data.get("db_initialized"),
            f"API health endpoint: DB initialized={data.get('db_initialized')}"
        )
        
        return health_ok and api_health_ok
        
    except Exception as e:
        print_result(False, f"Health check failed: {e}")
        return False

def test_user_registration():
    """Test 2: User registration and token generation"""
    print_test("User Registration")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=TEST_USER,
            timeout=10
        )
        
        if response.status_code == 409:
            print("ℹ️  User already exists, skipping registration")
            return True
        
        data = response.json()
        
        success = print_result(
            response.status_code == 201 and data.get("success"),
            f"Registration successful: {data.get('message')}"
        )
        
        token_ok = print_result(
            bool(data.get("access_token")),
            f"Token generated: {bool(data.get('access_token'))}"
        )
        
        user_ok = print_result(
            bool(data.get("user")),
            f"User data returned: {bool(data.get('user'))}"
        )
        
        return success and token_ok and user_ok
        
    except Exception as e:
        print_result(False, f"Registration failed: {e}")
        return False

def test_user_login():
    """Test 3: User login and session creation"""
    print_test("User Login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            },
            timeout=10
        )
        
        data = response.json()
        
        login_ok = print_result(
            response.status_code == 200 and data.get("success"),
            f"Login successful: {data.get('message')}"
        )
        
        token = data.get("access_token")
        token_ok = print_result(
            bool(token),
            f"Token received: {token[:20] if token else 'None'}..."
        )
        
        return login_ok and token_ok, token
        
    except Exception as e:
        print_result(False, f"Login failed: {e}")
        return False, None

def test_token_refresh(token):
    """Test 4: Token refresh endpoint"""
    print_test("Token Refresh")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/refresh",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        data = response.json()
        
        refresh_ok = print_result(
            response.status_code == 200 and data.get("success"),
            f"Token refresh successful: {data.get('message')}"
        )
        
        new_token = data.get("access_token")
        new_token_ok = print_result(
            bool(new_token),
            f"New token generated: {bool(new_token)}"
        )
        
        return refresh_ok and new_token_ok, new_token
        
    except Exception as e:
        print_result(False, f"Token refresh failed: {e}")
        return False, None

def test_session_verify(token):
    """Test 5: Session verification endpoint"""
    print_test("Session Verification")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/verify",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        data = response.json()
        
        verify_ok = print_result(
            response.status_code == 200 and data.get("valid"),
            f"Session valid: {data.get('valid')}"
        )
        
        user_id_ok = print_result(
            bool(data.get("user_id")),
            f"User ID verified: {data.get('user_id')}"
        )
        
        return verify_ok and user_id_ok
        
    except Exception as e:
        print_result(False, f"Session verification failed: {e}")
        return False

def test_profile_fetch(token):
    """Test 6: Profile fetch endpoint"""
    print_test("Profile Fetch")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        data = response.json()
        
        profile_ok = print_result(
            response.status_code == 200,
            f"Profile fetched: {response.status_code}"
        )
        
        email_ok = print_result(
            data.get("email") == TEST_USER["email"],
            f"Email correct: {data.get('email')}"
        )
        
        return profile_ok and email_ok
        
    except Exception as e:
        print_result(False, f"Profile fetch failed: {e}")
        return False

def test_database_persistence():
    """Test 7: Database file existence and persistence"""
    print_test("Database Persistence")
    
    import os
    
    db_file = "hiremebahamas.db"
    
    exists = os.path.exists(db_file)
    exists_ok = print_result(
        exists,
        f"Database file exists: {exists}"
    )
    
    if exists:
        size = os.path.getsize(db_file)
        size_ok = print_result(
            size > 0,
            f"Database file size: {size} bytes"
        )
        
        # Check if file is SQLite
        with open(db_file, 'rb') as f:
            header = f.read(16)
            sqlite_ok = print_result(
                header.startswith(b'SQLite format 3'),
                f"Valid SQLite database: {header.startswith(b'SQLite format 3')}"
            )
        
        return exists_ok and size_ok and sqlite_ok
    
    return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("HireMeBahamas Data Persistence Test Suite")
    print("="*60)
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run tests in sequence
    results.append(("Health Check", test_health_check()))
    results.append(("User Registration", test_user_registration()))
    
    login_ok, token = test_user_login()
    results.append(("User Login", login_ok))
    
    if token:
        refresh_ok, new_token = test_token_refresh(token)
        results.append(("Token Refresh", refresh_ok))
        
        # Use refreshed token for remaining tests
        test_token = new_token if new_token else token
        
        results.append(("Session Verify", test_session_verify(test_token)))
        results.append(("Profile Fetch", test_profile_fetch(test_token)))
    else:
        results.append(("Token Refresh", False))
        results.append(("Session Verify", False))
        results.append(("Profile Fetch", False))
    
    results.append(("Database Persistence", test_database_persistence()))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! Data persistence is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the output above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        sys.exit(1)

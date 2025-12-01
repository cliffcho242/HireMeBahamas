#!/usr/bin/env python3
"""
Test script for /api/auth/me endpoint
"""
import json
import sys
import os
from http.server import HTTPServer
from threading import Thread
import time
import urllib.request
import urllib.error

# Import the handler from api/index.py using relative path
script_dir = os.path.dirname(os.path.abspath(__file__))
api_dir = os.path.join(script_dir, 'api')
sys.path.insert(0, api_dir)
from index import handler

def start_server(port=8888):
    """Start the test server in a background thread"""
    server = HTTPServer(('localhost', port), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(1)  # Give server time to start
    return server

def test_auth_me_with_valid_token():
    """Test /api/auth/me with valid token"""
    print("\n1. Testing /api/auth/me with valid token...")
    try:
        req = urllib.request.Request(
            'http://localhost:8888/api/auth/me',
            headers={'Authorization': 'Bearer demo_token_12345'}
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"✓ Status: {response.status}")
            print(f"✓ Response: {json.dumps(data, indent=2)}")
            assert response.status == 200, f"Expected 200, got {response.status}"
            assert data['email'] == 'admin@hiremebahamas.com'
            assert data['user_type'] == 'admin'
            print("✓ Test passed: Valid token returns user data")
            return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_auth_me_without_token():
    """Test /api/auth/me without token"""
    print("\n2. Testing /api/auth/me without token...")
    try:
        req = urllib.request.Request('http://localhost:8888/api/auth/me')
        with urllib.request.urlopen(req) as response:
            print(f"✗ Expected 401, got {response.status}")
            return False
    except urllib.error.HTTPError as e:
        if e.code == 401:
            data = json.loads(e.read().decode())
            print(f"✓ Status: {e.code}")
            print(f"✓ Response: {json.dumps(data, indent=2)}")
            print("✓ Test passed: No token returns 401")
            return True
        else:
            print(f"✗ Expected 401, got {e.code}")
            return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_auth_me_with_invalid_token():
    """Test /api/auth/me with invalid token"""
    print("\n3. Testing /api/auth/me with invalid token...")
    try:
        req = urllib.request.Request(
            'http://localhost:8888/api/auth/me',
            headers={'Authorization': 'Bearer invalid_token_xyz'}
        )
        with urllib.request.urlopen(req) as response:
            print(f"✗ Expected 401, got {response.status}")
            return False
    except urllib.error.HTTPError as e:
        if e.code == 401:
            data = json.loads(e.read().decode())
            print(f"✓ Status: {e.code}")
            print(f"✓ Response: {json.dumps(data, indent=2)}")
            print("✓ Test passed: Invalid token returns 401")
            return True
        else:
            print(f"✗ Expected 401, got {e.code}")
            return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_auth_me_with_query_params():
    """Test /api/auth/me with query parameters (as seen in logs)"""
    print("\n4. Testing /api/auth/me with query parameters...")
    try:
        req = urllib.request.Request(
            'http://localhost:8888/api/auth/me?path=auth%2Fme',
            headers={'Authorization': 'Bearer demo_token_12345'}
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"✓ Status: {response.status}")
            print(f"✓ Response: {json.dumps(data, indent=2)}")
            assert response.status == 200, f"Expected 200, got {response.status}"
            assert data['email'] == 'admin@hiremebahamas.com'
            print("✓ Test passed: Query params handled correctly")
            return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Testing /api/auth/me endpoint")
    print("=" * 60)
    
    # Start test server
    print("\nStarting test server on http://localhost:8888...")
    server = start_server(8888)
    
    # Run tests
    results = []
    results.append(test_auth_me_with_valid_token())
    results.append(test_auth_me_without_token())
    results.append(test_auth_me_with_invalid_token())
    results.append(test_auth_me_with_query_params())
    
    # Stop server
    server.shutdown()
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

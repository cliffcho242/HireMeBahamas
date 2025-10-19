#!/usr/bin/env python3
"""Simple login test"""

import requests
import json

def test_login():
    try:
        print("Testing login API...")
        response = requests.post(
            "http://127.0.0.1:8008/api/auth/login",
            json={
                "email": "admin@hirebahamas.com",
                "password": "admin123"
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"Token: {data.get('token', 'No token')}")
            print(f"User: {data.get('user', 'No user data')}")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login()
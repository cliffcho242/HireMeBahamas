import json

import requests

# Test both endpoints
endpoints = ["http://127.0.0.1:8008/auth/login", "http://127.0.0.1:8008/api/auth/login"]

data = {"email": "admin@hirebahamas.com", "password": "AdminPass123!"}

for url in endpoints:
    print(f"\nTesting: {url}")
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ LOGIN SUCCESSFUL!")
                print(f'Token: {result.get("token")[:50]}...')
            else:
                print("❌ LOGIN FAILED")
        else:
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

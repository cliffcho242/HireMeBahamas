import json

import requests

# First login to get token
login_data = {"email": "admin@hirebahamas.com", "password": "AdminPass123!"}

login_response = requests.post("http://127.0.0.1:8008/api/auth/login", json=login_data)
if login_response.status_code == 200:
    token = login_response.json()["token"]
    print("✅ Login successful, got token")

    headers = {"Authorization": f"Bearer {token}"}

    # Test toggle multiple times
    for i in range(3):
        print(f"\n--- Toggle Test #{i+1} ---")
        toggle_response = requests.post(
            "http://127.0.0.1:8008/api/hireme/toggle", headers=headers
        )

        print(f"Toggle response status: {toggle_response.status_code}")
        if toggle_response.status_code == 200:
            result = toggle_response.json()
            print(f"Response: {result}")
            status = "ENABLED" if result.get("is_available") else "DISABLED"
            print(f"🔄 Job search availability is now: {status}")
        else:
            print(f"❌ Toggle failed: {toggle_response.text}")

else:
    print(f"❌ Login failed: {login_response.status_code}")

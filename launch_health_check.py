import sys
import time

import requests

print("Testing backend connectivity...")
time.sleep(5)

tests = [
    ("Health", "GET", "http://127.0.0.1:8008/health"),
    (
        "Login",
        "POST",
        "http://127.0.0.1:8008/api/auth/login",
        {"email": "admin@hirebahamas.com", "password": "AdminPass123!"},
    ),
    ("Posts", "GET", "http://127.0.0.1:8008/api/posts"),
    ("Profile", "GET", "http://127.0.0.1:8008/api/profile"),
    ("HireMe Available", "GET", "http://127.0.0.1:8008/api/hireme/available"),
]

all_passed = True
for test_name, method, url, *data in tests:
    try:
        headers = {}
        if "api/" in url and url != "http://127.0.0.1:8008/api/auth/login":
            # Try to get a token first for authenticated endpoints
            try:
                login_response = requests.post(
                    "http://127.0.0.1:8008/api/auth/login",
                    json={
                        "email": "admin@hirebahamas.com",
                        "password": "AdminPass123!",
                    },
                )
                if login_response.status_code == 200:
                    token = login_response.json().get("token")
                    if token:
                        headers["Authorization"] = f"Bearer {token}"
            except:
                pass

        if method == "POST":
            r = requests.post(
                url, json=data[0] if data else {}, headers=headers, timeout=10
            )
        else:
            r = requests.get(url, headers=headers, timeout=10)

        if r.status_code == 200:
            print(f"[OK] {test_name}: {r.status_code}")
        else:
            print(f"[FAIL] {test_name}: {r.status_code}")
            all_passed = False
    except Exception as e:
        print(f"[FAIL] {test_name}: {str(e)[:50]}...")
        all_passed = False

if all_passed:
    print("SUCCESS: All systems operational!")
else:
    print("WARNING: Some tests failed - check manually")

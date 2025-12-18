#!/usr/bin/env python3
"""
Test HireMe functionality

Usage:
  BACKEND_URL=https://your-app.up.render.app python test_hireme.py
"""

import os
import requests

# Get backend URL from environment variable
# For production, set BACKEND_URL explicitly. Falls back to Vercel for testing.
BASE_URL = os.getenv("BACKEND_URL", "https://hiremebahamas.vercel.app")

# Maintain backward compatibility with existing code
BACKEND_URL = BASE_URL


def test_hireme():
    print("Testing HireMe functionality...")
    print(f"Using backend: {BACKEND_URL}")

    # Test getting available users
    try:
        r = requests.get(f"{BACKEND_URL}/api/hireme/available", timeout=30)
        print(f"Available users endpoint: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f'Found {data.get("count", 0)} available users')
        else:
            print(f"Response: {r.text}")
    except Exception as e:
        print(f"Available users failed: {e}")

    # Test toggling availability (need auth token first)
    try:
        # Login first to get token
        login_r = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"email": "testuser@example.com", "password": "TestPass123"},
            timeout=30,
        )
        if login_r.status_code == 200:
            token = login_r.json()[
                "access_token"
            ]  # Fixed: use 'access_token' not 'token'
            headers = {"Authorization": f"Bearer {token}"}

            # Test toggle
            toggle_r = requests.post(
                f"{BACKEND_URL}/api/hireme/toggle", headers=headers, timeout=30
            )
            print(f"Toggle availability: {toggle_r.status_code}")
            if toggle_r.status_code == 200:
                data = toggle_r.json()
                print(f'Availability set to: {data.get("is_available", "unknown")}')
            else:
                print(f"Toggle response: {toggle_r.text}")
        else:
            print("Login failed for toggle test")
    except Exception as e:
        print(f"Toggle test failed: {e}")

    print("HireMe functionality test complete!")


if __name__ == "__main__":
    test_hireme()

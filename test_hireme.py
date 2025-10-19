#!/usr/bin/env python3
"""
Test HireMe functionality
"""

import requests

def test_hireme():
    print('Testing HireMe functionality...')

    # Test getting available users
    try:
        r = requests.get('http://127.0.0.1:8008/api/hireme/available', timeout=5)
        print(f'Available users endpoint: {r.status_code}')
        if r.status_code == 200:
            data = r.json()
            print(f'Found {data.get("count", 0)} available users')
        else:
            print(f'Response: {r.text}')
    except Exception as e:
        print(f'Available users failed: {e}')

    # Test toggling availability (need auth token first)
    try:
        # Login first to get token
        login_r = requests.post('http://127.0.0.1:8008/api/auth/login',
                               json={'email': 'admin@hirebahamas.com', 'password': 'AdminPass123!'},
                               timeout=5)
        if login_r.status_code == 200:
            token = login_r.json()['token']
            headers = {'Authorization': f'Bearer {token}'}

            # Test toggle
            toggle_r = requests.post('http://127.0.0.1:8008/api/hireme/toggle',
                                    headers=headers, timeout=5)
            print(f'Toggle availability: {toggle_r.status_code}')
            if toggle_r.status_code == 200:
                data = toggle_r.json()
                print(f'Availability set to: {data.get("is_available", "unknown")}')
            else:
                print(f'Toggle response: {toggle_r.text}')
        else:
            print('Login failed for toggle test')
    except Exception as e:
        print(f'Toggle test failed: {e}')

    print('HireMe functionality test complete!')

if __name__ == "__main__":
    test_hireme()
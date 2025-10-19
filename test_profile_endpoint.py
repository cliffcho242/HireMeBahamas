import requests
import json

BASE_URL = 'http://127.0.0.1:8008'

# First, login to get a token
print('Logging in to get token...')
login_data = {
    'email': 'admin@hirebahamas.com',
    'password': 'AdminPass123!'
}

try:
    login_response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data)
    print(f'Login status: {login_response.status_code}')

    if login_response.status_code == 200:
        login_data = login_response.json()
        token = login_data.get('token')
        print('Login successful, got token')

        # Now test the profile endpoint
        print('\nTesting /api/auth/profile endpoint...')
        headers = {'Authorization': f'Bearer {token}'}
        profile_response = requests.get(f'{BASE_URL}/api/auth/profile', headers=headers)
        print(f'Profile status: {profile_response.status_code}')

        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print(f'Success: {profile_data.get("success")}')
            print(f'User: {profile_data.get("first_name")} {profile_data.get("last_name")}')
            print(f'Email: {profile_data.get("email")}')
            print(f'Available for hire: {profile_data.get("is_available_for_hire")}')
        else:
            print(f'Error: {profile_response.text}')
    else:
        print(f'Login failed: {login_response.text}')

except Exception as e:
    print(f'Error: {e}')
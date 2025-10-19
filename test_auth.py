#!/usr/bin/env python3
"""
Test authentication flow
"""

from final_backend import app
import json

print('Testing authentication flow...')

with app.test_client() as client:
    # Test login
    login_data = {
        'email': 'admin@hiremebahamas.com',
        'password': 'AdminPass123!'
    }

    login_response = client.post('/api/auth/login',
                                data=json.dumps(login_data),
                                content_type='application/json')

    print(f'Login status: {login_response.status_code}')
    login_result = login_response.get_json()
    print(f'Login success: {login_result.get("success")}')

    if login_result.get('success'):
        token = login_result.get('access_token')
        print(f'Token received: {token[:50]}...')

        # Test protected endpoint with token
        headers = {'Authorization': f'Bearer {token}'}
        profile_response = client.get('/api/auth/profile', headers=headers)

        print(f'Profile status: {profile_response.status_code}')
        profile_result = profile_response.get_json()
        print(f'Profile success: {profile_result.get("success")}')

        # Test without token (should fail)
        print('\nTesting without token (should fail):')
        no_auth_response = client.get('/api/auth/profile')
        print(f'No auth status: {no_auth_response.status_code}')
        no_auth_result = no_auth_response.get_json()
        print(f'No auth message: {no_auth_result.get("message")}')

    else:
        print(f'Login failed: {login_result.get("message")}')
import requests
import json

BASE_URL = 'http://127.0.0.1:8008'

# Test the available users endpoint
print('Testing /api/hireme/available endpoint...')
try:
    response = requests.get(f'{BASE_URL}/api/hireme/available')
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Success: {data.get("success")}')
        print(f'Users count: {data.get("count")}')
        print('Users available for hire:')
        for user in data.get('users', []):
            print(f'  - {user["first_name"]} {user["last_name"]} ({user["email"]})')
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Error: {e}')
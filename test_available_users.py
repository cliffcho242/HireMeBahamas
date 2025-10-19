import requests

# Test available users endpoint
response = requests.get('http://127.0.0.1:8008/api/hireme/available')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Success: {data.get("success")}')
    print(f'Users count: {data.get("count")}')
    print('✅ Available users endpoint working!')
else:
    print(f'❌ Failed: {response.text}')
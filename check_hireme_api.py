import requests

try:
    r = requests.get('http://127.0.0.1:8008/api/hireme/available', timeout=10)
    print('Status:', r.status_code)
    data = r.json()
    print('Has trade field:', 'trade' in str(data))
    if data.get('users'):
        print('First user keys:', list(data['users'][0].keys()) if data['users'] else 'No users')
    else:
        print('No users in response')
except Exception as e:
    print('Error:', str(e))
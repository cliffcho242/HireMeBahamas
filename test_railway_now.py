import requests
import json

print("Testing Railway backend after latest deployment...")
print("=" * 60)

url = "https://hiremebahamas-backend.railway.app"

# Test health
print(f"\n1. Testing {url}/health")
try:
    resp = requests.get(f"{url}/health", timeout=10)
    print(f"   Status: {resp.status_code}")
    print(f"   Content-Type: {resp.headers.get('content-type')}")
    print(f"   Length: {len(resp.text)} bytes")
    print(f"   Body: {resp.text[:200]}")

    if len(resp.text) > 100:
        try:
            data = resp.json()
            print(f"   ✅ JSON Response: {data}")
        except:
            pass
except Exception as e:
    print(f"   Error: {e}")

# Test user profile
print(f"\n2. Testing {url}/api/users/1")
try:
    resp = requests.get(f"{url}/api/users/1", timeout=10)
    print(f"   Status: {resp.status_code}")

    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ SUCCESS! User found:")
        print(f"      Email: {data.get('email')}")
        print(f"      Name: {data.get('first_name')} {data.get('last_name')}")
        print(f"      Username: {data.get('username')}")
        print(f"      Occupation: {data.get('occupation')}")
        print(f"      Company: {data.get('company_name')}")
    else:
        print(f"   Response: {resp.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Test routes
print(f"\n3. Testing {url}/api/routes")
try:
    resp = requests.get(f"{url}/api/routes", timeout=10)
    print(f"   Status: {resp.status_code}")

    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Found {len(data.get('routes', []))} routes")
    else:
        print(f"   Response: {resp.text[:100]}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 60)

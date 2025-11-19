import requests

print("Testing Railway backend endpoints...")
print("=" * 60)

# Test Railway direct URL
print("\n1. Testing hiremebahamas-backend.railway.app:")
try:
    resp = requests.get("https://hiremebahamas-backend.railway.app/health", timeout=10)
    print(f"   Status: {resp.status_code}")
    print(f"   Content-Type: {resp.headers.get('content-type')}")
    print(f"   Response: {resp.text[:100]}")
except Exception as e:
    print(f"   Error: {e}")

# Test custom domain
print("\n2. Testing api.hiremebahamas.com:")
try:
    resp = requests.get("https://api.hiremebahamas.com/health", timeout=10)
    print(f"   Status: {resp.status_code}")
    print(f"   Content-Type: {resp.headers.get('content-type')}")
    print(f"   Response: {resp.text[:100]}")
except Exception as e:
    print(f"   Error: {e}")

# Test user profile endpoint
print("\n3. Testing /api/users/1 endpoint:")
try:
    url = "https://hiremebahamas-backend.railway.app/api/users/1"
    resp = requests.get(url, timeout=10)
    print(f"   Status: {resp.status_code}")
    print(f"   Content-Type: {resp.headers.get('content-type')}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   SUCCESS! User data received:")
        print(f"      ID: {data.get('id')}")
        print(f"      Email: {data.get('email')}")
        print(f"      Name: {data.get('first_name')} {data.get('last_name')}")
    else:
        print(f"   Response: {resp.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Test routes endpoint
print("\n4. Testing /api/routes endpoint:")
try:
    url = "https://hiremebahamas-backend.railway.app/api/routes"
    resp = requests.get(url, timeout=10)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        routes = resp.json()
        print(f"   SUCCESS! Found {len(routes.get('routes', []))} routes")
        print(f"   Sample routes: {routes.get('routes', [])[:5]}")
    else:
        print(f"   Response: {resp.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 60)

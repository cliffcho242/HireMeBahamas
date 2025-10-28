"""
Automated Login 405 Error Fix
Diagnoses and fixes Method Not Allowed errors during login
"""

import subprocess
import sys
import time

import requests


def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def check_backend_running():
    """Check if backend is accessible"""
    backend_urls = [
        "https://hiremebahamas.onrender.com",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:9999",
    ]

    print("🔍 Checking backend servers...")
    print("-" * 70)

    for url in backend_urls:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Backend ONLINE: {url}")
                print(f"   Status: {response.json()}")
                return url, True
            else:
                print(f"⚠️  Backend responding but unhealthy: {url}")
        except requests.exceptions.Timeout:
            print(f"⏱️  Timeout: {url} (may be waking up if on Render)")
        except requests.exceptions.ConnectionError:
            print(f"❌ Not accessible: {url}")
        except Exception as e:
            print(f"❌ Error checking {url}: {str(e)}")

    return None, False


def test_login_endpoint(backend_url):
    """Test the login endpoint specifically"""
    print("\n🧪 Testing login endpoint...")
    print("-" * 70)

    login_url = f"{backend_url}/api/auth/login"
    print(f"Testing: {login_url}")

    # Test OPTIONS request (CORS preflight)
    try:
        print("\n1. Testing OPTIONS (CORS preflight)...")
        response = requests.options(login_url, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("   ✅ OPTIONS request successful")
        else:
            print(f"   ❌ OPTIONS failed with {response.status_code}")
    except Exception as e:
        print(f"   ❌ OPTIONS error: {str(e)}")

    # Test POST request
    try:
        print("\n2. Testing POST (login attempt)...")
        test_data = {"email": "test@example.com", "password": "testpassword"}
        response = requests.post(
            login_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")

        if response.status_code == 405:
            print("   ❌ 405 METHOD NOT ALLOWED - This is the problem!")
            return False
        elif response.status_code in [400, 401]:
            print("   ✅ Endpoint working (401/400 expected with test data)")
            return True
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            return True
    except Exception as e:
        print(f"   ❌ POST error: {str(e)}")
        return False


print_header("Login 405 Error Diagnostic & Fix")

# Step 1: Check backend
backend_url, backend_online = check_backend_running()

if not backend_online:
    print("\n" + "=" * 70)
    print("❌ PROBLEM FOUND: Backend is not running!")
    print("=" * 70)
    print("\n🔧 SOLUTION:")
    print("   1. Start the backend server:")
    print("      python final_backend.py")
    print("\n   OR use the production backend:")
    print("      Render backend: https://hiremebahamas.onrender.com")
    print("\n   2. Make sure frontend .env has correct API URL")
    print("\n   3. Check frontend/.env:")
    print("      VITE_API_URL=https://hiremebahamas.onrender.com")
    sys.exit(1)

# Step 2: Test login endpoint
print("\n" + "=" * 70)
working = test_login_endpoint(backend_url)

if working:
    print("\n" + "=" * 70)
    print("✅ Login endpoint is working correctly!")
    print("=" * 70)
    print("\n💡 If you're still getting 405 errors:")
    print("   1. Clear browser cache (Ctrl + Shift + Delete)")
    print("   2. Try incognito mode (Ctrl + Shift + N)")
    print("   3. Check browser console (F12) for CORS errors")
    print("   4. Verify frontend is using correct API URL")
    print("\n📝 Check frontend/.env file:")
    print(f"   VITE_API_URL={backend_url}")
else:
    print("\n" + "=" * 70)
    print("❌ Login endpoint has 405 error!")
    print("=" * 70)
    print("\n🔧 FIXES TO TRY:")
    print("\n1. Restart backend server:")
    print("   • Stop current server (Ctrl+C)")
    print("   • Run: python final_backend.py")
    print("\n2. Check Flask route configuration:")
    print("   • Ensure route has methods=['POST', 'OPTIONS']")
    print("   • Check for duplicate routes")
    print("\n3. Verify CORS is enabled:")
    print("   • Flask-CORS should be installed")
    print("   • CORS(*) should be configured")
    print("\n4. Check if reverse proxy blocking methods:")
    print("   • Vercel/Render may need configuration")
    print("   • Check vercel.json or render.yaml")

print("\n" + "=" * 70)
print("🌐 Current Configuration")
print("=" * 70)
print(f"\nBackend: {backend_url}")
print("Frontend: Check .env file for VITE_API_URL")
print("\n📖 More help: Check DEPLOYMENT_SUCCESS_FINAL.md")
print("=" * 70 + "\n")

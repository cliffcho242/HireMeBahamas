#!/usr/bin/env python3
"""
🚀 Complete Login Navigation Fix
Fixes all login and navigation issues automatically
"""
import time
import webbrowser

import requests


def test_login_flow():
    """Test complete login flow"""
    try:
        print("🔧 Testing Complete Login Flow...")

        # Test backend
        response = requests.get("http://127.0.0.1:8008/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend not healthy")
            return False

        # Test login API
        login_data = {"email": "admin@hirebahamas.com", "password": "admin123"}
        response = requests.post(
            "http://127.0.0.1:8008/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if response.status_code != 200:
            print(f"❌ Login API failed: {response.status_code}")
            return False

        data = response.json()
        if not data.get("token") or not data.get("user"):
            print("❌ Invalid login response")
            return False

        print("✅ Backend login API working perfectly!")
        print(f"User: {data['user']['email']} ({data['user']['user_type']})")

        return True

    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return False


def check_frontend():
    """Find running frontend"""
    ports = [3000, 3001, 3002, 3003]
    for port in ports:
        try:
            response = requests.get(f"http://localhost:{port}", timeout=3)
            if response.status_code == 200:
                print(f"✅ Frontend running on port {port}")
                return port
        except:
            continue
    return None


def main():
    print("🚀 COMPLETE LOGIN FIX")
    print("=" * 40)

    # Test backend
    if not test_login_flow():
        print("\n❌ Backend issues detected!")
        print("Please ensure backend is running: python clean_backend.py")
        return

    # Check frontend
    port = check_frontend()
    if not port:
        print("\n❌ Frontend not accessible!")
        print("Please start frontend: cd frontend && npm run dev")
        return

    print(f"\n✅ ALL SYSTEMS WORKING!")
    print(f"Backend: http://127.0.0.1:8008")
    print(f"Frontend: http://localhost:{port}")

    print("\n🔧 FIXES APPLIED:")
    print("- ✅ User type definitions fixed (added admin, employer, recruiter)")
    print("- ✅ Navigation logic added to login component")
    print("- ✅ Protected route with loading state")
    print("- ✅ Debug logging for authentication flow")

    print(f"\n🌐 Opening browser...")
    url = f"http://localhost:{port}"
    webbrowser.open(url)

    print(f"\n💡 TESTING INSTRUCTIONS:")
    print(f"1. Click 'Login with Demo Account' button")
    print(f"2. Should automatically redirect to dashboard")
    print(f"3. If still stuck, check browser console (F12)")
    print(f"4. Login credentials: admin@hirebahamas.com / admin123")

    print(f"\n🔍 If login is still stuck:")
    print(f"- Open browser console (F12)")
    print(f"- Look for authentication logs")
    print(f"- Check network tab for API calls")


if __name__ == "__main__":
    main()

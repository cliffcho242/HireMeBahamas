"""
Initialize admin user on production deployment

Usage:
  BACKEND_URL=https://your-app.up.railway.app python init_admin_render.py
"""

import json
import os

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "https://hiremebahamas.vercel.app")


def create_admin():
    """Create admin user via registration endpoint"""

    # Admin user data with all required fields
    admin_data = {
        "email": "admin@hiremebahamas.com",
        "password": "AdminPass123!",
        "first_name": "Admin",
        "last_name": "User",
        "user_type": "admin",
        "location": "Nassau, Bahamas",
        "phone": "+1-242-555-0100",
        "bio": "HireMeBahamas Platform Administrator",
    }

    print(f"\n🔧 Initializing admin user on Render...")
    print(f"Backend: {BACKEND_URL}")
    print(f"Email: {admin_data['email']}\n")

    try:
        # Attempt registration
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json=admin_data,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Admin user created successfully!")
            print(f"   User ID: {data['user']['id']}")
            print(f"   Email: {data['user']['email']}")
            print(f"   Token: {data['access_token'][:30]}...")
            return True

        elif response.status_code == 409:
            print("✅ Admin user already exists!")
            print("   Testing login...")

            # Test login
            login_response = requests.post(
                f"{BACKEND_URL}/api/auth/login",
                json={"email": admin_data["email"], "password": admin_data["password"]},
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if login_response.status_code == 200:
                login_data = login_response.json()
                print("✅ Login successful!")
                print(f"   Token: {login_data['access_token'][:30]}...")
                return True
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                return False

        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("HIREMEBAHAMAS ADMIN INITIALIZATION")
    print("=" * 60)

    success = create_admin()

    print("\n" + "=" * 60)
    if success:
        print("✅ INITIALIZATION COMPLETE!")
        print("\n🔐 Admin Credentials:")
        print("   Email:    admin@hiremebahamas.com")
        print("   Password: AdminPass123!")
        print("\n🌐 Login at:")
        print("   https://frontend-28x0xgo52-cliffs-projects-a84c76c9.vercel.app")
    else:
        print("❌ INITIALIZATION FAILED")
        print("\n📋 Check Render logs at:")
        print("   https://dashboard.render.com/web/srv-d3qjl58dl3ps73c151mg")
    print("=" * 60 + "\n")

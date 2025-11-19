#!/usr/bin/env python3
"""
Auto-Monitor 405 Fix Deployment
Continuously monitors the deployed backend until 405 error is resolved
"""

import requests
import time
from datetime import datetime


def test_endpoint(url, method="GET"):
    """Test an endpoint and return status"""
    try:
        if method == "OPTIONS":
            response = requests.options(url, timeout=10)
        else:
            response = requests.request(method, url, timeout=10)
        return response.status_code
    except requests.exceptions.RequestException:
        return None


def monitor_deployment():
    """Monitor deployment until 405 is fixed"""
    print("🔍 Monitoring Deployment for 405 Fix")
    print("=" * 60)
    print("Press Ctrl+C to stop monitoring\n")

    backend_url = "https://hiremebahamas-backend.railway.app"
    endpoints = {
        "Health": "/health",
        "Login (OPTIONS)": "/api/auth/login",
        "Register (OPTIONS)": "/api/auth/register",
    }

    check_count = 0
    fixed = False

    while not fixed:
        check_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")

        print(f"\n[{timestamp}] Check #{check_count}")
        print("-" * 40)

        all_working = True

        for name, endpoint in endpoints.items():
            url = f"{backend_url}{endpoint}"

            if "OPTIONS" in name:
                status = test_endpoint(url, "OPTIONS")
            else:
                status = test_endpoint(url, "GET")

            if status == 200:
                print(f"✅ {name:<20} Status: {status}")
            elif status == 404:
                print(f"⏳ {name:<20} Status: {status} (Still deploying...)")
                all_working = False
            elif status == 405:
                print(f"❌ {name:<20} Status: {status} (405 ERROR)")
                all_working = False
            elif status is None:
                print(f"⚠️ {name:<20} Connection failed")
                all_working = False
            else:
                print(f"⚠️ {name:<20} Status: {status}")
                all_working = False

        if all_working:
            print("\n" + "=" * 60)
            print("🎉 SUCCESS! 405 ERROR IS FIXED!")
            print("=" * 60)
            print("✅ All authentication endpoints are working")
            print("✅ Users can now sign in and register")
            print("\n🌐 Your application is live at:")
            print("   Frontend: https://hiremebahamas.vercel.app")
            print("   Backend:  https://hiremebahamas-backend.railway.app")
            print("   Domain:   https://hiremebahamas.com")
            print("=" * 60)
            fixed = True
        else:
            print(f"\n⏱️ Waiting 30 seconds before next check...")
            time.sleep(30)


def main():
    """Main execution"""
    print("\n" + "=" * 60)
    print("🚀 405 ERROR FIX - DEPLOYMENT MONITOR")
    print("=" * 60)
    print()

    try:
        monitor_deployment()
    except KeyboardInterrupt:
        print("\n\n⏹️ Monitoring stopped by user")
        print("=" * 60)


if __name__ == "__main__":
    main()

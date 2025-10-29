#!/usr/bin/env python3
"""Create a simple test to see if Railway is using the latest deployment."""

import requests
import time

print("🔍 Checking Railway deployment version...")
print("=" * 60)

base_url = "https://hiremebahamas-backend.railway.app"

# Check health endpoint
try:
    response = requests.get(f"{base_url}/health", timeout=10)
    print(f"✅ Health check: {response.status_code}")
    print(f"   Response: {response.text}")

    # Check headers for deployment info
    print(f"\n📋 Response Headers:")
    for key, value in response.headers.items():
        if key.lower() in ["date", "server", "via", "x-railway"]:
            print(f"   {key}: {value}")

except Exception as e:
    print(f"❌ Health check failed: {e}")

# Try to access a route that should exist
print(f"\n🔐 Testing auth route:")
try:
    response = requests.options(f"{base_url}/api/auth/login", timeout=10)
    print(f"   OPTIONS /api/auth/login: {response.status_code}")

    if response.status_code == 404:
        print("   ⚠️  Route not found - Railway may be using old code!")
    else:
        print("   ✅ Route found!")

except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("💡 If routes return 404, Railway needs to redeploy.")
print("   The latest code is in GitHub commit 7380c3fe")
print("   Railway should auto-deploy, but may take 5-10 minutes.")

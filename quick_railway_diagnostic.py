#!/usr/bin/env python3
"""
Quick diagnostic to determine the exact Railway issue.
Tests all possible endpoints to understand routing behavior.
"""

import requests

BACKEND_URL = "https://hiremebahamas-backend.railway.app"

print("=" * 70)
print("🔍 RAILWAY DEPLOYMENT DIAGNOSTIC")
print("=" * 70)

# Comprehensive endpoint test
endpoints = {
    "Root": "/",
    "Health": "/health",
    "API Routes Debug": "/api/routes",
    "Login OPTIONS": ("/api/auth/login", "OPTIONS"),
    "Login POST": ("/api/auth/login", "POST"),
    "Register OPTIONS": ("/api/auth/register", "OPTIONS"),
}

results = {}

for name, endpoint in endpoints.items():
    method = "GET"
    path = endpoint

    if isinstance(endpoint, tuple):
        path, method = endpoint

    url = f"{BACKEND_URL}{path}"

    try:
        if method == "GET":
            resp = requests.get(url, timeout=10)
        elif method == "OPTIONS":
            resp = requests.options(url, timeout=10)
        elif method == "POST":
            resp = requests.post(url, json={}, timeout=10)

        content_preview = resp.text[:100]
        is_railway_default = "Railway API" in resp.text
        is_flask = "HireBahamas" in resp.text or "success" in resp.text.lower()

        results[name] = {
            "status": resp.status_code,
            "is_railway_default": is_railway_default,
            "is_flask": is_flask,
            "content": content_preview,
        }

    except Exception as e:
        results[name] = {"error": str(e)}

# Display results
print("\n📊 RESULTS:")
print("-" * 70)

railway_default_count = 0
flask_count = 0
error_count = 0

for name, result in results.items():
    if "error" in result:
        print(f"\n❌ {name}")
        print(f"   Error: {result['error']}")
        error_count += 1
    else:
        status = result["status"]
        icon = "✅" if status < 400 else "❌"

        print(f"\n{icon} {name}")
        print(f"   Status: {status}")

        if result["is_railway_default"]:
            print(f"   🚨 RAILWAY DEFAULT PAGE DETECTED")
            railway_default_count += 1
        elif result["is_flask"]:
            print(f"   ✅ Flask app detected")
            flask_count += 1
        elif status == 404:
            print(f"   ⚠️  Route not found")
        else:
            print(f"   Content: {result['content'][:50]}...")

# Summary
print("\n" + "=" * 70)
print("📋 SUMMARY")
print("=" * 70)

if railway_default_count > 0:
    print(f"\n🚨 CRITICAL ISSUE:")
    print(f"   Railway is serving DEFAULT PAGE ({railway_default_count} endpoints)")
    print(f"   Your Flask app is NOT deployed or NOT connected")
    print(f"\n   ACTION REQUIRED: Check Railway dashboard")
    print(f"   URL: https://railway.app/dashboard")

elif flask_count > 0 and error_count == 0:
    print(f"\n🎉 SUCCESS!")
    print(f"   Flask app is deployed and working")
    print(f"   {flask_count} endpoints responding correctly")

else:
    print(f"\n⚠️  MIXED RESULTS:")
    print(f"   Flask endpoints: {flask_count}")
    print(f"   Errors: {error_count}")
    print(f"   Railway defaults: {railway_default_count}")

print("\n" + "=" * 70)

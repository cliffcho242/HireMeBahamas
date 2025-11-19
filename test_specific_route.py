#!/usr/bin/env python3
"""Diagnostic script to understand why /api/ routes return 404."""

import sys

# First, let's verify locally that the routes exist
print("=" * 70)
print("🔍 LOCAL FLASK APP INSPECTION")
print("=" * 70)

try:
    # Import the Flask app
    from final_backend import app

    print(f"\n✅ Flask app imported successfully")
    print(f"   App name: {app.name}")
    print(f"   Debug mode: {app.debug}")

    # List all registered routes
    print(f"\n📋 ALL REGISTERED ROUTES ({len(app.url_map._rules)} total):")
    print("-" * 70)

    auth_routes = []
    other_routes = []

    for rule in app.url_map.iter_rules():
        route_info = f"{rule.rule:<50} {','.join(rule.methods)}"
        if "/api/auth/" in rule.rule:
            auth_routes.append(route_info)
        else:
            other_routes.append(route_info)

    print("\n🔐 AUTHENTICATION ROUTES:")
    for route in sorted(auth_routes):
        print(f"   {route}")

    print(f"\n📍 OTHER ROUTES ({len(other_routes)} routes):")
    for route in sorted(other_routes)[:10]:  # Show first 10
        print(f"   {route}")

    if len(other_routes) > 10:
        print(f"   ... and {len(other_routes) - 10} more routes")

    # Now test live deployment
    print("\n" + "=" * 70)
    print("🌐 LIVE DEPLOYMENT TEST")
    print("=" * 70)

    import requests

    base_url = "https://hiremebahamas-backend.railway.app"

    test_cases = [
        ("GET", "/health", None),
        ("OPTIONS", "/api/auth/login", None),
        ("POST", "/api/auth/login", {"email": "test@test.com", "password": "test"}),
        ("OPTIONS", "/api/auth/register", None),
    ]

    for method, path, data in test_cases:
        url = f"{base_url}{path}"
        try:
            if method == "GET":
                resp = requests.get(url, timeout=5)
            elif method == "OPTIONS":
                resp = requests.options(url, timeout=5)
            elif method == "POST":
                resp = requests.post(url, json=data, timeout=5)

            status_icon = "✅" if resp.status_code < 400 else "❌"
            print(f"\n{status_icon} {method:7} {path}")
            print(f"   Status: {resp.status_code}")
            print(f"   Response: {resp.text[:100]}")

        except Exception as e:
            print(f"\n❌ {method:7} {path}")
            print(f"   Error: {e}")

    print("\n" + "=" * 70)

except ImportError as e:
    print(f"❌ Failed to import Flask app: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

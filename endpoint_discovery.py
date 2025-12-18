#!/usr/bin/env python3
"""
Backend Endpoint Discovery Tool
Find what endpoints are actually available on the deployed backend
"""

import requests


def discover_endpoints():
    """Try to discover what endpoints are available"""
    base_url = "https://hiremebahamas-backend.render.app"

    # Test common endpoint patterns
    test_endpoints = [
        "/",
        "/health",
        "/api",
        "/api/auth",
        "/api/auth/login",
        "/api/auth/register",
        "/auth",
        "/auth/login",
        "/auth/register",
        "/login",
        "/register",
        "/admin",
        "/admin/auth/login",
    ]

    print(f"🔍 Discovering endpoints on {base_url}")
    print("=" * 60)

    available_endpoints = []

    for endpoint in test_endpoints:
        url = f"{base_url}{endpoint}"

        try:
            # Try GET first
            response = requests.get(url, timeout=5)
            status = response.status_code

            if status != 404:
                available_endpoints.append((endpoint, "GET", status))
                print(f"✅ {endpoint:<20} GET   {status}")
            else:
                print(f"❌ {endpoint:<20} GET   404")

        except requests.exceptions.RequestException as e:
            print(f"⚠️  {endpoint:<20} GET   ERROR: {e}")

    print(f"\n📋 Found {len(available_endpoints)} available endpoints:")
    for endpoint, method, status in available_endpoints:
        print(f"   {endpoint} ({method} -> {status})")

    return available_endpoints


def test_auth_methods():
    """Test specific auth endpoint methods"""
    base_url = "https://hiremebahamas-backend.render.app"

    # Based on final_backend.py, these should exist
    auth_endpoints = ["/api/auth/login", "/api/auth/register"]

    print(f"\n🔐 Testing authentication methods:")
    print("=" * 40)

    for endpoint in auth_endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\nTesting {endpoint}:")

        methods = ["GET", "POST", "OPTIONS"]
        for method in methods:
            try:
                response = requests.request(method, url, timeout=5)
                status = response.status_code
                print(f"  {method:<8} -> {status}")

                if status == 405:
                    print(f"    ❌ Method {method} not allowed")
                elif status == 200:
                    print(f"    ✅ Method {method} working")
                elif status == 404:
                    print(f"    ❌ Endpoint not found")

            except requests.exceptions.RequestException as e:
                print(f"  {method:<8} -> ERROR: {e}")


if __name__ == "__main__":
    print("🚀 Backend Endpoint Discovery Tool")
    print("=" * 60)

    # Discover available endpoints
    available = discover_endpoints()

    # Test auth methods specifically
    test_auth_methods()

    print("\n" + "=" * 60)
    print("💡 ANALYSIS:")

    if not available:
        print("❌ No endpoints responding - backend may be down")
    elif any("/api/auth" in ep[0] for ep in available):
        print("✅ Auth endpoints found - checking method support")
    else:
        print("⚠️  No auth endpoints found - wrong backend deployed?")
        print("   Check if correct backend file is deployed to Render")

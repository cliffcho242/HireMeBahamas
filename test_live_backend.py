#!/usr/bin/env python3
"""Test the live Render backend to diagnose 404 errors on auth routes."""

import requests
import json

BACKEND_URL = "https://hiremebahamas-backend.render.app"

print("🔍 Testing HireBahamas Render Backend")
print("=" * 60)

# Test 1: Health Check
print("\n1️⃣ Testing /health endpoint...")
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    print(f"   Headers: {dict(response.headers)}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: OPTIONS on login (CORS preflight)
print("\n2️⃣ Testing OPTIONS /api/auth/login (CORS preflight)...")
try:
    response = requests.options(f"{BACKEND_URL}/api/auth/login", timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: POST to login
print("\n3️⃣ Testing POST /api/auth/login...")
try:
    response = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"email": "test@test.com", "password": "test123"},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:500]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Check if it's a routing issue
print("\n4️⃣ Testing alternate routes...")
test_routes = [
    "/",
    "/api",
    "/api/",
    "/api/auth",
    "/api/auth/",
]
for route in test_routes:
    try:
        response = requests.get(f"{BACKEND_URL}{route}", timeout=5)
        print(f"   {route:<20} → {response.status_code}")
    except Exception as e:
        print(f"   {route:<20} → Error")

print("\n" + "=" * 60)
print("✅ Test complete!")

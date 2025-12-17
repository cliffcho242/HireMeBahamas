#!/usr/bin/env python3
"""
Demonstration of the PANIC SHIELD (Global Exception Guard)

This script demonstrates how the panic shield catches unhandled exceptions
and returns a calm, user-friendly error message while logging the full details.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from fastapi import Request
from fastapi.testclient import TestClient

print("=" * 70)
print("PANIC SHIELD DEMONSTRATION")
print("=" * 70)
print()
print("This demonstrates how the global exception handler works:")
print("  1. User triggers an endpoint that crashes")
print("  2. User sees a calm, friendly error message")
print("  3. Developers get full logs with stack trace")
print()

# Create some demo endpoints that crash
@app.get("/demo/crash-division")
async def crash_division(request: Request):
    """Endpoint that crashes with division by zero"""
    request.state.id = "demo-div-001"
    result = 10 / 0  # This will crash
    return {"result": result}

@app.get("/demo/crash-none")
async def crash_none(request: Request):
    """Endpoint that crashes accessing None attribute"""
    request.state.id = "demo-none-002"
    user = None
    return {"name": user.name}  # This will crash

@app.get("/demo/crash-keyerror")
async def crash_keyerror(request: Request):
    """Endpoint that crashes with KeyError"""
    request.state.id = "demo-key-003"
    data = {"a": 1}
    return {"value": data["missing_key"]}  # This will crash

# Create test client
client = TestClient(app, raise_server_exceptions=False)

# Test each crash scenario
scenarios = [
    ("/demo/crash-division", "Division by Zero"),
    ("/demo/crash-none", "None Attribute Access"),
    ("/demo/crash-keyerror", "Missing Key Error"),
]

for endpoint, description in scenarios:
    print(f"Scenario: {description}")
    print(f"  Endpoint: {endpoint}")
    
    response = client.get(endpoint)
    
    print(f"  User sees:")
    print(f"    Status: {response.status_code}")
    print(f"    Message: {response.json()}")
    print()

print("=" * 70)
print("KEY BENEFITS:")
print("=" * 70)
print("  ✅ Users never see ugly stack traces")
print("  ✅ Users get a calm, reassuring message")
print("  ✅ Developers get full error details in logs")
print("  ✅ Request IDs make debugging easy")
print("  ✅ Application never crashes, just recovers")
print()

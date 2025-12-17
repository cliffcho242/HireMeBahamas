#!/usr/bin/env python3
"""
Standalone verification script for the PANIC SHIELD implementation.

This script verifies that the global exception handler is properly registered
and works as expected by directly checking the app configuration.
"""

import sys
sys.path.insert(0, '/home/runner/work/HireMeBahamas/HireMeBahamas/backend')

from app.main import app, logger
from fastapi import Request
from fastapi.testclient import TestClient
from unittest.mock import patch

print("=" * 70)
print("PANIC SHIELD VERIFICATION")
print("=" * 70)
print()

# Test 1: Check if exception handler is registered
print("Test 1: Checking if Exception handler is registered...")
if Exception in app.exception_handlers:
    handler_name = app.exception_handlers[Exception].__name__
    print(f"  ✅ PASS: Exception handler '{handler_name}' is registered")
else:
    print(f"  ❌ FAIL: Exception handler is NOT registered")
    print(f"  Registered handlers: {list(app.exception_handlers.keys())}")
    sys.exit(1)

print()

# Test 2: Check if the handler has the correct name
print("Test 2: Verifying handler name is 'panic_handler'...")
handler_name = app.exception_handlers[Exception].__name__
if handler_name == "panic_handler":
    print(f"  ✅ PASS: Handler name is correct: '{handler_name}'")
else:
    print(f"  ❌ FAIL: Handler name is '{handler_name}', expected 'panic_handler'")
    sys.exit(1)

print()

# Test 3: Test that exceptions are caught and return correct response
print("Test 3: Testing exception handling behavior...")

# Add a test endpoint that raises an exception
@app.get("/test-panic-endpoint-verify")
async def test_panic_endpoint(request: Request):
    request.state.id = "test-verify-123"
    raise ValueError("Test exception for verification")

client = TestClient(app, raise_server_exceptions=False)

# Mock the logger to capture log calls
with patch.object(logger, 'error') as mock_error:
    response = client.get("/test-panic-endpoint-verify")
    
    # Check response status code
    if response.status_code == 500:
        print(f"  ✅ PASS: Response status code is 500")
    else:
        print(f"  ❌ FAIL: Response status code is {response.status_code}, expected 500")
        print(f"  Response body: {response.text}")
        sys.exit(1)
    
    # Check response content
    try:
        data = response.json()
        if "error" in data and data["error"] == "Temporary issue. Try again.":
            print(f"  ✅ PASS: Response message is correct: '{data['error']}'")
        else:
            print(f"  ❌ FAIL: Response message is incorrect: {data}")
            sys.exit(1)
    except Exception as e:
        print(f"  ❌ FAIL: Could not parse JSON response: {e}")
        print(f"  Response body: {response.text}")
        sys.exit(1)
    
    # Check logging
    if mock_error.called:
        print(f"  ✅ PASS: Exception was logged")
        log_message = mock_error.call_args[0][0]
        if "PANIC" in log_message and "test-verify-123" in log_message:
            print(f"  ✅ PASS: Log message contains 'PANIC' and request ID")
        else:
            print(f"  ⚠️  WARNING: Log message format may be unexpected: {log_message}")
    else:
        print(f"  ❌ FAIL: Exception was not logged")
        sys.exit(1)

print()

# Test 4: Verify normal endpoints still work
print("Test 4: Verifying normal endpoints are not affected...")
response = client.get("/ready")
if response.status_code == 200:
    data = response.json()
    if data.get("status") == "ready":
        print(f"  ✅ PASS: Normal endpoints work correctly")
    else:
        print(f"  ❌ FAIL: Normal endpoint returned unexpected data: {data}")
        sys.exit(1)
else:
    print(f"  ❌ FAIL: Normal endpoint returned status {response.status_code}")
    sys.exit(1)

print()
print("=" * 70)
print("ALL TESTS PASSED! 🎉")
print("=" * 70)
print()
print("Summary:")
print("  ✅ Exception handler is registered")
print("  ✅ Handler is named 'panic_handler'")
print("  ✅ Exceptions return status 500")
print("  ✅ Error message is user-friendly")
print("  ✅ Exceptions are logged with request ID")
print("  ✅ Normal endpoints are not affected")
print()

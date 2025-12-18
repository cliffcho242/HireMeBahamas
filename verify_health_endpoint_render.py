#!/usr/bin/env python3
"""
Verify Health Endpoint for Render Deployment
============================================

This script verifies that the health endpoints are properly configured
and meet all Render requirements.

Run this script before deploying to Render to ensure health checks will pass.
"""

import sys
import os
from pathlib import Path

# Add api/backend_app to path
api_backend_path = Path(__file__).parent / 'api' / 'backend_app'
sys.path.insert(0, str(api_backend_path))


def test_health_endpoints():
    """Verify both /health and /api/health endpoints"""
    print("\n" + "=" * 80)
    print("🔍 RENDER HEALTH ENDPOINT VERIFICATION")
    print("=" * 80)
    
    try:
        from main import app
        from fastapi.testclient import TestClient
    except ImportError as e:
        print(f"\n❌ Failed to import: {e}")
        print("   Install dependencies: pip install fastapi httpx")
        return False
    
    client = TestClient(app)
    all_tests_passed = True
    
    # Test both endpoints
    endpoints = ["/health", "/api/health"]
    
    for endpoint in endpoints:
        print(f"\n{'─' * 80}")
        print(f"Testing: {endpoint}")
        print(f"{'─' * 80}")
        
        # Test GET request
        print(f"\n1️⃣  GET {endpoint}")
        try:
            response = client.get(endpoint)
            print(f"   Status: {response.status_code}")
            print(f"   Body: {response.json()}")
            
            if response.status_code != 200:
                print(f"   ❌ FAIL: Expected 200, got {response.status_code}")
                all_tests_passed = False
            elif response.json().get("status") != "ok":
                print(f"   ❌ FAIL: Expected {{'status': 'ok'}}, got {response.json()}")
                all_tests_passed = False
            else:
                print(f"   ✅ PASS: Returns 200 with correct format")
        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            all_tests_passed = False
        
        # Test HEAD request
        print(f"\n2️⃣  HEAD {endpoint}")
        try:
            response = client.head(endpoint)
            print(f"   Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ❌ FAIL: Expected 200, got {response.status_code}")
                all_tests_passed = False
            else:
                print(f"   ✅ PASS: HEAD method supported")
        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            all_tests_passed = False
        
        # Test response time
        print(f"\n3️⃣  Response Time Test")
        try:
            import time
            start = time.time()
            response = client.get(endpoint)
            elapsed_ms = (time.time() - start) * 1000
            print(f"   Response time: {elapsed_ms:.2f}ms")
            
            if elapsed_ms > 100:
                print(f"   ⚠️  WARNING: Response time > 100ms (still acceptable)")
            else:
                print(f"   ✅ PASS: Fast response (< 100ms)")
        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            all_tests_passed = False
        
        # Test no authentication required
        print(f"\n4️⃣  Authentication Test")
        try:
            # Try without any headers
            response = client.get(endpoint)
            if response.status_code == 200:
                print(f"   ✅ PASS: No authentication required")
            else:
                print(f"   ❌ FAIL: Requires authentication (status {response.status_code})")
                all_tests_passed = False
        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            all_tests_passed = False
    
    # Final summary
    render_url = os.getenv('RENDER_EXTERNAL_URL', 'https://hiremebahamas.onrender.com')
    
    print("\n" + "=" * 80)
    if all_tests_passed:
        print("✅ ALL TESTS PASSED - HEALTH ENDPOINTS READY FOR RENDER")
        print("=" * 80)
        print("\n📋 Next Steps:")
        print("   1. Deploy to Render")
        print("   2. In Render Dashboard → Settings → Health Check Path:")
        print("      Set to: /api/health (or /health)")
        print("   3. Expected Render logs:")
        print("      ==> Health check passed")
        print("      ==> Service is live")
        print(f"\n🔗 Manual verification URLs:")
        print(f"   • {render_url}/api/health")
        print(f"   • {render_url}/health")
        print("\n✅ Expected response: {'status': 'ok'} or 200 OK")
        print("\nNote: URLs based on RENDER_EXTERNAL_URL env var or default.")
    else:
        print("❌ SOME TESTS FAILED - REVIEW ERRORS ABOVE")
        print("=" * 80)
    
    return all_tests_passed


def print_render_configuration():
    """Print Render configuration instructions"""
    # Get deployment URL from environment or use default
    render_url = os.getenv('RENDER_EXTERNAL_URL', 'https://hiremebahamas.onrender.com')
    
    print("\n" + "=" * 80)
    print("📋 RENDER CONFIGURATION GUIDE")
    print("=" * 80)
    print(f"""
In your Render Dashboard:

1. Go to: Your Backend Service → Settings
2. Find: Health Check Path
3. Set one of:
   • /api/health (Recommended)
   • /health (Alternative)
4. Click: Save Changes

Expected Behavior After Configuration:
✅ Health check passed
✅ Service is live
✅ No SIGTERM errors
✅ No timeout errors
✅ No repeated restarts

Manual Verification (30 seconds):
• Open: {render_url}/api/health
• Should see: {{"status":"ok"}} or 200 OK
• Should NOT see: 404, 401, timeout

🏁 Once configured, your Render deployment will be STABLE.

Note: Using deployment URL from RENDER_EXTERNAL_URL env var or default.
""")


if __name__ == "__main__":
    success = test_health_endpoints()
    print_render_configuration()
    
    sys.exit(0 if success else 1)

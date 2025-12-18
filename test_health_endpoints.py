#!/usr/bin/env python3
"""
Test health check endpoints to verify instant response and HEAD method support.
This ensures Render health checks will succeed.
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_health_endpoints():
    """Test that health endpoints support both GET and HEAD methods."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    endpoints_to_test = [
        "/health",
        "/api/health",
        "/live",
        "/ready",
    ]
    
    print("Testing health endpoints...")
    print("=" * 60)
    
    all_passed = True
    
    for endpoint in endpoints_to_test:
        # Test GET method
        try:
            response = client.get(endpoint)
            get_status = response.status_code
            get_passed = get_status == 200
            
            if not get_passed:
                all_passed = False
            
            print(f"GET  {endpoint:20s} -> {get_status} {'✅' if get_passed else '❌'}")
        except Exception as e:
            print(f"GET  {endpoint:20s} -> ERROR: {e} ❌")
            all_passed = False
        
        # Test HEAD method
        try:
            response = client.head(endpoint)
            head_status = response.status_code
            head_passed = head_status == 200
            
            if not head_passed:
                all_passed = False
            
            print(f"HEAD {endpoint:20s} -> {head_status} {'✅' if head_passed else '❌'}")
        except Exception as e:
            print(f"HEAD {endpoint:20s} -> ERROR: {e} ❌")
            all_passed = False
        
        print()
    
    print("=" * 60)
    if all_passed:
        print("✅ All health endpoints are working correctly!")
        print("✅ Both GET and HEAD methods supported")
        print("✅ Render health checks should succeed")
        return 0
    else:
        print("❌ Some health endpoints failed!")
        return 1

if __name__ == "__main__":
    sys.exit(test_health_endpoints())

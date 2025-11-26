#!/usr/bin/env python3
"""
Test script to verify health check endpoints are exempt from rate limiting
"""
import sys
import time
import requests

def test_health_endpoint_no_rate_limit(base_url="http://localhost:8080"):
    """Test that health check endpoints can be called frequently without rate limiting"""
    
    print("Testing health check endpoints for rate limiting...")
    print(f"Base URL: {base_url}")
    print("-" * 60)
    
    endpoints = ["/health", "/", "/api/health"]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\nTesting {endpoint}...")
        
        # Make 60 requests (more than the 50 per hour limit)
        success_count = 0
        rate_limited_count = 0
        
        for i in range(60):
            try:
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited_count += 1
                    print(f"  ❌ Request {i+1}: Got 429 (Rate Limited)")
                else:
                    print(f"  ⚠️  Request {i+1}: Got unexpected status {response.status_code}")
                
                # Small delay to avoid overwhelming the server
                if i % 10 == 0:
                    print(f"  Progress: {i+1}/60 requests...")
                    
            except requests.exceptions.RequestException as e:
                print(f"  ❌ Request {i+1}: Connection error - {e}")
                break
        
        print(f"\n  Results for {endpoint}:")
        print(f"    ✅ Successful (200): {success_count}/60")
        print(f"    ❌ Rate Limited (429): {rate_limited_count}/60")
        
        if rate_limited_count > 0:
            print(f"    ❌ FAILED: Health check endpoint is being rate limited!")
            return False
        elif success_count == 60:
            print(f"    ✅ PASSED: All requests succeeded without rate limiting")
        else:
            print(f"    ⚠️  WARNING: Only {success_count}/60 requests succeeded")
    
    print("\n" + "=" * 60)
    print("✅ All health check endpoints are exempt from rate limiting!")
    return True

if __name__ == "__main__":
    # Check if a custom URL was provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    
    success = test_health_endpoint_no_rate_limit(base_url)
    sys.exit(0 if success else 1)

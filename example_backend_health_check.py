#!/usr/bin/env python3
"""
Example: Backend Health Check using BACKEND_URL environment variable

This demonstrates the recommended pattern for using BACKEND_URL in production scripts.

Usage:
  export BACKEND_URL=https://hiremebahamas.vercel.app
  python example_backend_health_check.py

Or inline:
  BACKEND_URL=https://hiremebahamas.vercel.app python example_backend_health_check.py
"""

import os
import sys
import requests

# Get backend URL from environment variable (required)
# This will raise KeyError if BACKEND_URL is not set
try:
    BASE_URL = os.environ["BACKEND_URL"]
except KeyError:
    print("❌ ERROR: BACKEND_URL environment variable is not set")
    print()
    print("Please set BACKEND_URL before running this script:")
    print("  export BACKEND_URL=https://your-backend-url.com")
    print()
    print("Or run with:")
    print("  BACKEND_URL=https://your-backend-url.com python example_backend_health_check.py")
    sys.exit(1)

def check_health():
    """Check backend health endpoint"""
    print(f"Checking backend health at: {BASE_URL}")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"❌ Backend returned status: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = check_health()
    sys.exit(0 if success else 1)

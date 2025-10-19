#!/usr/bin/env python3
"""Test the simple HTTP server"""

import requests
import json

def test_simple_server():
    try:
        print("Testing simple HTTP server...")
        
        # Test health endpoint
        response = requests.get("http://127.0.0.1:8009/health", timeout=5)
        print(f"Health check - Status: {response.status_code}")
        print(f"Health check - Response: {response.text}")
        
        # Test login endpoint
        response = requests.post(
            "http://127.0.0.1:8009/api/auth/login",
            json={
                "email": "admin@hirebahamas.com",
                "password": "admin123"
            },
            timeout=5
        )
        
        print(f"Login test - Status: {response.status_code}")
        print(f"Login test - Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Simple server is working!")
        else:
            print("❌ Simple server has issues")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to simple server")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_server()
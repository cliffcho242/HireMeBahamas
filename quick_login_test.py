#!/usr/bin/env python3
import requests
import json

def test_login():
    """Test the login API directly"""
    try:
        print("🔧 Testing Login API...")
        
        login_data = {
            "email": "admin@hirebahamas.com", 
            "password": "admin123"
        }
        
        response = requests.post(
            'http://127.0.0.1:8008/api/auth/login',
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ LOGIN API WORKS!")
            print(f"User: {data.get('user', {})}")
            print(f"Token: {data.get('token', '')[:50]}...")
            return True
        else:
            print("❌ LOGIN API FAILED!")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def check_frontend():
    """Check frontend accessibility"""
    ports = [3000, 3001, 3002, 3003]
    for port in ports:
        try:
            response = requests.get(f'http://localhost:{port}', timeout=3)
            if response.status_code == 200:
                print(f"✅ Frontend running on port {port}")
                return port
        except:
            continue
    return None

if __name__ == "__main__":
    print("QUICK LOGIN TEST")
    print("================")
    
    # Test API
    api_works = test_login()
    
    # Check frontend
    frontend_port = check_frontend()
    
    if api_works and frontend_port:
        print(f"\n✅ BOTH SYSTEMS WORKING")
        print(f"Backend: http://127.0.0.1:8008")
        print(f"Frontend: http://localhost:{frontend_port}")
        print(f"\nIf login is stuck, the issue is in the frontend navigation logic.")
        print(f"Check the browser console for errors!")
    else:
        print("\n❌ ISSUES DETECTED")
        if not api_works:
            print("- Backend/API not working")
        if not frontend_port:
            print("- Frontend not accessible")
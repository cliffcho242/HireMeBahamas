#!/usr/bin/env python3
"""
Automated HireBahamas Platform Diagnostic and Fix Script
Diagnoses network issues, starts servers, and tests endpoints
"""

import subprocess
import time
import requests
import json
import os
import sys
from pathlib import Path

def run_command(cmd, shell=True, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=capture_output, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def kill_existing_processes():
    """Kill existing Python and Node processes"""
    print("🔄 Killing existing Python and Node processes...")
    
    # Kill Python processes
    run_command("taskkill /F /IM python.exe", shell=True)
    time.sleep(2)
    
    # Kill Node processes  
    run_command("taskkill /F /IM node.exe", shell=True)
    time.sleep(2)
    
    print("✅ Processes cleaned up")

def check_port_usage():
    """Check if ports 8005 and 3000 are in use"""
    print("🔍 Checking port usage...")
    
    # Check backend port 8005
    code, stdout, stderr = run_command("netstat -an | findstr :8005")
    if code == 0 and stdout.strip():
        print(f"⚠️  Port 8005 is in use: {stdout.strip()}")
    else:
        print("✅ Port 8005 is available")
    
    # Check frontend port 3000
    code, stdout, stderr = run_command("netstat -an | findstr :3000")
    if code == 0 and stdout.strip():
        print(f"⚠️  Port 3000 is in use: {stdout.strip()}")
    else:
        print("✅ Port 3000 is available")

def start_backend():
    """Start the backend server"""
    print("🚀 Starting backend server...")
    
    # Get Python executable path
    python_exe = r"C:/Users/Dell/OneDrive/Desktop/HireBahamas/.venv/Scripts/python.exe"
    backend_script = "backend/app/flask_backend.py"
    
    # Start backend in background
    try:
        process = subprocess.Popen([python_exe, backend_script], 
                                 cwd=os.getcwd(),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        print(f"✅ Backend started with PID: {process.pid}")
        time.sleep(5)  # Give it time to start
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the frontend server"""
    print("🚀 Starting frontend server...")
    
    try:
        # Change to frontend directory and start
        process = subprocess.Popen(["npm", "run", "dev"], 
                                 cwd="frontend",
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        print(f"✅ Frontend started with PID: {process.pid}")
        time.sleep(5)  # Give it time to start
        return process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 Testing backend health...")
    
    try:
        response = requests.get("http://127.0.0.1:8005/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend health check failed with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not responding (connection refused)")
        return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_frontend():
    """Test frontend server"""
    print("🔍 Testing frontend server...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend server is accessible")
            return True
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend is not responding (connection refused)")
        return False
    except Exception as e:
        print(f"❌ Frontend test error: {e}")
        return False

def test_login_endpoint():
    """Test login endpoint with admin credentials"""
    print("🔍 Testing login endpoint...")
    
    try:
        login_data = {
            "email": "admin@hirebahamas.com",
            "password": "AdminPass123!"
        }
        
        response = requests.post("http://127.0.0.1:8005/auth/login", 
                               json=login_data, 
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        
        if response.status_code == 200:
            print("✅ Login endpoint test passed")
            result = response.json()
            if result.get("success"):
                print("✅ Login authentication successful")
                print(f"   Token received: {result.get('token', 'No token')[:50]}...")
                return True
            else:
                print(f"❌ Login failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Login endpoint returned status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to login endpoint")
        return False
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False

def main():
    """Main diagnostic and fix routine"""
    print("🎯 HireBahamas Automated Diagnostic and Fix")
    print("=" * 50)
    
    # Step 1: Clean up existing processes
    kill_existing_processes()
    
    # Step 2: Check port usage
    check_port_usage()
    
    # Step 3: Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Cannot proceed without backend")
        return False
    
    # Step 4: Start frontend
    frontend_process = start_frontend()
    
    # Step 5: Test backend health
    backend_healthy = test_backend_health()
    
    # Step 6: Test frontend
    frontend_working = test_frontend()
    
    # Step 7: Test login endpoint
    login_working = test_login_endpoint()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print(f"Backend Health: {'✅ PASS' if backend_healthy else '❌ FAIL'}")
    print(f"Frontend Access: {'✅ PASS' if frontend_working else '❌ FAIL'}")
    print(f"Login Endpoint: {'✅ PASS' if login_working else '❌ FAIL'}")
    
    if backend_healthy and frontend_working and login_working:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("🌐 Backend: http://127.0.0.1:8005")
        print("🌐 Frontend: http://localhost:3000")
        print("📋 Admin Login: admin@hirebahamas.com / AdminPass123!")
    else:
        print("\n⚠️  ISSUES DETECTED - Check logs for details")
        print("📄 Backend logs: backend_debug.log")
        
        # Show backend process output if available
        if backend_process and backend_process.poll() is not None:
            stdout, stderr = backend_process.communicate()
            if stderr:
                print(f"\n❌ Backend Error Output:\n{stderr}")

    return backend_healthy and frontend_working and login_working

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
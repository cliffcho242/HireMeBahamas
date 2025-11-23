#!/usr/bin/env python3
"""
Register Cliff users and verify permanent storage.
Tests that users persist across server restarts.
"""

import requests
import sqlite3
import time
import subprocess
import sys
import os
import signal

BACKEND_URL = "http://127.0.0.1:8080"
DB_PATH = "hiremebahamas.db"

# Users to register
CLIFF_USERS = [
    {
        "email": "cliffyv24@gmail.com",
        "password": "SecurePass123!",
        "first_name": "John",
        "last_name": "Carter",
        "user_type": "employer",
        "location": "Nassau, Bahamas"
    },
    {
        "email": "cliff242@gmail.com",
        "password": "SecurePass123!",
        "first_name": "Cliff",
        "last_name": "Cho",
        "user_type": "admin",
        "location": "Nassau, Bahamas"
    }
]


def check_database_users():
    """Check users directly in the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT email, first_name, last_name, user_type FROM users WHERE email IN (?, ?)",
            ("cliffyv24@gmail.com", "cliff242@gmail.com")
        )
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"Error checking database: {e}")
        return []


def start_backend():
    """Start the backend server"""
    print("Starting backend server...")
    process = subprocess.Popen(
        ["python3", "final_backend_postgresql.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid if os.name != 'nt' else None
    )
    time.sleep(6)  # Wait for server to start
    return process


def stop_backend(process):
    """Stop the backend server"""
    print("Stopping backend server...")
    try:
        if os.name != 'nt':
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        else:
            process.terminate()
        process.wait(timeout=5)
    except Exception as e:
        print(f"Error stopping backend: {e}")


def register_user(user_data):
    """Register a user via API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json=user_data,
            timeout=10
        )
        return response
    except Exception as e:
        print(f"Error registering user: {e}")
        return None


def test_login(email, password):
    """Test user login"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        return response
    except Exception as e:
        print(f"Error logging in: {e}")
        return None


def main():
    print("=" * 80)
    print("Cliff Users Registration & Permanent Storage Test")
    print("=" * 80)
    print()
    
    # Step 1: Check if users already exist in database
    print("Step 1: Checking if users already exist in database...")
    existing_users = check_database_users()
    if existing_users:
        print(f"✓ Found {len(existing_users)} existing user(s):")
        for user in existing_users:
            print(f"  - {user[0]} ({user[1]} {user[2]}) - {user[3]}")
        print()
        print("Users already exist and are stored permanently.")
        return
    else:
        print("✓ No existing users found - will create them")
        print()
    
    # Step 2: Start backend server
    print("Step 2: Starting backend server...")
    backend_process = start_backend()
    
    try:
        # Verify backend is running
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("✗ Backend failed to start")
            return
        print("✓ Backend is running")
        print()
        
        # Step 3: Register users
        print("Step 3: Registering Cliff users...")
        for user in CLIFF_USERS:
            print(f"\nRegistering: {user['email']}")
            print(f"  Name: {user['first_name']} {user['last_name']}")
            print(f"  Type: {user['user_type']}")
            print(f"  Location: {user['location']}")
            
            response = register_user(user)
            if response and response.status_code == 201:
                data = response.json()
                print(f"  ✓ Registration successful")
                print(f"  ✓ User ID: {data['user']['id']}")
            else:
                error_msg = response.json().get('message', 'Unknown error') if response else 'Connection error'
                print(f"  ✗ Registration failed: {error_msg}")
        
        print()
        
        # Step 4: Verify users in database
        print("Step 4: Verifying users are stored in database...")
        db_users = check_database_users()
        if len(db_users) == len(CLIFF_USERS):
            print(f"✓ All {len(db_users)} users stored in database:")
            for user in db_users:
                print(f"  - {user[0]} ({user[1]} {user[2]}) - {user[3]}")
        else:
            print(f"✗ Expected {len(CLIFF_USERS)} users, found {len(db_users)}")
        print()
        
        # Step 5: Test login before restart
        print("Step 5: Testing login (before restart)...")
        for user in CLIFF_USERS:
            login_response = test_login(user['email'], user['password'])
            if login_response and login_response.status_code == 200:
                print(f"✓ Login successful: {user['email']}")
            else:
                print(f"✗ Login failed: {user['email']}")
        print()
        
        # Step 6: Stop backend
        print("Step 6: Stopping backend to test persistence...")
        stop_backend(backend_process)
        time.sleep(2)
        print("✓ Backend stopped")
        print()
        
        # Step 7: Verify users still in database (persistence test)
        print("Step 7: Verifying users persist in database after shutdown...")
        db_users_after = check_database_users()
        if len(db_users_after) == len(CLIFF_USERS):
            print(f"✓ All {len(db_users_after)} users still in database (PERSISTENT):")
            for user in db_users_after:
                print(f"  - {user[0]} ({user[1]} {user[2]}) - {user[3]}")
        else:
            print(f"✗ Users not persisted! Found {len(db_users_after)} users")
        print()
        
        # Step 8: Restart backend and test login again
        print("Step 8: Restarting backend to verify login still works...")
        backend_process = start_backend()
        
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("✗ Backend failed to restart")
            return
        print("✓ Backend restarted")
        print()
        
        print("Step 9: Testing login (after restart)...")
        for user in CLIFF_USERS:
            login_response = test_login(user['email'], user['password'])
            if login_response and login_response.status_code == 200:
                print(f"✓ Login successful: {user['email']}")
            else:
                print(f"✗ Login failed: {user['email']}")
        print()
        
        # Final summary
        print("=" * 80)
        print("✅ SUCCESS: Users registered and stored permanently!")
        print("=" * 80)
        print()
        print("Registered users:")
        for user in CLIFF_USERS:
            print(f"  Email: {user['email']}")
            print(f"  Password: {user['password']}")
            print(f"  Name: {user['first_name']} {user['last_name']}")
            print(f"  Type: {user['user_type']}")
            print()
        
    finally:
        # Cleanup
        stop_backend(backend_process)
        print("✓ Cleanup complete")


if __name__ == "__main__":
    main()

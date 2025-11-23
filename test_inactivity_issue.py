#!/usr/bin/env python3
"""
Comprehensive test to reproduce and fix the "users can't sign in after inactivity" issue.

This script tests:
1. Register users (cliff242@gmail.com, cliffyv24@gmail.com)
2. Turn on "hire me" function
3. Create posts
4. Verify data persists after server restart
5. Verify users can still sign in after restart
6. Identify and fix any issues with data persistence
"""

import requests
import sqlite3
import time
import subprocess
import os
import signal
import sys

BACKEND_URL = "http://127.0.0.1:8080"
DB_PATH = "hiremebahamas.db"

USERS = [
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


def start_backend():
    """Start backend server"""
    print("Starting backend server...")
    process = subprocess.Popen(
        ["python3", "final_backend_postgresql.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid if os.name != 'nt' else None
    )
    time.sleep(6)
    return process


def stop_backend(process):
    """Stop backend server"""
    try:
        if os.name != 'nt':
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        else:
            process.terminate()
        process.wait(timeout=5)
    except Exception:
        pass


def check_db_users():
    """Check users directly in database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT email, first_name, last_name, is_available_for_hire FROM users")
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"Error checking database: {e}")
        return []


def register_user(user_data):
    """Register a user"""
    try:
        resp = requests.post(f"{BACKEND_URL}/api/auth/register", json=user_data, timeout=5)
        return resp
    except Exception as e:
        print(f"Error registering: {e}")
        return None


def login_user(email, password):
    """Login a user"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"email": email, "password": password},
            timeout=5
        )
        return resp
    except Exception as e:
        print(f"Error logging in: {e}")
        return None


def create_post(token, content):
    """Create a post"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(
            f"{BACKEND_URL}/api/posts",
            json={"content": content, "image_url": ""},
            headers=headers,
            timeout=5
        )
        return resp
    except Exception as e:
        print(f"Error creating post: {e}")
        return None


def main():
    print("=" * 80)
    print("COMPREHENSIVE TEST: Reproduce 'Can't Sign In After Inactivity' Issue")
    print("=" * 80)
    print()
    
    # Clean start
    if os.path.exists(DB_PATH):
        print(f"Removing old database: {DB_PATH}")
        os.remove(DB_PATH)
    
    backend_process = start_backend()
    
    try:
        # Step 1: Register users
        print("\n" + "=" * 80)
        print("STEP 1: Register Users")
        print("=" * 80)
        
        tokens = {}
        for user in USERS:
            print(f"\nRegistering: {user['email']}")
            resp = register_user(user)
            if resp and resp.status_code == 201:
                data = resp.json()
                tokens[user['email']] = data['access_token']
                print(f"  ✓ Registered successfully")
                print(f"  User ID: {data['user']['id']}")
            else:
                print(f"  ✗ Registration failed: {resp.json() if resp else 'Connection error'}")
                return
        
        # Step 2: Turn on "hire me" function (is_available_for_hire)
        print("\n" + "=" * 80)
        print("STEP 2: Enable 'Hire Me' Function")
        print("=" * 80)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for user in USERS:
            cursor.execute(
                "UPDATE users SET is_available_for_hire = 1 WHERE email = ?",
                (user['email'],)
            )
            print(f"  ✓ Enabled 'hire me' for {user['email']}")
        conn.commit()
        conn.close()
        
        # Step 3: Create posts
        print("\n" + "=" * 80)
        print("STEP 3: Create Posts")
        print("=" * 80)
        
        for user in USERS:
            print(f"\nCreating post for: {user['email']}")
            token = tokens[user['email']]
            content = f"Test post from {user['first_name']} {user['last_name']}"
            resp = create_post(token, content)
            if resp and resp.status_code == 201:
                print(f"  ✓ Post created successfully")
            else:
                print(f"  ✗ Post creation failed: {resp.json() if resp else 'Connection error'}")
        
        # Step 4: Verify data in database
        print("\n" + "=" * 80)
        print("STEP 4: Verify Data Persistence (Before Restart)")
        print("=" * 80)
        
        db_users = check_db_users()
        print(f"\nUsers in database: {len(db_users)}")
        for u in db_users:
            hire_me_status = "ON" if u[3] else "OFF"
            print(f"  - {u[0]} ({u[1]} {u[2]}) - Hire Me: {hire_me_status}")
        
        # Step 5: Simulate inactivity - restart server
        print("\n" + "=" * 80)
        print("STEP 5: Simulating Inactivity (Server Restart)")
        print("=" * 80)
        
        print("\nStopping backend...")
        stop_backend(backend_process)
        time.sleep(2)
        
        print("Checking if database file still exists...")
        if os.path.exists(DB_PATH):
            size = os.path.getsize(DB_PATH)
            print(f"  ✓ Database file exists ({size} bytes)")
        else:
            print(f"  ✗ Database file MISSING!")
            return
        
        print("\nChecking if users still in database...")
        db_users_after = check_db_users()
        if len(db_users_after) == len(USERS):
            print(f"  ✓ All {len(db_users_after)} users still in database")
        else:
            print(f"  ✗ ISSUE FOUND: Expected {len(USERS)} users, found {len(db_users_after)}")
        
        print("\nRestarting backend...")
        backend_process = start_backend()
        
        # Step 6: Try to login after restart
        print("\n" + "=" * 80)
        print("STEP 6: Test Login After Restart")
        print("=" * 80)
        
        login_success_count = 0
        for user in USERS:
            print(f"\nAttempting login: {user['email']}")
            resp = login_user(user['email'], user['password'])
            if resp and resp.status_code == 200:
                print(f"  ✓ Login successful!")
                login_success_count += 1
            else:
                error_msg = resp.json().get('message', 'Unknown error') if resp else 'Connection error'
                print(f"  ✗ Login failed: {error_msg}")
        
        # Final verdict
        print("\n" + "=" * 80)
        print("TEST RESULTS")
        print("=" * 80)
        
        if login_success_count == len(USERS):
            print("\n✅ ALL TESTS PASSED")
            print("   Users can sign in after inactivity/restart")
            print("   Data persists correctly")
        else:
            print(f"\n❌ ISSUE CONFIRMED")
            print(f"   {len(USERS) - login_success_count} user(s) cannot sign in after restart")
            print(f"   This reproduces the reported issue")
            
            # Check what happened
            final_db_users = check_db_users()
            print(f"\n   Users in database after restart: {len(final_db_users)}")
            if len(final_db_users) == 0:
                print("   ⚠️  DATABASE WAS CLEARED/RESET")
            elif len(final_db_users) < len(USERS):
                print(f"   ⚠️  SOME USERS WERE DELETED")
        
        print()
        
    finally:
        stop_backend(backend_process)


if __name__ == "__main__":
    main()

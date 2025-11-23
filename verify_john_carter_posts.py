#!/usr/bin/env python3
"""
Verification script: John Carter (cliffyv24@gmail.com) can create posts.
This script demonstrates that the reported issue has been fixed.
"""

import requests
import sys
import time
import subprocess
import os
import signal

BACKEND_URL = "http://127.0.0.1:8080"

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

def main():
    print("=" * 80)
    print("VERIFICATION: John Carter (cliffyv24@gmail.com) Can Create Posts")
    print("=" * 80)
    print()
    
    backend_process = start_backend()
    
    try:
        # Verify backend is running
        health_resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health_resp.status_code != 200:
            print("✗ Backend failed to start")
            return
        print("✓ Backend is running\n")
        
        # Register John Carter with cliffyv24@gmail.com
        user_data = {
            "email": "cliffyv24@gmail.com",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Carter",
            "user_type": "employer",
            "location": "Nassau, Bahamas"
        }
        
        print(f"Step 1: Registering John Carter")
        print(f"  Email: {user_data['email']}")
        print(f"  Name: {user_data['first_name']} {user_data['last_name']}")
        
        reg_resp = requests.post(f"{BACKEND_URL}/api/auth/register", json=user_data, timeout=5)
        
        if reg_resp.status_code != 201:
            print(f"  ✗ Registration failed: {reg_resp.json()}")
            return
        
        reg_data = reg_resp.json()
        token = reg_data['access_token']
        user_id = reg_data['user']['id']
        print(f"  ✓ Registration successful (User ID: {user_id})\n")
        
        # Test creating a post
        print(f"Step 2: Creating a post as John Carter")
        post_data = {
            "content": "This is a test post from John Carter to verify the fix.",
            "image_url": ""
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        post_resp = requests.post(
            f"{BACKEND_URL}/api/posts",
            json=post_data,
            headers=headers,
            timeout=5
        )
        
        if post_resp.status_code != 201:
            print(f"  ✗ Failed to create post")
            print(f"  Error: {post_resp.json()}")
            return
        
        post_result = post_resp.json()
        post_id = post_result['post']['id']
        creator = post_result['post']['user']
        
        print(f"  ✓ Post created successfully!")
        print(f"  Post ID: {post_id}")
        print(f"  Creator: {creator['first_name']} {creator['last_name']}")
        print(f"  Email: {creator['email']}\n")
        
        # Verify the post shows correct user information
        print(f"Step 3: Verifying post attribution")
        get_resp = requests.get(f"{BACKEND_URL}/api/posts", timeout=5)
        
        if get_resp.status_code != 200:
            print(f"  ✗ Failed to retrieve posts")
            return
        
        posts_data = get_resp.json()
        posts = posts_data.get('posts', [])
        
        john_carter_post = None
        for post in posts:
            if post['user']['email'] == 'cliffyv24@gmail.com':
                john_carter_post = post
                break
        
        if john_carter_post:
            print(f"  ✓ Post found with correct attribution:")
            print(f"    Creator: {john_carter_post['user']['first_name']} {john_carter_post['user']['last_name']}")
            print(f"    Email: {john_carter_post['user']['email']}")
            print(f"    Content: {john_carter_post['content'][:60]}...")
        else:
            print(f"  ✗ Could not find John Carter's post")
            return
        
        print()
        print("=" * 80)
        print("✅ VERIFICATION SUCCESSFUL")
        print("=" * 80)
        print()
        print("Summary:")
        print(f"  • John Carter (cliffyv24@gmail.com) registered successfully")
        print(f"  • Post creation works without errors")
        print(f"  • Posts display accurate user information")
        print(f"  • Issue 'failed to create post' has been resolved")
        print()
        
    finally:
        stop_backend(backend_process)

if __name__ == "__main__":
    main()

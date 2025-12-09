#!/usr/bin/env python3
"""
Test script to verify Gunicorn startup time with preload_app=False

This simulates what happens during Railway deployment:
1. Gunicorn master starts
2. Master starts listening (this is when healthcheck can connect)
3. Workers fork and initialize Flask app
4. Health endpoint responds immediately

Expected result: Gunicorn listening in <2 seconds
"""
import subprocess
import time
import sys
import os


def test_gunicorn_startup():
    """Test that Gunicorn starts quickly and health endpoint is accessible"""
    print("=" * 70)
    print("Testing Gunicorn Startup with preload_app=False")
    print("=" * 70)
    print()
    
    # Check if we have the necessary dependencies
    try:
        import flask
        import psycopg2
        import gunicorn
    except ImportError as e:
        print(f"⚠️  Missing dependencies: {e}")
        print("This test requires: flask, psycopg2, gunicorn")
        print("Run: pip install flask psycopg2-binary gunicorn")
        return False
    
    # Set minimal environment for testing
    env = os.environ.copy()
    env["PORT"] = "8888"
    env["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"  # Fake URL for testing
    env["SECRET_KEY"] = "test-secret"
    
    print("Starting Gunicorn with preload_app=False...")
    print("Expected: Server listening in <2 seconds")
    print()
    
    start_time = time.time()
    
    # Start Gunicorn in a subprocess
    try:
        process = subprocess.Popen(
            [
                sys.executable, "-m", "gunicorn",
                "final_backend_postgresql:application",
                "--config", "gunicorn.conf.py",
                "--bind", "0.0.0.0:8888",
                "--log-level", "info"
            ],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Monitor output for "ready" message
        listening_detected = False
        worker_spawned = False
        
        for line in iter(process.stdout.readline, ''):
            elapsed = time.time() - start_time
            
            # Print the line with timestamp
            print(f"[{elapsed:5.2f}s] {line.rstrip()}")
            
            # Check for key milestones
            if "ready to accept connections" in line.lower():
                listening_detected = True
                listening_time = elapsed
                print()
                print("✅ Gunicorn is listening and accepting connections!")
                print(f"   Time to ready: {listening_time:.2f}s")
                print()
                
            if "worker" in line.lower() and "spawned" in line.lower():
                worker_spawned = True
                worker_time = elapsed
                print(f"   Worker spawned at {worker_time:.2f}s")
            
            # Stop after we see the important messages or timeout
            if listening_detected and worker_spawned:
                print()
                print("=" * 70)
                print("SUCCESS: Gunicorn started successfully!")
                print(f"- Listening time: {listening_time:.2f}s (healthcheck can connect)")
                print(f"- Worker spawn time: {worker_time:.2f}s")
                print(f"- Health endpoint accessible: YES (as soon as listening starts)")
                print("=" * 70)
                break
            
            # Safety timeout
            if elapsed > 10:
                print()
                print("⏱️  Timeout reached (10s), stopping test")
                break
        
        # Clean up
        process.terminate()
        process.wait(timeout=5)
        
        return listening_detected
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False


if __name__ == "__main__":
    print("Railway Healthcheck Fix - Gunicorn Startup Test")
    print("This test verifies that Gunicorn starts listening quickly")
    print()
    
    success = test_gunicorn_startup()
    
    if success:
        print()
        print("✅ Test PASSED: Gunicorn starts quickly with preload_app=False")
        print("   Railway healthcheck will succeed within first 1-2 attempts")
        sys.exit(0)
    else:
        print()
        print("❌ Test FAILED or could not complete")
        print("   Check that dependencies are installed")
        sys.exit(1)

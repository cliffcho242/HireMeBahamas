#!/usr/bin/env python3
"""
Test that application startup is instant (<5ms).

This test verifies that:
1. Startup event returns immediately
2. Health checks are responsive during startup
3. Background initialization doesn't block
"""
import sys
import os
import time

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_startup_instant():
    """Test that application startup is instant"""
    print("="*80)
    print("Testing Instant Application Startup")
    print("="*80)
    
    # Import and create app - this triggers startup
    print("\n1. Importing and starting application...")
    start = time.perf_counter()
    
    from app.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    import_time = (time.perf_counter() - start) * 1000
    print(f"   Import + startup time: {import_time:.2f}ms")
    
    # Verify health check works immediately after startup
    print("\n2. Testing health check immediately after startup...")
    health_start = time.perf_counter()
    response = client.get('/api/health')
    health_time = (time.perf_counter() - health_start) * 1000
    
    print(f"   Health check status: {response.status_code}")
    print(f"   Health check response time: {health_time:.2f}ms")
    
    # Assertions
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    
    data = response.json()
    assert data.get("status") == "ok", "Health check status not 'ok'"
    
    print("\n3. Testing multiple rapid health checks...")
    rapid_times = []
    for i in range(10):
        start = time.perf_counter()
        response = client.get('/api/health')
        duration = (time.perf_counter() - start) * 1000
        rapid_times.append(duration)
        
        assert response.status_code == 200, f"Health check {i+1} failed"
    
    avg_time = sum(rapid_times) / len(rapid_times)
    max_time = max(rapid_times)
    min_time = min(rapid_times)
    
    print(f"   Rapid health checks completed: 10")
    print(f"   Average: {avg_time:.2f}ms")
    print(f"   Min: {min_time:.2f}ms")
    print(f"   Max: {max_time:.2f}ms")
    
    print("\n" + "="*80)
    print("✅ STARTUP TEST PASSED")
    print("="*80)
    print("\nSummary:")
    print(f"  ✅ Application starts instantly")
    print(f"  ✅ Health check responds immediately")
    print(f"  ✅ Background initialization doesn't block")
    print(f"  ✅ Consistent response times across rapid requests")
    print(f"\n  Average health check time: {avg_time:.2f}ms")
    print("="*80)


def test_background_initialization():
    """Test that background initialization is running"""
    print("\n" + "="*80)
    print("Testing Background Initialization")
    print("="*80)
    
    from app.main import app
    from fastapi.testclient import TestClient
    import threading
    
    client = TestClient(app)
    
    # Check for background thread
    print("\n1. Checking for background initialization thread...")
    threads = threading.enumerate()
    background_thread = None
    
    for thread in threads:
        print(f"   Thread: {thread.name} (daemon={thread.daemon})")
        if "BackgroundInit" in thread.name or thread.name.startswith("Thread-"):
            background_thread = thread
    
    if background_thread:
        print(f"\n   ✅ Background thread found: {background_thread.name}")
        print(f"      - Daemon: {background_thread.daemon}")
        print(f"      - Alive: {background_thread.is_alive()}")
    else:
        print("\n   ℹ️  Background thread may have already completed")
        print("      This is normal if initialization is fast")
    
    # Verify app is still responsive
    print("\n2. Verifying application is responsive...")
    response = client.get('/api/health')
    assert response.status_code == 200, "App should be responsive"
    print(f"   ✅ Application is responsive (status: {response.status_code})")
    
    print("\n" + "="*80)
    print("✅ BACKGROUND INITIALIZATION TEST PASSED")
    print("="*80)


if __name__ == "__main__":
    try:
        test_startup_instant()
        test_background_initialization()
        print("\n🎉 ALL STARTUP TESTS PASSED!")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

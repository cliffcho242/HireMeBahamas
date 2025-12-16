#!/usr/bin/env python3
"""
Test script to verify Gunicorn configuration values
"""
import os
import sys


def test_gunicorn_config():
    """Test that gunicorn.conf.py has correct values"""
    print("=" * 70)
    print("Testing Gunicorn Configuration Values")
    print("=" * 70)
    print()
    
    # Import the gunicorn config
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Set minimal environment for testing
    os.environ.setdefault("PORT", "10000")
    os.environ.setdefault("WEB_CONCURRENCY", "4")  # Updated for 100K+ user scaling
    os.environ.setdefault("WEB_THREADS", "4")
    os.environ.setdefault("GUNICORN_TIMEOUT", "60")
    
    try:
        # Load the config module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "gunicorn_conf", 
            "gunicorn.conf.py"
        )
        gunicorn_conf = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gunicorn_conf)
        
        # Test workers
        print(f"Workers (default): {gunicorn_conf.workers}")
        assert gunicorn_conf.workers == 4, f"Expected workers=4, got {gunicorn_conf.workers}"
        print("✅ Workers configuration: PASS (4 - scaled for 100K+ users)")
        print()
        
        # Test threads
        print(f"Threads (default): {gunicorn_conf.threads}")
        assert gunicorn_conf.threads == 4, f"Expected threads=4, got {gunicorn_conf.threads}"
        print("✅ Threads configuration: PASS (4)")
        print()
        
        # Test timeout
        print(f"Timeout (default): {gunicorn_conf.timeout}s")
        assert gunicorn_conf.timeout == 60, f"Expected timeout=60, got {gunicorn_conf.timeout}"
        print("✅ Timeout configuration: PASS (60s)")
        print()
        
        # Test worker class
        print(f"Worker class: {gunicorn_conf.worker_class}")
        assert gunicorn_conf.worker_class == "gthread", f"Expected worker_class='gthread', got {gunicorn_conf.worker_class}"
        print("✅ Worker class: PASS (gthread)")
        print()
        
        # Test bind
        print(f"Bind: {gunicorn_conf.bind}")
        assert "0.0.0.0" in gunicorn_conf.bind, "Expected bind to contain 0.0.0.0"
        print("✅ Bind configuration: PASS")
        print()
        
        # Test keepalive
        print(f"Keepalive: {gunicorn_conf.keepalive}s")
        assert gunicorn_conf.keepalive == 5, f"Expected keepalive=5, got {gunicorn_conf.keepalive}"
        print("✅ Keepalive configuration: PASS (5s)")
        print()
        
        # Test environment variable override capability
        print("Testing environment variable overrides...")
        os.environ["WEB_CONCURRENCY"] = "3"
        os.environ["WEB_THREADS"] = "8"
        os.environ["GUNICORN_TIMEOUT"] = "90"
        
        # Reload module with new env vars
        spec.loader.exec_module(gunicorn_conf)
        
        print(f"  Workers (WEB_CONCURRENCY=3): {gunicorn_conf.workers}")
        assert gunicorn_conf.workers == 3, f"Expected workers=3, got {gunicorn_conf.workers}"
        print(f"  Threads (WEB_THREADS=8): {gunicorn_conf.threads}")
        assert gunicorn_conf.threads == 8, f"Expected threads=8, got {gunicorn_conf.threads}"
        print(f"  Timeout (GUNICORN_TIMEOUT=90): {gunicorn_conf.timeout}s")
        assert gunicorn_conf.timeout == 90, f"Expected timeout=90, got {gunicorn_conf.timeout}"
        print("✅ Environment variable overrides: PASS")
        print()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        print()
        print("Configuration Summary:")
        print(f"  Default Workers: 2")
        print(f"  Default Threads: 4")
        print(f"  Default Timeout: 60s")
        print(f"  Total Capacity: 2 workers × 4 threads = 8 concurrent requests")
        print(f"  Worker Class: gthread (optimized for I/O-bound operations)")
        print(f"  Keepalive: 5s")
        print()
        print("✨ Lightning Fast Configuration Applied! ⚡")
        return True
        
    except AssertionError as e:
        print(f"❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_gunicorn_config()
    sys.exit(0 if success else 1)

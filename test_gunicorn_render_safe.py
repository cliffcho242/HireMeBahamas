#!/usr/bin/env python3
"""
Test script to verify Gunicorn Render-safe configuration
"""
import os
import sys


def test_gunicorn_render_safe_config():
    """Test that gunicorn.conf.py has Render-safe configuration"""
    print("=" * 70)
    print("Testing Gunicorn Render-Safe Configuration")
    print("=" * 70)
    print()
    
    # Import the gunicorn config
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Load the config module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "gunicorn_conf", 
            "gunicorn.conf.py"
        )
        gunicorn_conf = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gunicorn_conf)
        
        # Test bind
        print(f"Bind: {gunicorn_conf.bind}")
        assert gunicorn_conf.bind == "0.0.0.0:10000", f"Expected bind='0.0.0.0:10000', got {gunicorn_conf.bind}"
        print("✅ Bind configuration: PASS (0.0.0.0:10000)")
        print()
        
        # Test workers
        print(f"Workers: {gunicorn_conf.workers}")
        assert gunicorn_conf.workers == 2, f"Expected workers=2, got {gunicorn_conf.workers}"
        print("✅ Workers configuration: PASS (2)")
        print()
        
        # Test worker class
        print(f"Worker class: {gunicorn_conf.worker_class}")
        assert gunicorn_conf.worker_class == "uvicorn.workers.UvicornWorker", f"Expected worker_class='uvicorn.workers.UvicornWorker', got {gunicorn_conf.worker_class}"
        print("✅ Worker class: PASS (uvicorn.workers.UvicornWorker)")
        print()
        
        # Test timeout
        print(f"Timeout: {gunicorn_conf.timeout}s")
        assert gunicorn_conf.timeout == 120, f"Expected timeout=120, got {gunicorn_conf.timeout}"
        print("✅ Timeout configuration: PASS (120s)")
        print()
        
        # Test keepalive
        print(f"Keepalive: {gunicorn_conf.keepalive}s")
        assert gunicorn_conf.keepalive == 5, f"Expected keepalive=5, got {gunicorn_conf.keepalive}"
        print("✅ Keepalive configuration: PASS (5s)")
        print()
        
        # Test preload_app
        print(f"Preload app: {gunicorn_conf.preload_app}")
        assert gunicorn_conf.preload_app == False, f"Expected preload_app=False, got {gunicorn_conf.preload_app}"
        print("✅ Preload app: PASS (False - safe for DB/network)")
        print()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED - Render-Safe Configuration Verified")
        print("=" * 70)
        print()
        print("Configuration Summary (Render-Safe):")
        print(f"  bind = '0.0.0.0:10000'")
        print(f"  workers = 2")
        print(f"  worker_class = 'uvicorn.workers.UvicornWorker'")
        print(f"  timeout = 120")
        print(f"  keepalive = 5")
        print(f"  preload_app = False  # IMPORTANT 🚫 DO NOT preload when DB/network involved")
        print()
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
    success = test_gunicorn_render_safe_config()
    sys.exit(0 if success else 1)

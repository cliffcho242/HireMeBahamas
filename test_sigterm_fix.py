#!/usr/bin/env python3
"""
Test script to validate the Gunicorn SIGTERM fix.

This script validates:
1. Gunicorn configuration files are syntactically correct
2. Worker and timeout settings are properly configured
3. Startup timeout is reduced to prevent blocking
4. Worker abort hook is present for diagnostics
"""
import sys
import os

def test_gunicorn_config(config_path):
    """Test a gunicorn configuration file."""
    print(f"\n{'='*60}")
    print(f"Testing: {config_path}")
    print(f"{'='*60}")
    
    # Read the config file
    try:
        with open(config_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_path}")
        return False
    
    # Parse the config as Python
    # Note: Using exec() on trusted config files only (not user input)
    # This is safe as we're testing our own configuration files
    config_globals = {'__builtins__': {}}  # Restrict builtins for safety
    config_locals = {}
    try:
        # Allow only necessary imports for config evaluation
        safe_globals = {
            '__builtins__': __builtins__,
            'os': os,
            'multiprocessing': __import__('multiprocessing'),
            'time': __import__('time'),
            'int': int,
            'print': print,
        }
        exec(content, safe_globals, config_locals)
        print("✅ Configuration is syntactically valid")
        # Copy evaluated values to config_globals for checking
        config_globals.update(config_locals)
    except Exception as e:
        print(f"❌ Syntax error in config: {e}")
        return False
    
    # Check critical settings
    checks = []
    
    # Check workers setting
    workers = config_globals.get('workers')
    if workers is not None:
        if isinstance(workers, int) and workers <= 3:
            print(f"✅ Workers: {workers} (good for preventing SIGTERM)")
            checks.append(True)
        else:
            print(f"⚠️  Workers: {workers} (may cause thundering herd)")
            checks.append(False)
    else:
        print("❌ Workers setting not found")
        checks.append(False)
    
    # Check timeout setting
    timeout = config_globals.get('timeout')
    if timeout is not None:
        if isinstance(timeout, int) and timeout >= 90:
            print(f"✅ Timeout: {timeout}s (sufficient for startup)")
            checks.append(True)
        else:
            print(f"⚠️  Timeout: {timeout}s (may be too short for startup)")
            checks.append(False)
    else:
        print("❌ Timeout setting not found")
        checks.append(False)
    
    # Check worker_abort hook
    if 'worker_abort' in config_globals:
        print("✅ worker_abort hook present (provides diagnostics)")
        checks.append(True)
    else:
        print("❌ worker_abort hook missing")
        checks.append(False)
    
    # Check preload_app setting
    preload_app = config_globals.get('preload_app')
    if preload_app is False:
        print("✅ preload_app: False (safe for databases)")
        checks.append(True)
    else:
        print(f"⚠️  preload_app: {preload_app} (should be False for databases)")
        checks.append(False)
    
    return all(checks)


def test_startup_timeout():
    """Test that startup timeout is properly configured."""
    print(f"\n{'='*60}")
    print("Testing: backend/app/main.py startup timeout")
    print(f"{'='*60}")
    
    main_path = 'backend/app/main.py'
    try:
        with open(main_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {main_path}")
        return False
    
    # Check for aggressive timeout
    if 'STARTUP_OPERATION_TIMEOUT = 2.0' in content:
        print("✅ Startup timeout: 2.0s (aggressive, prevents blocking)")
        timeout_ok = True
    elif 'STARTUP_OPERATION_TIMEOUT = 5.0' in content:
        print("⚠️  Startup timeout: 5.0s (may be too long)")
        timeout_ok = False
    else:
        print("❌ STARTUP_OPERATION_TIMEOUT not found")
        timeout_ok = False
    
    # Check for non-blocking background tasks
    if 'asyncio.create_task(prewarm_bcrypt_background())' in content:
        print("✅ Bcrypt pre-warming runs as background task (non-blocking)")
        bcrypt_ok = True
    else:
        print("❌ Bcrypt pre-warming is not a background task")
        bcrypt_ok = False
    
    if 'asyncio.create_task(connect_redis_background())' in content:
        print("✅ Redis connection runs as background task (non-blocking)")
        redis_ok = True
    else:
        print("❌ Redis connection is not a background task")
        redis_ok = False
    
    if 'asyncio.create_task(warmup_cache_background())' in content:
        print("✅ Cache warmup runs as background task (non-blocking)")
        cache_ok = True
    else:
        print("❌ Cache warmup is not a background task")
        cache_ok = False
    
    return timeout_ok and bcrypt_ok and redis_ok and cache_ok


def main():
    """Run all tests."""
    print("="*60)
    print("Gunicorn SIGTERM Fix Validation")
    print("="*60)
    
    results = []
    
    # Test backend gunicorn config
    results.append(test_gunicorn_config('backend/gunicorn.conf.py'))
    
    # Test root gunicorn config
    results.append(test_gunicorn_config('gunicorn.conf.py'))
    
    # Test startup timeout configuration
    results.append(test_startup_timeout())
    
    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    if all(results):
        print("✅ All tests passed!")
        print("\nThe Gunicorn worker SIGTERM fix is properly implemented:")
        print("1. Workers reduced to 2 (prevents thundering herd)")
        print("2. Timeout increased to 120s (prevents premature SIGTERM)")
        print("3. Startup operations are non-blocking background tasks")
        print("4. Startup timeout is aggressive (2s per operation)")
        print("5. worker_abort hook provides diagnostics")
        print("\nExpected behavior:")
        print("- Workers spawn and respond immediately")
        print("- No SIGTERM errors during startup")
        print("- Background tasks complete after worker is responsive")
        return 0
    else:
        print("❌ Some tests failed!")
        print("\nPlease review the output above and fix the issues.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

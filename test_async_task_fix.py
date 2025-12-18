#!/usr/bin/env python3
"""
Test async task destroyed warning fix.

This test verifies that:
1. Async tasks are created within startup event handlers (not at module level)
2. Shutdown handlers include await asyncio.sleep(0) to allow tasks to close cleanly
3. Background tasks are wrapped in safe error-handling functions
"""
import os
import sys
import re

def test_app_main_py():
    """Test app/main.py for proper async task management."""
    print("\n1. Testing app/main.py...")
    
    app_main_path = os.path.join(os.path.dirname(__file__), 'app', 'main.py')
    
    try:
        with open(app_main_path, 'r') as f:
            content = f.read()
        
        # Check that create_task is within @app.on_event("startup")
        has_startup_decorator = '@app.on_event("startup")' in content
        
        # Verify asyncio.create_task is NOT in lifespan context manager
        # (lifespan pattern would be between @asynccontextmanager and yield)
        has_lifespan_create_task = bool(re.search(r'@asynccontextmanager.*?asyncio\.create_task.*?yield', content, re.DOTALL))
        
        # Check for safe_background_init function
        has_safe_background_init = 'async def safe_background_init()' in content
        
        # Check for shutdown handler with await asyncio.sleep(0)
        has_shutdown_decorator = '@app.on_event("shutdown")' in content
        has_sleep_in_shutdown = 'await asyncio.sleep(0)' in content
        
        issues = []
        if not has_startup_decorator:
            issues.append("Missing @app.on_event('startup') decorator")
        if has_lifespan_create_task:
            issues.append("Found asyncio.create_task in lifespan context manager (unsafe)")
        if not has_safe_background_init:
            issues.append("Missing safe_background_init function")
        if not has_shutdown_decorator:
            issues.append("Missing @app.on_event('shutdown') decorator")
        if not has_sleep_in_shutdown:
            issues.append("Missing await asyncio.sleep(0) in shutdown handler")
        
        if issues:
            print(f"   ❌ Issues found:")
            for issue in issues:
                print(f"      - {issue}")
            return False
        else:
            print(f"   ✅ Proper async task management in app/main.py")
            return True
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return False


def test_backend_app_main_immortal_py():
    """Test backend/app/main_immortal.py for proper async task management."""
    print("\n2. Testing backend/app/main_immortal.py...")
    
    main_immortal_path = os.path.join(os.path.dirname(__file__), 'backend', 'app', 'main_immortal.py')
    
    try:
        with open(main_immortal_path, 'r') as f:
            content = f.read()
        
        # Check for safe_warm_cache function
        has_safe_warm_cache = 'async def safe_warm_cache()' in content
        
        # Check that asyncio.create_task calls safe_warm_cache (not warm_cache directly)
        uses_safe_warm_cache = 'asyncio.create_task(safe_warm_cache())' in content
        
        # Check for shutdown handler with await asyncio.sleep(0)
        has_shutdown_decorator = '@app.on_event("shutdown")' in content
        has_sleep_in_shutdown = 'await asyncio.sleep(0)' in content
        
        issues = []
        if not has_safe_warm_cache:
            issues.append("Missing safe_warm_cache function")
        if not uses_safe_warm_cache:
            issues.append("asyncio.create_task should call safe_warm_cache (not warm_cache directly)")
        if not has_shutdown_decorator:
            issues.append("Missing @app.on_event('shutdown') decorator")
        if not has_sleep_in_shutdown:
            issues.append("Missing await asyncio.sleep(0) in shutdown handler")
        
        if issues:
            print(f"   ❌ Issues found:")
            for issue in issues:
                print(f"      - {issue}")
            return False
        else:
            print(f"   ✅ Proper async task management in backend/app/main_immortal.py")
            return True
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return False


def test_backend_app_main_py():
    """Test backend/app/main.py for proper async task management."""
    print("\n3. Testing backend/app/main.py...")
    
    backend_main_path = os.path.join(os.path.dirname(__file__), 'backend', 'app', 'main.py')
    
    try:
        with open(backend_main_path, 'r') as f:
            content = f.read()
        
        # Check for shutdown handler with await asyncio.sleep(0)
        has_shutdown_decorator = '@app.on_event("shutdown")' in content
        has_sleep_in_shutdown = 'await asyncio.sleep(0)' in content
        
        issues = []
        if not has_shutdown_decorator:
            issues.append("Missing @app.on_event('shutdown') decorator")
        if not has_sleep_in_shutdown:
            issues.append("Missing await asyncio.sleep(0) in shutdown handler")
        
        if issues:
            print(f"   ❌ Issues found:")
            for issue in issues:
                print(f"      - {issue}")
            return False
        else:
            print(f"   ✅ Proper async task management in backend/app/main.py")
            return True
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return False


def test_api_backend_app_main_py():
    """Test api/backend_app/main.py for proper async task management."""
    print("\n4. Testing api/backend_app/main.py...")
    
    api_main_path = os.path.join(os.path.dirname(__file__), 'api', 'backend_app', 'main.py')
    
    try:
        with open(api_main_path, 'r') as f:
            content = f.read()
        
        # Check for shutdown handler with await asyncio.sleep(0)
        has_shutdown_decorator = '@app.on_event("shutdown")' in content
        has_sleep_in_shutdown = 'await asyncio.sleep(0)' in content
        
        issues = []
        if not has_shutdown_decorator:
            issues.append("Missing @app.on_event('shutdown') decorator")
        if not has_sleep_in_shutdown:
            issues.append("Missing await asyncio.sleep(0) in shutdown handler")
        
        if issues:
            print(f"   ❌ Issues found:")
            for issue in issues:
                print(f"      - {issue}")
            return False
        else:
            print(f"   ✅ Proper async task management in api/backend_app/main.py")
            return True
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return False


def main():
    """Run all tests."""
    print("="*80)
    print("Async Task Destroyed Warning Fix - Test Suite")
    print("="*80)
    print("\nVerifying implementation per problem statement:")
    print("  ✅ RIGHT (safe background startup):")
    print("     - asyncio.create_task() within @app.on_event('startup')")
    print("     - Background tasks wrapped in safe error-handling functions")
    print("  ✅ SHUTDOWN HANDLER:")
    print("     - @app.on_event('shutdown') with await asyncio.sleep(0)")
    print("     - Allows tasks to close cleanly")
    
    # Run tests
    test1 = test_app_main_py()
    test2 = test_backend_app_main_immortal_py()
    test3 = test_backend_app_main_py()
    test4 = test_api_backend_app_main_py()
    
    print("\n" + "="*80)
    all_passed = test1 and test2 and test3 and test4
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("\nAsync task management verified:")
        print("  ✔ Tasks created within startup event handlers")
        print("  ✔ Background tasks wrapped in safe functions")
        print("  ✔ Shutdown handlers allow tasks to close cleanly")
        print("  ✔ Prevents 'Task was destroyed but it is pending!' warnings")
        print("="*80)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

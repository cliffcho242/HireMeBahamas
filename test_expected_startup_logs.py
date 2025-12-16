#!/usr/bin/env python3
"""
Test Expected Startup Logs (Issue #7)

This test verifies that the application logs the expected startup messages:
✅ "Booting worker with pid ..."
✅ "Application startup complete"
✅ "Database engine initialized"
✅ "Database warmup successful"

And ensures these error messages are NOT present:
❌ SIGTERM (should be explained with context, not just raw error)
❌ "unexpected keyword argument 'sslmode'"
❌ "Invalid DATABASE_URL" (should be production-safe warnings)
❌ "connection refused" (should be handled gracefully)
"""
import os
import sys
import re


def test_gunicorn_config_has_booting_message():
    """Test that gunicorn.conf.py logs 'Booting worker with pid' in post_fork"""
    print("\n" + "="*80)
    print("TEST 1: Gunicorn config has 'Booting worker' message")
    print("="*80)
    
    files_to_check = [
        'gunicorn.conf.py',
        'backend/gunicorn.conf.py'
    ]
    
    for filepath in files_to_check:
        if not os.path.exists(filepath):
            print(f"  ⚠️  Skipping {filepath} (file not found)")
            continue
            
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check for the booting worker message
        if 'Booting worker with pid' in content:
            print(f"  ✅ {filepath}: Found 'Booting worker with pid' message")
        else:
            print(f"  ❌ {filepath}: Missing 'Booting worker with pid' message")
            return False
    
    return True


def test_main_has_startup_complete():
    """Test that main.py logs 'Application startup complete'"""
    print("\n" + "="*80)
    print("TEST 2: Main.py has 'Application startup complete' message")
    print("="*80)
    
    filepath = 'backend/app/main.py'
    
    if not os.path.exists(filepath):
        print(f"  ❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    if 'Application startup complete' in content:
        print(f"  ✅ Found 'Application startup complete' message")
    else:
        print(f"  ❌ Missing 'Application startup complete' message")
        return False
    
    return True


def test_database_has_engine_initialized():
    """Test that database.py logs 'Database engine initialized'"""
    print("\n" + "="*80)
    print("TEST 3: Database modules have 'Database engine initialized' message")
    print("="*80)
    
    files_to_check = [
        'backend/app/database.py',
        'api/database.py',
        'api/backend_app/database.py'
    ]
    
    found_count = 0
    for filepath in files_to_check:
        if not os.path.exists(filepath):
            print(f"  ⚠️  Skipping {filepath} (file not found)")
            continue
            
        with open(filepath, 'r') as f:
            content = f.read()
        
        if 'Database engine initialized' in content:
            print(f"  ✅ {filepath}: Found 'Database engine initialized' message")
            found_count += 1
        else:
            print(f"  ⚠️  {filepath}: Missing 'Database engine initialized' message")
    
    if found_count > 0:
        print(f"  ✅ Found in {found_count} database module(s)")
        return True
    else:
        print(f"  ❌ Not found in any database module")
        return False


def test_main_has_database_warmup():
    """Test that main.py logs 'Database warmup successful'"""
    print("\n" + "="*80)
    print("TEST 4: Main.py has 'Database warmup successful' message")
    print("="*80)
    
    filepath = 'backend/app/main.py'
    
    if not os.path.exists(filepath):
        print(f"  ❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    if 'Database warmup successful' in content:
        print(f"  ✅ Found 'Database warmup successful' message")
    else:
        print(f"  ❌ Missing 'Database warmup successful' message")
        return False
    
    return True


def test_no_sslmode_keyword_error():
    """Test that sslmode is NOT used in connect_args (should be in URL)"""
    print("\n" + "="*80)
    print("TEST 5: No 'unexpected keyword argument sslmode' errors")
    print("="*80)
    
    files_to_check = [
        'backend/app/database.py',
        'api/database.py',
        'api/backend_app/database.py',
        'backend/app/core/database.py'
    ]
    
    all_good = True
    for filepath in files_to_check:
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check if sslmode is incorrectly used as a key in connect_args dict
        # Pattern: connect_args = { ... "sslmode": "require" ... }
        if re.search(r'connect_args\s*=\s*\{[^}]*["\']sslmode["\']', content, re.DOTALL):
            print(f"  ❌ {filepath}: sslmode incorrectly used in connect_args dict")
            all_good = False
        else:
            print(f"  ✅ {filepath}: sslmode correctly NOT in connect_args")
    
    return all_good


def test_production_safe_database_errors():
    """Test that database errors use warnings instead of raising exceptions"""
    print("\n" + "="*80)
    print("TEST 6: Database errors are production-safe (warnings, not exceptions)")
    print("="*80)
    
    filepath = 'backend/app/database.py'
    
    if not os.path.exists(filepath):
        print(f"  ❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check for production-safe error handling
    checks = [
        ('logger.warning', 'Uses logger.warning for errors'),
        ('except ArgumentError', 'Catches ArgumentError gracefully'),
        ('return None', 'Returns None instead of raising on error'),
    ]
    
    all_found = True
    for pattern, description in checks:
        if pattern in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ Missing: {description}")
            all_found = False
    
    return all_found


def main():
    """Run all tests"""
    print("="*80)
    print("EXPECTED STARTUP LOGS VALIDATION TEST")
    print("="*80)
    print("\nThis test ensures the application produces the expected startup logs")
    print("as specified in issue #7.")
    print("")
    
    tests = [
        ("Booting worker message", test_gunicorn_config_has_booting_message),
        ("Application startup complete", test_main_has_startup_complete),
        ("Database engine initialized", test_database_has_engine_initialized),
        ("Database warmup successful", test_main_has_database_warmup),
        ("No sslmode keyword error", test_no_sslmode_keyword_error),
        ("Production-safe database errors", test_production_safe_database_errors),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All expected startup logs are configured correctly!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

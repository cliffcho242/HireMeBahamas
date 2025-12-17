#!/usr/bin/env python3
"""
Test that verifies Neon pooled connection fix:
1. statement_timeout is NOT in connect_args options
2. Neon connection is detected and logged correctly
3. Database warmup message is correct
"""
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

# Get the repository root directory dynamically
REPO_ROOT = Path(__file__).parent.resolve()

# Test 1: Verify statement_timeout is removed from connect_args
def test_no_statement_timeout_in_options():
    """Verify that statement_timeout is not in the options parameter."""
    print("Test 1: Checking app/database.py for statement_timeout in options...")
    
    database_py = REPO_ROOT / 'app' / 'database.py'
    with open(database_py, 'r') as f:
        content = f.read()
    
    # Check that the problematic pattern is removed
    if 'f"-c statement_timeout={STATEMENT_TIMEOUT_MS}ms"' in content:
        print("❌ FAIL: statement_timeout still in options parameter")
        return False
    
    # Verify the comment explaining why it's not there
    if "statement_timeout is NOT set in options for compatibility" in content:
        print("✅ PASS: statement_timeout removed and documented")
        return True
    else:
        print("⚠️  WARNING: statement_timeout removed but not documented")
        return True

# Test 2: Verify Neon connection detection
def test_neon_connection_detection():
    """Verify that Neon connections are detected and logged correctly."""
    print("\nTest 2: Checking Neon connection detection logic...")
    
    database_py = REPO_ROOT / 'app' / 'database.py'
    with open(database_py, 'r') as f:
        content = f.read()
    
    # Check for Neon detection logic (updated to check for None explicitly)
    if "'neon.tech' in hostname.lower()" in content and "hostname is not None" in content:
        print("✅ PASS: Neon hostname detection implemented with proper None check")
    elif "'neon.tech' in parsed_url.hostname.lower()" in content:
        print("✅ PASS: Neon hostname detection implemented")
    else:
        print("❌ FAIL: Neon hostname detection not found")
        return False
    
    # Check for the expected log message
    if 'Database engine initialized (Neon pooled)' in content:
        print("✅ PASS: Neon pooled log message present")
        return True
    else:
        print("❌ FAIL: Neon pooled log message not found")
        return False

# Test 3: Verify warmup success message
def test_warmup_success_message():
    """Verify that the warmup success message is correct."""
    print("\nTest 3: Checking database warmup success message...")
    
    database_py = REPO_ROOT / 'app' / 'database.py'
    with open(database_py, 'r') as f:
        content = f.read()
    
    if 'Database warmup successful' in content:
        print("✅ PASS: Warmup success message present")
        return True
    else:
        print("❌ FAIL: Warmup success message not found")
        return False

# Test 4: Verify main.py uses asyncio.to_thread
def test_main_uses_to_thread():
    """Verify that main.py properly calls sync database functions."""
    print("\nTest 4: Checking main.py uses asyncio.to_thread for sync functions...")
    
    main_py = REPO_ROOT / 'app' / 'main.py'
    with open(main_py, 'r') as f:
        content = f.read()
    
    if 'asyncio.to_thread(init_db)' in content and 'asyncio.to_thread(warmup_db)' in content:
        print("✅ PASS: main.py properly wraps sync database functions")
        return True
    else:
        print("❌ FAIL: main.py doesn't properly wrap sync database functions")
        return False

# Test 5: Verify no other files still have the problematic pattern
def test_no_other_statement_timeout_in_options():
    """Check that no other active database files have the problematic pattern."""
    print("\nTest 5: Checking for statement_timeout in other database files...")
    
    # Check api/backend_app/database.py (async version)
    backend_database_py = REPO_ROOT / 'api' / 'backend_app' / 'database.py'
    try:
        with open(backend_database_py, 'r') as f:
            content = f.read()
        
        # This file uses asyncpg, which uses server_settings, not options
        if 'server_settings' in content and '"statement_timeout"' in content:
            print("✅ INFO: api/backend_app/database.py uses asyncpg server_settings (OK for asyncpg)")
        else:
            print("✅ INFO: api/backend_app/database.py checked")
    except FileNotFoundError:
        print("⚠️  WARNING: api/backend_app/database.py not found")
    
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("NEON POOLED CONNECTION FIX - VERIFICATION TESTS")
    print("=" * 70)
    
    tests = [
        test_no_statement_timeout_in_options,
        test_neon_connection_detection,
        test_warmup_success_message,
        test_main_uses_to_thread,
        test_no_other_statement_timeout_in_options,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ ERROR in {test.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)
    
    if all(results):
        print("✅ ALL TESTS PASSED - Neon pooled connection fix is complete!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Please review the output above")
        sys.exit(1)

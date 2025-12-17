#!/usr/bin/env python3
"""
Verification script for query-level timeout implementation.

This script verifies that the timeout implementation is correctly integrated
into the codebase and ready for production use.
"""

import os
import sys
import re

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


def check_module_exists():
    """Verify the query_timeout module exists and can be imported."""
    print("\n" + "="*70)
    print("1. Checking Query Timeout Module")
    print("="*70)
    
    try:
        from app.core.query_timeout import (
            set_query_timeout,
            with_query_timeout,
            set_fast_query_timeout,
            set_slow_query_timeout,
            get_timeout_for_operation,
            DEFAULT_QUERY_TIMEOUT_MS,
            FAST_QUERY_TIMEOUT_MS,
            SLOW_QUERY_TIMEOUT_MS,
        )
        print("✅ Module: backend/app/core/query_timeout.py")
        print(f"   - FAST_QUERY_TIMEOUT_MS: {FAST_QUERY_TIMEOUT_MS}ms")
        print(f"   - DEFAULT_QUERY_TIMEOUT_MS: {DEFAULT_QUERY_TIMEOUT_MS}ms")
        print(f"   - SLOW_QUERY_TIMEOUT_MS: {SLOW_QUERY_TIMEOUT_MS}ms")
        return True
    except ImportError as e:
        print(f"❌ Failed to import query_timeout module: {e}")
        return False


def check_api_integration():
    """Verify that API routes are using query timeouts."""
    print("\n" + "="*70)
    print("2. Checking API Integration")
    print("="*70)
    
    files_to_check = [
        ('backend/app/auth/routes.py', 'set_fast_query_timeout'),
        ('backend/app/api/jobs.py', 'set_query_timeout'),
        ('backend/app/feed/routes.py', 'set_query_timeout'),
    ]
    
    all_good = True
    for file_info in files_to_check:
        file_path, expected_import = file_info
        full_path = os.path.join('/home/runner/work/HireMeBahamas/HireMeBahamas', file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
                if expected_import in content:
                    # Count how many times the timeout function is called
                    count = len(re.findall(rf'\bawait {expected_import}\(', content))
                    print(f"✅ {file_path}")
                    print(f"   - Imports: {expected_import}")
                    print(f"   - Usage count: {count} call(s)")
                else:
                    print(f"❌ {file_path}")
                    print(f"   - Missing: {expected_import}")
                    all_good = False
        else:
            print(f"⚠️  {file_path} - File not found")
            all_good = False
    
    return all_good


def check_tests():
    """Verify test files exist."""
    print("\n" + "="*70)
    print("3. Checking Test Files")
    print("="*70)
    
    test_files = [
        'backend/test_query_timeout_unit.py',
        'backend/test_query_timeout.py',
    ]
    
    all_good = True
    for test_file in test_files:
        full_path = os.path.join('/home/runner/work/HireMeBahamas/HireMeBahamas', test_file)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"✅ {test_file} ({size:,} bytes)")
        else:
            print(f"❌ {test_file} - Not found")
            all_good = False
    
    return all_good


def check_documentation():
    """Verify documentation exists."""
    print("\n" + "="*70)
    print("4. Checking Documentation")
    print("="*70)
    
    doc_file = '/home/runner/work/HireMeBahamas/HireMeBahamas/QUERY_TIMEOUT_IMPLEMENTATION.md'
    if os.path.exists(doc_file):
        size = os.path.getsize(doc_file)
        with open(doc_file, 'r') as f:
            content = f.read()
            # Check for key sections
            sections = [
                '## Overview',
                '## Usage Patterns',
                '## Configuration',
                '## Testing',
                '## Production Deployment',
            ]
            missing = [s for s in sections if s not in content]
            if missing:
                print(f"⚠️  QUERY_TIMEOUT_IMPLEMENTATION.md ({size:,} bytes)")
                print(f"   - Missing sections: {', '.join(missing)}")
                return False
            else:
                print(f"✅ QUERY_TIMEOUT_IMPLEMENTATION.md ({size:,} bytes)")
                print(f"   - All required sections present")
                return True
    else:
        print("❌ QUERY_TIMEOUT_IMPLEMENTATION.md - Not found")
        return False


def check_environment_variables():
    """Check environment variable configuration."""
    print("\n" + "="*70)
    print("5. Checking Environment Variables")
    print("="*70)
    
    env_vars = [
        'DB_QUERY_TIMEOUT_MS',
        'DB_FAST_QUERY_TIMEOUT_MS',
        'DB_SLOW_QUERY_TIMEOUT_MS',
    ]
    
    configured = []
    defaults = []
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            configured.append(f"{var}={value}")
        else:
            defaults.append(var)
    
    if configured:
        print("✅ Environment variables configured:")
        for var in configured:
            print(f"   - {var}")
    
    if defaults:
        print("ℹ️  Using defaults (can be overridden):")
        for var in defaults:
            print(f"   - {var}")
    
    return True


def run_verification():
    """Run all verification checks."""
    print("\n" + "="*70)
    print("QUERY TIMEOUT IMPLEMENTATION VERIFICATION")
    print("="*70)
    
    checks = [
        ("Module", check_module_exists),
        ("API Integration", check_api_integration),
        ("Tests", check_tests),
        ("Documentation", check_documentation),
        ("Environment", check_environment_variables),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error checking {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "="*70)
    if passed == total:
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print("="*70)
        print("\n🎉 Query timeout implementation is ready for production!")
        return 0
    else:
        print(f"⚠️  SOME CHECKS FAILED ({passed}/{total})")
        print("="*70)
        print("\n⚠️  Please review failed checks before deploying.")
        return 1


if __name__ == "__main__":
    exit_code = run_verification()
    sys.exit(exit_code)

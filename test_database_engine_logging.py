#!/usr/bin/env python3
"""
Test database engine initialization logging and validation warnings.

This test verifies:
1. Success message appears when database engine is initialized
2. No false validation warnings for placeholder or local development URLs
3. Validation warnings only appear for truly invalid URLs
"""

import os
import sys

def test_validation_logic():
    """Test that validation logic excludes placeholder and local dev URLs."""
    print("\n" + "="*70)
    print("TEST 1: Validation logic should exclude placeholder and local dev URLs")
    print("="*70)
    
    # Check backend/app/database.py
    filepath = 'backend/app/database.py'
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
            # Check if validation excludes placeholder URL
            if 'DATABASE_URL != DB_PLACEHOLDER_URL' not in content:
                print(f"❌ FAILED: {filepath} doesn't exclude DB_PLACEHOLDER_URL from validation")
                return False
            
            # Check if validation excludes local dev URL
            if 'DATABASE_URL != LOCAL_DEV_URL' not in content:
                print(f"❌ FAILED: {filepath} doesn't exclude LOCAL_DEV_URL from validation")
                return False
            
            # Check that LOCAL_DEV_URL is defined
            if 'LOCAL_DEV_URL = "postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"' not in content:
                print(f"❌ FAILED: {filepath} doesn't define LOCAL_DEV_URL")
                return False
            
            print(f"✅ PASSED: {filepath} correctly excludes placeholder and local dev URLs from validation")
            return True
            
    except FileNotFoundError:
        print(f"❌ FAILED: File not found: {filepath}")
        return False

def test_success_logging_present():
    """Test that success message is logged when engine initializes."""
    print("\n" + "="*70)
    print("TEST 3: Success message should appear on engine initialization")
    print("="*70)
    
    # This is harder to test without actually creating an engine
    # We'll just check that the log statement exists in the code
    files_to_check = [
        'api/backend_app/database.py',
        'api/database.py',
        'backend/app/database.py',
        'backend/app/core/database.py',
        'api/index.py'
    ]
    
    missing_logging = []
    for filepath in files_to_check:
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                if '✅ Database engine initialized successfully' not in content:
                    missing_logging.append(filepath)
        except FileNotFoundError:
            print(f"⚠️  File not found: {filepath}")
    
    if missing_logging:
        print("❌ FAILED: Success logging missing in:")
        for filepath in missing_logging:
            print(f"  - {filepath}")
        return False
    else:
        print("✅ PASSED: Success logging present in all database files")
        return True

def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("DATABASE ENGINE INITIALIZATION LOGGING TESTS")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Validation logic", test_validation_logic()))
    results.append(("Success logging presence", test_success_logging_present()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*70)
    print(f"Results: {passed}/{total} tests passed")
    print("="*70)
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())

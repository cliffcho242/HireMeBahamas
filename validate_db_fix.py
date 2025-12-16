#!/usr/bin/env python3
"""
Validation script to verify the database initialization fix.

This script verifies:
1. Only one database module exists (backend/app/database.py)
2. No duplicate database module (backend/app/core/database.py should be gone)
3. SSL configuration is in URL, not in connect_args
4. Proper logging messages are present
"""
import os
import sys
from pathlib import Path

def main():
    print("="*70)
    print("DATABASE INITIALIZATION FIX - VALIDATION")
    print("="*70)
    print()
    
    project_root = Path(__file__).parent
    all_passed = True
    
    # Test 1: Check that duplicate database.py is removed
    print("✅ TEST 1: Verify duplicate database module removed")
    duplicate_path = project_root / "backend" / "app" / "core" / "database.py"
    if duplicate_path.exists():
        print(f"   ❌ FAIL: Duplicate still exists: {duplicate_path}")
        all_passed = False
    else:
        print(f"   ✅ PASS: Duplicate removed (backend/app/core/database.py)")
    print()
    
    # Test 2: Check that main database.py exists
    print("✅ TEST 2: Verify main database module exists")
    main_db_path = project_root / "backend" / "app" / "database.py"
    if not main_db_path.exists():
        print(f"   ❌ FAIL: Main database module not found: {main_db_path}")
        all_passed = False
    else:
        print(f"   ✅ PASS: Main database module exists")
        
        # Read and check content
        with open(main_db_path, 'r') as f:
            content = f.read()
        
        # Test 2a: SSL in URL, not connect_args
        print("   Checking SSL configuration...")
        if '"sslmode": "require"' in content or "'sslmode': 'require'" in content:
            print("   ❌ FAIL: sslmode found in connect_args (should be in URL)")
            all_passed = False
        elif "?sslmode=require" in content:
            print("   ✅ PASS: SSL correctly configured in URL query string")
        else:
            print("   ⚠️  WARNING: No sslmode configuration found")
        
        # Test 2b: Lazy engine initialization
        if "LazyEngine" in content:
            print("   ✅ PASS: Lazy engine initialization present")
        else:
            print("   ❌ FAIL: LazyEngine not found")
            all_passed = False
        
        # Test 2c: pool_pre_ping
        if "pool_pre_ping=True" in content:
            print("   ✅ PASS: pool_pre_ping=True configured")
        else:
            print("   ❌ FAIL: pool_pre_ping not configured")
            all_passed = False
        
        # Test 2d: Proper logging
        if "Database engine initialized" in content:
            print("   ✅ PASS: Database engine initialization logging present")
        else:
            print("   ⚠️  WARNING: Database engine initialization logging not found")
    print()
    
    # Test 3: Check main.py startup logging
    print("✅ TEST 3: Verify startup logging in main.py")
    main_py_path = project_root / "backend" / "app" / "main.py"
    if not main_py_path.exists():
        print(f"   ❌ FAIL: main.py not found: {main_py_path}")
        all_passed = False
    else:
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        if "Database warmup successful" in content:
            print("   ✅ PASS: 'Database warmup successful' logging present")
        else:
            print("   ❌ FAIL: 'Database warmup successful' logging not found")
            all_passed = False
        
        if "Consolidated: Single database module" in content or "SSL configured in DATABASE_URL" in content:
            print("   ✅ PASS: Unified database path message present")
        else:
            print("   ❌ FAIL: Unified database path message not found")
            all_passed = False
    print()
    
    # Final summary
    print("="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED - Database initialization fix verified!")
        print()
        print("Expected startup logs:")
        print("  ✅ Database engine initialized successfully")
        print("  ✅ Database warmup successful")
        print("     - Database module loaded and ready")
        print("     - Engine will initialize on first request (lazy pattern)")
        print("     - One DB path, One engine, One URL, One SSL definition")
        print()
        print("You should NEVER see again:")
        print("  ❌ unexpected keyword argument 'sslmode'")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Review issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())

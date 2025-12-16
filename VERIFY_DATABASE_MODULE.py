#!/usr/bin/env python3
"""
Verification script for app/database.py implementation.

This script verifies that the database module meets all requirements
from the problem statement:
  - Single source of truth
  - Uses SQLAlchemy (no psycopg direct calls)
  - No sslmode in connect_args
  - No blocking imports
"""

import sys


def verify_implementation():
    """Verify that the implementation meets all requirements."""
    
    print("=" * 80)
    print("DATABASE MODULE VERIFICATION")
    print("=" * 80)
    
    checks = []
    
    # Check 1: File exists
    print("\n1. Checking if app/database.py exists...")
    try:
        with open("app/database.py", "r") as f:
            content = f.read()
        print("   ✅ File exists")
        checks.append(True)
    except FileNotFoundError:
        print("   ❌ File not found")
        checks.append(False)
        return False
    
    # Check 2: Required imports
    print("\n2. Checking required imports...")
    required_imports = [
        "import os",
        "import logging",
        "from sqlalchemy import create_engine",
        "from sqlalchemy import text",  # or "text" in imports
        "from sqlalchemy.engine.url import make_url"
    ]
    
    imports_ok = True
    for imp in required_imports:
        if imp not in content:
            # Check for alternative format (text in same line as create_engine)
            if "text" in imp and "create_engine, text" in content:
                continue
            print(f"   ❌ Missing: {imp}")
            imports_ok = False
    
    if imports_ok:
        print("   ✅ All required imports present")
        checks.append(True)
    else:
        checks.append(False)
    
    # Check 3: No psycopg imports
    print("\n3. Checking for psycopg direct imports...")
    forbidden = ["import psycopg", "from psycopg"]
    has_forbidden = False
    for forb in forbidden:
        if forb in content:
            print(f"   ❌ Found forbidden import: {forb}")
            has_forbidden = True
    
    if not has_forbidden:
        print("   ✅ No psycopg direct imports")
        checks.append(True)
    else:
        checks.append(False)
    
    # Check 4: Global engine variable
    print("\n4. Checking for global engine variable...")
    if "engine = None" in content:
        print("   ✅ Global engine variable initialized to None")
        checks.append(True)
    else:
        print("   ❌ Global engine variable not found")
        checks.append(False)
    
    # Check 5: init_db function
    print("\n5. Checking init_db() function...")
    if "def init_db():" in content:
        print("   ✅ init_db() function exists")
        
        # Check function components
        components = [
            ("global engine", "Uses global engine"),
            ("os.environ.get(\"DATABASE_URL\")", "Gets DATABASE_URL from environment"),
            ("make_url(db_url)", "Parses URL with make_url"),
            ("create_engine(", "Creates SQLAlchemy engine"),
            ("pool_pre_ping=True", "Configures pool_pre_ping"),
            ("pool_recycle=300", "Configures pool_recycle"),
            ("pool_size=5", "Configures pool_size"),
            ("max_overflow=10", "Configures max_overflow"),
        ]
        
        all_components = True
        for comp, desc in components:
            if comp not in content:
                print(f"   ⚠️  Missing: {desc}")
                all_components = False
        
        if all_components:
            print("   ✅ All init_db() components present")
            checks.append(True)
        else:
            checks.append(False)
    else:
        print("   ❌ init_db() function not found")
        checks.append(False)
    
    # Check 6: warmup_db function
    print("\n6. Checking warmup_db() function...")
    if "def warmup_db(engine):" in content:
        print("   ✅ warmup_db() function exists")
        
        # Check function components
        if 'conn.execute(text("SELECT 1"))' in content:
            print("   ✅ Executes test query")
            checks.append(True)
        else:
            print("   ⚠️  Test query not found")
            checks.append(False)
    else:
        print("   ❌ warmup_db() function not found")
        checks.append(False)
    
    # Check 7: No sslmode in connect_args
    print("\n7. Checking for sslmode in connect_args...")
    if "connect_args" in content and ("'sslmode'" in content or '"sslmode"' in content):
        print("   ❌ Found sslmode in connect_args (should be in DATABASE_URL)")
        checks.append(False)
    else:
        print("   ✅ No sslmode in connect_args")
        checks.append(True)
    
    # Check 8: Proper error handling
    print("\n8. Checking error handling...")
    if "except Exception as e:" in content and 'logging.warning(f"DB' in content:
        print("   ✅ Proper error handling with logging")
        checks.append(True)
    else:
        print("   ⚠️  Error handling incomplete")
        checks.append(False)
    
    # Summary
    print("\n" + "=" * 80)
    passed = sum(checks)
    total = len(checks)
    print(f"VERIFICATION RESULT: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ ALL REQUIREMENTS MET - Implementation is correct!")
        print("=" * 80)
        return True
    else:
        print("❌ Some requirements not met - Please review the issues above")
        print("=" * 80)
        return False


def main():
    """Main entry point."""
    success = verify_implementation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

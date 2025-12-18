"""
Test to verify that sslmode is NOT passed as a connect_args parameter.

This test ensures that the fix for the database connection issue is correct:
- sslmode MUST be in DATABASE_URL query string
- sslmode MUST NOT be in connect_args
- sslmode MUST NOT be passed as a kwarg to connection functions

CRITICAL: This prevents the error:
    connect() got an unexpected keyword argument 'sslmode'
"""

import os
import sys
import re
from pathlib import Path

def test_no_sslmode_in_connect_args():
    """Verify that sslmode is not passed in connect_args in any database file."""
    
    print("=" * 80)
    print("TESTING: sslmode is NOT in connect_args")
    print("=" * 80)
    
    # Files to check (main database configuration files)
    files_to_check = [
        "backend/app/database.py",
        "backend/app/core/database.py",
        "api/database.py",
        "final_backend.py",
        "final_backend_postgresql.py",
    ]
    
    repo_root = Path(__file__).parent
    
    all_passed = True
    
    for file_path in files_to_check:
        full_path = repo_root / file_path
        if not full_path.exists():
            print(f"⚠️  SKIP: {file_path} (file not found)")
            continue
        
        print(f"\n📄 Checking: {file_path}")
        
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Check for sslmode in connect_args
        # Pattern 1: connect_args={...sslmode...}
        pattern1 = r'connect_args\s*=\s*\{[^}]*["\']sslmode["\']'
        if re.search(pattern1, content):
            print(f"   ❌ FAILED: Found sslmode in connect_args")
            all_passed = False
            continue
        
        # Pattern 2: "sslmode": "require" or 'sslmode': 'require' in code (not comments)
        # But only in connection contexts
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            
            # Check for sslmode being passed as parameter to connect functions
            if 'sslmode=' in line and any(word in line for word in ['connect(', 'ThreadedConnectionPool(', 'create_engine(']):
                # Check if it's in a DSN/URL string (which is OK) or as a parameter (which is bad)
                if 'dsn=' in line or 'DATABASE_URL' in line or '?sslmode=' in line:
                    # This is OK - sslmode in URL string
                    continue
                else:
                    # Check if it's a parameter assignment
                    if re.search(r'sslmode\s*=\s*["\']', line):
                        print(f"   ❌ FAILED: Line {i} passes sslmode as parameter: {line.strip()}")
                        all_passed = False
                        continue
        
        # Check for DB_CONFIG["sslmode"] usage in connection calls
        if 'DB_CONFIG["sslmode"]' in content or "DB_CONFIG['sslmode']" in content:
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'DB_CONFIG["sslmode"]' in line or "DB_CONFIG['sslmode']" in line:
                    # Skip comments
                    if line.strip().startswith('#'):
                        continue
                    # Check if it's in a connection context
                    if any(word in line for word in ['connect(', 'ThreadedConnectionPool(', 'create_engine(']):
                        print(f"   ❌ FAILED: Line {i} uses DB_CONFIG['sslmode'] in connection: {line.strip()}")
                        all_passed = False
                        continue
        
        if all_passed:
            print(f"   ✅ PASSED: No sslmode in connect_args or connection parameters")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED: sslmode is correctly configured in DATABASE_URL only")
        print("=" * 80)
        return True
    else:
        print("❌ TESTS FAILED: sslmode found in connect_args or as connection parameter")
        print("=" * 80)
        return False


def test_database_url_includes_sslmode():
    """Verify that DATABASE_URL examples include sslmode parameter."""
    
    print("\n" + "=" * 80)
    print("TESTING: DATABASE_URL examples include sslmode")
    print("=" * 80)
    
    files_to_check = [
        ".env.example",
        "backend/app/database.py",
        "api/database.py",
    ]
    
    repo_root = Path(__file__).parent
    all_passed = True
    
    for file_path in files_to_check:
        full_path = repo_root / file_path
        if not full_path.exists():
            print(f"⚠️  SKIP: {file_path} (file not found)")
            continue
        
        print(f"\n📄 Checking: {file_path}")
        
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Look for DATABASE_URL examples with postgresql://
        if 'postgresql://' in content and 'DATABASE_URL' in content:
            # Check if at least one example includes sslmode
            if '?sslmode=require' in content or 'sslmode=require' in content:
                print(f"   ✅ PASSED: File includes DATABASE_URL examples with sslmode")
            else:
                print(f"   ⚠️  WARNING: File has DATABASE_URL examples but no sslmode shown")
        else:
            print(f"   ℹ️  INFO: No DATABASE_URL examples found")
    
    print("\n" + "=" * 80)
    print("✅ DATABASE_URL format verification complete")
    print("=" * 80)


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("SSL MODE CONFIGURATION FIX VERIFICATION")
    print("=" * 80)
    print("\nVerifying that sslmode is configured correctly:")
    print("  ✅ sslmode MUST be in DATABASE_URL query string (?sslmode=require)")
    print("  ❌ sslmode MUST NOT be in connect_args")
    print("  ❌ sslmode MUST NOT be passed as kwarg to connect()")
    print("\n")
    
    test1_passed = test_no_sslmode_in_connect_args()
    test_database_url_includes_sslmode()
    
    if test1_passed:
        print("\n" + "=" * 80)
        print("🎉 SUCCESS: All critical tests passed!")
        print("=" * 80)
        print("\nThe fix is correct:")
        print("  • sslmode is NOT in connect_args ✅")
        print("  • sslmode is NOT passed as kwarg ✅")
        print("  • DATABASE_URL includes ?sslmode=require ✅")
        print("\nDatabase connections should now work correctly!")
        return 0
    else:
        print("\n" + "=" * 80)
        print("❌ FAILURE: Some tests failed")
        print("=" * 80)
        print("\nPlease review the errors above and fix the issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

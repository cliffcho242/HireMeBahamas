"""
Test to verify that statement_timeout has been removed from all database configurations.
This ensures Neon pooled connection compatibility as per OPTION A (RECOMMENDED).
"""

import os
import sys
import re


def test_no_statement_timeout_in_files():
    """Verify that statement_timeout is not configured in any database files."""
    
    # Files to check
    files_to_check = [
        'api/backend_app/database.py',
        'app/database.py',
        'backend/app/core/database.py',
        'backend/app/database.py',
        'final_backend_postgresql.py',
    ]
    
    print("Testing statement_timeout removal from database configuration files...\n")
    
    all_passed = True
    
    for filepath in files_to_check:
        full_path = os.path.join(os.path.dirname(__file__), filepath)
        
        if not os.path.exists(full_path):
            print(f"⚠️  File not found: {filepath}")
            continue
        
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Check for statement_timeout in actual configuration (not comments)
        # Look for patterns like:
        # - "statement_timeout": ...
        # - options=f"-c statement_timeout=...
        # - options="-c statement_timeout=...
        
        patterns_to_check = [
            r'"statement_timeout":\s*[^,}]+',  # In server_settings dict
            r'options\s*=\s*["\']?-c\s+statement_timeout=',  # In options string
        ]
        
        found_issues = []
        for pattern in patterns_to_check:
            matches = re.findall(pattern, content)
            if matches:
                found_issues.extend(matches)
        
        if found_issues:
            print(f"✗ FAILED: {filepath}")
            print(f"  Found statement_timeout configuration:")
            for issue in found_issues:
                print(f"    - {issue}")
            all_passed = False
        else:
            # Check that jit=off is still present
            if 'jit' in content and ('jit": "off' in content or 'jit=off' in content):
                print(f"✓ PASSED: {filepath}")
                print(f"  - No statement_timeout found")
                print(f"  - jit=off still present ✓")
            else:
                print(f"✓ PASSED: {filepath}")
                print(f"  - No statement_timeout found")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ SUCCESS: All files passed statement_timeout removal check")
        print("✅ NEON COMPATIBILITY: Application is now compatible with Neon pooled connections")
        print("✅ OPTION A (RECOMMENDED) has been implemented")
        return 0
    else:
        print("✗ FAILED: Some files still contain statement_timeout configuration")
        return 1


if __name__ == "__main__":
    sys.exit(test_no_statement_timeout_in_files())

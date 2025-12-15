#!/usr/bin/env python3
"""
Verification script for DATABASE_URL validation requirements.

This script verifies that the validation enforces all 4 requirements:
1. Host present (not localhost, 127.0.0.1, or empty)
2. Port present (explicit port number)
3. TCP enforced (no Unix sockets)
4. SSL required (sslmode parameter)
"""
import sys
import os

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from db_url_utils import validate_database_url_structure


def check_requirement(requirement_name, test_cases):
    """Check a specific requirement with test cases."""
    print(f"\n{'=' * 80}")
    print(f"Requirement: {requirement_name}")
    print('=' * 80)
    
    passed = 0
    failed = 0
    
    for description, url, should_be_valid in test_cases:
        is_valid, error = validate_database_url_structure(url)
        
        if is_valid == should_be_valid:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"{status}: {description}")
        if not is_valid and error:
            print(f"         Error: {error}")
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def main():
    """Run verification tests for all requirements."""
    print("=" * 80)
    print("DATABASE_URL Validation Requirements Verification")
    print("=" * 80)
    
    all_passed = True
    
    # Requirement 1: Host must be present (not localhost, 127.0.0.1, or empty)
    host_tests = [
        ("Valid remote host", "postgresql://u:p@db.example.com:5432/db?sslmode=require", True),
        ("Valid Neon host", "postgresql://u:p@ep-xxx.neon.tech:5432/db?sslmode=require", True),
        ("Valid Railway host", "postgresql://u:p@db.railway.internal:5432/db?sslmode=require", True),
        ("Empty host (socket usage)", "postgresql://u:p@/db?sslmode=require", False),
        ("localhost host", "postgresql://u:p@localhost:5432/db?sslmode=require", False),
        ("127.0.0.1 host", "postgresql://u:p@127.0.0.1:5432/db?sslmode=require", False),
    ]
    
    if not check_requirement("1. Host must be present (not localhost/127.0.0.1)", host_tests):
        all_passed = False
    
    # Requirement 2: Port must be present
    port_tests = [
        ("Valid with port :5432", "postgresql://u:p@db.example.com:5432/db?sslmode=require", True),
        ("Valid with port :5433", "postgresql://u:p@db.example.com:5433/db?sslmode=require", True),
        ("Missing port", "postgresql://u:p@db.example.com/db?sslmode=require", False),
    ]
    
    if not check_requirement("2. Port must be present (explicit)", port_tests):
        all_passed = False
    
    # Requirement 3: TCP enforced (combined with requirement 1, no Unix sockets)
    tcp_tests = [
        ("Valid TCP connection", "postgresql://u:p@db.example.com:5432/db?sslmode=require", True),
        ("Empty host triggers socket", "postgresql://u:p@/db?sslmode=require", False),
    ]
    
    if not check_requirement("3. TCP enforced (no Unix sockets)", tcp_tests):
        all_passed = False
    
    # Requirement 4: SSL required
    ssl_tests = [
        ("Valid with sslmode=require", "postgresql://u:p@db.example.com:5432/db?sslmode=require", True),
        ("Valid with sslmode=verify-ca", "postgresql://u:p@db.example.com:5432/db?sslmode=verify-ca", True),
        ("Valid with sslmode=verify-full", "postgresql://u:p@db.example.com:5432/db?sslmode=verify-full", True),
        ("Missing sslmode", "postgresql://u:p@db.example.com:5432/db", False),
    ]
    
    if not check_requirement("4. SSL required (sslmode parameter)", ssl_tests):
        all_passed = False
    
    # Final summary
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL REQUIREMENTS VERIFIED")
        print("=" * 80)
        print("\nThe DATABASE_URL validation successfully enforces:")
        print("  ✔ Host present (not localhost, 127.0.0.1, or empty)")
        print("  ✔ Port present (explicit port number)")
        print("  ✔ TCP enforced (no Unix sockets)")
        print("  ✔ SSL required (sslmode parameter)")
        print("\nThe implementation meets all requirements from the problem statement.")
        return 0
    else:
        print("❌ SOME REQUIREMENTS FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())

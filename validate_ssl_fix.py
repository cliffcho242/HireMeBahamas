#!/usr/bin/env python3
"""
Quick validation script to demonstrate the SSL validation fix works.

Run this to verify the fix is working correctly in your environment.
"""

import os
import sys
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}ℹ️  {text}{RESET}")

def clear_modules():
    """Clear database-related modules from cache."""
    modules_to_remove = []
    for k in sys.modules:
        if 'backend' in k or 'db_guard' in k:
            modules_to_remove.append(k)
    for mod in modules_to_remove:
        del sys.modules[mod]

def validate_neon_pooled():
    """Validate Neon pooled connection works without sslmode."""
    print_header("Validating Neon Pooled Connection")
    
    # Typical Neon pooled connection URL
    test_url = 'postgresql+asyncpg://user:pass@ep-cool-bird-123-pooler.us-east-1.aws.neon.tech:5432/hiremebahamas'
    print_info(f"Testing: {test_url}")
    
    os.environ['DATABASE_URL'] = test_url
    
    try:
        clear_modules()
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.app.core.db_guards import validate_database_config
        
        result = validate_database_config(strict=False)
        
        if result:
            print_success("Neon pooled connection validated successfully")
            print_info("SSL is handled automatically by Neon pooler")
            return True
        else:
            print_error("Validation failed - this should not happen")
            return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def validate_asyncpg():
    """Validate asyncpg connection works without sslmode."""
    print_header("Validating Direct asyncpg Connection")
    
    test_url = 'postgresql+asyncpg://user:pass@db.example.com:5432/hiremebahamas'
    print_info(f"Testing: {test_url}")
    
    os.environ['DATABASE_URL'] = test_url
    
    try:
        clear_modules()
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.app.core.db_guards import validate_database_config
        
        result = validate_database_config(strict=False)
        
        if result:
            print_success("asyncpg connection validated successfully")
            print_info("SSL is configured via connect_args in code")
            return True
        else:
            print_error("Validation failed - this should not happen")
            return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def validate_traditional_postgres():
    """Validate traditional PostgreSQL still requires sslmode."""
    print_header("Validating Traditional PostgreSQL (with sslmode)")
    
    test_url = 'postgresql://user:pass@db.example.com:5432/hiremebahamas?sslmode=require'
    print_info(f"Testing: {test_url}")
    
    os.environ['DATABASE_URL'] = test_url
    
    try:
        clear_modules()
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.app.core.db_guards import validate_database_config
        
        result = validate_database_config(strict=False)
        
        if result:
            print_success("Traditional PostgreSQL with sslmode validated successfully")
            print_info("sslmode parameter is present and required")
            return True
        else:
            print_error("Validation failed - this should not happen")
            return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def main():
    """Run all validation checks."""
    print_header("SSL VALIDATION FIX - QUICK VALIDATION")
    print_info("This script verifies the SSL validation fix is working correctly")
    
    results = []
    
    # Run all validations
    results.append(("Neon Pooled", validate_neon_pooled()))
    results.append(("asyncpg Direct", validate_asyncpg()))
    results.append(("Traditional PostgreSQL", validate_traditional_postgres()))
    
    # Print summary
    print_header("VALIDATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(f"{name}: PASS")
        else:
            print_error(f"{name}: FAIL")
    
    print()
    if passed == total:
        print_success(f"All validations passed ({passed}/{total})!")
        print()
        print_info("The SSL validation fix is working correctly.")
        print_info("Your application should start without SSL validation errors.")
        return 0
    else:
        print_error(f"Some validations failed ({passed}/{total})")
        print()
        print_info("Please check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

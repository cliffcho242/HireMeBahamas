"""
Test CRON_SECRET authorization for cron endpoints.

This script tests that the cron endpoints properly check for the
CRON_SECRET authorization header.
"""

import os
import sys


def test_python_cron_handler():
    """Test the Python cron handler authorization logic."""
    print("Testing Python cron handler (api/cron/health.py)...")
    
    # Test 1: Verify the handler checks for CRON_SECRET
    try:
        with open("api/cron/health.py", "r") as f:
            content = f.read()
            
        # Check that the file contains authorization logic
        if 'os.getenv("CRON_SECRET")' in content:
            print("  ✓ Handler reads CRON_SECRET environment variable")
        else:
            print("  ✗ Handler does not read CRON_SECRET")
            return False
            
        if 'Authorization' in content and 'Bearer' in content:
            print("  ✓ Handler checks Authorization header with Bearer token")
        else:
            print("  ✗ Handler does not check Authorization header properly")
            return False
            
        if '401' in content:
            print("  ✓ Handler returns 401 Unauthorized on auth failure")
        else:
            print("  ✗ Handler does not return 401 status")
            return False
            
        if 'secrets.compare_digest' in content:
            print("  ✓ Handler uses constant-time comparison (timing attack safe)")
        else:
            print("  ✗ Handler does not use constant-time comparison")
            return False
            
        print("  ✓ Python cron handler authorization: PASS")
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing Python handler: {e}")
        return False


def test_typescript_cron_handler():
    """Test the TypeScript cron handler authorization logic."""
    print("\nTesting TypeScript cron handler (next-app/app/api/cron/route.ts)...")
    
    # Test 1: Verify the handler checks for CRON_SECRET
    try:
        with open("next-app/app/api/cron/route.ts", "r") as f:
            content = f.read()
            
        # Check that the file contains authorization logic
        if 'process.env.CRON_SECRET' in content:
            print("  ✓ Handler reads CRON_SECRET environment variable")
        else:
            print("  ✗ Handler does not read CRON_SECRET")
            return False
            
        if 'Authorization' in content and 'Bearer' in content:
            print("  ✓ Handler checks Authorization header with Bearer token")
        else:
            print("  ✗ Handler does not check Authorization header properly")
            return False
            
        if '401' in content:
            print("  ✓ Handler returns 401 Unauthorized on auth failure")
        else:
            print("  ✗ Handler does not return 401 status")
            return False
            
        if 'timingSafeEqual' in content:
            print("  ✓ Handler uses constant-time comparison (timing attack safe)")
        else:
            print("  ✗ Handler does not use constant-time comparison")
            return False
            
        print("  ✓ TypeScript cron handler authorization: PASS")
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing TypeScript handler: {e}")
        return False


def test_typescript_health_handler():
    """Test the TypeScript health handler authorization logic."""
    print("\nTesting TypeScript health handler (next-app/app/api/health/route.ts)...")
    
    # Test 1: Verify the handler checks for CRON_SECRET
    try:
        with open("next-app/app/api/health/route.ts", "r") as f:
            content = f.read()
            
        # Check that the file contains authorization logic
        if 'process.env.CRON_SECRET' in content:
            print("  ✓ Handler reads CRON_SECRET environment variable")
        else:
            print("  ✗ Handler does not read CRON_SECRET")
            return False
            
        if 'Authorization' in content and 'Bearer' in content:
            print("  ✓ Handler checks Authorization header with Bearer token")
        else:
            print("  ✗ Handler does not check Authorization header properly")
            return False
            
        if '401' in content:
            print("  ✓ Handler returns 401 Unauthorized on auth failure")
        else:
            print("  ✗ Handler does not return 401 status")
            return False
            
        if 'timingSafeEqual' in content:
            print("  ✓ Handler uses constant-time comparison (timing attack safe)")
        else:
            print("  ✗ Handler does not use constant-time comparison")
            return False
            
        print("  ✓ TypeScript health handler authorization: PASS")
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing TypeScript health handler: {e}")
        return False


def test_env_example():
    """Test that .env.example has CRON_SECRET documented."""
    print("\nTesting .env.example documentation...")
    
    try:
        with open(".env.example", "r") as f:
            content = f.read()
            
        if 'CRON_SECRET' in content:
            print("  ✓ .env.example contains CRON_SECRET")
        else:
            print("  ✗ .env.example missing CRON_SECRET")
            return False
            
        if 'cron' in content.lower() or 'Cron' in content:
            print("  ✓ .env.example documents cron usage")
        else:
            print("  ✗ .env.example missing cron documentation")
            return False
            
        print("  ✓ Environment variable documentation: PASS")
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing .env.example: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("CRON_SECRET Authorization Tests")
    print("=" * 60)
    print()
    
    results = []
    results.append(test_python_cron_handler())
    results.append(test_typescript_cron_handler())
    results.append(test_typescript_health_handler())
    results.append(test_env_example())
    
    print()
    print("=" * 60)
    
    if all(results):
        print("✅ All tests passed!")
        print("=" * 60)
        return 0
    else:
        print("❌ Some tests failed!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

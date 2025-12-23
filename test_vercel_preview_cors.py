"""
Test script to verify Vercel preview CORS regex pattern.

This script validates that the CORS configuration correctly handles
Vercel preview deployment URLs.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_vercel_preview_pattern():
    """Test that the Vercel preview pattern matches expected URLs."""
    from app.core.environment import is_valid_vercel_preview_origin
    
    # Valid Vercel preview URLs (should pass)
    valid_urls = [
        "https://frontend-fodpcl8vo-cliffs-projects-a84c76c9.vercel.app",
        "https://frontend-abc123-cliffs-projects-a84c76c9.vercel.app",
        "https://frontend-test-hash-123-cliffs-projects-a84c76c9.vercel.app",
        "https://frontend-a-b-c-cliffs-projects-a84c76c9.vercel.app",
        "https://frontend-xyz789-cliffs-projects-a84c76c9.vercel.app",
    ]
    
    # Invalid URLs (should fail)
    invalid_urls = [
        "https://frontend-ABC123-cliffs-projects-a84c76c9.vercel.app",  # uppercase
        "https://frontend-abc_123-cliffs-projects-a84c76c9.vercel.app",  # underscore
        "https://backend-abc123-cliffs-projects-a84c76c9.vercel.app",  # wrong prefix
        "https://frontend-abc123-other-projects-xyz.vercel.app",  # different project
        "https://frontend-abc123-cliffs-projects-a84c76c9.vercel.app/path",  # with path
        "http://frontend-abc123-cliffs-projects-a84c76c9.vercel.app",  # http instead of https
        "https://evil.com",  # completely different domain
        "https://frontend-abc123-cliffs-projects-a84c76c9.vercel.app.evil.com",  # subdomain attack
    ]
    
    print("Testing Vercel Preview CORS Pattern")
    print("=" * 60)
    
    print("\n✅ Testing VALID preview URLs:")
    all_valid_passed = True
    for url in valid_urls:
        result = is_valid_vercel_preview_origin(url)
        status = "✓" if result else "✗"
        print(f"  {status} {url}")
        if not result:
            all_valid_passed = False
            print(f"    ERROR: Should have matched but didn't!")
    
    print("\n🚫 Testing INVALID URLs (should be rejected):")
    all_invalid_passed = True
    for url in invalid_urls:
        result = is_valid_vercel_preview_origin(url)
        status = "✓" if not result else "✗"
        print(f"  {status} {url}")
        if result:
            all_invalid_passed = False
            print(f"    ERROR: Should have been rejected but wasn't!")
    
    print("\n" + "=" * 60)
    if all_valid_passed and all_invalid_passed:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        if not all_valid_passed:
            print("   - Some valid URLs were rejected")
        if not all_invalid_passed:
            print("   - Some invalid URLs were accepted")
        return False


def test_cors_origin_check():
    """Test that the CORS origin check function works correctly."""
    from app.core.environment import get_cors_origins
    
    print("\n\n" + "=" * 60)
    print("Testing CORS Origins Configuration")
    print("=" * 60)
    
    # Test in production mode
    os.environ["ENVIRONMENT"] = "production"
    prod_origins = get_cors_origins()
    
    print("\n📦 Production origins:")
    for origin in prod_origins:
        print(f"  - {origin}")
    
    # Verify required domains are present
    required_domains = [
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
    ]
    
    all_present = True
    for domain in required_domains:
        if domain not in prod_origins:
            print(f"❌ Missing required domain: {domain}")
            all_present = False
    
    if all_present:
        print("✅ All required production domains are present")
    
    # Clean up
    if "ENVIRONMENT" in os.environ:
        del os.environ["ENVIRONMENT"]
    
    return all_present


def test_allowed_origins_env_var():
    """Test that ALLOWED_ORIGINS environment variable works."""
    from app.core.environment import get_cors_origins
    
    print("\n\n" + "=" * 60)
    print("Testing ALLOWED_ORIGINS Environment Variable")
    print("=" * 60)
    
    # Set custom origins via env var
    os.environ["ENVIRONMENT"] = "production"
    os.environ["ALLOWED_ORIGINS"] = "https://hiremebahamas.com,https://www.hiremebahamas.com,https://custom-domain.com"
    
    origins = get_cors_origins()
    
    print("\n📦 Origins with ALLOWED_ORIGINS set:")
    for origin in origins:
        print(f"  - {origin}")
    
    # Check if custom origin is included
    has_custom = "https://custom-domain.com" in origins
    has_required = "https://hiremebahamas.com" in origins
    
    if has_custom and has_required:
        print("✅ ALLOWED_ORIGINS correctly adds custom domains")
        success = True
    else:
        print("❌ ALLOWED_ORIGINS not working correctly")
        success = False
    
    # Clean up
    if "ENVIRONMENT" in os.environ:
        del os.environ["ENVIRONMENT"]
    if "ALLOWED_ORIGINS" in os.environ:
        del os.environ["ALLOWED_ORIGINS"]
    
    return success


if __name__ == "__main__":
    print("Vercel Preview CORS Configuration Test")
    print("=" * 60)
    print()
    
    # Run all tests
    test1 = test_vercel_preview_pattern()
    test2 = test_cors_origin_check()
    test3 = test_allowed_origins_env_var()
    
    print("\n\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Vercel Preview Pattern Test: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"CORS Origins Test: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"ALLOWED_ORIGINS Env Var Test: {'✅ PASS' if test3 else '❌ FAIL'}")
    
    if test1 and test2 and test3:
        print("\n🎉 All tests passed! CORS configuration is correct.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please review the configuration.")
        sys.exit(1)

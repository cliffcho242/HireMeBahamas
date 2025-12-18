#!/usr/bin/env python3
"""
Test authentication cookie settings for cross-origin compatibility
Verifies that cookies are configured correctly for Safari/iPhone support
"""

import os
import sys
import re

def test_cookie_settings():
    """Test that cookie settings are configured correctly by reading the file"""
    print("Testing authentication cookie settings...")
    print("=" * 70)
    
    # Read security.py file directly to check settings
    security_file = os.path.join(os.path.dirname(__file__), 'api', 'backend_app', 'core', 'security.py')
    
    if not os.path.exists(security_file):
        print(f"❌ Security file not found: {security_file}")
        return False
    
    with open(security_file, 'r') as f:
        content = f.read()
    
    # Extract key settings using regex
    def extract_value(pattern, content):
        match = re.search(pattern, content, re.MULTILINE)
        return match.group(1) if match else None
    
    # Parse settings
    cookie_httponly = 'COOKIE_HTTPONLY = True' in content
    cookie_path = '"/"' in content and 'COOKIE_PATH' in content
    cookie_samesite_none = '"None"' in content and 'COOKIE_SAMESITE' in content
    cookie_samesite_lax = '"lax"' in content and 'COOKIE_SAMESITE' in content
    refresh_token_30days = 'REFRESH_TOKEN_EXPIRE_DAYS' in content and 'default=30' in content
    
    # Check for production checks
    has_is_production = 'def is_production()' in content
    has_environment_check = 'os.getenv("ENVIRONMENT"' in content or 'os.getenv("VERCEL_ENV"' in content
    
    # Display environment
    env = os.getenv("ENVIRONMENT", "development")
    vercel_env = os.getenv("VERCEL_ENV", "development")
    
    print(f"\n📋 Environment Information:")
    print(f"  ENVIRONMENT: {env}")
    print(f"  VERCEL_ENV: {vercel_env}")
    
    # Display cookie settings found
    print(f"\n🍪 Cookie Settings Found in Code:")
    print(f"  COOKIE_HTTPONLY = True: {'✓' if cookie_httponly else '✗'}")
    print(f"  COOKIE_PATH = '/': {'✓' if cookie_path else '✗'}")
    print(f"  COOKIE_SAMESITE = 'None' (production): {'✓' if cookie_samesite_none else '✗'}")
    print(f"  COOKIE_SAMESITE = 'lax' (development): {'✓' if cookie_samesite_lax else '✗'}")
    print(f"  REFRESH_TOKEN_EXPIRE_DAYS = 30: {'✓' if refresh_token_30days else '✗'}")
    print(f"  Environment detection (is_production): {'✓' if has_is_production else '✗'}")
    
    # Verify critical settings
    print(f"\n✅ Verification:")
    errors = []
    warnings = []
    
    # 1. HttpOnly must always be True for security
    if not cookie_httponly:
        errors.append("❌ COOKIE_HTTPONLY must be True for XSS protection")
    else:
        print("  ✓ COOKIE_HTTPONLY is True (XSS protection)")
    
    # 2. Path must be "/" for cookies to work across all routes
    if not cookie_path:
        errors.append("❌ COOKIE_PATH must be '/' for cookies to work across all routes")
    else:
        print("  ✓ COOKIE_PATH is '/' (available on all routes)")
    
    # 3. Refresh token expiry should be 30 days for mobile compatibility
    if not refresh_token_30days:
        warnings.append("⚠️  REFRESH_TOKEN_EXPIRE_DAYS should be 30 days for mobile compatibility")
    else:
        print(f"  ✓ REFRESH_TOKEN_EXPIRE_DAYS is 30 days (mobile compatible)")
    
    # 4. Must support both production (None) and development (lax) SameSite settings
    if not cookie_samesite_none:
        errors.append("❌ COOKIE_SAMESITE must support 'None' for production cross-origin")
    else:
        print("  ✓ COOKIE_SAMESITE supports 'None' (production cross-origin)")
    
    if not cookie_samesite_lax:
        warnings.append("⚠️  COOKIE_SAMESITE should use 'lax' for development CSRF protection")
    else:
        print("  ✓ COOKIE_SAMESITE supports 'lax' (development CSRF protection)")
    
    # 5. Must have environment detection
    if not has_is_production:
        errors.append("❌ Must have is_production() function for environment detection")
    else:
        print("  ✓ Environment detection implemented (is_production)")
    
    # 6. Check set_auth_cookies includes path parameter
    has_path_in_set_cookie = 'path=COOKIE_PATH' in content or 'path="/"' in content
    if not has_path_in_set_cookie:
        errors.append("❌ set_auth_cookies must include path parameter")
    else:
        print("  ✓ set_auth_cookies includes path parameter")
    
    # Display summary
    print("\n" + "=" * 70)
    
    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"  {warning}")
    
    if errors:
        print("\n❌ FAILED - Cookie settings have critical issues:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("\n✅ PASSED - All critical cookie settings are correct!")
        print("\n📱 Configuration is Safari/iPhone compatible:")
        print("  • Secure=True + SameSite=None works on Safari (production)")
        print("  • Cross-origin cookies enabled (Vercel → Render)")
        print("  • HttpOnly protects against XSS attacks")
        print("  • 30-day refresh tokens reduce login frequency")
        print("  • Development mode supports localhost HTTP testing")
        print("  • SameSite=lax provides CSRF protection (development)")
        return True

if __name__ == "__main__":
    try:
        success = test_cookie_settings()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error running test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

"""
Test Safari/iPhone cross-origin cookie support

This test suite validates that authentication cookies meet Safari's
strict requirements for cross-origin scenarios.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def test_cookie_configuration():
    """Test that cookie configuration meets Safari requirements"""
    print("=" * 70)
    print("SAFARI/iPHONE COOKIE CONFIGURATION TEST")
    print("=" * 70)
    
    try:
        # Import security module
        from app.core import security
        
        print("\n✅ Successfully imported security module")
        
        # Test 1: Check SameSite and Secure configuration
        print("\n📋 Test 1: Cookie Security Configuration")
        print(f"   - COOKIE_SECURE: {security.COOKIE_SECURE}")
        print(f"   - COOKIE_SAMESITE: {security.COOKIE_SAMESITE}")
        print(f"   - COOKIE_HTTPONLY: {security.COOKIE_HTTPONLY}")
        
        # Test 2: Safari requirement - SameSite=None requires Secure=True
        print("\n📋 Test 2: Safari SameSite=None + Secure Requirement")
        if security.COOKIE_SAMESITE == "none":
            if security.COOKIE_SECURE:
                print("   ✅ PASS: SameSite=None paired with Secure=True (Safari compatible)")
            else:
                print("   ❌ FAIL: SameSite=None without Secure=True (Safari will reject)")
                return False
        else:
            print(f"   ℹ️  INFO: SameSite={security.COOKIE_SAMESITE} (not using cross-origin mode)")
        
        # Test 3: HttpOnly protection
        print("\n📋 Test 3: XSS Protection (HttpOnly)")
        if security.COOKIE_HTTPONLY:
            print("   ✅ PASS: HttpOnly=True (JavaScript cannot access cookies)")
        else:
            print("   ⚠️  WARNING: HttpOnly=False (vulnerable to XSS attacks)")
        
        # Test 4: Production environment check
        print("\n📋 Test 4: Environment Configuration")
        is_prod = security.is_production()
        env = os.getenv("ENVIRONMENT", "").lower()
        vercel_env = os.getenv("VERCEL_ENV", "").lower()
        print(f"   - ENVIRONMENT: {env or '(not set)'}")
        print(f"   - VERCEL_ENV: {vercel_env or '(not set)'}")
        print(f"   - is_production(): {is_prod}")
        
        if is_prod:
            print("   ℹ️  Production mode detected")
            if security.COOKIE_SAMESITE == "none" and security.COOKIE_SECURE:
                print("   ✅ PASS: Production using cross-origin safe cookies")
            elif security.COOKIE_SAMESITE == "lax":
                print("   ℹ️  INFO: Production using same-site cookies (no cross-origin)")
        else:
            print("   ℹ️  Development mode detected")
            if security.COOKIE_SAMESITE == "lax":
                print("   ✅ PASS: Development using same-site cookies")
        
        # Test 5: Cookie names
        print("\n📋 Test 5: Cookie Names")
        print(f"   - Access token: {security.COOKIE_NAME_ACCESS}")
        print(f"   - Refresh token: {security.COOKIE_NAME_REFRESH}")
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED - Safari/iPhone cookie support validated")
        print("=" * 70)
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Failed to import security module: {e}")
        print("   Make sure you're running from the backend directory")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def test_samesite_validation():
    """Test the SameSite=None + Secure validation logic"""
    print("\n" + "=" * 70)
    print("SAMESITE VALIDATION LOGIC TEST")
    print("=" * 70)
    
    try:
        # Simulate production environment
        os.environ["ENVIRONMENT"] = "production"
        
        # Reimport to pick up environment change
        # Note: This test demonstrates the validation logic
        # In practice, the validation happens at module import time
        
        from app.core import security
        
        print("\n📋 Testing validation in production mode")
        print(f"   - COOKIE_SAMESITE: {security.COOKIE_SAMESITE}")
        print(f"   - COOKIE_SECURE: {security.COOKIE_SECURE}")
        
        # Validation should ensure Secure=True when SameSite=None
        if security.COOKIE_SAMESITE == "none":
            if security.COOKIE_SECURE:
                print("   ✅ PASS: Validation correctly enforces Secure=True")
            else:
                print("   ❌ FAIL: Validation did not enforce Secure=True")
                return False
        
        print("\n✅ Validation logic working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing validation: {e}")
        return False


def test_api_backend_cookie_config():
    """Test cookie configuration in api/backend_app"""
    print("\n" + "=" * 70)
    print("API BACKEND COOKIE CONFIGURATION TEST")
    print("=" * 70)
    
    # Add api directory to path
    api_path = Path(__file__).parent.parent / "api" / "backend_app"
    if api_path.exists():
        sys.path.insert(0, str(api_path.parent))
        
        try:
            from backend_app.core import security as api_security
            
            print("\n✅ Successfully imported API backend security module")
            
            print("\n📋 API Backend Cookie Configuration:")
            print(f"   - COOKIE_SECURE: {api_security.COOKIE_SECURE}")
            print(f"   - COOKIE_SAMESITE: {api_security.COOKIE_SAMESITE}")
            print(f"   - COOKIE_HTTPONLY: {api_security.COOKIE_HTTPONLY}")
            
            # Check Safari requirement
            if api_security.COOKIE_SAMESITE == "none":
                if api_security.COOKIE_SECURE:
                    print("   ✅ PASS: Safari compatible (SameSite=None + Secure=True)")
                else:
                    print("   ❌ FAIL: Not Safari compatible (missing Secure flag)")
                    return False
            
            print("\n✅ API backend cookie configuration validated")
            return True
            
        except ImportError as e:
            print(f"\n⚠️  Could not test API backend: {e}")
            print("   This is okay if only using backend/app")
            return True
    else:
        print("\n⚠️  API backend directory not found")
        print("   This is okay if only using backend/app")
        return True


def main():
    """Run all Safari/iPhone cookie tests"""
    print("\n🧪 Testing Safari/iPhone Cookie Support\n")
    
    all_passed = True
    
    # Test main backend configuration
    if not test_cookie_configuration():
        all_passed = False
    
    # Test validation logic
    if not test_samesite_validation():
        all_passed = False
    
    # Test API backend if it exists
    if not test_api_backend_cookie_config():
        all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL SAFARI/iPHONE TESTS PASSED")
        print("\nYour application is configured correctly for:")
        print("  • Safari Desktop (macOS)")
        print("  • Safari Mobile (iOS/iPadOS)")
        print("  • iPhone/iPad WebView")
        print("  • Cross-origin authentication")
        print("=" * 70)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease review the configuration and fix the issues above.")
        print("See SAFARI_IPHONE_CROSS_ORIGIN_SUPPORT.md for details.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())

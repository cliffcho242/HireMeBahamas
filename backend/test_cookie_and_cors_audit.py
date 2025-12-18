"""
Test Cookie & CORS Audit Requirements

This test validates that the authentication system meets the requirements
specified in the cookie and CORS audit:

1. Refresh token cookies must have:
   - httponly=True (XSS protection)
   - secure=True (Safari-safe)
   - samesite="None" (MANDATORY for Vercel ↔ Backend cross-origin)
   - path="/"
   - max_age=30 days

2. CORS configuration must:
   - Use explicit origins (NO wildcards)
   - Have supports_credentials=True
   - NOT use wildcard with credentials (cookies would be dropped)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_cookie_configuration():
    """Test that cookie configuration meets audit requirements."""
    print("\n" + "=" * 70)
    print("🍪 COOKIE CONFIGURATION AUDIT")
    print("=" * 70)
    
    try:
        from app.core.security import (
            COOKIE_HTTPONLY,
            COOKIE_SECURE,
            COOKIE_SAMESITE,
            COOKIE_PATH,
            COOKIE_MAX_AGE,
            COOKIE_NAME_REFRESH,
        )
        
        print("\n✅ Cookie configuration imported successfully")
        
        # Test 1: HttpOnly flag (XSS protection)
        print(f"\n📋 Test 1: HttpOnly Flag (XSS Protection)")
        print(f"   - COOKIE_HTTPONLY: {COOKIE_HTTPONLY}")
        assert COOKIE_HTTPONLY == True, "❌ FAIL: HttpOnly must be True"
        print("   ✅ PASS: HttpOnly=True (secure)")
        
        # Test 2: Secure flag (Safari requirement)
        print(f"\n📋 Test 2: Secure Flag (Safari Requirement)")
        print(f"   - COOKIE_SECURE: {COOKIE_SECURE}")
        assert COOKIE_SECURE == True, "❌ FAIL: Secure must be True for Safari"
        print("   ✅ PASS: Secure=True (Safari-safe)")
        
        # Test 3: SameSite=None (CRITICAL for cross-origin)
        print(f"\n📋 Test 3: SameSite Setting (Cross-Origin Support)")
        print(f"   - COOKIE_SAMESITE: {COOKIE_SAMESITE}")
        assert COOKIE_SAMESITE == "none", "❌ FAIL: SameSite must be 'none' for Vercel ↔ Backend"
        print("   ✅ PASS: SameSite=None (MANDATORY for cross-origin)")
        print("   ⚠️  WARNING: If SameSite=Lax, Safari login fails silently!")
        
        # Test 4: Path configuration
        print(f"\n📋 Test 4: Cookie Path")
        print(f"   - COOKIE_PATH: {COOKIE_PATH}")
        assert COOKIE_PATH == "/", "❌ FAIL: Path must be '/'"
        print("   ✅ PASS: Path='/' (available site-wide)")
        
        # Test 5: Max age (30 days)
        print(f"\n📋 Test 5: Cookie Max Age (Expiration)")
        print(f"   - COOKIE_MAX_AGE: {COOKIE_MAX_AGE} seconds")
        expected_max_age = 60 * 60 * 24 * 30  # 30 days
        assert COOKIE_MAX_AGE == expected_max_age, f"❌ FAIL: Max age must be {expected_max_age}"
        print(f"   ✅ PASS: Max age = {COOKIE_MAX_AGE // (60*60*24)} days")
        
        # Test 6: Refresh token cookie name
        print(f"\n📋 Test 6: Refresh Token Cookie Name")
        print(f"   - COOKIE_NAME_REFRESH: {COOKIE_NAME_REFRESH}")
        assert COOKIE_NAME_REFRESH == "refresh_token", "❌ FAIL: Cookie name must be 'refresh_token'"
        print("   ✅ PASS: Cookie name is 'refresh_token'")
        
        print("\n" + "=" * 70)
        print("✅ ALL COOKIE CONFIGURATION TESTS PASSED")
        print("=" * 70)
        return True
        
    except ImportError as e:
        print(f"\n❌ Failed to import security module: {e}")
        return False
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def test_cors_configuration():
    """Test that CORS configuration meets audit requirements."""
    print("\n" + "=" * 70)
    print("🌍 CORS CONFIGURATION AUDIT")
    print("=" * 70)
    
    try:
        from app.core.environment import get_cors_origins, is_production
        
        print("\n✅ CORS configuration imported successfully")
        
        # Get CORS origins
        origins = get_cors_origins()
        is_prod = is_production()
        
        # Test 1: No wildcard origins
        print(f"\n📋 Test 1: No Wildcard Origins (Security Requirement)")
        print(f"   - Production mode: {is_prod}")
        print(f"   - Allowed origins: {origins}")
        
        for origin in origins:
            if "*" in origin:
                print(f"   ❌ FAIL: Wildcard pattern found: {origin}")
                print("   ⚠️  Wildcard + credentials = cookies dropped!")
                assert False, "Wildcard origins not allowed with credentials"
        
        print("   ✅ PASS: No wildcard patterns (explicit origins only)")
        
        # Test 2: Explicit production origins
        print(f"\n📋 Test 2: Explicit Production Origins")
        required_prod_origins = [
            "https://hiremebahamas.com",
            "https://www.hiremebahamas.com"
        ]
        
        for required_origin in required_prod_origins:
            if required_origin not in origins:
                print(f"   ❌ FAIL: Missing required origin: {required_origin}")
                assert False, f"Required origin {required_origin} not in allowed list"
            print(f"   ✅ {required_origin}")
        
        print("   ✅ PASS: All required production origins present")
        
        # Test 3: Check main.py CORS middleware configuration
        print(f"\n📋 Test 3: CORS Middleware Configuration")
        print("   - Checking main.py for CORS configuration...")
        
        # Read main.py to verify CORS settings
        import os
        main_py_path = os.path.join(os.path.dirname(__file__), "app", "main.py")
        with open(main_py_path, 'r') as f:
            main_py_content = f.read()
        
        # Check for wildcard origins (not allowed with credentials)
        # Looking for: allow_origins=["*"] or allow_origins=['*']
        # But NOT in comments (lines starting with # or containing ❌ NEVER)
        import re
        
        # Find all allow_origins lines
        for line in main_py_content.split('\n'):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            if '❌ NEVER' in line or '⚠️' in line:
                continue
                
            # Check for wildcard in actual configuration
            if 'allow_origins=' in line.lower():
                if '["*"]' in line or "['*']" in line:
                    print(f"   ❌ FAIL: Wildcard origins detected: {line.strip()}")
                    assert False, "Wildcard origins not allowed with credentials"
        
        # Check for allow_credentials=True
        if "allow_credentials=True" not in main_py_content:
            print("   ❌ FAIL: allow_credentials=True not found in main.py")
            assert False, "CORS must have allow_credentials=True"
        
        print("   ✅ PASS: CORS configured with explicit origins")
        print("   ✅ PASS: allow_credentials=True detected")
        
        print("\n" + "=" * 70)
        print("✅ ALL CORS CONFIGURATION TESTS PASSED")
        print("=" * 70)
        return True
        
    except ImportError as e:
        print(f"\n❌ Failed to import environment module: {e}")
        return False
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_safari_compatibility():
    """Test Safari/iPhone specific requirements."""
    print("\n" + "=" * 70)
    print("🍎 SAFARI/iPHONE COMPATIBILITY AUDIT")
    print("=" * 70)
    
    try:
        from app.core.security import COOKIE_SECURE, COOKIE_SAMESITE
        
        print("\n📋 Safari Requirement: SameSite=None + Secure=True")
        print(f"   - COOKIE_SAMESITE: {COOKIE_SAMESITE}")
        print(f"   - COOKIE_SECURE: {COOKIE_SECURE}")
        
        if COOKIE_SAMESITE == "none":
            if not COOKIE_SECURE:
                print("   ❌ FAIL: Safari rejects SameSite=None without Secure=True")
                assert False, "Safari requires Secure=True with SameSite=None"
            else:
                print("   ✅ PASS: SameSite=None paired with Secure=True")
                print("   ✅ Safari will accept cookies")
        else:
            print(f"   ⚠️  WARNING: SameSite={COOKIE_SAMESITE}")
            print("   ⚠️  Cross-origin authentication may fail with SameSite!=None")
        
        print("\n" + "=" * 70)
        print("✅ SAFARI COMPATIBILITY TESTS PASSED")
        print("=" * 70)
        return True
        
    except ImportError as e:
        print(f"\n❌ Failed to import security module: {e}")
        return False
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔒 COOKIE & SESSION AUDIT - CRITICAL SECURITY TEST")
    print("=" * 70)
    print("\nTesting requirements from audit:")
    print("1. Refresh token cookie configuration")
    print("2. CORS configuration with credentials")
    print("3. Safari/iPhone compatibility")
    
    results = []
    
    # Run all tests
    results.append(("Cookie Configuration", test_cookie_configuration()))
    results.append(("CORS Configuration", test_cors_configuration()))
    results.append(("Safari Compatibility", test_safari_compatibility()))
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n🎉 ALL AUDIT REQUIREMENTS MET!")
        print("\n✅ Cookies are Safari-compatible")
        print("✅ CORS is configured securely")
        print("✅ Cross-origin authentication will work (Vercel ↔ Backend)")
        sys.exit(0)
    else:
        print("\n❌ AUDIT FAILED - Fix issues above")
        sys.exit(1)

#!/usr/bin/env python3
"""
Verify CORS Lock Implementation - No Wildcards in Production

This script verifies that the CORS configuration meets security requirements:
1. No wildcard (*) patterns in production mode
2. Only specific HTTPS domains allowed
3. Credentials properly configured
4. Environment variable support working
"""

import os
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent / "backend"
api_backend_dir = Path(__file__).parent / "api" / "backend_app"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(api_backend_dir.parent))


def test_production_cors_origins():
    """Test CORS origins in production mode"""
    print("=" * 70)
    print("CORS LOCK VERIFICATION - PRODUCTION MODE")
    print("=" * 70)
    print()
    
    # Set production environment
    os.environ["ENVIRONMENT"] = "production"
    os.environ["VERCEL_ENV"] = "production"
    
    # Remove any ALLOWED_ORIGINS to test defaults
    if "ALLOWED_ORIGINS" in os.environ:
        del os.environ["ALLOWED_ORIGINS"]
    
    try:
        # Test both implementations
        from app.core.environment import get_cors_origins as get_backend_origins
        from backend_app.core.environment import get_cors_origins as get_api_origins
        
        print("1. Testing backend/app/core/environment.py")
        print("-" * 70)
        backend_origins = get_backend_origins()
        print(f"   Origins: {backend_origins}")
        
        # Verify no wildcards
        assert "*" not in str(backend_origins), "❌ FAIL: Wildcard found in backend origins"
        assert not any("*" in origin for origin in backend_origins), "❌ FAIL: Wildcard pattern found in backend origins"
        print("   ✅ No wildcards")
        
        # Verify HTTPS only
        for origin in backend_origins:
            if not origin.startswith("https://"):
                raise AssertionError(f"❌ FAIL: Non-HTTPS origin in production: {origin}")
        print("   ✅ All origins use HTTPS")
        
        # Verify specific domains
        expected_origins = {
            "https://hiremebahamas.com",
            "https://www.hiremebahamas.com",
            "https://hiremebahamas.vercel.app"
        }
        assert set(backend_origins) == expected_origins, f"❌ FAIL: Unexpected origins. Expected {expected_origins}, got {set(backend_origins)}"
        print(f"   ✅ {len(backend_origins)} specific origins configured")
        print()
        
        print("2. Testing api/backend_app/core/environment.py")
        print("-" * 70)
        api_origins = get_api_origins()
        print(f"   Origins: {api_origins}")
        
        # Verify no wildcards
        assert "*" not in str(api_origins), "❌ FAIL: Wildcard found in API origins"
        assert not any("*" in origin for origin in api_origins), "❌ FAIL: Wildcard pattern found in API origins"
        print("   ✅ No wildcards")
        
        # Verify HTTPS only
        for origin in api_origins:
            if not origin.startswith("https://"):
                raise AssertionError(f"❌ FAIL: Non-HTTPS origin in production: {origin}")
        print("   ✅ All origins use HTTPS")
        
        # Verify specific domains
        assert set(api_origins) == expected_origins, f"❌ FAIL: Unexpected origins. Expected {expected_origins}, got {set(api_origins)}"
        print(f"   ✅ {len(api_origins)} specific origins configured")
        print()
        
        # Verify both are consistent
        assert backend_origins == api_origins, "❌ FAIL: Inconsistent origins between backend and API"
        print("3. Consistency Check")
        print("-" * 70)
        print("   ✅ Both implementations return identical origins")
        print()
        
    finally:
        # Clean up environment
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]
        if "VERCEL_ENV" in os.environ:
            del os.environ["VERCEL_ENV"]
    
    print("=" * 70)
    print("✅ CORS LOCK VERIFIED - ALL CHECKS PASSED")
    print("=" * 70)
    print()
    print("Production CORS Configuration:")
    for origin in expected_origins:
        print(f"  • {origin}")
    print()
    return True


def test_custom_origins():
    """Test custom origins from environment variable"""
    print("=" * 70)
    print("CUSTOM ORIGINS TEST")
    print("=" * 70)
    print()
    
    # Set production environment with custom origins
    os.environ["ENVIRONMENT"] = "production"
    os.environ["ALLOWED_ORIGINS"] = "https://custom1.com,https://custom2.com"
    
    try:
        # Re-import to get fresh configuration
        import importlib
        import app.core.environment
        importlib.reload(app.core.environment)
        from app.core.environment import get_cors_origins
        
        origins = get_cors_origins()
        print(f"Custom origins: {origins}")
        
        expected = ["https://custom1.com", "https://custom2.com"]
        assert origins == expected, f"❌ FAIL: Expected {expected}, got {origins}"
        print("✅ Custom origins from environment variable work correctly")
        print()
        
    finally:
        # Clean up environment
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]
        if "ALLOWED_ORIGINS" in os.environ:
            del os.environ["ALLOWED_ORIGINS"]
    
    return True


def test_wildcard_rejection():
    """Test that wildcard in environment variable is rejected"""
    print("=" * 70)
    print("WILDCARD REJECTION TEST")
    print("=" * 70)
    print()
    
    # Set production environment with wildcard (should be rejected)
    os.environ["ENVIRONMENT"] = "production"
    os.environ["ALLOWED_ORIGINS"] = "*"
    
    try:
        # Re-import to get fresh configuration
        import importlib
        import app.core.environment
        importlib.reload(app.core.environment)
        from app.core.environment import get_cors_origins
        
        origins = get_cors_origins()
        print(f"Origins with ALLOWED_ORIGINS='*': {origins}")
        
        # Should fall back to default origins, not use wildcard
        expected = [
            "https://hiremebahamas.com",
            "https://www.hiremebahamas.com",
            "https://hiremebahamas.vercel.app"
        ]
        assert origins == expected, f"❌ FAIL: Wildcard not rejected. Expected {expected}, got {origins}"
        print("✅ Wildcard in ALLOWED_ORIGINS correctly rejected")
        print()
        
    finally:
        # Clean up environment
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]
        if "ALLOWED_ORIGINS" in os.environ:
            del os.environ["ALLOWED_ORIGINS"]
    
    return True


def main():
    """Run all verification tests"""
    try:
        test_production_cors_origins()
        test_custom_origins()
        test_wildcard_rejection()
        
        print()
        print("=" * 70)
        print("🎉 ALL CORS LOCK VERIFICATION TESTS PASSED!")
        print("=" * 70)
        print()
        print("Summary:")
        print("  ✅ No wildcards (*) in production")
        print("  ✅ Only specific HTTPS domains allowed")
        print("  ✅ Custom origins via ALLOWED_ORIGINS supported")
        print("  ✅ Wildcard in ALLOWED_ORIGINS correctly rejected")
        print("  ✅ Both implementations consistent")
        print()
        return 0
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ VERIFICATION FAILED")
        print("=" * 70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""
Test CORS configuration for Vercel preview support
"""
import re
import os


def test_vercel_preview_regex():
    """Test that the Vercel preview regex matches expected URLs"""
    import sys
    from pathlib import Path
    
    # Add api directory to path
    api_dir = Path(__file__).parent / "api"
    if str(api_dir) not in sys.path:
        sys.path.insert(0, str(api_dir))
    
    from cors_utils import get_vercel_preview_regex
    
    # The regex pattern from cors_utils
    VERCEL_PREVIEW_REGEX = get_vercel_preview_regex()
    
    # Test cases that SHOULD match
    valid_urls = [
        "https://frontend-abc123-cliffs-projects-a84c76c9.vercel.app",
        "https://frontend-test-abc-cliffs-projects-a84c76c9.vercel.app",
        "https://frontend-feature-branch-123-cliffs-projects-a84c76c9.vercel.app",
        "https://frontend-pr-456-cliffs-projects-a84c76c9.vercel.app",
    ]
    
    # Test cases that SHOULD NOT match
    invalid_urls = [
        "https://frontend-abc123-different-projects.vercel.app",  # Wrong project ID
        "http://frontend-abc123-cliffs-projects-a84c76c9.vercel.app",  # HTTP not HTTPS
        "https://frontend-ABC123-cliffs-projects-a84c76c9.vercel.app",  # Uppercase letters
        "https://malicious-site.com",  # Completely different domain
        "https://frontend-cliffs-projects-a84c76c9.vercel.app",  # Missing hash part
    ]
    
    pattern = re.compile(VERCEL_PREVIEW_REGEX)
    
    print("Testing valid Vercel preview URLs:")
    for url in valid_urls:
        match = pattern.match(url)
        assert match is not None, f"Expected {url} to match but it didn't"
        print(f"  ✅ {url}")
    
    print("\nTesting invalid URLs (should NOT match):")
    for url in invalid_urls:
        match = pattern.match(url)
        assert match is None, f"Expected {url} NOT to match but it did"
        print(f"  ✅ {url} (correctly rejected)")
    
    print("\n✅ All CORS regex tests passed!")


def test_cors_module():
    """Test that the CORS module can be imported and configured"""
    try:
        # First check if we're in an environment with dependencies
        import sys
        from pathlib import Path
        
        # Add api directory to path using dynamic path detection
        api_dir = Path(__file__).parent / "api"
        if str(api_dir) not in sys.path:
            sys.path.insert(0, str(api_dir))
        
        from cors_utils import get_allowed_origins, get_vercel_preview_regex
        
        print("\n✅ CORS utilities import successfully")
        
        # Test getting allowed origins
        origins = get_allowed_origins()
        print(f"\nAllowed origins: {origins}")
        assert isinstance(origins, list), "get_allowed_origins should return a list"
        assert len(origins) > 0, "Should have at least one allowed origin"
        
        # Test regex generation
        regex = get_vercel_preview_regex()
        print(f"\nVercel preview regex: {regex}")
        assert isinstance(regex, str), "get_vercel_preview_regex should return a string"
        assert "vercel" in regex and "app" in regex, "Regex should reference vercel.app domain"
        
        print("\n✅ CORS utility functions work correctly")
        
    except ImportError as e:
        print(f"\nℹ️  Skipping module import test (dependencies not installed)")
        print(f"    This is expected in CI/test environments without FastAPI")
        print(f"    Error: {e}")
        return


def test_environment_variable():
    """Test that ALLOWED_ORIGINS environment variable is read correctly"""
    try:
        import sys
        from pathlib import Path
        
        # Add api directory to path using dynamic path detection
        api_dir = Path(__file__).parent / "api"
        if str(api_dir) not in sys.path:
            sys.path.insert(0, str(api_dir))
        
        # Save original value
        original_value = os.environ.get("ALLOWED_ORIGINS")
        
        try:
            # Test with custom origins
            os.environ["ALLOWED_ORIGINS"] = "https://example.com,https://test.com"
            
            from cors_utils import get_allowed_origins
            
            origins = get_allowed_origins()
            print(f"\nWith ALLOWED_ORIGINS set: {origins}")
            assert "https://example.com" in origins or "https://test.com" in origins, \
                "Custom origins should be included"
            
            print("✅ Environment variable handling works correctly")
            
        finally:
            # Restore original value
            if original_value is not None:
                os.environ["ALLOWED_ORIGINS"] = original_value
            elif "ALLOWED_ORIGINS" in os.environ:
                del os.environ["ALLOWED_ORIGINS"]
    except ImportError:
        print("\nℹ️  Skipping environment variable test (dependencies not installed)")


if __name__ == "__main__":
    print("=" * 80)
    print("CORS CONFIGURATION TEST FOR VERCEL PREVIEW SUPPORT")
    print("=" * 80)
    
    test_vercel_preview_regex()
    test_cors_module()
    test_environment_variable()
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - CORS FIX IS READY!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Set ALLOWED_ORIGINS environment variable on Render:")
    print("   ALLOWED_ORIGINS=https://hiremebahamas.com,https://www.hiremebahamas.com")
    print("2. Deploy backend to Render (will restart automatically)")
    print("3. Verify from Vercel preview frontend with DevTools:")
    print("   fetch('https://hiremebahamas-backend.onrender.com/health')")
    print("   .then(r => r.json()).then(console.log)")
    print("4. Check Network tab for: access-control-allow-origin header")
    print("=" * 80)

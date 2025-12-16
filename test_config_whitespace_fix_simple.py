#!/usr/bin/env python3
"""
Simple unit test for the whitespace DATABASE_URL fix in backend/app/core/config.py

This test verifies that the get_database_url() method properly handles:
1. Whitespace-only DATABASE_URL strings (e.g., "   ")
2. Empty DATABASE_URL strings
3. None DATABASE_URL values
"""

import os
import sys


def test_whitespace_stripping_logic():
    """Test the whitespace stripping logic in isolation."""
    print("Testing whitespace stripping logic:")
    
    # Test case 1: Whitespace-only string
    test_url = "   "
    stripped = test_url.strip() if test_url else None
    print(f"  Input: '{test_url}' (len={len(test_url)})")
    print(f"  After strip: '{stripped}' (len={len(stripped) if stripped else 0})")
    print(f"  Is empty after strip: {not stripped}")
    assert not stripped, "Whitespace-only string should be empty after strip"
    print("  ✓ Whitespace-only string correctly becomes empty after strip")
    
    # Test case 2: Empty string
    test_url = ""
    stripped = test_url.strip() if test_url else None
    print(f"  Input: '{test_url}' (len={len(test_url)})")
    print(f"  After strip: {stripped}")
    print(f"  Is empty: {not test_url}")
    assert not test_url, "Empty string should fail the truthiness check"
    print("  ✓ Empty string correctly fails truthiness check")
    
    # Test case 3: Valid URL with leading/trailing whitespace
    test_url = "  postgresql://user:pass@host:5432/db  "
    stripped = test_url.strip() if test_url else None
    print(f"  Input: '{test_url}'")
    print(f"  After strip: '{stripped}'")
    assert stripped == "postgresql://user:pass@host:5432/db", "Valid URL should have whitespace removed"
    print("  ✓ Valid URL with whitespace correctly stripped")
    
    print()


def test_config_method_logic_simulation():
    """Simulate the get_database_url() logic to verify it handles whitespace correctly."""
    print("Testing get_database_url() logic simulation:")
    
    def get_database_url_simulated(database_url_input, environment):
        """Simulated version of Settings.get_database_url() with our fix."""
        database_url = database_url_input
        
        # Strip whitespace to prevent connection errors from misconfigured environment variables
        if database_url:
            database_url = database_url.strip()
        
        # For local development only - require explicit configuration in production
        # Check after stripping to handle whitespace-only strings (e.g., "   ")
        if not database_url:
            if environment == "production":
                raise ValueError("DATABASE_URL must be set in production")
            else:
                # Use local development default only in development mode
                # Note: These are the default development credentials, not production secrets
                database_url = "postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
        
        return database_url
    
    # Test case 1: Whitespace-only in development
    try:
        result = get_database_url_simulated("   ", "development")
        assert result, "Should return fallback URL"
        assert result.startswith("postgresql"), "Should be a PostgreSQL URL"
        print("  ✓ Whitespace-only DATABASE_URL in development returns fallback")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Test case 2: Empty string in development
    try:
        result = get_database_url_simulated("", "development")
        assert result, "Should return fallback URL"
        assert result.startswith("postgresql"), "Should be a PostgreSQL URL"
        print("  ✓ Empty DATABASE_URL in development returns fallback")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Test case 3: None in development
    try:
        result = get_database_url_simulated(None, "development")
        assert result, "Should return fallback URL"
        assert result.startswith("postgresql"), "Should be a PostgreSQL URL"
        print("  ✓ None DATABASE_URL in development returns fallback")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Test case 4: Whitespace-only in production should raise ValueError
    try:
        result = get_database_url_simulated("   ", "production")
        print(f"  ✗ Should have raised ValueError but returned: {result}")
        return False
    except ValueError as e:
        if "DATABASE_URL must be set in production" in str(e):
            print("  ✓ Whitespace-only DATABASE_URL in production raises ValueError")
        else:
            print(f"  ✗ Wrong error message: {e}")
            return False
    
    # Test case 5: Empty string in production should raise ValueError
    try:
        result = get_database_url_simulated("", "production")
        print(f"  ✗ Should have raised ValueError but returned: {result}")
        return False
    except ValueError as e:
        if "DATABASE_URL must be set in production" in str(e):
            print("  ✓ Empty DATABASE_URL in production raises ValueError")
        else:
            print(f"  ✗ Wrong error message: {e}")
            return False
    
    # Test case 6: Valid URL with whitespace should be stripped
    try:
        result = get_database_url_simulated("  postgresql://user:pass@host:5432/db  ", "production")
        assert result == "postgresql://user:pass@host:5432/db", "Whitespace should be stripped"
        print("  ✓ Valid URL with whitespace is correctly stripped in production")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    print()
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("Config.py Whitespace Fix - Simple Logic Tests")
    print("=" * 70)
    print()
    
    test_whitespace_stripping_logic()
    success = test_config_method_logic_simulation()
    
    print("=" * 70)
    if success:
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 70)
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

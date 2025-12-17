#!/usr/bin/env python3
"""
Test DATABASE_URL auto-fix logging.

This test verifies that the port auto-fix logs appropriate messages.
"""

import sys
import os
import logging
from io import StringIO

# Set up logging to capture output
log_stream = StringIO()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(log_stream),
        logging.StreamHandler(sys.stdout)
    ]
)

# Add backend path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'app', 'core'))

# Import the db_utils module
from db_utils import ensure_port_in_url, strip_sslmode_from_url


def test_logging():
    """Test that appropriate log messages are generated."""
    
    print("=" * 80)
    print("DATABASE_URL AUTO-FIX LOGGING TEST")
    print("=" * 80)
    
    # Test 1: URL without port (should log)
    print("\nTest 1: URL without port")
    url_no_port = "postgresql://user:password@host/database"
    result = ensure_port_in_url(url_no_port)
    print(f"Input:  {url_no_port}")
    print(f"Output: {result}")
    assert ":5432" in result, "Port should be added"
    
    # Test 2: URL with port (should not log about port)
    print("\nTest 2: URL with port already present")
    url_with_port = "postgresql://user:password@host:5432/database"
    result = ensure_port_in_url(url_with_port)
    print(f"Input:  {url_with_port}")
    print(f"Output: {result}")
    assert result == url_with_port, "URL should not change"
    
    # Test 3: URL with sslmode (should log about removal)
    print("\nTest 3: URL with sslmode parameter")
    url_with_ssl = "postgresql://user:password@host:5432/database?sslmode=require"
    result = strip_sslmode_from_url(url_with_ssl)
    print(f"Input:  {url_with_ssl}")
    print(f"Output: {result}")
    assert "sslmode=" not in result, "sslmode should be removed"
    
    # Check log output
    log_output = log_stream.getvalue()
    print("\n" + "=" * 80)
    print("LOG OUTPUT:")
    print("=" * 80)
    print(log_output)
    
    # Verify expected log messages
    checks = [
        ("Added default port", "Port addition message"),
        ("Removed sslmode from DATABASE_URL", "SSL mode removal message"),
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "=" * 80)
    print("LOG MESSAGE CHECKS:")
    print("=" * 80)
    
    for expected_text, description in checks:
        if expected_text in log_output:
            print(f"✅ {description}: Found")
            passed += 1
        else:
            print(f"❌ {description}: Not found")
            failed += 1
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n✅ All logging tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} logging test(s) failed!")
        return 1


if __name__ == "__main__":
    sys.exit(test_logging())

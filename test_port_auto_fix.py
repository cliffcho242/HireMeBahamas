#!/usr/bin/env python3
"""
Test DATABASE_URL port auto-fix functionality.

This test verifies that the ensure_port_in_url function correctly adds
the default PostgreSQL port (5432) when it's missing from the URL.
"""

import sys
import os
from urllib.parse import urlparse, urlunparse

# Default port for PostgreSQL
DEFAULT_POSTGRES_PORT = 5432


def ensure_port_in_url(database_url: str, default_port: int = DEFAULT_POSTGRES_PORT) -> str:
    """
    Ensure the DATABASE_URL includes an explicit port number.
    
    This is a standalone implementation for testing without imports.
    """
    if not database_url:
        return database_url
    
    parsed_url = urlparse(database_url)
    
    # Check if port is already specified
    if parsed_url.port:
        return database_url
    
    # Port is missing - add default port
    if not parsed_url.hostname:
        # Can't add port without hostname
        return database_url
    
    # Construct new netloc with port
    netloc = parsed_url.hostname
    if default_port is not None:
        netloc = f"{netloc}:{default_port}"
    
    # Add username and password if present
    if parsed_url.username:
        auth = parsed_url.username
        if parsed_url.password:
            auth = f"{auth}:{parsed_url.password}"
        netloc = f"{auth}@{netloc}"
    
    # Reconstruct URL with explicit port
    fixed_url = urlunparse((
        parsed_url.scheme,
        netloc,
        parsed_url.path,
        parsed_url.params,
        parsed_url.query,
        parsed_url.fragment
    ))
    
    return fixed_url


def test_port_auto_fix():
    """Test various DATABASE_URL formats for port auto-fix."""
    
    tests = [
        # (input_url, expected_output, description)
        (
            "postgresql://user:password@host/database",
            "postgresql://user:password@host:5432/database",
            "Simple URL without port"
        ),
        (
            "postgresql+asyncpg://user:password@host/database",
            "postgresql+asyncpg://user:password@host:5432/database",
            "AsyncPG URL without port"
        ),
        (
            "postgresql://user:password@host:5432/database",
            "postgresql://user:password@host:5432/database",
            "URL with port already present (no change)"
        ),
        (
            "postgresql://user:password@ep-xxxx.us-east-1.aws.neon.tech/database",
            "postgresql://user:password@ep-xxxx.us-east-1.aws.neon.tech:5432/database",
            "Neon URL without port"
        ),
        (
            "postgresql://user:password@containers-us-west-1.railway.app/railway",
            "postgresql://user:password@containers-us-west-1.railway.app:5432/railway",
            "Railway URL without port"
        ),
        (
            "postgresql://user:p%40ssw0rd@host/database",
            "postgresql://user:p%40ssw0rd@host:5432/database",
            "URL with encoded password without port"
        ),
        (
            "postgresql://user:password@host/database?sslmode=require",
            "postgresql://user:password@host:5432/database?sslmode=require",
            "URL with query parameters but no port"
        ),
        (
            "postgresql://user:password@host:3306/database",
            "postgresql://user:password@host:3306/database",
            "URL with non-standard port (should not change)"
        ),
        (
            "",
            "",
            "Empty URL (no change)"
        ),
        (
            None,
            None,
            "None URL (no change)"
        ),
    ]
    
    print("=" * 80)
    print("DATABASE_URL PORT AUTO-FIX TEST")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for input_url, expected_output, description in tests:
        print(f"\nTest: {description}")
        print(f"Input:    {input_url}")
        print(f"Expected: {expected_output}")
        
        result = ensure_port_in_url(input_url)
        print(f"Result:   {result}")
        
        if result == expected_output:
            print("✅ PASS")
            passed += 1
        else:
            print("❌ FAIL")
            failed += 1
        
        print("-" * 80)
    
    print(f"\n{'=' * 80}")
    print(f"SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n✅ All tests passed! Port auto-fix is working correctly.")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed! Port auto-fix has issues.")
        return 1


if __name__ == "__main__":
    sys.exit(test_port_auto_fix())

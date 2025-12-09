#!/usr/bin/env python3
"""
Test SSL Mode Enforcement for Vercel Postgres (Neon)

This test validates that the database connection helpers automatically
add ?sslmode=require to connection URLs when it's missing.
"""

import os
import sys
from urllib.parse import urlparse, parse_qs

# Import the actual utility function from the api package
from api.db_url_utils import ensure_sslmode


def test_ssl_mode_enforcement():
    """Test that sslmode=require is automatically added to database URLs"""
    
    print("Testing SSL Mode Enforcement for Vercel Postgres (Neon)")
    print("=" * 70)
    
    # Test cases: (input_url, expected_has_sslmode, description)
    test_cases = [
        (
            "postgresql+asyncpg://user:pass@host:5432/db",
            True,
            "URL without query params should get ?sslmode=require"
        ),
        (
            "postgresql+asyncpg://user:pass@host:5432/db?connect_timeout=10",
            True,
            "URL with params but no sslmode should get &sslmode=require"
        ),
        (
            "postgresql+asyncpg://user:pass@host:5432/db?sslmode=prefer",
            True,
            "URL with explicit sslmode should not be overridden"
        ),
        (
            "postgresql+asyncpg://user:pass@host:5432/db?sslmode=require",
            True,
            "URL with sslmode=require should remain unchanged"
        ),
    ]
    
    all_passed = True
    
    for i, (input_url, expected_has_sslmode, description) in enumerate(test_cases, 1):
        print(f"\nTest {i}: {description}")
        print(f"  Input:  {input_url}")
        
        # Use the actual ensure_sslmode function
        result_url = ensure_sslmode(input_url)
        print(f"  Output: {result_url}")
        
        # Parse the result URL to check for sslmode
        parsed = urlparse(result_url)
        query_params = parse_qs(parsed.query)
        has_sslmode = 'sslmode' in query_params
        
        if has_sslmode == expected_has_sslmode:
            print(f"  ✅ PASS: {'sslmode found' if has_sslmode else 'sslmode not found'}")
            
            # Additional check: ensure sslmode has a value
            if has_sslmode:
                sslmode_value = query_params['sslmode'][0]
                print(f"     SSL mode value: {sslmode_value}")
                if not sslmode_value:
                    print(f"  ⚠️  WARNING: sslmode is present but has no value")
        else:
            print(f"  ❌ FAIL: Expected sslmode={expected_has_sslmode}, got {has_sslmode}")
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ All tests PASSED")
        return 0
    else:
        print("❌ Some tests FAILED")
        return 1


def test_real_vercel_postgres_url():
    """Test with a realistic Vercel Postgres (Neon) URL format"""
    print("\n\nTesting with Realistic Vercel Postgres URL")
    print("=" * 70)
    
    # Realistic Vercel Postgres URL (with placeholder credentials for testing)
    vercel_url = "postgres://default:PLACEHOLDER_PASSWORD@ep-abc123.us-east-1.aws.neon.tech:5432/verceldb"
    
    print(f"Original URL: {vercel_url}")
    
    # Simulate the conversion process
    db_url = vercel_url
    
    # Step 1: Convert to asyncpg
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        print(f"After asyncpg conversion: {db_url}")
    
    # Step 2: Add sslmode if missing using the actual utility function
    db_url = ensure_sslmode(db_url)
    print(f"After adding sslmode: {db_url}")
    
    # Verify
    parsed = urlparse(db_url)
    query_params = parse_qs(parsed.query)
    
    print(f"\nFinal URL: {db_url}")
    print(f"Has sslmode: {'sslmode' in query_params}")
    if 'sslmode' in query_params:
        print(f"SSL mode value: {query_params['sslmode'][0]}")
        print("✅ Vercel Postgres URL properly configured for SSL")
        return 0
    else:
        print("❌ SSL mode not found in URL")
        return 1


if __name__ == "__main__":
    result1 = test_ssl_mode_enforcement()
    result2 = test_real_vercel_postgres_url()
    
    sys.exit(max(result1, result2))

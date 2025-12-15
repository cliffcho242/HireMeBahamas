#!/usr/bin/env python3
"""
Manual test to demonstrate DATABASE_URL validation.

This script shows how the validation rejects invalid URLs and accepts valid ones.
"""
import sys
import os

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from db_url_utils import validate_database_url_structure


def test_url(url, description):
    """Test a single URL and print the result."""
    print(f"\nTesting: {description}")
    print(f"URL: {url}")
    is_valid, error = validate_database_url_structure(url)
    if is_valid:
        print("✅ VALID - URL meets all requirements")
    else:
        print(f"❌ INVALID - {error}")
    print("-" * 80)


def main():
    """Run manual tests."""
    print("=" * 80)
    print("DATABASE_URL Validation Test")
    print("=" * 80)
    
    # BAD Examples (should be rejected)
    print("\n🚫 BAD EXAMPLES (should be rejected):")
    
    test_url(
        "postgresql://user:pass@/dbname",
        "Missing hostname (causes socket usage)"
    )
    
    test_url(
        "postgresql://user:pass@localhost/dbname",
        "Using localhost (may cause socket usage)"
    )
    
    test_url(
        "postgresql://user:pass@127.0.0.1/dbname",
        "Using 127.0.0.1 (may cause socket usage)"
    )
    
    test_url(
        "postgresql://user:pass@db.example.com/dbname",
        "Missing port number"
    )
    
    test_url(
        "postgresql://user:pass@db.example.com:5432/dbname",
        "Missing sslmode parameter"
    )
    
    # GOOD Examples (should be accepted)
    print("\n\n✅ GOOD EXAMPLES (should be accepted):")
    
    test_url(
        "postgresql://user:password@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname?sslmode=require",
        "Neon PostgreSQL (all requirements met)"
    )
    
    test_url(
        "postgresql://user:password@db.railway.internal:5432/railway?sslmode=require",
        "Railway PostgreSQL (all requirements met)"
    )
    
    test_url(
        "postgresql+asyncpg://user:password@db.example.com:5432/dbname?sslmode=require",
        "With asyncpg driver (all requirements met)"
    )
    
    test_url(
        "postgresql://user:p@ssw0rd!@db.example.com:5432/dbname?sslmode=require&timeout=10",
        "With special chars and extra parameters (all requirements met)"
    )
    
    print("\n" + "=" * 80)
    print("Test complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

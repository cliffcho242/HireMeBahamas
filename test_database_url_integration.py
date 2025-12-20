#!/usr/bin/env python3
"""
Integration test for DATABASE_URL normalization.

This test verifies that the same DATABASE_URL can be used for both
async (SQLAlchemy + asyncpg) and sync (psycopg2) connections by
normalizing the URL appropriately for each driver.
"""
import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from backend_app.core.db_url_normalizer import normalize_database_url

print("="*70)
print("DATABASE_URL Normalization Integration Test")
print("="*70)
print()

# Test with common DATABASE_URL formats
test_scenarios = [
    {
        "name": "Neon with asyncpg suffix",
        "database_url": "postgresql+asyncpg://user:pass@ep-dawn-cloud.us-east-1.aws.neon.tech:5432/mydb",
        "description": "Common format when using SQLAlchemy async"
    },
    {
        "name": "Render without suffix",
        "database_url": "postgresql://user:pass@mydb.internal:5432/mydb",
        "description": "Common format for Render internal network"
    },
    {
        "name": "Heroku-style postgres scheme",
        "database_url": "postgres://user:pass@ec2-host.compute-1.amazonaws.com:5432/mydb",
        "description": "Common format for Heroku Postgres"
    }
]

print("Testing URL normalization for different scenarios:")
print("-"*70)
print()

for scenario in test_scenarios:
    print(f"Scenario: {scenario['name']}")
    print(f"Description: {scenario['description']}")
    print()
    
    db_url = scenario['database_url']
    
    # Normalize for sync driver (psycopg2)
    sync_url = normalize_database_url(db_url, for_async=False)
    
    # Normalize for async driver (asyncpg)
    async_url = normalize_database_url(db_url, for_async=True)
    
    print(f"Original URL:  {db_url}")
    print(f"Sync URL:      {sync_url}")
    print(f"Async URL:     {async_url}")
    print()
    
    # Verify sync URL has no driver suffix
    if "+asyncpg" in sync_url or "+psycopg2" in sync_url or "+psycopg" in sync_url:
        print("❌ ERROR: Sync URL should not have driver suffix!")
        sys.exit(1)
    
    # Verify async URL has asyncpg suffix
    if "+asyncpg" not in async_url:
        print("❌ ERROR: Async URL should have +asyncpg suffix!")
        sys.exit(1)
    
    # Verify both use postgresql scheme
    if not sync_url.startswith("postgresql://"):
        print("❌ ERROR: Sync URL should start with postgresql://!")
        sys.exit(1)
    
    if not async_url.startswith("postgresql+asyncpg://"):
        print("❌ ERROR: Async URL should start with postgresql+asyncpg://!")
        sys.exit(1)
    
    print("✅ URLs normalized correctly for both drivers")
    print("-"*70)
    print()

print()
print("="*70)
print("✅ All integration tests passed!")
print("="*70)
print()
print("Summary:")
print("- Same DATABASE_URL can be used for both async and sync connections")
print("- URL is automatically normalized based on driver requirements")
print("- No manual URL manipulation needed in application code")
print()
print("Next Steps:")
print("1. Set DATABASE_URL in your environment (any format works)")
print("2. Async connections (SQLAlchemy) will get postgresql+asyncpg:// format")
print("3. Sync connections (psycopg2) will get postgresql:// format")
print("4. Both drivers will work correctly with the same environment variable")

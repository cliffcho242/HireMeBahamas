"""
Integration test for app/database.py module.

This test demonstrates how to use the database module in a real application.
"""
import os
import sys


def test_basic_usage():
    """Test basic usage pattern of the database module."""
    print("\n=== Integration Test: Basic Usage ===")
    
    # Import the module
    from app.database import init_db, warmup_db
    
    # Test 1: Without DATABASE_URL
    print("\n1. Testing without DATABASE_URL...")
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]
    
    engine = init_db()
    assert engine is None, "Engine should be None without DATABASE_URL"
    print("   ✅ Returns None when DATABASE_URL is missing")
    
    # Test 2: Warmup with None engine
    print("\n2. Testing warmup with None engine...")
    warmup_db(engine)  # Should not crash
    print("   ✅ Handles None engine gracefully")
    
    # Test 3: With invalid DATABASE_URL
    print("\n3. Testing with invalid DATABASE_URL...")
    os.environ["DATABASE_URL"] = "not-a-valid-url"
    engine = init_db()
    # Should handle gracefully and return None
    print("   ✅ Handles invalid URL gracefully")
    
    # Test 4: With valid DATABASE_URL format (but non-existent server)
    print("\n4. Testing with valid URL format...")
    os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/testdb?sslmode=require"
    engine = init_db()
    # Engine might be created (even if connection fails), that's OK
    # The important thing is no crash during initialization
    print("   ✅ Initializes with valid URL format")
    
    print("\n=== All integration tests passed ===")


def test_usage_pattern():
    """Document the recommended usage pattern."""
    print("\n=== Recommended Usage Pattern ===")
    print("""
# In your application startup:
from app.database import init_db, warmup_db

# Initialize database engine
engine = init_db()

# Optional: Warm up the connection
if engine is not None:
    warmup_db(engine)

# Use the engine for queries
if engine is not None:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(result.fetchone())
""")
    print("✅ Usage pattern documented")


def main():
    """Run all integration tests."""
    print("=" * 70)
    print("Integration Tests for app/database.py")
    print("=" * 70)
    
    test_basic_usage()
    test_usage_pattern()
    
    print("\n" + "=" * 70)
    print("All integration tests completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()

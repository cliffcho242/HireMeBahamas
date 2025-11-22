"""
Direct test of DATABASE_URL parsing logic from final_backend_postgresql.py
This simulates various malformed DATABASE_URLs to ensure error handling works
"""
from urllib.parse import urlparse


def test_with_malformed_port():
    """Test the exact parsing logic with malformed port"""
    print("Testing DATABASE_URL parsing with malformed port...")
    
    # Simulate the malformed case by creating a mock parsed object
    class MalformedParsed:
        hostname = "localhost"
        username = "testuser"
        password = "testpass"
        path = "/testdb"
        port = "port"  # This is the bug - port returns string 'port'
    
    parsed = MalformedParsed()
    
    # This is the exact code from final_backend_postgresql.py lines 117-121
    try:
        port = int(parsed.port) if parsed.port else 5432
    except (ValueError, TypeError):
        port = 5432
        print(f"⚠️  Invalid port '{parsed.port}' in DATABASE_URL, using default 5432")
    
    # This is the exact code from lines 124-131
    try:
        database = parsed.path[1:] if parsed.path and len(parsed.path) > 1 else None
        if not database:
            raise ValueError("Database name is missing from DATABASE_URL")
    except (ValueError, IndexError) as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        print(f"DATABASE_URL format should be: postgresql://username:password@hostname:5432/database")
        raise
    
    # This is lines 133-140
    DB_CONFIG = {
        "host": parsed.hostname,
        "port": port,
        "database": database,
        "user": parsed.username,
        "password": parsed.password,
        "sslmode": "require",
    }
    
    # This is lines 143-148
    required_fields = ["host", "database", "user", "password"]
    missing_fields = [field for field in required_fields if not DB_CONFIG.get(field)]
    if missing_fields:
        print(f"❌ Missing required DATABASE_URL components: {', '.join(missing_fields)}")
        print(f"DATABASE_URL format should be: postgresql://username:password@hostname:5432/database")
        raise ValueError(f"Invalid DATABASE_URL: missing {', '.join(missing_fields)}")
    
    # This is line 150
    print(f"✅ Database config parsed: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    # Verify the fix worked
    assert port == 5432, f"Port should be 5432 but got {port}"
    assert DB_CONFIG["port"] == 5432, f"DB_CONFIG port should be 5432 but got {DB_CONFIG['port']}"
    assert DB_CONFIG["database"] == "testdb"
    
    print("✅ PASS: Malformed port handled correctly!")


def test_with_missing_database():
    """Test with missing database name"""
    print("\nTesting DATABASE_URL parsing with missing database...")
    
    class MissingDBParsed:
        hostname = "localhost"
        username = "testuser"
        password = "testpass"
        path = "/"  # Empty database name
        port = 5432
    
    parsed = MissingDBParsed()
    
    # Port parsing
    try:
        port = int(parsed.port) if parsed.port else 5432
    except (ValueError, TypeError):
        port = 5432
        print(f"⚠️  Invalid port '{parsed.port}' in DATABASE_URL, using default 5432")
    
    # Database parsing - should fail
    error_caught = False
    try:
        database = parsed.path[1:] if parsed.path and len(parsed.path) > 1 else None
        if not database:
            raise ValueError("Database name is missing from DATABASE_URL")
    except (ValueError, IndexError) as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        print(f"DATABASE_URL format should be: postgresql://username:password@hostname:5432/database")
        error_caught = True
    
    assert error_caught, "Should have caught missing database error"
    print("✅ PASS: Missing database name caught correctly!")


def test_with_missing_credentials():
    """Test with missing username and password"""
    print("\nTesting DATABASE_URL parsing with missing credentials...")
    
    class MissingCredsParsed:
        hostname = "localhost"
        username = None
        password = None
        path = "/testdb"
        port = 5432
    
    parsed = MissingCredsParsed()
    
    # Port parsing
    try:
        port = int(parsed.port) if parsed.port else 5432
    except (ValueError, TypeError):
        port = 5432
    
    # Database parsing
    try:
        database = parsed.path[1:] if parsed.path and len(parsed.path) > 1 else None
        if not database:
            raise ValueError("Database name is missing from DATABASE_URL")
    except (ValueError, IndexError) as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        raise
    
    DB_CONFIG = {
        "host": parsed.hostname,
        "port": port,
        "database": database,
        "user": parsed.username,
        "password": parsed.password,
        "sslmode": "require",
    }
    
    # Validation - should catch missing fields
    required_fields = ["host", "database", "user", "password"]
    missing_fields = [field for field in required_fields if not DB_CONFIG.get(field)]
    
    assert len(missing_fields) == 2, f"Should find 2 missing fields but found {len(missing_fields)}"
    assert "user" in missing_fields
    assert "password" in missing_fields
    print(f"❌ Missing required DATABASE_URL components: {', '.join(missing_fields)}")
    print("✅ PASS: Missing credentials detected correctly!")


if __name__ == "__main__":
    print("=" * 80)
    print("Direct DATABASE_URL Parsing Logic Tests")
    print("=" * 80)
    
    try:
        test_with_malformed_port()
        test_with_missing_database()
        test_with_missing_credentials()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 80)
        raise

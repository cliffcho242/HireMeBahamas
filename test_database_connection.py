#!/usr/bin/env python3
"""
Database Connection Validator

This script tests your PostgreSQL connection and provides detailed diagnostics
to help identify and fix connection issues.

Usage:
    python test_database_connection.py
    
    # Or with explicit DATABASE_URL
    DATABASE_URL="postgresql://user:pass@host:5432/db" python test_database_connection.py
"""

import os
import sys
from urllib.parse import urlparse

try:
    import psycopg2
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("\nInstall required packages:")
    print("  pip install psycopg2-binary python-dotenv")
    sys.exit(1)


# Minimum expected password length for validation warning
MIN_PASSWORD_LENGTH = 8


def mask_password(url):
    """Mask password in URL for safe logging."""
    if not url or "@" not in url:
        return url
    try:
        parts = url.split("@")
        auth_part = parts[0]
        if ":" in auth_part:
            user_scheme = auth_part.rsplit(":", 1)[0]
            return f"{user_scheme}:****@{'@'.join(parts[1:])}"
    except Exception:
        pass
    return url


def parse_and_validate_url(url):
    """Parse and validate DATABASE_URL."""
    print("\n📋 Parsing DATABASE_URL...")
    
    try:
        parsed = urlparse(url)
        
        # Extract components
        scheme = parsed.scheme
        username = parsed.username
        password = parsed.password
        hostname = parsed.hostname
        port = parsed.port or 5432
        database = parsed.path[1:] if parsed.path else None
        
        # Validate components
        issues = []
        if not scheme or scheme not in ["postgres", "postgresql"]:
            issues.append(f"Invalid scheme: '{scheme}' (should be 'postgresql://')")
        
        if not username:
            issues.append("Missing username")
        
        if not password:
            issues.append("Missing password")
        elif len(password) < MIN_PASSWORD_LENGTH:
            issues.append(f"Password seems too short (< {MIN_PASSWORD_LENGTH} chars) - might be truncated")
        
        if not hostname:
            issues.append("Missing hostname")
        
        if not database:
            issues.append("Missing database name")
        
        # Display results
        print(f"   Scheme:   {scheme}")
        print(f"   Username: {username or '[MISSING]'}")
        print(f"   Password: {'*' * len(password) if password else '[MISSING]'} ({len(password) if password else 0} chars)")
        print(f"   Hostname: {hostname or '[MISSING]'}")
        print(f"   Port:     {port}")
        print(f"   Database: {database or '[MISSING]'}")
        
        # Check for special indicators
        if hostname:
            if ".railway.internal" in hostname:
                print("\n✅ Detected Railway PRIVATE network connection (recommended for Railway backend)")
            elif ".railway.app" in hostname:
                print("\n✅ Detected Railway PUBLIC connection")
            elif hostname.startswith("dpg-") or hostname.endswith(".render.com"):
                print("\n⚠️  Detected Render database - if backend is on Railway, consider migrating to Railway PostgreSQL")
            elif hostname.endswith(".neon.tech") or hostname.startswith("ep-"):
                print("\n✅ Detected Vercel/Neon Postgres")
            elif hostname == "localhost" or hostname == "127.0.0.1":
                print("\n💻 Local database connection")
        
        if issues:
            print("\n❌ URL Validation Issues:")
            for issue in issues:
                print(f"   - {issue}")
            return None, None
        
        print("\n✅ DATABASE_URL format is valid")
        
        return parsed, {
            "host": hostname,
            "port": port,
            "database": database,
            "user": username,
            "password": password,
        }
        
    except Exception as e:
        print(f"❌ Failed to parse DATABASE_URL: {e}")
        return None, None


def test_connection(conn_params):
    """Test actual database connection."""
    print("\n🔌 Testing database connection...")
    
    # Determine SSL mode based on hostname
    # Use 'prefer' for localhost (better compatibility), 'require' for cloud databases
    hostname = conn_params["host"]
    is_local = hostname in ("localhost", "127.0.0.1", "::1")
    sslmode = "prefer" if is_local else "require"
    
    print(f"   SSL mode: {sslmode} ({'local database' if is_local else 'cloud database'})")
    
    try:
        # Attempt connection
        conn = psycopg2.connect(
            host=conn_params["host"],
            port=conn_params["port"],
            database=conn_params["database"],
            user=conn_params["user"],
            password=conn_params["password"],
            connect_timeout=10,
            sslmode=sslmode,
        )
        
        print("✅ Connection successful!")
        
        # Test query
        print("\n🔍 Testing query execution...")
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL version: {version.split(',')[0]}")
        
        # Check application name
        cursor.execute("SELECT current_setting('application_name')")
        app_name = cursor.fetchone()[0]
        print(f"   Application name: {app_name}")
        
        # List tables
        print("\n📊 Listing tables...")
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        tables = cursor.fetchall()
        if tables:
            print(f"   Found {len(tables)} tables:")
            for table in tables[:10]:  # Show first 10
                print(f"   - {table[0]}")
            if len(tables) > 10:
                print(f"   ... and {len(tables) - 10} more")
        else:
            print("   ⚠️  No tables found (database is empty)")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"❌ Connection failed: {error_msg}")
        
        # Provide specific guidance based on error
        if "password authentication failed" in error_msg.lower():
            print("\n🔍 DIAGNOSIS: Authentication Failed")
            print("   - The username or password is incorrect")
            print("   - The database user may not exist")
            print("\n💡 SOLUTIONS:")
            print("   1. Verify credentials in your database dashboard")
            print("   2. Copy the connection string again (may have been updated)")
            print("   3. Check for typos in username/password")
            print("   4. For Railway: Use DATABASE_PRIVATE_URL from PostgreSQL service")
            print("   5. For Render: Get connection string from Render dashboard")
            
        elif "could not connect to server" in error_msg.lower():
            print("\n🔍 DIAGNOSIS: Cannot Reach Server")
            print("   - Server is down or unreachable")
            print("   - Hostname is incorrect")
            print("   - Network/firewall blocking connection")
            print("\n💡 SOLUTIONS:")
            print("   1. Verify database service is running")
            print("   2. Check hostname in DATABASE_URL")
            print("   3. For Railway: Ensure using .railway.internal for private network")
            print("   4. Test from a different network")
            
        elif "timeout" in error_msg.lower():
            print("\n🔍 DIAGNOSIS: Connection Timeout")
            print("   - Database is slow to respond")
            print("   - Network latency too high")
            print("   - Database may be cold-starting")
            print("\n💡 SOLUTIONS:")
            print("   1. Try again in a few seconds")
            print("   2. Increase connect_timeout")
            print("   3. Check database resource usage")
            
        elif "does not exist" in error_msg.lower():
            print("\n🔍 DIAGNOSIS: Database Does Not Exist")
            print("   - The database name is incorrect")
            print("   - Database was deleted")
            print("\n💡 SOLUTIONS:")
            print("   1. Verify database name in your dashboard")
            print("   2. Create the database if it doesn't exist")
            print("   3. Check DATABASE_URL path component")
        
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main test function."""
    print("=" * 70)
    print("Database Connection Validator")
    print("=" * 70)
    
    # Load environment variables
    load_dotenv()
    
    # Get DATABASE_URL
    database_url = os.getenv("DATABASE_PRIVATE_URL") or os.getenv("DATABASE_URL")
    
    if not database_url:
        print("\n❌ No DATABASE_URL found!")
        print("\n💡 SOLUTIONS:")
        print("   1. Set DATABASE_URL environment variable:")
        print("      export DATABASE_URL='postgresql://user:pass@host:5432/db'")
        print("   2. Create .env file with DATABASE_URL")
        print("   3. Pass DATABASE_URL as environment variable:")
        print("      DATABASE_URL='...' python test_database_connection.py")
        sys.exit(1)
    
    # Show which variable is being used
    if os.getenv("DATABASE_PRIVATE_URL"):
        print("\n✅ Using DATABASE_PRIVATE_URL (Railway private network)")
    else:
        print("\n✅ Using DATABASE_URL")
    
    print(f"   {mask_password(database_url)}")
    
    # Parse and validate URL
    parsed, conn_params = parse_and_validate_url(database_url)
    if not conn_params:
        print("\n❌ Cannot proceed with invalid DATABASE_URL")
        print("\nCorrect format:")
        print("   postgresql://username:password@hostname:5432/database")
        sys.exit(1)
    
    # Test connection
    success = test_connection(conn_params)
    
    # Summary
    print("\n" + "=" * 70)
    if success:
        print("✅ ALL TESTS PASSED")
        print("\nYour database connection is working correctly!")
        print("The application should be able to connect successfully.")
    else:
        print("❌ CONNECTION FAILED")
        print("\nPlease review the errors above and apply the suggested solutions.")
        print("\nFor more help, see:")
        print("   - FIX_DATABASE_AUTH_ERROR.md")
        print("   - DATABASE_AUTHENTICATION_TROUBLESHOOTING.md")
    print("=" * 70)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

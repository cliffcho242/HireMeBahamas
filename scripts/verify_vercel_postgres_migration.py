#!/usr/bin/env python3
"""
Vercel Postgres Migration Verification Script
Validates database migration from Railway/Render to Vercel Postgres

Usage:
    python scripts/verify_vercel_postgres_migration.py
    
    # For CI/CD (non-interactive mode)
    NON_INTERACTIVE=true python scripts/verify_vercel_postgres_migration.py
    
    # Custom table list
    VERIFY_TABLES="users,posts,jobs" python scripts/verify_vercel_postgres_migration.py
    
Environment Variables Required:
    VERCEL_POSTGRES_URL or DATABASE_URL - Vercel Postgres connection string
    
Environment Variables Optional:
    NON_INTERACTIVE - Set to 'true' to skip user prompts (default: false)
    VERIFY_TABLES - Comma-separated list of tables to verify (default: users,posts,jobs,messages,notifications)
"""

import os
import sys
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import asyncio

# Check for required dependencies at startup
try:
    import asyncpg
except ImportError:
    print("ERROR: asyncpg is not installed")
    print("Install with: pip install asyncpg")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


def print_header(msg: str) -> None:
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}{msg.center(60)}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")


def print_success(msg: str) -> None:
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.NC}")


def print_warning(msg: str) -> None:
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.NC}")


def print_error(msg: str) -> None:
    """Print an error message"""
    print(f"{Colors.RED}✗ {msg}{Colors.NC}")


def print_info(msg: str) -> None:
    """Print an info message"""
    print(f"{Colors.CYAN}ℹ {msg}{Colors.NC}")


def strip_sslmode_from_url(db_url: str) -> str:
    """Remove sslmode parameter from database URL.
    
    asyncpg doesn't accept 'sslmode' as a connection parameter.
    It handles SSL automatically based on the server's requirements.
    
    Args:
        db_url: Database URL that may contain sslmode parameter
        
    Returns:
        Database URL without sslmode parameter
    """
    from urllib.parse import parse_qs, urlencode
    
    parsed = urlparse(db_url)
    if not parsed.query:
        return db_url
    
    # Parse query parameters
    query_params = parse_qs(parsed.query)
    
    # Remove sslmode if present
    if 'sslmode' in query_params:
        del query_params['sslmode']
    
    # Rebuild query string
    new_query = urlencode(query_params, doseq=True)
    
    # Rebuild URL
    new_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    
    return new_url


def get_database_url() -> str:
    """Get and validate database URL from environment"""
    db_url = os.environ.get('VERCEL_POSTGRES_URL') or os.environ.get('DATABASE_URL')
    
    if not db_url:
        print_error("Neither VERCEL_POSTGRES_URL nor DATABASE_URL is set")
        print("\nSet one of them with:")
        print("  export VERCEL_POSTGRES_URL='postgresql://...'")
        print("  export DATABASE_URL='postgresql://...'")
        sys.exit(1)
    
    # Validate URL format
    try:
        parsed = urlparse(db_url)
        if not parsed.scheme or not parsed.hostname:
            raise ValueError("Invalid URL format")
        
        # Check if it's a Neon/Vercel Postgres URL
        non_interactive = os.environ.get('NON_INTERACTIVE', 'false').lower() == 'true'
        if 'neon.tech' not in parsed.hostname and not non_interactive:
            print_warning(f"Database host ({parsed.hostname}) doesn't appear to be Vercel Postgres (Neon)")
            print_warning("Expected hostname to contain 'neon.tech'")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                sys.exit(1)
        
        return db_url
    except Exception as e:
        print_error(f"Invalid DATABASE_URL format: {e}")
        sys.exit(1)


async def test_connection(db_url: str) -> bool:
    """Test database connectivity"""
    print_header("TESTING DATABASE CONNECTION")
    
    # asyncpg is already imported and verified at startup
    try:
        # Convert to asyncpg format if needed
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        elif db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://')
        
        # Strip sslmode parameter - asyncpg handles SSL automatically
        db_url = strip_sslmode_from_url(db_url)
        
        print_info("Attempting to connect to database...")
        conn = await asyncpg.connect(db_url, timeout=30)
        
        print_success("Connected successfully!")
        
        # Test basic query
        result = await conn.fetchval('SELECT 1')
        if result == 1:
            print_success("Basic query test passed")
        else:
            print_error(f"Basic query returned unexpected value: {result}")
            return False
        
        await conn.close()
        return True
        
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False


async def verify_tables(db_url: str) -> bool:
    """Verify required tables exist"""
    print_header("VERIFYING DATABASE TABLES")
    
    try:
        import asyncpg
        
        # Convert to asyncpg format
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        elif db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://')
        
        # Strip sslmode parameter - asyncpg handles SSL automatically
        db_url = strip_sslmode_from_url(db_url)
        
        conn = await asyncpg.connect(db_url, timeout=30)
        
        # Expected tables
        expected_tables = ['users', 'posts', 'jobs', 'messages', 'notifications', 'followers']
        
        # Get actual tables
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        rows = await conn.fetch(query)
        actual_tables = [row['table_name'] for row in rows]
        
        print_info(f"Found {len(actual_tables)} tables:")
        for table in actual_tables:
            if table in expected_tables:
                print_success(f"  {table}")
            else:
                print_info(f"  {table}")
        
        # Check for missing tables
        missing_tables = [t for t in expected_tables if t not in actual_tables]
        if missing_tables:
            print_warning(f"Missing expected tables: {', '.join(missing_tables)}")
            print_info("These tables may be optional or not yet created")
        else:
            print_success("All expected tables found!")
        
        await conn.close()
        return len(actual_tables) > 0
        
    except Exception as e:
        print_error(f"Table verification failed: {e}")
        return False


async def check_row_counts(db_url: str) -> bool:
    """Check row counts for key tables"""
    print_header("CHECKING ROW COUNTS")
    
    try:
        import asyncpg
        
        # Convert to asyncpg format
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        elif db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://')
        
        # Strip sslmode parameter - asyncpg handles SSL automatically
        db_url = strip_sslmode_from_url(db_url)
        
        conn = await asyncpg.connect(db_url, timeout=30)
        
        # Get tables to check from environment or use defaults
        default_tables = 'users,posts,jobs,messages,notifications'
        tables_str = os.environ.get('VERIFY_TABLES', default_tables)
        tables = [t.strip() for t in tables_str.split(',')]
        
        print_info(f"Checking row counts for tables: {', '.join(tables)}")
        total_rows = 0
        
        for table in tables:
            try:
                # Use proper identifier quoting to prevent SQL injection
                # asyncpg doesn't have _quote_name, so we use format with identifier validation
                # Validate table name contains only safe characters
                if not table.replace('_', '').isalnum():
                    print_warning(f"  {table}: Skipped (invalid table name)")
                    continue
                
                # Use asyncpg's built-in identifier quoting
                query = f'SELECT COUNT(*) FROM "{table}"'
                count = await conn.fetchval(query)
                total_rows += count
                
                if count > 0:
                    print_success(f"  {table}: {count:,} rows")
                else:
                    print_info(f"  {table}: 0 rows (empty)")
            except Exception as e:
                print_warning(f"  {table}: Error - {str(e)[:50]}")
        
        print(f"\n{Colors.CYAN}Total rows across all tables: {total_rows:,}{Colors.NC}")
        
        if total_rows == 0:
            print_warning("No data found in database")
            print_info("This is expected for a new installation")
            print_info("If you migrated data, verify the migration completed successfully")
        
        await conn.close()
        return True
        
    except Exception as e:
        print_error(f"Row count check failed: {e}")
        return False


async def verify_indexes(db_url: str) -> bool:
    """Verify database indexes"""
    print_header("VERIFYING DATABASE INDEXES")
    
    try:
        import asyncpg
        
        # Convert to asyncpg format
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        elif db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://')
        
        # Strip sslmode parameter - asyncpg handles SSL automatically
        db_url = strip_sslmode_from_url(db_url)
        
        conn = await asyncpg.connect(db_url, timeout=30)
        
        # Get indexes
        query = """
            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """
        rows = await conn.fetch(query)
        
        if not rows:
            print_warning("No indexes found")
            print_info("Indexes will be created automatically on first use")
            await conn.close()
            return True
        
        # Group by table
        indexes_by_table = {}
        for row in rows:
            table = row['tablename']
            if table not in indexes_by_table:
                indexes_by_table[table] = []
            indexes_by_table[table].append(row['indexname'])
        
        print_info(f"Found {len(rows)} indexes across {len(indexes_by_table)} tables:")
        for table, indexes in sorted(indexes_by_table.items()):
            print_success(f"  {table}: {len(indexes)} index(es)")
        
        await conn.close()
        return True
        
    except Exception as e:
        print_error(f"Index verification failed: {e}")
        return False


async def test_query_performance(db_url: str) -> bool:
    """Test basic query performance"""
    print_header("TESTING QUERY PERFORMANCE")
    
    try:
        import asyncpg
        import time
        
        # Convert to asyncpg format
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        elif db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://')
        
        # Strip sslmode parameter - asyncpg handles SSL automatically
        db_url = strip_sslmode_from_url(db_url)
        
        conn = await asyncpg.connect(db_url, timeout=30)
        
        # Test 1: Simple SELECT 1
        start = time.time()
        await conn.fetchval('SELECT 1')
        duration = (time.time() - start) * 1000
        
        if duration < 100:
            print_success(f"Simple query: {duration:.2f}ms (excellent)")
        elif duration < 500:
            print_info(f"Simple query: {duration:.2f}ms (good)")
        else:
            print_warning(f"Simple query: {duration:.2f}ms (slow, may improve with connection pooling)")
        
        # Test 2: Table scan (if users table exists)
        try:
            start = time.time()
            await conn.fetchval('SELECT COUNT(*) FROM users')
            duration = (time.time() - start) * 1000
            
            if duration < 100:
                print_success(f"Table scan (users): {duration:.2f}ms (excellent)")
            elif duration < 500:
                print_info(f"Table scan (users): {duration:.2f}ms (good)")
            else:
                print_warning(f"Table scan (users): {duration:.2f}ms (consider adding indexes)")
        except:
            print_info("Skipping table scan test (users table not found)")
        
        await conn.close()
        return True
        
    except Exception as e:
        print_error(f"Performance test failed: {e}")
        return False


async def check_ssl_configuration(db_url: str) -> bool:
    """Verify SSL/TLS configuration"""
    print_header("VERIFYING SSL CONFIGURATION")
    
    parsed = urlparse(db_url)
    
    # Check SSL mode in URL
    if 'sslmode=' in db_url:
        if 'sslmode=require' in db_url:
            print_success("SSL mode: require (secure connection)")
        elif 'sslmode=disable' in db_url:
            print_error("SSL mode: disable (insecure!)")
            print_warning("For production, use sslmode=require")
            return False
        else:
            print_info(f"SSL mode: {db_url.split('sslmode=')[1].split('&')[0]}")
    else:
        print_warning("SSL mode not specified in connection string")
        print_info("Recommended: Add '?sslmode=require' to DATABASE_URL")
    
    # Check hostname
    if 'neon.tech' in parsed.hostname:
        print_success("Using Vercel Postgres (Neon) - SSL enforced by default")
    
    return True


def print_summary(results: dict) -> None:
    """Print summary of verification results"""
    print_header("VERIFICATION SUMMARY")
    
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    failed_checks = total_checks - passed_checks
    
    print(f"Total checks: {total_checks}")
    print(f"{Colors.GREEN}Passed: {passed_checks}{Colors.NC}")
    if failed_checks > 0:
        print(f"{Colors.RED}Failed: {failed_checks}{Colors.NC}")
    
    print("\nCheck details:")
    for check, result in results.items():
        if result:
            print_success(check)
        else:
            print_error(check)
    
    if failed_checks == 0:
        print(f"\n{Colors.GREEN}{'=' * 60}{Colors.NC}")
        print(f"{Colors.GREEN}All verification checks passed! ✓{Colors.NC}")
        print(f"{Colors.GREEN}{'=' * 60}{Colors.NC}")
        print(f"\n{Colors.CYAN}Your Vercel Postgres database is ready to use!{Colors.NC}\n")
    else:
        print(f"\n{Colors.RED}{'=' * 60}{Colors.NC}")
        print(f"{Colors.RED}Some verification checks failed{Colors.NC}")
        print(f"{Colors.RED}{'=' * 60}{Colors.NC}")
        print(f"\n{Colors.YELLOW}Review the errors above and fix them before proceeding.{Colors.NC}\n")


async def main():
    """Main verification function"""
    print_header("VERCEL POSTGRES MIGRATION VERIFICATION")
    print_info("This script verifies your Vercel Postgres database setup")
    print_info("Ensure DATABASE_URL or VERCEL_POSTGRES_URL is set\n")
    
    # Get database URL
    db_url = get_database_url()
    parsed = urlparse(db_url)
    print_success(f"Database: {parsed.hostname}")
    print_info(f"Database name: {parsed.path.lstrip('/')}\n")
    
    # Run all verification checks
    results = {}
    
    results['Connection Test'] = await test_connection(db_url)
    if not results['Connection Test']:
        print_error("Cannot connect to database. Fix connection issues before continuing.")
        sys.exit(1)
    
    results['SSL Configuration'] = await check_ssl_configuration(db_url)
    results['Table Verification'] = await verify_tables(db_url)
    results['Row Count Check'] = await check_row_counts(db_url)
    results['Index Verification'] = await verify_indexes(db_url)
    results['Performance Test'] = await test_query_performance(db_url)
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Verification cancelled by user{Colors.NC}")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

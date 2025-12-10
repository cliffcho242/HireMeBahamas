#!/usr/bin/env python3
"""
Pre-Deployment Health Check Script
===================================

Local health check script that mirrors CI checks.
Run this before pushing to catch issues early.

Usage:
    python scripts/pre_deployment_check.py
    
    # Verbose mode
    python scripts/pre_deployment_check.py --verbose
    
    # Check specific components
    python scripts/pre_deployment_check.py --check environment
    python scripts/pre_deployment_check.py --check database
    python scripts/pre_deployment_check.py --check security

Exit codes:
    0 - All checks passed
    1 - Some checks failed
    2 - Critical failures detected
"""

import os
import sys
import argparse
import time
from urllib.parse import urlparse

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color


def print_header(msg: str) -> None:
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 70}{Colors.NC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{msg.center(70)}{Colors.NC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 70}{Colors.NC}\n")


def print_success(msg: str) -> None:
    """Print a success message"""
    print(f"{Colors.GREEN}✅ {msg}{Colors.NC}")


def print_warning(msg: str) -> None:
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.NC}")


def print_error(msg: str) -> None:
    """Print an error message"""
    print(f"{Colors.RED}❌ {msg}{Colors.NC}")


def print_info(msg: str) -> None:
    """Print an info message"""
    print(f"{Colors.CYAN}ℹ️  {msg}{Colors.NC}")


def check_environment(verbose: bool = False) -> tuple[int, int, int]:
    """
    Check environment configuration.
    Returns (passed, warnings, errors)
    """
    print_header("Environment Configuration Check")
    
    passed = 0
    warnings = 0
    errors = 0
    
    # Placeholder values to check for
    placeholders = [
        "host", "username", "your-secret-key-here",
        "your-jwt-secret", "change-in-production"
    ]
    
    # 1. Check DATABASE_URL
    database_url = os.environ.get('DATABASE_URL', '')
    if database_url:
        has_placeholder = any(p in database_url.lower() for p in placeholders)
        
        if has_placeholder:
            print_error("DATABASE_URL contains placeholder values")
            errors += 1
        elif database_url.startswith('postgresql://') or database_url.startswith('postgres://'):
            print_success("DATABASE_URL: Valid PostgreSQL format")
            
            # Check SSL mode
            if 'sslmode=require' in database_url:
                print_success("DATABASE_URL: SSL mode enabled")
                passed += 1
            else:
                print_warning("DATABASE_URL: SSL mode not explicitly required")
                warnings += 1
            
            if verbose:
                parsed = urlparse(database_url)
                print_info(f"  Host: {parsed.hostname}")
                print_info(f"  Port: {parsed.port or 5432}")
                print_info(f"  Database: {parsed.path.lstrip('/')}")
        else:
            print_warning("DATABASE_URL format may be invalid")
            warnings += 1
    else:
        print_error("DATABASE_URL not set")
        errors += 1
    
    # 2. Check SECRET_KEY
    secret_key = os.environ.get('SECRET_KEY', '')
    if secret_key:
        if any(p in secret_key.lower() for p in placeholders):
            print_error("SECRET_KEY using default/placeholder value")
            errors += 1
        else:
            print_success("SECRET_KEY: Custom value configured")
            passed += 1
    else:
        print_warning("SECRET_KEY not set")
        warnings += 1
    
    # 3. Check JWT_SECRET_KEY
    jwt_secret = os.environ.get('JWT_SECRET_KEY', '')
    if jwt_secret:
        if any(p in jwt_secret.lower() for p in placeholders):
            print_error("JWT_SECRET_KEY using default/placeholder value")
            errors += 1
        else:
            print_success("JWT_SECRET_KEY: Custom value configured")
            passed += 1
    else:
        print_warning("JWT_SECRET_KEY not set")
        warnings += 1
    
    # 4. Check PORT
    port = os.environ.get('PORT', '')
    if port:
        print_success(f"PORT configured: {port}")
        passed += 1
    else:
        print_info("PORT not set (will use default)")
    
    print(f"\n{Colors.BOLD}Environment Check: {passed} passed, {warnings} warnings, {errors} errors{Colors.NC}")
    return (passed, warnings, errors)


def check_database(verbose: bool = False) -> tuple[int, int, int]:
    """
    Check database connectivity.
    Returns (passed, warnings, errors)
    """
    print_header("Database Connectivity Check")
    
    passed = 0
    warnings = 0
    errors = 0
    
    database_url = os.environ.get('DATABASE_URL', '')
    if not database_url:
        print_error("DATABASE_URL not set - skipping connectivity test")
        return (0, 0, 1)
    
    # Try to import database libraries
    try:
        import asyncpg
        use_asyncpg = True
    except ImportError:
        try:
            import psycopg2
            use_asyncpg = False
        except ImportError:
            print_error("Neither asyncpg nor psycopg2 installed")
            print_info("Install with: pip install asyncpg")
            return (0, 0, 1)
    
    # Test connection
    try:
        if use_asyncpg:
            import asyncio
            
            async def test_connection():
                start = time.time()
                conn = await asyncpg.connect(database_url)
                
                # Test query
                result = await conn.fetchval('SELECT 1')
                
                # List tables
                tables = await conn.fetch("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public'
                """)
                
                await conn.close()
                elapsed = int((time.time() - start) * 1000)
                
                return True, elapsed, len(tables)
            
            success, elapsed, table_count = asyncio.run(test_connection())
        else:
            import psycopg2
            
            start = time.time()
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            
            # Test query
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            
            # List tables
            cursor.execute("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """)
            tables = cursor.fetchall()
            
            cursor.close()
            conn.close()
            elapsed = int((time.time() - start) * 1000)
            
            success = True
            table_count = len(tables)
        
        if success:
            print_success(f"Database connection successful ({elapsed}ms)")
            print_success("Query test passed")
            print_success(f"Found {table_count} tables in database")
            passed += 3
            
            if elapsed > 5000:
                print_warning(f"Connection slow (>{elapsed}ms)")
                warnings += 1
        
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        errors += 1
    
    print(f"\n{Colors.BOLD}Database Check: {passed} passed, {warnings} warnings, {errors} errors{Colors.NC}")
    return (passed, warnings, errors)


def check_security(verbose: bool = False) -> tuple[int, int, int]:
    """
    Check security configuration.
    Returns (passed, warnings, errors)
    """
    print_header("Security Audit")
    
    passed = 0
    warnings = 0
    errors = 0
    
    # 1. Check for hardcoded secrets in common files
    import glob
    
    secret_patterns = ['SECRET_KEY', 'JWT_SECRET', 'API_KEY', 'PASSWORD']
    suspicious_files = []
    
    for pattern in ['*.py', 'api/*.py']:
        for filepath in glob.glob(pattern):
            if 'test' in filepath or 'example' in filepath:
                continue
            
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    for secret in secret_patterns:
                        if f'{secret} = "' in content or f"{secret} = '" in content:
                            if 'os.environ' not in content and 'getenv' not in content:
                                suspicious_files.append(filepath)
                                break
            except Exception:
                pass
    
    if suspicious_files:
        print_warning(f"Found potential hardcoded secrets in {len(suspicious_files)} file(s)")
        if verbose:
            for f in suspicious_files[:5]:
                print_info(f"  {f}")
        warnings += 1
    else:
        print_success("No hardcoded secrets detected")
        passed += 1
    
    # 2. Check SSL configuration
    database_url = os.environ.get('DATABASE_URL', '')
    if 'sslmode=require' in database_url:
        print_success("SSL/TLS enforcement configured")
        passed += 1
    else:
        print_warning("SSL/TLS not explicitly enforced in DATABASE_URL")
        warnings += 1
    
    # 3. Check for .env file (shouldn't be committed)
    if os.path.exists('.env'):
        print_info(".env file found (ensure it's in .gitignore)")
        # Check if in gitignore
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as f:
                if '.env' in f.read():
                    print_success(".env is in .gitignore")
                    passed += 1
                else:
                    print_warning(".env not in .gitignore - could expose secrets!")
                    warnings += 1
    
    print(f"\n{Colors.BOLD}Security Check: {passed} passed, {warnings} warnings, {errors} errors{Colors.NC}")
    return (passed, warnings, errors)


def check_imports(verbose: bool = False) -> tuple[int, int, int]:
    """
    Check Python imports validity.
    Returns (passed, warnings, errors)
    """
    print_header("Import Validation")
    
    passed = 0
    warnings = 0
    errors = 0
    
    # Check main API files
    api_files = ['api/index.py', 'api/main.py']
    
    for api_file in api_files:
        if os.path.exists(api_file):
            try:
                import py_compile
                py_compile.compile(api_file, doraise=True)
                print_success(f"{api_file}: Syntax valid")
                passed += 1
            except Exception as e:
                print_error(f"{api_file}: Syntax error - {e}")
                errors += 1
        elif verbose:
            print_info(f"{api_file}: Not found (skipping)")
    
    print(f"\n{Colors.BOLD}Import Check: {passed} passed, {warnings} warnings, {errors} errors{Colors.NC}")
    return (passed, warnings, errors)


def main():
    parser = argparse.ArgumentParser(description='Pre-deployment health check')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose output')
    parser.add_argument('--check', '-c', choices=['environment', 'database', 'security', 'imports'],
                       help='Run specific check only')
    
    args = parser.parse_args()
    
    print_header("🏥 Pre-Deployment Health Check")
    print(f"{Colors.CYAN}Version: 1.0.0{Colors.NC}")
    print(f"{Colors.CYAN}Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}{Colors.NC}\n")
    
    start_time = time.time()
    
    total_passed = 0
    total_warnings = 0
    total_errors = 0
    
    # Run checks
    if args.check is None or args.check == 'environment':
        p, w, e = check_environment(args.verbose)
        total_passed += p
        total_warnings += w
        total_errors += e
    
    if args.check is None or args.check == 'database':
        p, w, e = check_database(args.verbose)
        total_passed += p
        total_warnings += w
        total_errors += e
    
    if args.check is None or args.check == 'security':
        p, w, e = check_security(args.verbose)
        total_passed += p
        total_warnings += w
        total_errors += e
    
    if args.check is None or args.check == 'imports':
        p, w, e = check_imports(args.verbose)
        total_passed += p
        total_warnings += w
        total_errors += e
    
    elapsed = time.time() - start_time
    
    # Final summary
    print_header("Summary")
    print(f"{Colors.BOLD}Total Checks:{Colors.NC}")
    print(f"  {Colors.GREEN}✅ Passed: {total_passed}{Colors.NC}")
    print(f"  {Colors.YELLOW}⚠️  Warnings: {total_warnings}{Colors.NC}")
    print(f"  {Colors.RED}❌ Errors: {total_errors}{Colors.NC}")
    print(f"\n{Colors.CYAN}Completed in {elapsed:.2f}s{Colors.NC}\n")
    
    # Exit code
    if total_errors > 0:
        if total_errors >= 3:
            print_error("CRITICAL: Multiple failures detected - deployment NOT recommended")
            return 2
        else:
            print_warning("Errors detected - fix before deploying")
            return 1
    elif total_warnings > 0:
        print_warning("Warnings detected - review before deploying")
        return 0
    else:
        print_success("All checks passed - ready to deploy!")
        return 0


if __name__ == '__main__':
    sys.exit(main())

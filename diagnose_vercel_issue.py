#!/usr/bin/env python3
"""
Diagnostic Script for Vercel Database Connection Issues
Run this to identify what's preventing users from signing in
"""

import os
import sys
import json
from urllib.parse import urlparse

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("=" * 60)
    print("🔍 CHECKING ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    required_vars = {
        'DATABASE_URL': 'PostgreSQL connection string',
        'SECRET_KEY': 'JWT secret key for authentication',
        'JWT_SECRET_KEY': 'Alternative JWT secret key',
        'ENVIRONMENT': 'Environment setting (production/development)',
    }
    
    optional_vars = {
        'POSTGRES_URL': 'Alternative database URL',
        'DATABASE_PRIVATE_URL': 'Private network database URL',
        'FRONTEND_URL': 'Frontend URL for CORS',
        'DB_CONNECT_TIMEOUT': 'Database connection timeout',
        'DB_POOL_SIZE': 'Database connection pool size',
    }
    
    issues = []
    warnings = []
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive data
            if 'SECRET' in var or 'PASSWORD' in var:
                display_value = '***REDACTED***'
            elif 'DATABASE_URL' in var or 'POSTGRES_URL' in var:
                try:
                    parsed = urlparse(value)
                    display_value = f"{parsed.scheme}://***:***@{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}"
                except:
                    display_value = '***REDACTED***'
            else:
                display_value = value
            
            print(f"✅ {var}: {display_value}")
            print(f"   → {description}")
        else:
            print(f"❌ {var}: NOT SET")
            print(f"   → {description}")
            issues.append(f"{var} is not set")
    
    print()
    
    # Check optional variables
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            if 'SECRET' in var or 'PASSWORD' in var:
                display_value = '***REDACTED***'
            elif 'DATABASE_URL' in var or 'POSTGRES_URL' in var:
                try:
                    parsed = urlparse(value)
                    display_value = f"{parsed.scheme}://***:***@{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}"
                except:
                    display_value = '***REDACTED***'
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"⚠️  {var}: NOT SET (optional)")
            warnings.append(f"{var} is not set (optional)")
    
    print()
    return issues, warnings


def check_database_url_format():
    """Validate DATABASE_URL format"""
    print("=" * 60)
    print("🔍 CHECKING DATABASE_URL FORMAT")
    print("=" * 60)
    
    database_url = (
        os.getenv("DATABASE_PRIVATE_URL") or 
        os.getenv("POSTGRES_URL") or
        os.getenv("DATABASE_URL")
    )
    
    if not database_url:
        print("❌ No DATABASE_URL found")
        return ["DATABASE_URL not configured"]
    
    issues = []
    
    # Parse URL
    try:
        parsed = urlparse(database_url)
        print(f"✅ URL Scheme: {parsed.scheme}")
        print(f"✅ Hostname: {parsed.hostname}")
        print(f"✅ Port: {parsed.port or 5432}")
        print(f"✅ Database: {parsed.path.lstrip('/')}")
        print(f"✅ Username: {parsed.username}")
        print(f"✅ Password: {'***' if parsed.password else 'MISSING'}")
        
        # Check for common issues
        if not parsed.hostname:
            issues.append("DATABASE_URL missing hostname")
            print("❌ Missing hostname in DATABASE_URL")
        
        if not parsed.username:
            issues.append("DATABASE_URL missing username")
            print("❌ Missing username in DATABASE_URL")
        
        if not parsed.password:
            issues.append("DATABASE_URL missing password")
            print("❌ Missing password in DATABASE_URL")
        
        if not parsed.path or len(parsed.path) <= 1:
            issues.append("DATABASE_URL missing database name")
            print("❌ Missing database name in DATABASE_URL")
        
        # Check scheme
        if parsed.scheme not in ['postgres', 'postgresql', 'postgresql+asyncpg']:
            issues.append(f"Unexpected URL scheme: {parsed.scheme}")
            print(f"⚠️  Unusual scheme: {parsed.scheme}")
            print(f"   Expected: postgres:// or postgresql://")
        
        # Check for asyncpg
        if 'asyncpg' not in database_url:
            print("⚠️  URL doesn't include 'asyncpg' driver")
            print("   Note: The backend will automatically convert to postgresql+asyncpg://")
        
        # Check for SSL mode
        if 'sslmode' in database_url:
            sslmode = database_url.split('sslmode=')[1].split('&')[0] if 'sslmode=' in database_url else 'not set'
            print(f"✅ SSL Mode: {sslmode}")
        else:
            print("⚠️  SSL mode not specified (may default to 'prefer')")
        
    except Exception as e:
        issues.append(f"Failed to parse DATABASE_URL: {str(e)}")
        print(f"❌ Failed to parse DATABASE_URL: {e}")
    
    print()
    return issues


def check_python_dependencies():
    """Check if required Python packages are installed"""
    print("=" * 60)
    print("🔍 CHECKING PYTHON DEPENDENCIES")
    print("=" * 60)
    
    required_packages = {
        'fastapi': 'Web framework',
        'sqlalchemy': 'Database ORM',
        'asyncpg': 'PostgreSQL async driver',
        'jose': 'JWT authentication (from python-jose)',
        'passlib': 'Password hashing',
        'mangum': 'Serverless handler for Vercel',
    }
    
    issues = []
    
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {package}: Installed")
            print(f"   → {description}")
        except ImportError:
            print(f"❌ {package}: NOT INSTALLED")
            print(f"   → {description}")
            issues.append(f"Package '{package}' is not installed")
    
    print()
    return issues


def test_database_connection():
    """Test actual database connectivity"""
    print("=" * 60)
    print("🔍 TESTING DATABASE CONNECTION")
    print("=" * 60)
    
    try:
        import asyncio
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        database_url = (
            os.getenv("DATABASE_PRIVATE_URL") or 
            os.getenv("POSTGRES_URL") or
            os.getenv("DATABASE_URL")
        )
        
        if not database_url:
            print("❌ Cannot test: DATABASE_URL not set")
            return ["DATABASE_URL not set"]
        
        # Convert to asyncpg format
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif database_url.startswith("postgresql://") and "asyncpg" not in database_url:
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        async def test():
            try:
                print("Creating database engine...")
                engine = create_async_engine(
                    database_url,
                    pool_pre_ping=True,
                    pool_size=1,
                    max_overflow=0,
                    connect_args={"timeout": 10, "command_timeout": 10}
                )
                
                print("Testing connection...")
                async with engine.begin() as conn:
                    result = await conn.execute(text("SELECT 1"))
                    value = result.scalar()
                    if value == 1:
                        print("✅ Database connection successful!")
                        print("   Query executed: SELECT 1")
                        print(f"   Result: {value}")
                
                await engine.dispose()
                return []
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return [f"Database connection error: {str(e)}"]
        
        issues = asyncio.run(test())
        print()
        return issues
    except ImportError as e:
        print(f"❌ Cannot test connection: Missing dependencies ({e})")
        print()
        return [f"Missing dependencies for database test: {str(e)}"]
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print()
        return [f"Connection test error: {str(e)}"]


def check_vercel_configuration():
    """Check Vercel-specific configuration"""
    print("=" * 60)
    print("🔍 CHECKING VERCEL CONFIGURATION")
    print("=" * 60)
    
    issues = []
    
    # Check for Vercel environment
    vercel_env = os.getenv("VERCEL_ENV")
    vercel_url = os.getenv("VERCEL_URL")
    
    if vercel_env:
        print(f"✅ VERCEL_ENV: {vercel_env}")
    else:
        print("⚠️  VERCEL_ENV: Not set (may not be running on Vercel)")
    
    if vercel_url:
        print(f"✅ VERCEL_URL: {vercel_url}")
    else:
        print("⚠️  VERCEL_URL: Not set (may not be running on Vercel)")
    
    # Check for api/index.py
    api_index_path = os.path.join(os.path.dirname(__file__), 'api', 'index.py')
    if os.path.exists(api_index_path):
        print(f"✅ Vercel API handler exists: api/index.py")
    else:
        print(f"❌ Vercel API handler missing: api/index.py")
        issues.append("api/index.py not found")
    
    # Check vercel.json
    vercel_json_path = os.path.join(os.path.dirname(__file__), 'vercel.json')
    if os.path.exists(vercel_json_path):
        print(f"✅ Vercel config exists: vercel.json")
        try:
            with open(vercel_json_path, 'r') as f:
                config = json.load(f)
                if 'builds' in config:
                    print(f"   Builds: {len(config['builds'])} configured")
                if 'routes' in config:
                    print(f"   Routes: {len(config['routes'])} configured")
        except Exception as e:
            print(f"⚠️  Could not parse vercel.json: {e}")
    else:
        print(f"❌ Vercel config missing: vercel.json")
        issues.append("vercel.json not found")
    
    print()
    return issues


def main():
    """Run all diagnostic checks"""
    print("\n")
    print("=" * 60)
    print("🚀 HIREMEBAHAMAS VERCEL DIAGNOSTIC TOOL")
    print("=" * 60)
    print()
    
    all_issues = []
    all_warnings = []
    
    # Run checks
    env_issues, env_warnings = check_environment_variables()
    all_issues.extend(env_issues)
    all_warnings.extend(env_warnings)
    
    db_url_issues = check_database_url_format()
    all_issues.extend(db_url_issues)
    
    dep_issues = check_python_dependencies()
    all_issues.extend(dep_issues)
    
    conn_issues = test_database_connection()
    all_issues.extend(conn_issues)
    
    vercel_issues = check_vercel_configuration()
    all_issues.extend(vercel_issues)
    
    # Summary
    print("=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    if not all_issues:
        print("✅ All checks passed! No critical issues found.")
    else:
        print(f"❌ Found {len(all_issues)} critical issue(s):")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
    
    if all_warnings:
        print()
        print(f"⚠️  Found {len(all_warnings)} warning(s):")
        for i, warning in enumerate(all_warnings, 1):
            print(f"   {i}. {warning}")
    
    print()
    print("=" * 60)
    
    # Recommendations
    if all_issues:
        print("\n📋 RECOMMENDATIONS:")
        print()
        
        if any('DATABASE_URL' in issue for issue in all_issues):
            print("1. Set DATABASE_URL in Vercel Dashboard:")
            print("   → Go to: https://vercel.com/dashboard")
            print("   → Project Settings → Environment Variables")
            print("   → Add DATABASE_URL with your PostgreSQL connection string")
            print()
        
        if any('SECRET_KEY' in issue or 'JWT_SECRET_KEY' in issue for issue in all_issues):
            print("2. Set SECRET_KEY and JWT_SECRET_KEY:")
            print("   → Generate with: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\"")
            print("   → Add to Vercel Environment Variables")
            print()
        
        if any('not installed' in issue.lower() for issue in all_issues):
            print("3. Install missing dependencies:")
            print("   → Run: pip install -r requirements.txt")
            print("   → Ensure requirements.txt is in your repository")
            print()
        
        if any('connection' in issue.lower() for issue in all_issues):
            print("4. Verify database accessibility:")
            print("   → Check if database allows connections from Vercel IPs")
            print("   → Verify SSL mode is set correctly (sslmode=require)")
            print("   → Check firewall rules on your database host")
            print()
        
        print("For detailed fix instructions, see: FIX_VERCEL_DATABASE_CONNECTION.md")
        print()
    
    return 1 if all_issues else 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

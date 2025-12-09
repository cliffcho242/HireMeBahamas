#!/usr/bin/env python3
"""
Railway PostgreSQL Configuration Checker
=========================================

This script checks if Railway PostgreSQL is configured correctly to prevent
the "root execution of the PostgreSQL server is not permitted" error.

This script prints warnings but never blocks startup. It's informational only.

Usage:
    python railway_postgres_check.py

Exit codes:
    0 - Always (warnings displayed but startup not blocked)
"""

import os
import sys
from urllib.parse import urlparse


def print_critical_notice():
    """Print critical notice about PostgreSQL configuration."""
    # Check if this is being run in a PostgreSQL container context
    railway_service = os.getenv("RAILWAY_SERVICE_NAME", "").lower()
    pgdata = os.getenv("PGDATA")
    postgres_user = os.getenv("POSTGRES_USER")
    
    # If we detect PostgreSQL container indicators, print urgent warning
    if ("postgres" in railway_service) or (pgdata and postgres_user):
        print("\n" + "=" * 80)
        print("🚨 [CRITICAL] POSTGRESQL MISCONFIGURATION DETECTED")
        print("=" * 80)
        print("\n⚠️  [WARNING] THIS REPOSITORY SHOULD NOT BE DEPLOYED AS A POSTGRESQL SERVICE!")
        print("\n❌ If you see this error:")
        print('   "root" execution of the PostgreSQL server is not permitted')
        print("\n✅ YOU NEED TO:")
        print("   1. Delete this PostgreSQL container service from Railway")
        print("   2. Add managed database: + New → Database → PostgreSQL")
        print("   3. Redeploy your backend service")
        print("\n📖 FIX GUIDE: RAILWAY_POSTGRES_QUICKFIX.md")
        print("=" * 80 + "\n")


def check_railway_postgres():
    """Check Railway PostgreSQL configuration."""
    
    print("=" * 80)
    print("🔍 RAILWAY POSTGRESQL CONFIGURATION CHECK")
    print("=" * 80)
    
    # Check if running on Railway
    is_railway = os.getenv("RAILWAY_PROJECT_ID") is not None
    railway_service_name = os.getenv("RAILWAY_SERVICE_NAME", "unknown")
    railway_env = os.getenv("RAILWAY_ENVIRONMENT", "unknown")
    
    if not is_railway:
        print("ℹ️  Not running on Railway - check skipped")
        print("   This check only runs on Railway deployments")
        return 0
    
    print(f"\n✅ Railway Environment Detected:")
    print(f"   Service: {railway_service_name}")
    print(f"   Environment: {railway_env}")
    
    # Critical check: Detect if we're being run AS the PostgreSQL service
    # This would indicate a severe misconfiguration
    if "postgres" in railway_service_name.lower() or "postgresql" in railway_service_name.lower():
        print("\n" + "=" * 80)
        print("🚨 CRITICAL ERROR: POSTGRESQL CONTAINER SERVICE DETECTED!")
        print("=" * 80)
        print("\n❌ This repository should NOT be deployed as a PostgreSQL service!")
        print("❌ Railway is trying to run PostgreSQL in a container, which is NOT PERMITTED")
        print("\n🔥 THIS IS THE CAUSE OF THE ERROR:")
        print('   "root" execution of the PostgreSQL server is not permitted.')
        print('   The server must be started under an unprivileged user ID...')
        print("\n✅ IMMEDIATE ACTIONS REQUIRED:")
        print("   1. GO TO: Railway Dashboard → Your Project")
        print("   2. DELETE: This PostgreSQL container service")
        print("   3. ADD: + New → Database → PostgreSQL (managed database)")
        print("   4. REDEPLOY: Your backend service")
        print("\n📖 DETAILED INSTRUCTIONS:")
        print("   • RAILWAY_POSTGRES_QUICKFIX.md (5-minute fix)")
        print("   • RAILWAY_POSTGRES_ROOT_ERROR_FIX.md (complete guide)")
        print("\n⚠️  This deployment WILL FAIL with 'root execution not permitted' error")
        print("=" * 80)
        return 0
    
    # Check DATABASE_URL
    database_url = os.getenv("DATABASE_URL", "")
    database_private_url = os.getenv("DATABASE_PRIVATE_URL", "")
    
    print("\n🔍 Database Connection Check:")
    
    warnings = []
    
    if not database_url and not database_private_url:
        print("⚠️  WARNING: No DATABASE_URL or DATABASE_PRIVATE_URL found!")
        print("\n📖 RECOMMENDED ACTION:")
        print("   1. Go to Railway Dashboard → Your Project")
        print("   2. Click '+ New' → Database → PostgreSQL")
        print("   3. Railway will automatically inject DATABASE_URL")
        print("   4. Redeploy your backend service")
        warnings.append("No database connection configured")
    
    elif "railway.app" in database_url or "railway.internal" in database_url:
        print("✅ Using Railway managed PostgreSQL database")
        if database_private_url:
            print("✅ DATABASE_PRIVATE_URL available (recommended for internal communication)")
            if "railway.internal" in database_private_url:
                print("   Using internal Railway network - no egress fees!")
    
    elif database_url and "postgres" in database_url:
        print("⚠️  WARNING: DATABASE_URL detected but doesn't point to Railway")
        # Safely parse URL using urllib
        try:
            parsed = urlparse(database_url)
            host = parsed.hostname or "unknown"
            print(f"   Current URL host: {host}")
        except Exception as e:
            print(f"   Current URL: <unable to parse> ({e})")
        print("\n   ⚠️  If you see 'root execution not permitted' errors, this is the cause!")
        warnings.append("Non-Railway PostgreSQL detected")
    
    # Check for PostgreSQL server misconfiguration indicators
    print("\n🔍 PostgreSQL Server Misconfiguration Check:")
    
    # Check if there's a PostgreSQL service trying to run
    postgres_service_vars = {
        "POSTGRES_USER": os.getenv("POSTGRES_USER"),
        "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "POSTGRES_DB": os.getenv("POSTGRES_DB"),
        "PGDATA": os.getenv("PGDATA"),
    }
    
    postgres_indicators = [v for v in postgres_service_vars.values() if v]
    
    if postgres_indicators:
        print("🚨 [CRITICAL WARNING] PostgreSQL server environment variables detected!")
        print("   Found variables:", ", ".join([k for k, v in postgres_service_vars.items() if v]))
        print("\n   ❌ This is a MISCONFIGURATION - PostgreSQL is running as a container!")
        print("   instead of using Railway's managed database.")
        print("\n   🔥 [ERROR] This WILL cause these errors:")
        print("   • 'root execution of the PostgreSQL server is not permitted'")
        print("   • 'Mounting volume on: /var/lib/containers/railwayapp/bind-mounts'")
        print("   • 'possible system security compromise'")
        print("\n   ✅ FIX IMMEDIATELY:")
        print("   1. Delete PostgreSQL container service from Railway Dashboard")
        print("   2. Add: + New → Database → PostgreSQL (managed database)")
        print("   3. Redeploy backend service")
        print("\n   📖 QUICK FIX GUIDE: RAILWAY_POSTGRES_QUICKFIX.md")
        print("   📖 DETAILED GUIDE: RAILWAY_POSTGRES_ROOT_ERROR_FIX.md")
        warnings.append("PostgreSQL server environment variables detected (misconfigured)")
    else:
        print("✅ No PostgreSQL server environment variables detected")
        print("   (This is correct - your app should only CONNECT to PostgreSQL)")
    
    # Summary
    print("\n" + "=" * 80)
    
    if warnings:
        print(f"⚠️  {len(warnings)} WARNING(S) DETECTED:")
        for warning in warnings:
            print(f"   • {warning}")
        print("\n📖 For detailed fix instructions, see:")
        print("   • RAILWAY_POSTGRES_QUICKFIX.md (5-minute fix)")
        print("   • RAILWAY_POSTGRES_ROOT_ERROR_FIX.md (comprehensive guide)")
        print("\n✅ Continuing startup - warnings are informational only")
    else:
        print("✅ ALL CHECKS PASSED")
        print("   PostgreSQL is configured correctly!")
    
    print("=" * 80)
    return 0  # Always return 0 to not block startup


def main():
    """Main entry point."""
    # Print critical notice first, before any other checks
    print_critical_notice()
    
    try:
        exit_code = check_railway_postgres()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n⚠️  Error during check: {e}")
        print("   Continuing startup despite error...")
        sys.exit(0)  # Don't block startup on errors


if __name__ == "__main__":
    main()

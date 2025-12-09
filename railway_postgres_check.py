#!/usr/bin/env python3
"""
Railway PostgreSQL Configuration Checker
=========================================

This script checks if Railway PostgreSQL is configured correctly to prevent
the "root execution of the PostgreSQL server is not permitted" error.

Usage:
    python railway_postgres_check.py

Exit codes:
    0 - PostgreSQL is configured correctly
    1 - PostgreSQL misconfiguration detected
    2 - Not running on Railway (check skipped)
"""

import os
import sys


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
        print("   This script only runs on Railway deployments")
        return 2
    
    print(f"\n✅ Railway Environment Detected:")
    print(f"   Service: {railway_service_name}")
    print(f"   Environment: {railway_env}")
    
    # Check DATABASE_URL
    database_url = os.getenv("DATABASE_URL", "")
    database_private_url = os.getenv("DATABASE_PRIVATE_URL", "")
    
    print("\n🔍 Database Connection Check:")
    
    issues = []
    warnings = []
    
    if not database_url and not database_private_url:
        print("❌ CRITICAL: No DATABASE_URL or DATABASE_PRIVATE_URL found!")
        print("\n📖 FIX REQUIRED:")
        print("   1. Go to Railway Dashboard → Your Project")
        print("   2. Click '+ New' → Database → PostgreSQL")
        print("   3. Railway will automatically inject DATABASE_URL")
        print("   4. Redeploy your backend service")
        issues.append("No database connection configured")
    
    elif "railway.app" in database_url or "railway.internal" in database_url:
        print("✅ Using Railway managed PostgreSQL database")
        if database_private_url:
            print("✅ DATABASE_PRIVATE_URL available (recommended for internal communication)")
            if "railway.internal" in database_private_url:
                print("   Using internal Railway network - no egress fees!")
    
    elif database_url and "postgres" in database_url:
        print("⚠️  WARNING: DATABASE_URL detected but doesn't point to Railway")
        print(f"   Current URL: {database_url[:40]}...")
        print("\n   If you see 'root execution not permitted' errors, this is the cause!")
        warnings.append("Non-Railway PostgreSQL detected")
    
    # Check for PostgreSQL server misconfiguration indicators
    print("\n🔍 PostgreSQL Server Misconfiguration Check:")
    
    # Check if there's a PostgreSQL service trying to run
    postgres_service_indicators = [
        os.getenv("POSTGRES_USER"),
        os.getenv("POSTGRES_PASSWORD"),
        os.getenv("POSTGRES_DB"),
        os.getenv("PGDATA"),
    ]
    
    if any(postgres_service_indicators):
        print("⚠️  WARNING: PostgreSQL server environment variables detected!")
        print("   This suggests PostgreSQL might be running as a service container")
        print("   instead of using Railway's managed database.")
        print("\n   If you see these errors:")
        print("   • 'root execution of the PostgreSQL server is not permitted'")
        print("   • 'Mounting volume on: /var/lib/containers/railwayapp/bind-mounts'")
        print("\n   You have PostgreSQL misconfigured as a container service!")
        warnings.append("PostgreSQL server environment variables detected")
    else:
        print("✅ No PostgreSQL server environment variables detected")
        print("   (This is correct - your app should only CONNECT to PostgreSQL)")
    
    # Summary and instructions
    print("\n" + "=" * 80)
    
    if issues:
        print(f"❌ CRITICAL ISSUES DETECTED: {len(issues)}")
        for issue in issues:
            print(f"   • {issue}")
        print("\n📖 IMMEDIATE ACTION REQUIRED:")
        print("   Read: RAILWAY_POSTGRES_ROOT_ERROR_FIX.md")
        print("   Or run: cat RAILWAY_POSTGRES_ROOT_ERROR_FIX.md")
        print("=" * 80)
        return 1
    
    elif warnings:
        print(f"⚠️  WARNINGS DETECTED: {len(warnings)}")
        for warning in warnings:
            print(f"   • {warning}")
        print("\n📖 RECOMMENDED ACTION:")
        print("   If you're experiencing deployment issues, check:")
        print("   • Railway Dashboard → Services → Delete any PostgreSQL containers")
        print("   • Railway Dashboard → Add managed PostgreSQL database")
        print("   • Read: RAILWAY_POSTGRES_ROOT_ERROR_FIX.md")
        print("=" * 80)
        return 0
    
    else:
        print("✅ ALL CHECKS PASSED")
        print("   PostgreSQL is configured correctly!")
        print("=" * 80)
        return 0


def main():
    """Main entry point."""
    try:
        exit_code = check_railway_postgres()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Error during check: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Railway Deployment Validator
=============================

This script validates that Railway is configured correctly and helps prevent
common deployment mistakes, especially regarding PostgreSQL setup.

Run this before deploying to Railway to catch configuration issues early.
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def print_success(text):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"❌ {text}")


def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")


def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")


def check_postgresql_packages():
    """Check nixpacks.toml doesn't install PostgreSQL server packages"""
    print_header("Checking nixpacks.toml for PostgreSQL Configuration")
    
    nixpacks_path = Path("nixpacks.toml")
    if not nixpacks_path.exists():
        print_error("nixpacks.toml not found!")
        return False
    
    content = nixpacks_path.read_text()
    
    # Check for server packages (these should NOT be present)
    forbidden_packages = [
        '"postgresql"',
        '"postgresql-server"',
        '"postgresql-16"',
        '"postgresql-15"',
        '"postgresql-14"',
    ]
    
    issues_found = []
    for pkg in forbidden_packages:
        if pkg in content:
            issues_found.append(pkg)
    
    if issues_found:
        print_error("CRITICAL: PostgreSQL server packages found in nixpacks.toml!")
        print_error(f"Found: {', '.join(issues_found)}")
        print_error("These will cause deployment to fail!")
        print_info("Remove server packages - only keep postgresql-client, libpq-dev, libpq5")
        return False
    
    # Check for correct client packages
    if '"postgresql-client"' in content and '"libpq-dev"' in content:
        print_success("PostgreSQL client libraries configured correctly")
        return True
    else:
        print_warning("PostgreSQL client libraries may be missing")
        return True


def check_docker_compose():
    """Ensure docker-compose.yml is not being deployed"""
    print_header("Checking Docker Compose Configuration")
    
    railwayignore_path = Path(".railwayignore")
    if not railwayignore_path.exists():
        print_error(".railwayignore not found!")
        print_info("Docker-compose.yml might be deployed to Railway (this is wrong!)")
        return False
    
    content = railwayignore_path.read_text()
    
    if "docker-compose" in content:
        print_success("docker-compose.yml is excluded from Railway deployment")
        return True
    else:
        print_error("docker-compose.yml is NOT excluded from deployment!")
        print_error("Add 'docker-compose.yml' to .railwayignore")
        return False


def check_environment_variables():
    """Check if required environment variables are documented"""
    print_header("Checking Environment Variable Documentation")
    
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "ENVIRONMENT"
    ]
    
    # Check if we're in a Railway environment
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
    
    if is_railway:
        print_info("Running in Railway environment")
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print_error(f"Missing environment variables: {', '.join(missing_vars)}")
            print_info("Configure these in Railway dashboard → Service → Variables")
            return False
        else:
            print_success("All required environment variables are set")
            return True
    else:
        print_info("Not running in Railway environment (this is OK for local dev)")
        print_info(f"Required Railway variables: {', '.join(required_vars)}")
        return True


def check_readme_documentation():
    """Check if setup documentation exists"""
    print_header("Checking Documentation")
    
    required_docs = [
        ("RAILWAY_SETUP_REQUIRED.md", "Railway setup guide"),
        ("RAILWAY_POSTGRESQL_SETUP.md", "PostgreSQL setup guide"),
    ]
    
    all_exist = True
    for doc_file, description in required_docs:
        path = Path(doc_file)
        if path.exists():
            print_success(f"{description}: {doc_file}")
        else:
            print_warning(f"{description} not found: {doc_file}")
            all_exist = False
    
    return all_exist


def check_procfile():
    """Check Procfile configuration"""
    print_header("Checking Procfile")
    
    procfile_path = Path("Procfile")
    if not procfile_path.exists():
        print_warning("Procfile not found (Railway will use nixpacks start command)")
        return True
    
    content = procfile_path.read_text()
    
    # Check that Procfile doesn't try to start PostgreSQL
    if "postgres" in content.lower() and "psql" not in content.lower():
        print_error("Procfile mentions 'postgres' - you might be trying to start PostgreSQL!")
        print_error("Remove any PostgreSQL server commands from Procfile")
        return False
    
    print_success("Procfile looks OK")
    return True


def print_railway_setup_guide():
    """Print quick setup guide for Railway"""
    print_header("Railway PostgreSQL Setup Guide")
    
    print("To properly set up PostgreSQL on Railway:\n")
    print("1. Go to Railway Dashboard (https://railway.app/dashboard)")
    print("2. Open your project")
    print("3. Click '+ New' → 'Database' → 'Add PostgreSQL'")
    print("4. Wait for provisioning (~1-2 minutes)")
    print("5. Railway will auto-inject DATABASE_URL into your backend service")
    print("6. Redeploy your backend service\n")
    
    print("DO NOT:")
    print("  ❌ Deploy PostgreSQL as a container/application")
    print("  ❌ Try to run PostgreSQL in your Dockerfile")
    print("  ❌ Deploy docker-compose.yml to Railway\n")
    
    print("For detailed instructions, see:")
    print("  📄 RAILWAY_SETUP_REQUIRED.md")
    print("  📄 RAILWAY_POSTGRESQL_SETUP.md\n")


def main():
    """Run all validation checks"""
    print_header("Railway Deployment Configuration Validator")
    print("This script checks for common Railway deployment mistakes\n")
    
    checks = [
        ("PostgreSQL Packages", check_postgresql_packages),
        ("Docker Compose", check_docker_compose),
        ("Environment Variables", check_environment_variables),
        ("Documentation", check_readme_documentation),
        ("Procfile", check_procfile),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Error running {name} check: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Validation Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nScore: {passed}/{total} checks passed\n")
    
    if passed == total:
        print_success("All checks passed! ✨")
        print_info("Your configuration looks good for Railway deployment")
        print_railway_setup_guide()
        return 0
    else:
        print_error(f"{total - passed} check(s) failed")
        print_info("Fix the issues above before deploying to Railway")
        print_railway_setup_guide()
        return 1


if __name__ == "__main__":
    sys.exit(main())

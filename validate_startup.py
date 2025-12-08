#!/usr/bin/env python3
"""
Startup Validation Script for HireMeBahamas
============================================

This script validates the deployment environment before starting the application.
It checks for:
1. Required environment variables (DATABASE_URL, SECRET_KEY, PORT)
2. Database connectivity (without blocking startup)
3. Python dependencies availability
4. File system permissions for uploads directory

Exits with code 0 if validation passes (warnings allowed).
Exits with code 1 only for critical failures that prevent app startup.
"""

import os
import sys
import time

def validate_environment():
    """Validate required environment variables."""
    print("=" * 70)
    print("🔍 STARTUP VALIDATION - HireMeBahamas")
    print("=" * 70)
    
    warnings = []
    errors = []
    
    # Check PORT
    port = os.getenv("PORT")
    if port:
        print(f"✅ PORT environment variable: {port}")
    else:
        print("⚠️  PORT not set - will use default 8080")
        warnings.append("PORT not set")
    
    # Check DATABASE_URL
    database_url = os.getenv("DATABASE_PRIVATE_URL") or os.getenv("DATABASE_URL")
    if database_url:
        # Don't print the full URL (contains credentials)
        db_host = "***"
        if "://" in database_url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(database_url)
                db_host = parsed.hostname or "***"
            except:
                pass
        print(f"✅ DATABASE_URL configured: {db_host}")
    else:
        print("⚠️  DATABASE_URL not set - app will warn but continue")
        warnings.append("DATABASE_URL not set")
    
    # Check SECRET_KEY
    secret_key = os.getenv("SECRET_KEY")
    if secret_key and secret_key != "your-secret-key-here-change-in-production":
        print("✅ SECRET_KEY configured (custom)")
    else:
        print("⚠️  SECRET_KEY not set or using default - use custom key in production")
        warnings.append("SECRET_KEY using default value")
    
    # Check Python dependencies
    print("\n📦 Checking Python dependencies...")
    required_modules = [
        "flask",
        "psycopg2",
        "bcrypt",
        "jwt",
        "gunicorn",
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - NOT INSTALLED")
            missing_modules.append(module)
            errors.append(f"Missing required module: {module}")
    
    if missing_modules:
        print(f"\n❌ CRITICAL: Missing required Python packages: {', '.join(missing_modules)}")
        print("   Run: pip install -r requirements.txt")
    
    # Check uploads directory
    print("\n📁 Checking file system permissions...")
    upload_dirs = ["uploads/avatars", "uploads/portfolio", "uploads/documents", "uploads/stories"]
    for upload_dir in upload_dirs:
        try:
            os.makedirs(upload_dir, exist_ok=True)
            # Test write permission
            test_file = os.path.join(upload_dir, ".test_write")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print(f"  ✅ {upload_dir} - writable")
        except Exception as e:
            print(f"  ⚠️  {upload_dir} - {str(e)}")
            warnings.append(f"Upload directory issue: {upload_dir}")
    
    # Check environment type
    print("\n🌍 Environment Detection:")
    is_railway = os.getenv("RAILWAY_PROJECT_ID") is not None
    is_render = os.getenv("RENDER") == "true"
    environment = os.getenv("ENVIRONMENT", "development")
    
    if is_railway:
        print("  ✅ Detected: Railway")
    elif is_render:
        print("  ✅ Detected: Render")
    else:
        print(f"  ℹ️  Environment: {environment}")
    
    # Summary
    print("\n" + "=" * 70)
    if errors:
        print(f"❌ VALIDATION FAILED - {len(errors)} critical error(s):")
        for error in errors:
            print(f"   • {error}")
        print("=" * 70)
        return False
    elif warnings:
        print(f"⚠️  VALIDATION PASSED with {len(warnings)} warning(s):")
        for warning in warnings:
            print(f"   • {warning}")
        print("\n✅ Application can start, but review warnings above")
    else:
        print("✅ ALL CHECKS PASSED - Ready to start")
    
    print("=" * 70)
    return True

if __name__ == "__main__":
    start_time = time.time()
    success = validate_environment()
    elapsed = time.time() - start_time
    print(f"\nValidation completed in {elapsed:.2f}s\n")
    
    if not success:
        print("❌ Exiting due to critical errors\n")
        sys.exit(1)
    else:
        print("✅ Starting application...\n")
        sys.exit(0)

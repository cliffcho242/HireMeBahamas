#!/usr/bin/env python3
"""
Quick validation script for IMMORTAL DEPLOY 2025
Validates all configurations before deployment to Render/Vercel
"""
import sys
import os
from pathlib import Path

def check_file(path, description):
    """Check if a file exists"""
    if Path(path).exists():
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path} - NOT FOUND")
        return False

def check_requirements():
    """Validate requirements.txt"""
    print("\n📦 Checking requirements.txt...")
    with open("requirements.txt", "r") as f:
        content = f.read()
        
    required_packages = [
        ("fastapi", "0.115.5"),
        ("uvicorn", "0.32.0"),
        ("gunicorn", "23.0.0"),
        ("sqlalchemy", "2.0.36"),
    ]
    
    # Special checks for packages with version ranges
    version_range_packages = [
        ("asyncpg", ">=0.29.0,<0.30.0"),
    ]
    
    all_found = True
    for pkg_name, version in required_packages:
        # Check for package with version (handles [extras] in package names)
        if f"{pkg_name}[" in content and f"=={version}" in content:
            print(f"  ✅ {pkg_name}=={version}")
        elif f"{pkg_name}=={version}" in content:
            print(f"  ✅ {pkg_name}=={version}")
        else:
            print(f"  ❌ {pkg_name}=={version} - NOT FOUND")
            all_found = False
    
    # Check version range packages
    for pkg_name, version_range in version_range_packages:
        if f"{pkg_name}{version_range}" in content:
            print(f"  ✅ {pkg_name}{version_range}")
        else:
            print(f"  ❌ {pkg_name}{version_range} - NOT FOUND")
            all_found = False
    
    return all_found

def check_gunicorn_config():
    """Validate gunicorn.conf.py"""
    print("\n⚙️  Checking gunicorn.conf.py...")
    try:
        with open("gunicorn.conf.py", "r") as f:
            content = f.read()
        
        checks = [
            ("workers", "workers = int(os.environ.get"),
            ("timeout", "timeout = int(os.environ.get"),
            ("preload_app", "preload_app = True"),
            ("keepalive", "keepalive = 5"),
        ]
        
        all_found = True
        for name, check in checks:
            if check in content:
                print(f"  ✅ {name} configured")
            else:
                print(f"  ❌ {name} - NOT CONFIGURED")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"  ❌ Error reading gunicorn.conf.py: {e}")
        return False

def check_vercel_config():
    """Validate vercel.json"""
    print("\n🔷 Checking vercel.json...")
    import json
    try:
        with open("vercel.json", "r") as f:
            config = json.load(f)
        
        checks = [
            ("version", config.get("version") == 2),
            ("builds", len(config.get("builds", [])) > 0),
            ("functions", "api/**/*.py" in config.get("functions", {})),
            ("rewrites", any("/api/health" in str(r) for r in config.get("rewrites", []))),
        ]
        
        all_found = True
        for name, check in checks:
            if check:
                print(f"  ✅ {name} configured")
            else:
                print(f"  ⚠️  {name} - CHECK MANUALLY")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"  ❌ Error reading vercel.json: {e}")
        return False

def check_api_files():
    """Validate API files"""
    print("\n📁 Checking API files...")
    files = [
        ("api/index.py", "Vercel serverless handler"),
        ("api/requirements.txt", "Vercel dependencies"),
        ("api/database.py", "Database helper"),
        ("api/render.yaml", "Render configuration"),
    ]
    
    all_found = True
    for path, desc in files:
        if not check_file(path, desc):
            all_found = False
    
    return all_found

def check_imports():
    """Test if all imports work"""
    print("\n🐍 Testing Python imports...")
    try:
        # Add current directory to path for imports
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Test Vercel API
        from api.index import app
        print(f"  ✅ api.index imports successfully")
        print(f"     - {len(app.routes)} routes registered")
        
        # Test database helper
        from api.database import get_database_url
        print(f"  ✅ api.database imports successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False

def main():
    """Run all validation checks"""
    print("=" * 70)
    print("🚀 IMMORTAL DEPLOY 2025 - Configuration Validator")
    print("=" * 70)
    
    checks = [
        check_requirements(),
        check_gunicorn_config(),
        check_vercel_config(),
        check_api_files(),
        check_imports(),
    ]
    
    print("\n" + "=" * 70)
    if all(checks):
        print("✅ ALL CHECKS PASSED - Ready for deployment!")
        print("\n📋 Next Steps:")
        print("   1. Set DATABASE_URL in Render dashboard")
        print("   2. Deploy to Render: git push or use dashboard")
        print("   3. Deploy to Vercel: vercel --prod")
        print("   4. Test endpoints: /health and /ready")
        print("\n📖 Full guide: IMMORTAL_DEPLOY_2025.md")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Review errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Vercel Deployment Verification Script
Checks and validates Vercel deployment configuration
Helps diagnose 404: DEPLOYMENT_NOT_FOUND errors
"""
import json
import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report status."""
    path = Path(filepath)
    if path.exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} NOT FOUND: {filepath}")
        return False

def check_vercel_json():
    """Verify vercel.json configuration."""
    print("\n🔍 Checking vercel.json configuration...")
    
    if not check_file_exists("vercel.json", "Root vercel.json"):
        return False
    
    try:
        with open("vercel.json", "r") as f:
            config = json.load(f)
        
        # Check for required fields
        if "version" not in config:
            print("❌ Missing 'version' field in vercel.json")
            return False
        
        print(f"✅ Vercel API version: {config['version']}")
        
        # Check for modern configuration
        if "outputDirectory" in config:
            print(f"✅ Output directory: {config['outputDirectory']}")
            
            # Verify output directory exists after build
            output_dir = Path(config["outputDirectory"])
            if output_dir.exists():
                print(f"✅ Output directory exists: {output_dir}")
                
                # Check for index.html
                index_html = output_dir / "index.html"
                if index_html.exists():
                    print(f"✅ index.html found in output directory")
                else:
                    print(f"⚠️  WARNING: index.html not found in {output_dir}")
                    print("   Run 'cd frontend && npm run build' to generate it")
            else:
                print(f"⚠️  WARNING: Output directory doesn't exist: {output_dir}")
                print("   Run 'cd frontend && npm run build' to generate it")
        
        # Check for conflicting old API usage
        has_builds = "builds" in config
        has_routes = "routes" in config
        has_output_dir = "outputDirectory" in config
        
        if (has_builds or has_routes) and has_output_dir:
            print("❌ CONFLICT: Using both old API (builds/routes) and new API (outputDirectory)")
            print("   Remove 'builds' and 'routes' from vercel.json")
            return False
        
        # Check rewrites configuration
        if "rewrites" in config:
            print(f"✅ Rewrites configured: {len(config['rewrites'])} rules")
            for idx, rewrite in enumerate(config['rewrites']):
                print(f"   {idx + 1}. {rewrite['source']} -> {rewrite['destination']}")
        
        # Check for API directory
        if any(r['destination'].startswith('/api/') for r in config.get('rewrites', [])):
            if not check_file_exists("api/index.py", "API handler"):
                print("⚠️  WARNING: API routes configured but api/index.py not found")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in vercel.json: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading vercel.json: {e}")
        return False

def check_conflicting_configs():
    """Check for conflicting Vercel configuration files."""
    print("\n🔍 Checking for conflicting configuration files...")
    
    conflicts = []
    
    # Check for multiple vercel.json files
    frontend_vercel = Path("frontend/vercel.json")
    if frontend_vercel.exists():
        print(f"⚠️  WARNING: Found frontend/vercel.json")
        print("   This may conflict with root vercel.json")
        print("   Consider removing it and using only root vercel.json")
        conflicts.append(str(frontend_vercel))
    else:
        print("✅ No conflicting frontend/vercel.json")
    
    return len(conflicts) == 0

def check_api_structure():
    """Verify API directory structure."""
    print("\n🔍 Checking API directory structure...")
    
    all_ok = True
    
    if not check_file_exists("api/index.py", "API entry point"):
        all_ok = False
    
    if not check_file_exists("api/requirements.txt", "API requirements"):
        all_ok = False
    else:
        # Check if requirements.txt has mangum
        with open("api/requirements.txt", "r") as f:
            content = f.read()
            if "mangum" not in content.lower():
                print("⚠️  WARNING: 'mangum' not found in api/requirements.txt")
                print("   Mangum is required for Vercel serverless functions")
                all_ok = False
            else:
                print("✅ Mangum handler found in requirements.txt")
            
            if "fastapi" not in content.lower():
                print("⚠️  WARNING: 'fastapi' not found in api/requirements.txt")
                all_ok = False
            else:
                print("✅ FastAPI found in requirements.txt")
    
    # Check runtime.txt
    if check_file_exists("runtime.txt", "Python runtime specification"):
        with open("runtime.txt", "r") as f:
            runtime = f.read().strip()
            print(f"   Python runtime: {runtime}")
    
    return all_ok

def check_environment_vars():
    """Check if essential environment variables are documented."""
    print("\n🔍 Checking environment variable documentation...")
    
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY", 
        "JWT_SECRET_KEY"
    ]
    
    print("Required environment variables (must be set in Vercel):")
    for var in required_vars:
        print(f"   • {var}")
    
    print("\n⚠️  These MUST be configured in Vercel Dashboard:")
    print("   1. Go to https://vercel.com/dashboard")
    print("   2. Select your project")
    print("   3. Go to Settings > Environment Variables")
    print("   4. Add all required variables")
    
    return True

def check_gitignore():
    """Check .gitignore and .vercelignore."""
    print("\n🔍 Checking ignore files...")
    
    all_ok = True
    
    if check_file_exists(".gitignore", ".gitignore"):
        with open(".gitignore", "r") as f:
            content = f.read()
            if "frontend/dist" not in content and "dist/" not in content:
                print("⚠️  WARNING: frontend/dist should be in .gitignore")
                print("   (Vercel will build it automatically)")
            else:
                print("✅ Build output properly ignored in git")
    
    if check_file_exists(".vercelignore", ".vercelignore"):
        print("✅ .vercelignore configured for optimal deployment")
    
    return all_ok

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("🚀 Vercel Deployment Verification")
    print("=" * 60)
    
    # Change to repository root
    repo_root = Path(__file__).parent.parent
    os.chdir(repo_root)
    print(f"📁 Working directory: {os.getcwd()}\n")
    
    checks = [
        ("Vercel Configuration", check_vercel_json),
        ("Conflicting Configs", check_conflicting_configs),
        ("API Structure", check_api_structure),
        ("Environment Variables", check_environment_vars),
        ("Ignore Files", check_gitignore),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error during {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Verification Summary")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✅ All checks passed!")
        print("\n📝 Next steps:")
        print("1. Ensure GitHub secrets are configured:")
        print("   - VERCEL_TOKEN")
        print("   - VERCEL_ORG_ID")
        print("   - VERCEL_PROJECT_ID")
        print("2. Ensure Vercel environment variables are set:")
        print("   - DATABASE_URL")
        print("   - SECRET_KEY")
        print("   - JWT_SECRET_KEY")
        print("3. Push to main branch to trigger deployment")
        print("4. Check deployment status in Vercel dashboard")
        return 0
    else:
        print("❌ Some checks failed!")
        print("\n📖 Troubleshooting guides:")
        print("   • TROUBLESHOOTING_DEPLOYMENT_NOT_FOUND.md - Complete troubleshooting guide")
        print("   • VERCEL_DEPLOYMENT_404_FIX.md - Detailed fix documentation")
        print("   • FIX_SIGN_IN_DEPLOYMENT_GUIDE.md - Setup instructions")
        return 1

if __name__ == "__main__":
    sys.exit(main())

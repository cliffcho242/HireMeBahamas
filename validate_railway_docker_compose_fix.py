#!/usr/bin/env python3
"""
Validation script for Railway deployment configuration.
Ensures docker-compose files cannot be deployed to Railway.
"""

import json
import os
import sys
from pathlib import Path

def check_file_exists(filepath: str, should_exist: bool = True) -> tuple[bool, str]:
    """Check if a file exists or doesn't exist as expected."""
    exists = Path(filepath).exists()
    if should_exist:
        if exists:
            return True, f"✅ {filepath} exists"
        else:
            return False, f"❌ {filepath} does NOT exist (but should)"
    else:
        if not exists:
            return True, f"✅ {filepath} does NOT exist (correct)"
        else:
            return False, f"❌ {filepath} exists (should not exist)"

def check_file_content(filepath: str, patterns: list[str], should_contain: bool = True) -> tuple[bool, str]:
    """Check if a file contains or doesn't contain specific patterns."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        results = []
        for pattern in patterns:
            found = pattern in content
            if should_contain:
                if found:
                    results.append(f"✅ {filepath} contains '{pattern}'")
                else:
                    results.append(f"❌ {filepath} missing '{pattern}'")
            else:
                if not found:
                    results.append(f"✅ {filepath} does not contain '{pattern}' (correct)")
                else:
                    results.append(f"❌ {filepath} contains '{pattern}' (should not)")
        
        all_pass = all("✅" in r for r in results)
        return all_pass, "\n".join(results)
    except Exception as e:
        return False, f"❌ Error reading {filepath}: {e}"

def check_railway_json():
    """Validate railway.json configuration."""
    print("\n🔍 Checking railway.json configuration...")
    
    # Check file exists
    success, msg = check_file_exists("railway.json")
    print(msg)
    if not success:
        return False
    
    # Check content
    try:
        with open("railway.json", 'r') as f:
            config = json.load(f)
        
        # Check builder is NIXPACKS
        if config.get("build", {}).get("builder") == "NIXPACKS":
            print("✅ Builder is set to NIXPACKS")
        else:
            print("❌ Builder is not set to NIXPACKS")
            return False
        
        # Check dockerCompose is disabled
        docker_compose = config.get("build", {}).get("dockerCompose", None)
        if docker_compose is False:
            print("✅ dockerCompose is explicitly disabled")
        else:
            print("⚠️  dockerCompose is not explicitly disabled (should be set to false)")
        
        return True
    except json.JSONDecodeError as e:
        print(f"❌ railway.json is not valid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading railway.json: {e}")
        return False

def check_ignore_files():
    """Validate .railwayignore and .nixpacksignore files."""
    print("\n🔍 Checking ignore files...")
    
    all_pass = True
    
    # Check .railwayignore
    patterns = ["docker-compose", "docker-compose*.yml", "docker-compose*.yaml"]
    success, msg = check_file_content(".railwayignore", patterns)
    print(msg)
    all_pass = all_pass and success
    
    # Check .nixpacksignore
    patterns = ["docker-compose", ".dockerignore"]
    success, msg = check_file_content(".nixpacksignore", patterns)
    print(msg)
    all_pass = all_pass and success
    
    return all_pass

def check_docker_compose_files():
    """Check docker-compose file naming."""
    print("\n🔍 Checking docker-compose files...")
    
    all_pass = True
    
    # Should NOT exist: docker-compose.yml (old name)
    success, msg = check_file_exists("docker-compose.yml", should_exist=False)
    print(msg)
    all_pass = all_pass and success
    
    # Should exist: docker-compose.local.yml (new name)
    success, msg = check_file_exists("docker-compose.local.yml", should_exist=True)
    print(msg)
    all_pass = all_pass and success
    
    # Check docker-compose.local.yml has proper warnings
    if Path("docker-compose.local.yml").exists():
        patterns = [
            "LOCAL DEVELOPMENT",
            "DO NOT USE",
            "Railway",
            "managed PostgreSQL"
        ]
        success, msg = check_file_content("docker-compose.local.yml", patterns)
        print(msg)
        all_pass = all_pass and success
    
    return all_pass

def main():
    """Run all validation checks."""
    print("=" * 70)
    print("🚀 Railway Deployment Configuration Validator")
    print("=" * 70)
    print("\nThis script validates that Railway will NOT attempt to deploy")
    print("docker-compose files, preventing PostgreSQL root execution errors.")
    print("=" * 70)
    
    all_checks_pass = True
    
    # Run all checks
    all_checks_pass = check_railway_json() and all_checks_pass
    all_checks_pass = check_ignore_files() and all_checks_pass
    all_checks_pass = check_docker_compose_files() and all_checks_pass
    
    # Final summary
    print("\n" + "=" * 70)
    if all_checks_pass:
        print("✅ ALL CHECKS PASSED!")
        print("\nYour configuration is correct. Railway will:")
        print("  - Use Nixpacks builder (NOT Docker Compose)")
        print("  - Ignore docker-compose files")
        print("  - Deploy only the Python backend")
        print("  - NOT attempt to deploy PostgreSQL container")
        print("\nNext steps:")
        print("  1. Ensure you have a managed PostgreSQL database in Railway")
        print("  2. Deploy your backend service")
        print("  3. Verify DATABASE_URL is configured in Railway")
        print("\nFor detailed setup: RAILWAY_SETUP_REQUIRED.md")
    else:
        print("❌ SOME CHECKS FAILED!")
        print("\nPlease fix the issues above before deploying to Railway.")
        print("\nFor help: RAILWAY_SETUP_REQUIRED.md")
    print("=" * 70)
    
    return 0 if all_checks_pass else 1

if __name__ == "__main__":
    sys.exit(main())

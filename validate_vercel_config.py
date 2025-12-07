#!/usr/bin/env python3
"""
Vercel Frontend-Backend Configuration Validator

This script validates that your HireMeBahamas deployment is properly
configured to connect the frontend to the Vercel serverless backend.

Usage:
    python validate_vercel_config.py [deployment_url]

Examples:
    python validate_vercel_config.py https://hiremebahamas.vercel.app
    python validate_vercel_config.py https://hiremebahamas-git-main.vercel.app
"""

import sys
import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Tuple

def check_file_exists(filepath: str) -> Tuple[bool, str]:
    """Check if a file exists."""
    path = Path(filepath)
    if path.exists():
        return True, f"✅ Found: {filepath}"
    else:
        return False, f"❌ Missing: {filepath}"

def check_json_valid(filepath: str) -> Tuple[bool, str]:
    """Check if a JSON file is valid."""
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        return True, f"✅ Valid JSON: {filepath}"
    except json.JSONDecodeError as e:
        return False, f"❌ Invalid JSON in {filepath}: {e}"
    except FileNotFoundError:
        return False, f"❌ File not found: {filepath}"

def check_vercel_json_config() -> List[Tuple[bool, str]]:
    """Validate vercel.json configuration."""
    results = []
    
    # Check if vercel.json exists
    exists, msg = check_file_exists("vercel.json")
    results.append((exists, msg))
    if not exists:
        return results
    
    # Check if it's valid JSON
    valid, msg = check_json_valid("vercel.json")
    results.append((valid, msg))
    if not valid:
        return results
    
    # Check configuration details
    try:
        with open("vercel.json", 'r') as f:
            config = json.load(f)
        
        # Check rewrites
        if "rewrites" in config:
            rewrites = config["rewrites"]
            has_api_rewrite = any(
                r.get("source") == "/api/(.*)" and r.get("destination") == "/api/index.py"
                for r in rewrites
            )
            if has_api_rewrite:
                results.append((True, "✅ API rewrite configured correctly"))
            else:
                results.append((False, "❌ API rewrite missing or incorrect"))
        else:
            results.append((False, "❌ No rewrites configured"))
        
        # Check functions
        if "functions" in config:
            funcs = config["functions"]
            if "api/index.py" in funcs:
                results.append((True, "✅ API function configured"))
            else:
                results.append((False, "❌ API function not configured"))
        else:
            results.append((False, "❌ No functions configured"))
            
    except Exception as e:
        results.append((False, f"❌ Error reading vercel.json: {e}"))
    
    return results

def check_api_directory() -> List[Tuple[bool, str]]:
    """Validate api/ directory structure."""
    results = []
    
    # Check if api/ directory exists
    exists, msg = check_file_exists("api")
    results.append((exists, msg))
    if not exists:
        return results
    
    # Check required files
    required_files = [
        "api/index.py",
        "api/requirements.txt",
        "api/backend_app",
        "api/backend_app/main.py",
        "api/backend_app/database.py",
    ]
    
    for filepath in required_files:
        exists, msg = check_file_exists(filepath)
        results.append((exists, msg))
    
    return results

def check_frontend_config() -> List[Tuple[bool, str]]:
    """Validate frontend configuration."""
    results = []
    
    # Check if frontend directory exists
    exists, msg = check_file_exists("frontend")
    results.append((exists, msg))
    if not exists:
        return results
    
    # Check required files
    required_files = [
        "frontend/package.json",
        "frontend/vite.config.ts",
        "frontend/src/services/api.ts",
        "frontend/src/utils/backendRouter.ts",
    ]
    
    for filepath in required_files:
        exists, msg = check_file_exists(filepath)
        results.append((exists, msg))
    
    # Check .env.example
    exists, msg = check_file_exists("frontend/.env.example")
    results.append((exists, msg))
    
    # Check .env.production
    exists, msg = check_file_exists("frontend/.env.production")
    if exists:
        results.append((exists, msg))
    else:
        results.append((False, "⚠️  Recommended: Create frontend/.env.production for documentation"))
    
    return results

def check_api_smart_routing() -> List[Tuple[bool, str]]:
    """Check if frontend has smart routing for Vercel."""
    results = []
    
    api_file = "frontend/src/services/api.ts"
    if not Path(api_file).exists():
        results.append((False, f"❌ Missing: {api_file}"))
        return results
    
    try:
        with open(api_file, 'r') as f:
            content = f.read()
        
        # Check for Vercel detection
        if "isVercel" in content and "vercel.app" in content:
            results.append((True, "✅ Frontend has Vercel auto-detection"))
        else:
            results.append((False, "❌ Frontend missing Vercel auto-detection"))
        
        # Check for same-origin support
        if "window.location.origin" in content:
            results.append((True, "✅ Frontend supports same-origin API calls"))
        else:
            results.append((False, "❌ Frontend missing same-origin support"))
            
    except Exception as e:
        results.append((False, f"❌ Error reading {api_file}: {e}"))
    
    return results

def test_deployment_url(url: str) -> List[Tuple[bool, str]]:
    """Test a deployed URL."""
    results = []
    
    # Test health endpoint
    health_url = f"{url}/api/health"
    try:
        with urllib.request.urlopen(health_url, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "healthy":
                results.append((True, f"✅ Health endpoint OK: {health_url}"))
                if "platform" in data:
                    results.append((True, f"   Platform: {data['platform']}"))
            else:
                results.append((False, f"❌ Health endpoint returned unexpected data: {data}"))
    except urllib.error.HTTPError as e:
        results.append((False, f"❌ Health endpoint error ({e.code}): {health_url}"))
    except urllib.error.URLError as e:
        results.append((False, f"❌ Cannot reach: {health_url} ({e.reason})"))
    except Exception as e:
        results.append((False, f"❌ Error testing health endpoint: {e}"))
    
    # Test ready endpoint
    ready_url = f"{url}/api/ready"
    try:
        with urllib.request.urlopen(ready_url, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "ready":
                results.append((True, f"✅ Ready endpoint OK: {ready_url}"))
                if "database" in data:
                    results.append((True, f"   Database: {data['database']}"))
            else:
                results.append((False, f"⚠️  Ready endpoint returned: {data}"))
    except urllib.error.HTTPError as e:
        results.append((False, f"⚠️  Ready endpoint error ({e.code}): {ready_url}"))
    except Exception as e:
        results.append((False, f"⚠️  Error testing ready endpoint: {e}"))
    
    return results

def print_results(title: str, results: List[Tuple[bool, str]]):
    """Print formatted results."""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    
    for success, message in results:
        print(message)
    
    # Count successes and failures
    successes = sum(1 for s, _ in results if s)
    failures = sum(1 for s, _ in results if not s)
    
    print(f"\nResults: {successes} passed, {failures} failed")

def main():
    """Main validation function."""
    print("\n" + "="*70)
    print("VERCEL FRONTEND-BACKEND CONFIGURATION VALIDATOR")
    print("="*70)
    
    # Change to repository root if needed
    if Path("frontend").exists() and Path("api").exists():
        repo_root = Path.cwd()
    else:
        # Try to find repository root
        current = Path.cwd()
        while current != current.parent:
            if (current / "frontend").exists() and (current / "api").exists():
                os.chdir(current)
                repo_root = current
                break
            current = current.parent
        else:
            print("❌ Error: Could not find repository root")
            print("   Please run this script from the repository root directory")
            return 1
    
    print(f"Repository root: {repo_root}")
    
    # Run validation checks
    vercel_results = check_vercel_json_config()
    print_results("VERCEL.JSON CONFIGURATION", vercel_results)
    
    api_results = check_api_directory()
    print_results("API DIRECTORY STRUCTURE", api_results)
    
    frontend_results = check_frontend_config()
    print_results("FRONTEND CONFIGURATION", frontend_results)
    
    routing_results = check_api_smart_routing()
    print_results("SMART API ROUTING", routing_results)
    
    # Test deployment URL if provided
    if len(sys.argv) > 1:
        deployment_url = sys.argv[1].rstrip('/')
        deployment_results = test_deployment_url(deployment_url)
        print_results(f"DEPLOYMENT TEST: {deployment_url}", deployment_results)
    
    # Summary
    all_results = vercel_results + api_results + frontend_results + routing_results
    if len(sys.argv) > 1:
        all_results += deployment_results
    
    total_success = sum(1 for s, _ in all_results if s)
    total_tests = len(all_results)
    
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {total_success}")
    print(f"Failed: {total_tests - total_success}")
    
    if total_success == total_tests:
        print("\n✅ ALL CHECKS PASSED!")
        print("   Your Vercel configuration is ready for deployment.")
        return 0
    else:
        print("\n⚠️  SOME CHECKS FAILED")
        print("   Review the errors above and fix them before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

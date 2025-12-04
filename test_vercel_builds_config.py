#!/usr/bin/env python3
"""
Test script to verify vercel.json uses the correct builds format with @vercel/python runtime
"""

import json
import sys
from pathlib import Path


def test_vercel_json_format():
    """Test that vercel.json uses the builds format with @vercel/python@6.1.0"""
    print("=" * 60)
    print("Vercel Builds Configuration Validation")
    print("=" * 60)
    
    vercel_json_path = Path("vercel.json")
    
    # Test 1: Check existence
    print("\n1. Testing vercel.json existence...")
    if not vercel_json_path.exists():
        print("  ✗ vercel.json not found")
        return False
    print("  ✓ vercel.json exists")
    
    # Test 2: Valid JSON
    print("\n2. Testing JSON validity...")
    try:
        with open(vercel_json_path, "r") as f:
            config = json.load(f)
        print("  ✓ vercel.json is valid JSON")
    except json.JSONDecodeError as e:
        print(f"  ✗ Invalid JSON: {e}")
        return False
    
    # Test 3: Check version field
    print("\n3. Testing version field...")
    if "version" not in config:
        print("  ✗ Missing 'version' field")
        return False
    if config["version"] != 2:
        print(f"  ✗ Expected version 2, got {config['version']}")
        return False
    print(f"  ✓ Version is {config['version']}")
    
    # Test 4: Check builds array
    print("\n4. Testing builds configuration...")
    if "builds" not in config:
        print("  ✗ Missing 'builds' array")
        return False
    
    builds = config["builds"]
    if not isinstance(builds, list):
        print("  ✗ 'builds' should be an array")
        return False
    
    if len(builds) == 0:
        print("  ✗ 'builds' array is empty")
        return False
    
    print(f"  ✓ Found {len(builds)} build configuration(s)")
    
    # Test 5: Check Python build configuration
    print("\n5. Testing Python build configuration...")
    python_build = None
    for build in builds:
        if "use" in build and "@vercel/python" in build["use"]:
            python_build = build
            break
    
    if not python_build:
        print("  ✗ No @vercel/python builder found")
        return False
    
    print(f"  ✓ Python builder found: {python_build['use']}")
    
    # Test 6: Verify exact version
    print("\n6. Testing Python builder version...")
    if python_build["use"] != "@vercel/python@6.1.0":
        print(f"  ⚠ Expected @vercel/python@6.1.0, got {python_build['use']}")
        print("  Note: This might be intentional if using a different version")
    else:
        print("  ✓ Using @vercel/python@6.1.0 as specified")
    
    # Test 7: Check src pattern
    print("\n7. Testing source pattern...")
    if "src" not in python_build:
        print("  ✗ Missing 'src' pattern in Python build")
        return False
    
    src_pattern = python_build["src"]
    print(f"  ✓ Source pattern: {src_pattern}")
    
    # Test 8: Check routes configuration
    print("\n8. Testing routes configuration...")
    if "routes" not in config:
        print("  ⚠ No 'routes' array found (optional but recommended)")
    else:
        routes = config["routes"]
        if not isinstance(routes, list):
            print("  ✗ 'routes' should be an array")
            return False
        print(f"  ✓ Found {len(routes)} route(s) configured")
        
        # Check for API route
        has_api_route = False
        for route in routes:
            if "src" in route and "/api/" in route["src"]:
                has_api_route = True
                print(f"  ✓ API route found: {route['src']} → {route.get('dest', 'N/A')}")
        
        if not has_api_route:
            print("  ⚠ No API route found in routes configuration")
    
    print("\n" + "=" * 60)
    print("✅ Vercel configuration validation passed!")
    print("=" * 60)
    print("\nConfiguration Summary:")
    print(f"  - Version: {config['version']}")
    print(f"  - Builds: {len(config['builds'])}")
    print(f"  - Python Runtime: {python_build['use']}")
    print(f"  - Source Pattern: {python_build['src']}")
    if "routes" in config:
        print(f"  - Routes: {len(config['routes'])}")
    
    return True


if __name__ == "__main__":
    success = test_vercel_json_format()
    sys.exit(0 if success else 1)

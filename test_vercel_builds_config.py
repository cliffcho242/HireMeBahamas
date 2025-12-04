#!/usr/bin/env python3
"""
Test script to verify vercel.json uses modern serverless configuration (no builds)
"""

import json
import sys
from pathlib import Path


def test_vercel_json_format():
    """Test that vercel.json uses modern Vercel configuration without deprecated builds"""
    print("=" * 60)
    print("Vercel Modern Configuration Validation")
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
    
    # Test 4: Verify builds is NOT present (deprecated)
    print("\n4. Testing for deprecated builds configuration...")
    if "builds" in config:
        print("  ⚠ WARNING: 'builds' configuration is deprecated!")
        print("  Modern Vercel auto-detects Python serverless functions in api/ directory")
        print("  Consider removing 'builds' section")
        return False
    else:
        print("  ✓ No deprecated 'builds' section (using modern auto-detection)")
    
    # Test 5: Check functions configuration (optional but recommended)
    print("\n5. Testing functions configuration...")
    if "functions" not in config:
        print("  ⚠ No 'functions' configuration (using defaults)")
    else:
        functions = config["functions"]
        if not isinstance(functions, dict):
            print("  ✗ 'functions' should be an object")
            return False
        print(f"  ✓ Found {len(functions)} function(s) configured")
        
        for func_path, func_config in functions.items():
            print(f"    - {func_path}")
            if "memory" in func_config:
                print(f"      Memory: {func_config['memory']} MB")
            if "maxDuration" in func_config:
                print(f"      Max Duration: {func_config['maxDuration']}s")
    
    # Test 6: Check routes configuration
    print("\n6. Testing routes configuration...")
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
    
    # Test 7: Check that Python API files exist
    print("\n7. Testing Python API files...")
    api_dir = Path("api")
    if not api_dir.exists():
        print("  ✗ api/ directory not found")
        return False
    
    python_files = list(api_dir.glob("*.py"))
    if not python_files:
        print("  ✗ No Python files found in api/ directory")
        return False
    
    print(f"  ✓ Found {len(python_files)} Python file(s) in api/")
    for py_file in python_files:
        print(f"    - {py_file.name}")
    
    print("\n" + "=" * 60)
    print("✅ Vercel configuration validation passed!")
    print("=" * 60)
    print("\nConfiguration Summary:")
    print(f"  - Version: {config['version']}")
    print(f"  - Modern Format: Yes (auto-detects Python functions)")
    if "functions" in config:
        print(f"  - Functions: {len(config['functions'])}")
    if "routes" in config:
        print(f"  - Routes: {len(config['routes'])}")
    print(f"  - Python API Files: {len(python_files)}")
    
    return True


if __name__ == "__main__":
    success = test_vercel_json_format()
    sys.exit(0 if success else 1)

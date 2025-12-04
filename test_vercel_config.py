#!/usr/bin/env python3
"""
Test script to verify vercel.json configuration is valid
"""

import json
import os
import sys
from pathlib import Path


def test_vercel_json_exists():
    """Test that vercel.json exists"""
    print("Testing vercel.json existence...")
    if Path("vercel.json").exists():
        print("  ✓ vercel.json exists")
        return True
    else:
        print("  ✗ vercel.json missing")
        return False


def test_vercel_json_valid():
    """Test that vercel.json is valid JSON"""
    print("\nTesting vercel.json syntax...")
    try:
        with open("vercel.json", "r") as f:
            config = json.load(f)
        print("  ✓ vercel.json is valid JSON")
        return True, config
    except json.JSONDecodeError as e:
        print(f"  ✗ vercel.json has JSON error: {e}")
        return False, None


def test_vercel_builds_config(config):
    """Test that builds are properly configured (modern Vercel format)"""
    print("\nTesting builds configuration (modern format)...")
    
    if "builds" not in config:
        print("  ⚠ No 'builds' key in vercel.json (may be using legacy format)")
        return None  # Return None to indicate modern format not used
    
    builds = config["builds"]
    if not builds:
        print("  ✗ 'builds' is empty")
        return False
    
    print(f"  ✓ Found {len(builds)} build(s) configured")
    
    # Test each build configuration
    all_valid = True
    for build in builds:
        src = build.get("src", "")
        use = build.get("use", "")
        
        print(f"\n  Testing build: {src}")
        print(f"    ✓ Source pattern: {src}")
        
        # Check if 'use' is specified
        if use:
            print(f"    ✓ Builder specified: {use}")
            
            # Validate Python builder
            if "python" in src.lower() or src.endswith(".py"):
                if "@vercel/python" in use:
                    print(f"    ✓ Valid Python builder: {use}")
                else:
                    print(f"    ⚠ Non-standard builder for Python: {use}")
        else:
            print(f"    ✗ Missing 'use' (builder) specification")
            all_valid = False
    
    return all_valid


def test_vercel_functions_config(config):
    """Test that functions are properly configured"""
    print("\nTesting functions configuration...")
    
    if "functions" not in config:
        print("  ⚠ No 'functions' key in vercel.json (configuration may be in 'builds' section)")
        return None  # Return None to indicate no functions section
    
    functions = config["functions"]
    if not functions:
        print("  ✗ 'functions' is empty")
        return False
    
    print(f"  ✓ Found {len(functions)} function(s) configured")
    
    # Test each function configuration
    all_valid = True
    for func_path, func_config in functions.items():
        print(f"\n  Testing function: {func_path}")
        
        # Check if file exists (resolve relative to current directory)
        file_path = Path(func_path)
        if file_path.exists():
            print(f"    ✓ File exists: {func_path}")
        else:
            print(f"    ✗ File not found: {func_path}")
            all_valid = False
        
        # Check for runtime (legacy format - optional if using builds)
        if func_path.endswith(".py"):
            if "runtime" in func_config:
                runtime = func_config["runtime"]
                print(f"    ✓ Runtime specified: {runtime}")
                
                # Validate runtime version
                if runtime.startswith("python3."):
                    print(f"    ✓ Valid Python runtime: {runtime}")
                else:
                    print(f"    ⚠ Unusual runtime: {runtime}")
            else:
                # Check if builds section handles runtime
                if "builds" in config:
                    print(f"    ℹ Runtime specified in 'builds' section (modern format)")
                else:
                    print(f"    ✗ Missing 'runtime' for Python function")
                    all_valid = False
        
        # Check optional configurations
        if "memory" in func_config:
            print(f"    ✓ Memory: {func_config['memory']} MB")
        
        if "maxDuration" in func_config:
            print(f"    ✓ Max duration: {func_config['maxDuration']}s")
    
    return all_valid


def test_api_index_exists():
    """Test that api/index.py exists and has handler export"""
    import re
    
    print("\nTesting api/index.py structure...")
    
    api_index = Path("api/index.py")
    if not api_index.exists():
        print("  ✗ api/index.py not found")
        return False
    
    print("  ✓ api/index.py exists")
    
    # Check for handler export using regex to match assignment patterns
    with open(api_index, "r") as f:
        content = f.read()
    
    # Look for handler assignment (not in comments)
    handler_pattern = re.compile(r'^\s*handler\s*=\s*', re.MULTILINE)
    if handler_pattern.search(content):
        print("  ✓ Found handler export")
        return True
    else:
        print("  ✗ No handler export found")
        print("    Expected: handler = Mangum(app, ...)")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Vercel Configuration Validation")
    print("=" * 60)
    
    # Change to repository root
    repo_root = Path(__file__).parent
    os.chdir(repo_root)
    
    # Test existence
    if not test_vercel_json_exists():
        return 1
    
    # Test JSON validity
    valid, config = test_vercel_json_valid()
    if not valid:
        return 1
    
    # Test builds configuration (modern format)
    builds_result = test_vercel_builds_config(config)
    
    # Test functions configuration
    functions_result = test_vercel_functions_config(config)
    
    # Check if either builds or functions (with runtime) is valid
    has_valid_config = False
    if builds_result is True:
        print("\n✅ Modern builds configuration is valid")
        has_valid_config = True
    elif functions_result is True:
        print("\n✅ Legacy functions configuration is valid")
        has_valid_config = True
    elif builds_result is not None and builds_result is not False and functions_result is not None:
        # We have builds section and functions section (modern hybrid approach)
        print("\n✅ Hybrid configuration is valid (builds + functions)")
        has_valid_config = True
    
    if not has_valid_config:
        print("\n❌ Configuration has issues")
        return 1
    
    # Test api/index.py
    if not test_api_index_exists():
        print("\n❌ api/index.py validation failed")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Vercel configuration is valid.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())

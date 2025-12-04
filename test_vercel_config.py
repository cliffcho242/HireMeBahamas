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


def test_vercel_functions_config(config):
    """Test that functions are properly configured"""
    print("\nTesting functions configuration...")
    
    if "functions" not in config:
        print("  ✗ No 'functions' key in vercel.json")
        return False
    
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
        
        # Check for runtime (required for Python functions)
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
    
    # Test functions configuration
    if not test_vercel_functions_config(config):
        print("\n❌ Functions configuration has issues")
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

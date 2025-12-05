#!/usr/bin/env python3
"""
Test script to verify that vercel.json doesn't contain legacy build properties
that would override Vercel Project Settings.
"""

import json
import sys
from pathlib import Path

def test_vercel_config():
    """Test that vercel.json doesn't have legacy build properties."""
    
    vercel_json_path = Path(__file__).parent / "vercel.json"
    
    # Check if file exists
    if not vercel_json_path.exists():
        print(f"✗ {vercel_json_path} not found")
        return False
    
    # Load and parse JSON
    try:
        with open(vercel_json_path, 'r') as f:
            config = json.load(f)
        print(f"✓ {vercel_json_path} is valid JSON")
    except json.JSONDecodeError as e:
        print(f"✗ {vercel_json_path} has invalid JSON: {e}")
        return False
    
    # Check for legacy build properties that should not be present
    legacy_properties = ['buildCommand', 'outputDirectory', 'installCommand', 'builds']
    found_legacy = []
    
    for prop in legacy_properties:
        if prop in config:
            found_legacy.append(prop)
    
    if found_legacy:
        print(f"✗ Found legacy build properties in vercel.json: {', '.join(found_legacy)}")
        print("  These properties override Vercel Project Settings and should be removed.")
        return False
    
    print("✓ No legacy build properties found in vercel.json")
    
    # Verify that important configurations are still present
    expected_configs = ['rewrites', 'headers', 'crons']
    missing_configs = []
    
    for config_key in expected_configs:
        if config_key not in config:
            missing_configs.append(config_key)
    
    if missing_configs:
        print(f"⚠ Warning: Missing expected configurations: {', '.join(missing_configs)}")
    else:
        print("✓ All expected runtime configurations are present")
    
    # Check version
    if config.get('version') == 2:
        print("✓ Using Vercel configuration version 2")
    else:
        print(f"⚠ Warning: Unexpected version: {config.get('version')}")
    
    return True

if __name__ == "__main__":
    success = test_vercel_config()
    
    print("\n" + "="*60)
    if success:
        print("✓ Vercel configuration is correct!")
        print("Build settings should now be configured in Vercel Project Settings.")
        sys.exit(0)
    else:
        print("✗ Vercel configuration needs fixes")
        sys.exit(1)

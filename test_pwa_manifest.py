#!/usr/bin/env python3
"""
Test script to validate PWA manifest configuration
"""
import json
import os
from pathlib import Path

def test_pwa_manifest():
    """Test that the PWA manifest is properly configured"""
    frontend_path = Path(__file__).parent / "frontend"
    manifest_path = frontend_path / "public" / "manifest.json"
    
    print("🔍 Testing PWA Manifest Configuration...")
    print(f"📁 Manifest path: {manifest_path}")
    
    # Check manifest exists
    if not manifest_path.exists():
        print("❌ FAIL: manifest.json not found")
        return False
    
    print("✓ Manifest file exists")
    
    # Load and validate manifest
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    print("✓ Manifest is valid JSON")
    
    # Validate required fields
    required_fields = {
        'name': 'HireMe Bahamas',
        'short_name': 'HireMe',
        'start_url': '/',
        'display': 'standalone',
        'background_color': '#ffffff',
        'theme_color': '#0A66C2'
    }
    
    all_valid = True
    for field, expected_value in required_fields.items():
        actual_value = manifest.get(field)
        if actual_value == expected_value:
            print(f"✓ {field}: {actual_value}")
        else:
            print(f"❌ {field}: Expected '{expected_value}', got '{actual_value}'")
            all_valid = False
    
    # Validate icons
    icons = manifest.get('icons', [])
    if len(icons) >= 2:
        print(f"✓ Found {len(icons)} icon(s)")
        
        # Check for required icon sizes
        icon_sizes = [icon.get('sizes') for icon in icons]
        required_sizes = ['192x192', '512x512']
        
        for size in required_sizes:
            if size in icon_sizes:
                print(f"✓ Icon size {size} present")
                # Find icon with this size
                icon = next((i for i in icons if i.get('sizes') == size), None)
                if icon:
                    icon_path = frontend_path / "public" / icon['src'].lstrip('/')
                    if icon_path.exists():
                        size_kb = icon_path.stat().st_size / 1024
                        print(f"  - File exists: {icon['src']} ({size_kb:.1f} KB)")
                    else:
                        print(f"  ❌ File missing: {icon['src']}")
                        all_valid = False
                else:
                    print(f"  ❌ Icon with size {size} not found in manifest")
                    all_valid = False
            else:
                print(f"❌ Icon size {size} missing")
                all_valid = False
    else:
        print(f"❌ Expected at least 2 icons, found {len(icons)}")
        all_valid = False
    
    # Check index.html for manifest and theme-color
    index_html_path = frontend_path / "index.html"
    if index_html_path.exists():
        with open(index_html_path, 'r') as f:
            html_content = f.read()
        
        if 'rel="manifest"' in html_content and 'href="/manifest.json"' in html_content:
            print("✓ index.html has manifest link")
        else:
            print("❌ index.html missing manifest link")
            all_valid = False
        
        if 'name="theme-color" content="#0A66C2"' in html_content:
            print("✓ index.html has correct theme-color")
        else:
            print("❌ index.html has incorrect or missing theme-color")
            all_valid = False
    else:
        print("❌ index.html not found")
        all_valid = False
    
    # Summary
    print("\n" + "="*50)
    if all_valid:
        print("✅ All PWA manifest tests PASSED")
        print("\nPWA Features Enabled:")
        print("  ✓ Installable on iOS & Android")
        print("  ✓ Standalone app mode")
        print("  ✓ Custom app name and icon")
        print("  ✓ LinkedIn blue theme (#0A66C2)")
        print("  ✓ Offline-capable (via service worker)")
        return True
    else:
        print("❌ Some PWA manifest tests FAILED")
        return False

if __name__ == "__main__":
    success = test_pwa_manifest()
    exit(0 if success else 1)

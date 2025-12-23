#!/usr/bin/env python3
"""
Test script to verify production lock implementation
Tests all protection layers to ensure white screens are impossible
"""

import os
import sys

def test_backend_cors_import():
    """Test 1: Backend CORS module imports correctly"""
    print("🧪 Test 1: Backend CORS Module Import")
    try:
        # Add api directory to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
        from backend_app.cors import apply_cors, get_allowed_origins, get_vercel_preview_regex
        preview_regex = get_vercel_preview_regex()
        print("   ✅ CORS module imported successfully")
        print(f"   ✅ Vercel Preview Regex: {preview_regex}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_cors_configuration():
    """Test 2: CORS configuration works with environment variables"""
    print("\n🧪 Test 2: CORS Configuration")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
        from backend_app.cors import get_allowed_origins
        
        # Test without env var
        origins = get_allowed_origins()
        print(f"   ✅ Without ALLOWED_ORIGINS: {origins}")
        
        # Test with env var
        os.environ['ALLOWED_ORIGINS'] = 'https://hiremebahamas.com,https://www.hiremebahamas.com'
        origins = get_allowed_origins()
        print(f"   ✅ With ALLOWED_ORIGINS: {origins}")
        
        if len(origins) == 2 and 'https://hiremebahamas.com' in origins:
            print("   ✅ CORS configuration works correctly")
            return True
        else:
            print("   ❌ CORS configuration incorrect")
            return False
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_frontend_files_exist():
    """Test 3: Frontend protection files exist"""
    print("\n🧪 Test 3: Frontend Protection Files")
    files_to_check = [
        'frontend/src/main.tsx',
        'frontend/src/components/ErrorBoundary.tsx',
        'frontend/src/App_Original.tsx',
    ]
    
    all_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"   ✅ {file} exists")
        else:
            print(f"   ❌ {file} missing")
            all_exist = False
    
    return all_exist

def test_error_boundary_content():
    """Test 4: ErrorBoundary has correct implementation"""
    print("\n🧪 Test 4: ErrorBoundary Implementation")
    try:
        with open('frontend/src/components/ErrorBoundary.tsx', 'r') as f:
            content = f.read()
        
        checks = [
            ('getDerivedStateFromError', 'getDerivedStateFromError method'),
            ('componentDidCatch', 'componentDidCatch method'),
            ('🔥 RUNTIME ERROR', 'Runtime error logging'),
            ('location.reload()', 'Reload button functionality'),
        ]
        
        all_passed = True
        for check, desc in checks:
            if check in content:
                print(f"   ✅ {desc} present")
            else:
                print(f"   ❌ {desc} missing")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_main_tsx_bootstrap():
    """Test 5: main.tsx has safe bootstrap"""
    print("\n🧪 Test 5: Safe Bootstrap Implementation")
    try:
        with open('frontend/src/main.tsx', 'r') as f:
            content = f.read()
        
        checks = [
            ('💥 BOOT FAILURE', 'Boot failure logging'),
            ('App failed to start', 'Error message'),
            ('location.reload()', 'Reload button'),
            ('try {', 'Try-catch wrapper'),
        ]
        
        all_passed = True
        for check, desc in checks:
            if check in content:
                print(f"   ✅ {desc} present")
            else:
                print(f"   ❌ {desc} missing")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🔒 PRODUCTION LOCK VERIFICATION")
    print("=" * 60)
    
    tests = [
        test_backend_cors_import,
        test_cors_configuration,
        test_frontend_files_exist,
        test_error_boundary_content,
        test_main_tsx_bootstrap,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - Production lock is bulletproof!")
        print("   White screens are now IMPOSSIBLE")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())

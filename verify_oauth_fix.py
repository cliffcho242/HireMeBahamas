#!/usr/bin/env python3
"""
Verification script for OAuth fix
Tests that all dependencies are installed and working
"""
import sys
import subprocess

def test_system_dependencies():
    """Test system dependencies"""
    print("🔍 Testing System Dependencies...")
    packages = ['build-essential', 'libpq-dev', 'python3-dev', 'libssl-dev']
    for pkg in packages:
        result = subprocess.run(['dpkg', '-l', pkg], capture_output=True)
        if result.returncode == 0:
            print(f"  ✅ {pkg} installed")
        else:
            print(f"  ❌ {pkg} NOT installed")
            return False
    return True

def test_python_dependencies():
    """Test Python dependencies"""
    print("\n🔍 Testing Python Dependencies...")
    dependencies = [
        ('fastapi', 'FastAPI'),
        ('google.auth', 'Google Auth'),
        ('google.oauth2', 'Google OAuth2'),
        ('passlib', 'Passlib'),
        ('jose', 'Python-JOSE'),
        ('PIL', 'Pillow'),
        ('aiofiles', 'AioFiles'),
    ]
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name} - {e}")
            return False
    return True

def test_backend_imports():
    """Test backend module imports"""
    print("\n🔍 Testing Backend Module Imports...")
    sys.path.insert(0, 'backend')
    
    try:
        from app.api import auth
        print("  ✅ Backend auth module")
    except Exception as e:
        print(f"  ❌ Backend auth module - {e}")
        return False
    
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        print("  ✅ Google OAuth imports")
    except Exception as e:
        print(f"  ❌ Google OAuth imports - {e}")
        return False
    
    return True

def test_frontend_build():
    """Test frontend build"""
    print("\n🔍 Testing Frontend Build...")
    result = subprocess.run(
        ['npm', 'run', 'build'],
        cwd='frontend',
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  ✅ Frontend builds successfully")
        return True
    else:
        print(f"  ❌ Frontend build failed")
        print(result.stderr)
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("OAuth Fix Verification Script")
    print("=" * 60)
    
    tests = [
        ("System Dependencies", test_system_dependencies),
        ("Python Dependencies", test_python_dependencies),
        ("Backend Imports", test_backend_imports),
        ("Frontend Build", test_frontend_build),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} test failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! OAuth fix is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

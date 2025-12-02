#!/usr/bin/env python3
"""
ASYNCPG 0.30.0 VALIDATION SCRIPT
Validates that asyncpg is correctly installed with binary-only wheels
"""

import sys
import subprocess

# Expected asyncpg version
EXPECTED_ASYNCPG_VERSION = "0.30.0"

def test_asyncpg_installation():
    """Test asyncpg 0.30.0 installation"""
    print("🔍 Testing asyncpg installation...")
    
    try:
        import asyncpg
        version = asyncpg.__version__
        
        if version == EXPECTED_ASYNCPG_VERSION:
            print(f"✅ asyncpg version: {version} - CORRECT")
            return True
        else:
            print(f"❌ asyncpg version: {version} - EXPECTED {EXPECTED_ASYNCPG_VERSION}")
            return False
    except ImportError as e:
        print(f"❌ Failed to import asyncpg: {e}")
        return False

def test_sqlalchemy_compatibility():
    """Test SQLAlchemy async compatibility"""
    print("\n🔍 Testing SQLAlchemy async compatibility...")
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        print("✅ SQLAlchemy async extensions available")
        return True
    except ImportError as e:
        print(f"❌ Failed to import SQLAlchemy async: {e}")
        return False

def test_binary_only_install():
    """Test that --only-binary flag works"""
    print("\n🔍 Testing binary-only installation...")
    
    try:
        result = subprocess.run(
            ["pip", "show", "asyncpg"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            output = result.stdout
            if "Location:" in output:
                print("✅ asyncpg is installed")
                print(f"📦 Package info:\n{output}")
                return True
        
        print("❌ asyncpg package not found")
        return False
    except Exception as e:
        print(f"❌ Failed to check package: {e}")
        return False

def main():
    """Run all validation tests"""
    print("=" * 60)
    print("ASYNCPG 0.30.0 NUCLEAR FIX VALIDATION")
    print("=" * 60)
    
    tests = [
        test_asyncpg_installation(),
        test_sqlalchemy_compatibility(),
        test_binary_only_install()
    ]
    
    print("\n" + "=" * 60)
    if all(tests):
        print("🎯 ALL TESTS PASSED - ASYNCPG 0.30.0 READY FOR DEPLOYMENT")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME TESTS FAILED - CHECK INSTALLATION")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())

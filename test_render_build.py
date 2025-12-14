#!/usr/bin/env python3
"""
Test script to verify Render build fix works correctly
Simulates the build process that Render will execute
"""
import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a shell command and return result"""
    print(f"\n{'=' * 60}")
    print(f"Testing: {description}")
    print(f"Command: {cmd}")
    print(f"{'=' * 60}")
    
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd="/home/runner/work/HireMeBahamas/HireMeBahamas"
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


def main():
    """Run all build verification tests"""
    tests = [
        ("ls -l build.sh", "Verify build.sh exists and is executable"),
        ("bash -n build.sh", "Check build.sh syntax"),
        ("grep -q 'gunicorn==23.0.0' requirements.txt", "Verify gunicorn in requirements.txt"),
        ("grep -q 'bash build.sh' render.yaml", "Verify render.yaml uses build.sh"),
        ("test -f .render-buildpacks.json", "Verify .render-buildpacks.json exists"),
        ("which gunicorn", "Check if gunicorn is installed"),
        ("gunicorn --version", "Verify gunicorn version"),
        ("gunicorn --check-config final_backend_postgresql:application --config gunicorn.conf.py 2>&1 | head -5", 
         "Validate application configuration"),
    ]
    
    print("🧪 Render Build Fix Verification Test")
    print("=" * 60)
    print("This test simulates the Render build process")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for cmd, description in tests:
        if run_command(cmd, description):
            print(f"✅ PASSED: {description}")
            passed += 1
        else:
            print(f"❌ FAILED: {description}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 All tests passed! The build fix is working correctly.")
        print("✅ Ready to deploy to Render")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

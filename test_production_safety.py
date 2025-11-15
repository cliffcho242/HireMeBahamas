#!/usr/bin/env python3
"""
Test script for production_utils module and sample data scripts.

This test verifies that:
1. Production detection works correctly
2. Sample data scripts require --dev flag
3. Sample data scripts block in production mode
"""

import os
import subprocess
import sys


def test_production_detection():
    """Test production detection logic"""
    print("Testing production detection...")

    # Test 1: Default should be development
    from production_utils import is_production, is_development

    if not is_development():
        print("❌ FAIL: Default should be development mode")
        return False

    print("✅ PASS: Default is development mode")

    # Test 2: PRODUCTION=true should enable production
    os.environ["PRODUCTION"] = "true"
    from importlib import reload
    import production_utils

    reload(production_utils)
    if not production_utils.is_production():
        print("❌ FAIL: PRODUCTION=true should enable production mode")
        del os.environ["PRODUCTION"]
        return False

    print("✅ PASS: PRODUCTION=true enables production mode")
    del os.environ["PRODUCTION"]
    reload(production_utils)

    return True


def test_dev_flag_requirement():
    """Test that scripts require --dev flag"""
    print("\nTesting --dev flag requirement...")

    scripts = ["add_sample_posts.py", "seed_data.py"]

    for script in scripts:
        print(f"  Testing {script}...")

        # Run without --dev flag
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print(f"❌ FAIL: {script} should fail without --dev flag")
            return False

        if "--dev flag required" not in result.stdout:
            print(f"❌ FAIL: {script} should show --dev flag error")
            return False

        print(f"✅ PASS: {script} requires --dev flag")

    return True


def test_production_blocking():
    """Test that scripts block in production mode"""
    print("\nTesting production mode blocking...")

    # Set production mode
    os.environ["PRODUCTION"] = "true"

    try:
        result = subprocess.run(
            [sys.executable, "seed_data.py", "--dev"],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "PRODUCTION": "true"},
        )

        if result.returncode == 0:
            print("❌ FAIL: Script should fail in production mode")
            return False

        if "Cannot run in PRODUCTION mode" not in result.stdout:
            print("❌ FAIL: Should show production mode error")
            return False

        print("✅ PASS: Scripts block in production mode")
        return True

    finally:
        if "PRODUCTION" in os.environ:
            del os.environ["PRODUCTION"]


def test_cleanup_script():
    """Test that cleanup script syntax is valid"""
    print("\nTesting cleanup script...")

    result = subprocess.run(
        [sys.executable, "-m", "py_compile", "remove_fake_posts.py"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    if result.returncode != 0:
        print("❌ FAIL: Cleanup script has syntax errors")
        print(result.stderr)
        return False

    print("✅ PASS: Cleanup script syntax is valid")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("PRODUCTION UTILS AND SAFETY CHECKS TEST SUITE")
    print("=" * 60)
    print()

    tests = [
        ("Production Detection", test_production_detection),
        ("Dev Flag Requirement", test_dev_flag_requirement),
        ("Production Blocking", test_production_blocking),
        ("Cleanup Script", test_cleanup_script),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n⚠️  Test '{test_name}' FAILED\n")
        except Exception as e:
            failed += 1
            print(f"\n❌ Test '{test_name}' ERROR: {e}\n")

    print()
    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print()

    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

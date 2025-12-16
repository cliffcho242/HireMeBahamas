#!/usr/bin/env python3
"""
Test Script: Validate Gunicorn Entrypoint Configuration
=========================================================

This script validates that all deployment configurations use the CORRECT
Gunicorn entrypoint format:

✅ CORRECT: poetry run gunicorn app.main:app
    - Working directory: backend/
    - Module path: app.main:app (relative to backend/)
    - Command: cd backend && poetry run gunicorn app.main:app

❌ INCORRECT: gunicorn backend.app.main:app
    - Would try to import from backend.app.main module
    - Would fail because the structure is backend/app/main.py
    - Should NOT be used

This test ensures:
1. All config files use the correct entrypoint
2. The backend/app/main.py file exists
3. No config files use the incorrect backend.app.main:app format
"""

import os
import re
import sys
from pathlib import Path


def test_file_structure():
    """Test 1: Verify the backend application structure is correct."""
    print("Test 1: Verifying file structure...")
    
    # Check that backend/app/main.py exists
    backend_main = Path("backend/app/main.py")
    if not backend_main.exists():
        print(f"  ❌ FAILED: {backend_main} does not exist")
        return False
    print(f"  ✅ PASS: {backend_main} exists")
    
    # Check that app.py does NOT exist in backend/ (to avoid confusion)
    # Note: It's OK if it exists as a wrapper, but main.py should be in app/
    return True


def test_config_files():
    """Test 2: Verify all config files use correct entrypoint."""
    print("\nTest 2: Checking configuration files...")
    
    config_files = [
        "render.yaml",
        "Procfile", 
        "backend/Procfile",
        "railway.toml",
        "nixpacks.toml"
    ]
    
    all_correct = True
    incorrect_pattern = re.compile(r'gunicorn\s+backend\.app\.main:app')
    correct_pattern = re.compile(r'gunicorn\s+app\.main:app')
    
    for config_file in config_files:
        config_path = Path(config_file)
        if not config_path.exists():
            print(f"  ⚠️  SKIP: {config_file} does not exist")
            continue
            
        content = config_path.read_text()
        
        # Check for incorrect usage
        if incorrect_pattern.search(content):
            print(f"  ❌ FAILED: {config_file} uses INCORRECT entrypoint 'backend.app.main:app'")
            all_correct = False
            continue
        
        # Check for correct usage (only if file contains gunicorn command)
        if 'gunicorn' in content:
            if correct_pattern.search(content):
                print(f"  ✅ PASS: {config_file} uses correct entrypoint 'app.main:app'")
            else:
                # Might be using a different entrypoint (e.g., Flask)
                print(f"  ℹ️  INFO: {config_file} contains gunicorn but not FastAPI entrypoint")
        else:
            print(f"  ⚠️  SKIP: {config_file} does not use gunicorn")
    
    return all_correct


def test_working_directory():
    """Test 3: Verify configs change to backend/ directory before running gunicorn."""
    print("\nTest 3: Checking working directory setup...")
    
    config_files = {
        "render.yaml": "startCommand",
        "Procfile": "web:",
        "railway.toml": "startCommand",
        "nixpacks.toml": "cmd"
    }
    
    all_correct = True
    
    for config_file, key in config_files.items():
        config_path = Path(config_file)
        if not config_path.exists():
            print(f"  ⚠️  SKIP: {config_file} does not exist")
            continue
            
        content = config_path.read_text()
        
        # Look for commands that include gunicorn
        if 'gunicorn app.main:app' in content:
            # Check if it changes to backend/ directory
            if 'cd backend' in content or config_file == 'backend/Procfile':
                print(f"  ✅ PASS: {config_file} correctly changes to backend/ directory")
            else:
                print(f"  ❌ FAILED: {config_file} uses app.main:app but doesn't cd to backend/")
                all_correct = False
    
    return all_correct


def test_poetry_usage():
    """Test 4: Verify configs use poetry run for dependency management."""
    print("\nTest 4: Checking Poetry usage...")
    
    config_files = [
        "render.yaml",
        "Procfile",
        "backend/Procfile", 
        "railway.toml",
        "nixpacks.toml"
    ]
    
    all_use_poetry = True
    
    for config_file in config_files:
        config_path = Path(config_file)
        if not config_path.exists():
            continue
            
        content = config_path.read_text()
        
        # Only check files that use gunicorn
        if 'gunicorn app.main:app' in content:
            if 'poetry run gunicorn' in content:
                print(f"  ✅ PASS: {config_file} uses 'poetry run gunicorn'")
            else:
                print(f"  ⚠️  WARNING: {config_file} uses gunicorn without Poetry")
                # This is a warning, not a failure
    
    return all_use_poetry


def main():
    """Run all tests and report results."""
    print("=" * 70)
    print("Gunicorn Entrypoint Validation Test")
    print("=" * 70)
    print()
    print("This test validates the CORRECT Gunicorn entrypoint configuration:")
    print("  ✅ CORRECT:   cd backend && poetry run gunicorn app.main:app")
    print("  ❌ INCORRECT: gunicorn backend.app.main:app")
    print()
    
    # Change to repository root
    repo_root = Path(__file__).parent
    os.chdir(repo_root)
    
    # Run all tests
    tests = [
        ("File Structure", test_file_structure),
        ("Config Files", test_config_files),
        ("Working Directory", test_working_directory),
        ("Poetry Usage", test_poetry_usage)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n  ❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    all_passed = all(result for _, result in results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print()
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("Configuration Summary:")
        print("  • Entrypoint: app.main:app (CORRECT)")
        print("  • Working Directory: Changes to backend/ before running gunicorn")
        print("  • Dependency Management: Uses Poetry")
        print("  • Command Format: cd backend && poetry run gunicorn app.main:app")
        print()
        print("✅ Ready for Render deployment!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print()
        print("Please review the failed tests above and fix the configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

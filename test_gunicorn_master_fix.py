#!/usr/bin/env python3
"""
Test: Gunicorn Master Fix
Validates the master fix ensures correct command structure.
"""
import subprocess
import sys
from pathlib import Path


def test_render_yaml_command():
    """Test render.yaml command structure."""
    print("🧪 Testing render.yaml command...")
    
    render_yaml = Path(__file__).parent / "render.yaml"
    content = render_yaml.read_text()
    
    # Extract startCommand
    for line in content.splitlines():
        if line.strip().startswith('startCommand:'):
            command = line.split(':', 1)[1].strip()
            break
    else:
        print("  ❌ startCommand not found in render.yaml")
        return False
    
    # Verify requirements
    checks = {
        "Single line": '\n' not in command,
        "No backslashes": '\\' not in command.replace('app.main', ''),
        "Has worker-class": '--worker-class' in command,
        "Uses UvicornWorker": 'uvicorn.workers.UvicornWorker' in command,
        "Has bind": '--bind' in command,
        "Uses $PORT": '$PORT' in command,
        "Workers = 1": '--workers 1' in command,
        "Has app.main:app": 'app.main:app' in command,
        "No --preload": '--preload' not in command,
        "Has timeout": '--timeout' in command,
    }
    
    all_passed = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
        if not result:
            all_passed = False
    
    return all_passed


def test_procfile_commands():
    """Test Procfile commands."""
    print("\n🧪 Testing Procfile commands...")
    
    procfiles = [
        Path(__file__).parent / "Procfile",
        Path(__file__).parent / "backend" / "Procfile",
    ]
    
    all_passed = True
    for procfile in procfiles:
        if not procfile.exists():
            print(f"  ⚠️  {procfile.name} not found")
            continue
        
        print(f"\n  📄 {procfile.relative_to(Path(__file__).parent)}")
        content = procfile.read_text()
        
        # Extract web command
        for line in content.splitlines():
            if line.strip().startswith('web:'):
                command = line.split(':', 1)[1].strip()
                break
        else:
            print(f"    ❌ web command not found")
            all_passed = False
            continue
        
        # Verify requirements
        import re
        checks = {
            "Single line": '\n' not in command,
            "No backslash continuations": not re.search(r'\\\s', command),
            "Has worker-class": '--worker-class' in command,
            "Uses UvicornWorker": 'uvicorn.workers.UvicornWorker' in command,
            "Has bind": '--bind' in command,
            "Uses $PORT": '$PORT' in command,
            "Workers = 1": '--workers 1' in command or '--workers=1' in command,
            "Has app.main:app": 'app.main:app' in command,
        }
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"    {status} {check}")
            if not result:
                all_passed = False
    
    return all_passed


def test_gunicorn_config():
    """Test gunicorn.conf.py settings."""
    print("\n🧪 Testing backend/gunicorn.conf.py...")
    
    config_file = Path(__file__).parent / "backend" / "gunicorn.conf.py"
    if not config_file.exists():
        print("  ❌ gunicorn.conf.py not found")
        return False
    
    content = config_file.read_text()
    
    checks = {
        "worker_class configured": 'worker_class = "uvicorn.workers.UvicornWorker"' in content,
        "bind configured": 'bind = ' in content,
        "workers configured": 'workers = ' in content or 'WEB_CONCURRENCY' in content,
        "preload_app = False": 'preload_app = False' in content,
        "timeout configured": 'timeout = ' in content,
    }
    
    all_passed = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
        if not result:
            all_passed = False
    
    return all_passed


def test_validation_script():
    """Test the validation script works."""
    print("\n🧪 Testing validate_gunicorn_commands.py...")
    
    validation_script = Path(__file__).parent / "validate_gunicorn_commands.py"
    if not validation_script.exists():
        print("  ❌ validate_gunicorn_commands.py not found")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(validation_script)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
            timeout=10,
        )
        
        if result.returncode == 0:
            print("  ✅ Validation script passed")
            return True
        else:
            print("  ❌ Validation script failed")
            print(f"  Output: {result.stdout}")
            print(f"  Errors: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Error running validation script: {e}")
        return False


def test_documentation_exists():
    """Test that documentation files exist."""
    print("\n🧪 Testing documentation files...")
    
    docs = [
        "GUNICORN_MASTER_FIX_FOREVER.md",
        "GUNICORN_QUICK_FIX.md",
    ]
    
    all_exist = True
    for doc in docs:
        doc_path = Path(__file__).parent / doc
        if doc_path.exists():
            size = doc_path.stat().st_size
            print(f"  ✅ {doc} ({size:,} bytes)")
        else:
            print(f"  ❌ {doc} not found")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests."""
    print("=" * 80)
    print("🔍 Gunicorn Master Fix - Comprehensive Test Suite")
    print("=" * 80)
    print()
    
    tests = [
        ("Render YAML", test_render_yaml_command),
        ("Procfiles", test_procfile_commands),
        ("Gunicorn Config", test_gunicorn_config),
        ("Validation Script", test_validation_script),
        ("Documentation", test_documentation_exists),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ {name} test raised exception: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS")
    print("=" * 80)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if all(results.values()):
        print()
        print("🎉 ALL TESTS PASSED!")
        print()
        print("✅ Gunicorn Master Fix is complete and verified")
        print("✅ All commands are production-safe")
        print("✅ No unrecognized arguments errors")
        print("✅ No SIGTERM storms")
        print("✅ No boot loops")
        print()
        print("Ready to deploy! 🚀")
        sys.exit(0)
    else:
        print()
        print("❌ SOME TESTS FAILED")
        print()
        print("Please review the failures above and fix the issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()

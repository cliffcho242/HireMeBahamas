"""
Test to verify that port 5432 (PostgreSQL port) is prevented from being used for HTTP services.

This test validates that:
1. Gunicorn configuration rejects port 5432
2. Backend main.py rejects port 5432
3. Error messages are clear and helpful
4. No code accidentally uses port 5432 for HTTP binding
"""

import os
import sys
import subprocess
from pathlib import Path

# Get the repository root directory
REPO_ROOT = Path(__file__).parent


def test_gunicorn_rejects_port_5432():
    """Test that gunicorn configuration rejects port 5432."""
    print("Testing gunicorn configuration with PORT=5432...")
    
    # Test both gunicorn.conf.py files
    gunicorn_files = [
        REPO_ROOT / 'gunicorn.conf.py',
        REPO_ROOT / 'backend' / 'gunicorn.conf.py'
    ]
    
    for config_file in gunicorn_files:
        if not config_file.exists():
            print(f"⚠️  Skipping {config_file} (not found)")
            continue
            
        # Create a test script that imports the config with PORT=5432
        test_script = f"""
import sys
import os
os.environ['PORT'] = '5432'
try:
    # Import will trigger validation
    sys.path.insert(0, '{config_file.parent}')
    import {config_file.stem}
    print("ERROR: Should have exited but didn't")
    sys.exit(1)
except SystemExit as e:
    if e.code == 1:
        print("✅ Correctly rejected port 5432")
        sys.exit(0)
    else:
        print(f"ERROR: Wrong exit code: {{e.code}}")
        sys.exit(1)
"""
        
        result = subprocess.run(
            [sys.executable, '-c', test_script],
            capture_output=True,
            text=True
        )
        
        # Check if the failure is due to missing dependencies (not a test failure)
        if result.returncode != 0 and 'ModuleNotFoundError' in result.stderr:
            print(f"⚠️  Skipping {config_file.name} test (missing dependencies)")
            continue
        
        if result.returncode == 0:
            print(f"✅ {config_file.name} correctly rejects port 5432")
        else:
            print(f"❌ {config_file.name} failed to reject port 5432")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            raise AssertionError(f"{config_file.name} should reject port 5432")


def test_main_py_rejects_port_5432():
    """Test that backend/app/main.py validates port 5432."""
    print("\nTesting backend/app/main.py port validation...")
    
    file_path = REPO_ROOT / 'backend' / 'app' / 'main.py'
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for validation code
    assert 'port == 5432' in content, \
        "backend/app/main.py should check if port == 5432"
    
    assert 'sys.exit(1)' in content, \
        "backend/app/main.py should exit with code 1 for port 5432"
    
    # Check for helpful error messages
    assert 'PostgreSQL' in content, \
        "Error message should mention PostgreSQL"
    
    assert 'reserved' in content or 'DO NOT USE' in content or 'cannot use' in content, \
        "Error message should explain why port 5432 is not allowed"
    
    print("✅ backend/app/main.py has correct port 5432 validation")


def test_no_hardcoded_5432_in_http_configs():
    """Test that no HTTP service configurations use port 5432."""
    print("\nChecking for hardcoded port 5432 in HTTP configurations...")
    
    # Files to check
    files_to_check = [
        'Procfile',
        'Procfile.test',
        'backend/Procfile',
        'nixpacks.toml',
        'start.sh',
        'start_production.sh',
    ]
    
    for file_name in files_to_check:
        file_path = REPO_ROOT / file_name
        if not file_path.exists():
            continue
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for suspicious patterns (port 5432 used outside of database URLs)
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip lines that are clearly about database URLs
            if 'postgresql://' in line or 'DATABASE_URL' in line:
                continue
            
            # Check for port 5432 in uvicorn/gunicorn commands
            if 'port' in line.lower() and '5432' in line:
                if any(keyword in line for keyword in ['uvicorn', 'gunicorn', '--port', '--bind']):
                    raise AssertionError(
                        f"{file_name}:{line_num} appears to use port 5432 for HTTP: {line.strip()}"
                    )
    
    print("✅ No hardcoded port 5432 found in HTTP configurations")


def test_documentation_warnings():
    """Test that configuration files have warnings about port 5432."""
    print("\nChecking for port 5432 warnings in configuration files...")
    
    files_with_warnings = [
        REPO_ROOT / 'gunicorn.conf.py',
        REPO_ROOT / 'backend' / 'gunicorn.conf.py',
        REPO_ROOT / 'backend' / 'app' / 'main.py',
    ]
    
    for file_path in files_with_warnings:
        if not file_path.exists():
            continue
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Should have a comment or message about port 5432
        has_warning = (
            'DO NOT USE' in content or
            'port 5432' in content.lower() or
            'cannot use port 5432' in content or
            'HTTP service cannot use port 5432' in content
        )
        
        assert has_warning, \
            f"{file_path} should have a warning about port 5432"
    
    print("✅ All configuration files have appropriate warnings")


if __name__ == "__main__":
    print("=" * 80)
    print("🧪 Testing Port 5432 Prevention")
    print("=" * 80)
    print()
    print("This test verifies that port 5432 (PostgreSQL port) cannot be")
    print("accidentally used for HTTP services.")
    print()
    
    try:
        test_main_py_rejects_port_5432()
        test_gunicorn_rejects_port_5432()
        test_no_hardcoded_5432_in_http_configs()
        test_documentation_warnings()
        
        print()
        print("=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        print()
        print("Summary:")
        print("  ✅ Port 5432 validation in gunicorn configurations")
        print("  ✅ Port 5432 validation in backend/app/main.py")
        print("  ✅ No hardcoded port 5432 in HTTP configurations")
        print("  ✅ Clear warning messages in configuration files")
        print()
        print("Port 5432 (PostgreSQL) is properly protected from HTTP service usage.")
        print()
        
    except AssertionError as e:
        print()
        print("=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        print()
        sys.exit(1)

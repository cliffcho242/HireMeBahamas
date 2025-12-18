"""
Test DATABASE_URL simple validation (after removing auto-fix logic).

This test validates that:
1. DATABASE_URL is required in production
2. Whitespace is stripped
3. No auto-fixes are applied (port parsing, typo fixes, driver conversions)
"""

import os
import sys
import subprocess


def test_production_requires_database_url():
    """Test that production mode requires DATABASE_URL to be set."""
    # Run in subprocess to avoid module caching issues
    # Remove DATABASE_URL from environment and set production mode
    env = {k: v for k, v in os.environ.items() if k != 'DATABASE_URL'}
    env['ENV'] = 'production'
    env['ENVIRONMENT'] = 'production'
    
    result = subprocess.run(
        ['python3', '-c', '''
import sys
sys.path.insert(0, ".")

try:
    from api import database
    print("FAIL: Should have raised RuntimeError")
    sys.exit(1)
except RuntimeError as e:
    if "DATABASE_URL is required in production" in str(e):
        print("PASS")
        sys.exit(0)
    else:
        print(f"FAIL: Wrong error: {e}")
        sys.exit(1)
'''],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        capture_output=True,
        text=True,
        env=env
    )
    
    assert result.returncode == 0, f"Test failed: {result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout


def test_development_allows_missing_database_url():
    """Test that development mode allows missing DATABASE_URL."""
    # Remove DATABASE_URL from environment and set development mode
    env = {k: v for k, v in os.environ.items() if k != 'DATABASE_URL'}
    env['ENV'] = 'development'
    env['ENVIRONMENT'] = 'development'
    
    result = subprocess.run(
        ['python3', '-c', '''
import sys
sys.path.insert(0, ".")

try:
    from api import database
    print("PASS")
    sys.exit(0)
except Exception as e:
    print(f"FAIL: Unexpected error: {e}")
    sys.exit(1)
'''],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        capture_output=True,
        text=True,
        env=env
    )
    
    assert result.returncode == 0, f"Test failed: {result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout


def test_whitespace_stripping():
    """Test that whitespace is stripped from DATABASE_URL."""
    env = {**os.environ, 'DATABASE_URL': '  postgresql://user:pass@host:5432/db  '}
    
    result = subprocess.run(
        ['python3', '-c', '''
import sys
sys.path.insert(0, ".")
from api import database
if database.DATABASE_URL == "postgresql://user:pass@host:5432/db":
    print("PASS")
    sys.exit(0)
else:
    print(f"FAIL: Expected stripped URL, got: {database.DATABASE_URL}")
    sys.exit(1)
'''],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        capture_output=True,
        text=True,
        env=env
    )
    
    assert result.returncode == 0, f"Test failed: {result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout


def test_no_typo_auto_fix():
    """Test that typos are NOT auto-fixed."""
    env = {**os.environ, 'DATABASE_URL': 'ostgresql://user:pass@host:5432/db'}
    
    result = subprocess.run(
        ['python3', '-c', '''
import sys
sys.path.insert(0, ".")
from api import database
if database.DATABASE_URL == "ostgresql://user:pass@host:5432/db":
    print("PASS")
    sys.exit(0)
else:
    print(f"FAIL: URL was modified to: {database.DATABASE_URL}")
    sys.exit(1)
'''],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        capture_output=True,
        text=True,
        env=env
    )
    
    assert result.returncode == 0, f"Test failed: {result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout


def test_no_port_auto_add():
    """Test that ports are NOT auto-added."""
    env = {**os.environ, 'DATABASE_URL': 'postgresql://user:pass@host/db'}
    
    result = subprocess.run(
        ['python3', '-c', '''
import sys
sys.path.insert(0, ".")
from api import database
if database.DATABASE_URL == "postgresql://user:pass@host/db":
    print("PASS")
    sys.exit(0)
else:
    print(f"FAIL: URL was modified to: {database.DATABASE_URL}")
    sys.exit(1)
'''],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        capture_output=True,
        text=True,
        env=env
    )
    
    assert result.returncode == 0, f"Test failed: {result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout


def test_no_driver_conversion():
    """Test that postgres:// is NOT converted to postgresql+asyncpg://."""
    env = {**os.environ, 'DATABASE_URL': 'postgres://user:pass@host:5432/db'}
    
    result = subprocess.run(
        ['python3', '-c', '''
import sys
sys.path.insert(0, ".")
from api import database
if database.DATABASE_URL == "postgres://user:pass@host:5432/db":
    print("PASS")
    sys.exit(0)
else:
    print(f"FAIL: URL was modified to: {database.DATABASE_URL}")
    sys.exit(1)
'''],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        capture_output=True,
        text=True,
        env=env
    )
    
    assert result.returncode == 0, f"Test failed: {result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout


if __name__ == "__main__":
    # Run tests individually
    print("Running test_production_requires_database_url...")
    test_production_requires_database_url()
    print("✅ PASS\n")
    
    print("Running test_development_allows_missing_database_url...")
    test_development_allows_missing_database_url()
    print("✅ PASS\n")
    
    print("Running test_whitespace_stripping...")
    test_whitespace_stripping()
    print("✅ PASS\n")
    
    print("Running test_no_typo_auto_fix...")
    test_no_typo_auto_fix()
    print("✅ PASS\n")
    
    print("Running test_no_port_auto_add...")
    test_no_port_auto_add()
    print("✅ PASS\n")
    
    print("Running test_no_driver_conversion...")
    test_no_driver_conversion()
    print("✅ PASS\n")
    
    print("✅ All tests passed!")

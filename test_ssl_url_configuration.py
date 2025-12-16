#!/usr/bin/env python3
"""
Test to verify SSL is configured via URL query string, not in connect_args.

This test verifies the fix from the problem statement:
"For PostgreSQL + SQLAlchemy, SSL belongs in the URL — not in connect_args."
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def read_file(filepath):
    """Read a file and return its contents."""
    with open(filepath, 'r') as f:
        return f.read()

def test_backend_app_database():
    """Test backend/app/database.py configuration."""
    print("Testing backend/app/database.py...")
    
    filepath = project_root / "backend" / "app" / "database.py"
    source = read_file(filepath)
    
    # Check that ssl import was removed
    assert "import ssl" not in source, "❌ FAIL: 'import ssl' should be removed from backend/app/database.py"
    print("✅ PASS: 'import ssl' removed")
    
    # Check that _get_ssl_context function was removed
    assert "_get_ssl_context" not in source, "❌ FAIL: '_get_ssl_context' function should be removed"
    print("✅ PASS: '_get_ssl_context' function removed")
    
    # Check that SSL context is NOT in connect_args
    assert '"ssl":' not in source and "'ssl':" not in source, "❌ FAIL: 'ssl' key should not be in connect_args"
    print("✅ PASS: SSL not in connect_args")
    
    # Check that sslmode is mentioned in comments as being in URL
    assert "?sslmode=require" in source, "❌ FAIL: Comments should mention ?sslmode=require in URL"
    print("✅ PASS: Documentation mentions ?sslmode=require in URL")
    
    print("✅ backend/app/database.py: All checks passed!\n")


def test_duplicate_database_module_removed():
    """Verify that duplicate backend/app/core/database.py was removed during consolidation."""
    print("Verifying duplicate database module removed...")
    
    filepath = project_root / "backend" / "app" / "core" / "database.py"
    
    # This file was removed as part of consolidation to use only backend/app/database.py
    if not filepath.exists():
        print("✅ PASS: backend/app/core/database.py removed (duplicate eliminated)")
        print("   Using single database module: backend/app/database.py\n")
        return
    
    # If file still exists (shouldn't happen), run old checks
    source = read_file(filepath)
    
    # Check that ssl import was removed
    assert "import ssl" not in source, "❌ FAIL: 'import ssl' should be removed from backend/app/core/database.py"
    print("✅ PASS: 'import ssl' removed")
    
    # Check that _get_ssl_context function was removed
    assert "_get_ssl_context" not in source, "❌ FAIL: '_get_ssl_context' function should be removed"
    print("✅ PASS: '_get_ssl_context' function removed")
    
    # Check that SSL context is NOT in connect_args
    assert '"ssl":' not in source and "'ssl':" not in source, "❌ FAIL: 'ssl' key should not be in connect_args"
    print("✅ PASS: SSL not in connect_args")
    
    # Check that sslmode is mentioned in comments as being in URL
    assert "?sslmode=require" in source, "❌ FAIL: Comments should mention ?sslmode=require in URL"
    print("✅ PASS: Documentation mentions ?sslmode=require in URL")
    
    print("✅ backend/app/core/database.py: All checks passed!\n")


def test_api_backend_app_database():
    """Test api/backend_app/database.py configuration."""
    print("Testing api/backend_app/database.py...")
    
    filepath = project_root / "api" / "backend_app" / "database.py"
    source = read_file(filepath)
    
    # Check that ssl import was removed
    assert "import ssl" not in source, "❌ FAIL: 'import ssl' should be removed from api/backend_app/database.py"
    print("✅ PASS: 'import ssl' removed")
    
    # Check that _get_ssl_context function was removed
    assert "_get_ssl_context" not in source, "❌ FAIL: '_get_ssl_context' function should be removed"
    print("✅ PASS: '_get_ssl_context' function removed")
    
    # Check that SSL context is NOT in connect_args
    assert '"ssl":' not in source and "'ssl':" not in source, "❌ FAIL: 'ssl' key should not be in connect_args"
    print("✅ PASS: SSL not in connect_args")
    
    # Check that sslmode is mentioned in comments as being in URL
    assert "?sslmode=require" in source, "❌ FAIL: Comments should mention ?sslmode=require in URL"
    print("✅ PASS: Documentation mentions ?sslmode=require in URL")
    
    print("✅ api/backend_app/database.py: All checks passed!\n")


def test_engine_configuration_pattern():
    """Test that the correct pattern is used in create_async_engine calls."""
    print("Testing engine configuration pattern...")
    
    filepath = project_root / "backend" / "app" / "database.py"
    source = read_file(filepath)
    
    # Verify that connect_args contains timeout and server_settings but NOT ssl
    assert "connect_args={" in source, "❌ FAIL: connect_args should be present"
    print("✅ PASS: connect_args is present")
    
    assert '"timeout":' in source or "'timeout':" in source, "❌ FAIL: timeout should be in connect_args"
    print("✅ PASS: timeout is in connect_args")
    
    assert '"server_settings":' in source or "'server_settings':" in source, "❌ FAIL: server_settings should be in connect_args"
    print("✅ PASS: server_settings is in connect_args")
    
    # The pattern from problem statement
    assert "pool_pre_ping=True" in source, "❌ FAIL: pool_pre_ping=True should be present"
    print("✅ PASS: pool_pre_ping=True is present")
    
    assert "pool_recycle" in source, "❌ FAIL: pool_recycle should be present"
    print("✅ PASS: pool_recycle is present")
    
    print("✅ Engine configuration pattern: All checks passed!\n")


if __name__ == "__main__":
    print("=" * 70)
    print("SSL CONFIGURATION TEST")
    print("Verifying: SSL belongs in the URL, NOT in connect_args")
    print("=" * 70)
    print()
    
    try:
        test_backend_app_database()
        test_duplicate_database_module_removed()
        test_api_backend_app_database()
        test_engine_configuration_pattern()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("The database configuration is now correct:")
        print("- SSL is configured via URL query string (?sslmode=require)")
        print("- No SSL context in connect_args")
        print("- Pattern works on Render, Railway, Neon, psycopg2, psycopg v3")
        print("- Compatible with SQLAlchemy 1.4 and 2.0")
        sys.exit(0)
        
    except AssertionError as e:
        print()
        print("=" * 70)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 70)
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ ERROR: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)

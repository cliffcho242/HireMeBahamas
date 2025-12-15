#!/usr/bin/env python3
"""
Test to verify socket-proof SQLAlchemy configuration across all database files.

This test verifies that all database engines are configured with:
1. pool_pre_ping=True - Validate connections before use
2. pool_recycle=300 (or configurable) - Recycle connections periodically
3. sslmode="require" in connect_args - Force TCP + SSL

And that forbidden patterns are absent:
- No warm-up pings
- No background keepalive loops
- No connect-on-import
"""

import re
import os
from pathlib import Path


def test_socket_proof_config():
    """Test that all database files have socket-proof configuration."""
    
    # Database files to check
    db_files = [
        "api/database.py",
        "backend/app/database.py",
        "backend/app/core/database.py",
        "api/backend_app/database.py"
    ]
    
    print("=" * 80)
    print("SOCKET-PROOF CONFIGURATION TEST")
    print("=" * 80)
    
    all_passed = True
    
    for filepath in db_files:
        print(f"\n{filepath}:")
        print("-" * 80)
        
        if not os.path.exists(filepath):
            print(f"  ❌ File not found")
            all_passed = False
            continue
            
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Test 1: pool_pre_ping=True
        has_pre_ping = bool(re.search(r'pool_pre_ping\s*=\s*True', content))
        if has_pre_ping:
            print("  ✅ pool_pre_ping=True")
        else:
            print("  ❌ pool_pre_ping=True MISSING")
            all_passed = False
        
        # Test 2: pool_recycle
        has_recycle = bool(re.search(r'pool_recycle\s*=', content))
        if has_recycle:
            print("  ✅ pool_recycle configured")
        else:
            print("  ❌ pool_recycle MISSING")
            all_passed = False
        
        # Test 3: sslmode="require" in connect_args
        has_sslmode = bool(re.search(r'"sslmode"\s*:\s*"require"', content))
        if has_sslmode:
            print('  ✅ connect_args={"sslmode": "require"}')
        else:
            print('  ❌ connect_args={"sslmode": "require"} MISSING')
            all_passed = False
        
        # Test 4: Lazy initialization
        has_lazy = bool(re.search(r'def get_engine\(\)', content))
        if has_lazy:
            print("  ✅ Lazy initialization (get_engine)")
        else:
            print("  ⚠️  No get_engine() function")
        
        # Test 5: No startup connections
        has_startup = bool(re.search(
            r'@app\.on_event\(["\']startup["\']\)|on_startup.*test_connection',
            content
        ))
        if not has_startup:
            print("  ✅ No startup connections")
        else:
            print("  ❌ Found startup connection")
            all_passed = False
        
        # Test 6: No warm-up pings
        has_warmup = bool(re.search(r'warm.?up.*ping', content, re.IGNORECASE))
        if not has_warmup:
            print("  ✅ No warm-up pings")
        else:
            print("  ❌ Found warm-up ping")
            all_passed = False
        
        # Test 7: No background keepalive
        has_keepalive = bool(re.search(
            r'background.*keepalive|keepalive.*loop|threading.*ping',
            content,
            re.IGNORECASE
        ))
        if not has_keepalive:
            print("  ✅ No background keepalive")
        else:
            print("  ❌ Found background keepalive")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED - Socket-proof configuration verified")
        return True
    else:
        print("❌ SOME TESTS FAILED - Review configuration")
        return False


def test_requirements_summary():
    """Print summary of socket-proof requirements."""
    print("\n" + "=" * 80)
    print("SOCKET-PROOF REQUIREMENTS")
    print("=" * 80)
    print("""
Required Configuration:
  engine = create_async_engine(
      DATABASE_URL,
      pool_pre_ping=True,      # Validate connections before use
      pool_recycle=300,         # Recycle connections every 5 minutes  
      connect_args={
          "sslmode": "require"  # Force TCP + SSL
      }
  )

Forbidden Patterns:
  🚫 No warm-up pings
  🚫 No background keepalive loops
  🚫 No connect-on-import
""")
    print("=" * 80)


if __name__ == "__main__":
    test_requirements_summary()
    success = test_socket_proof_config()
    exit(0 if success else 1)

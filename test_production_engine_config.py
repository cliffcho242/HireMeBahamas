#!/usr/bin/env python3
"""
Test to verify production-grade SQLAlchemy engine configuration.

This test verifies that all database engines are configured with production-ready settings:
1. pool_size=5 (default) - Adequate for production load
2. max_overflow=10 (default) - Burst capacity for traffic spikes
3. pool_pre_ping=True - Validate connections before use (prevents hanging requests)
4. pool_recycle=300 - Recycle connections every 5 minutes (prevents dead connections)
5. connect_timeout=5 - Handle cold starts and DNS stalls
6. sslmode="require" - Force SSL encryption
"""

import re
import os
from pathlib import Path


def test_production_engine_config():
    """Test that all database files have production-grade configuration."""
    
    # Database files to check
    db_files = [
        "api/database.py",
        "api/backend_app/database.py",
        "backend/app/database.py",
        "backend/app/core/config.py"
    ]
    
    print("=" * 80)
    print("PRODUCTION ENGINE CONFIGURATION TEST")
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
        
        # Check if this is a config file (Pydantic settings)
        is_config_file = 'config.py' in filepath
        
        if is_config_file:
            # Test config file with Pydantic syntax: DB_POOL_SIZE: int = int(os.getenv(...))
            pool_size_match = re.search(r'DB_POOL_SIZE:\s*int\s*=\s*int\(os\.getenv\("DB_POOL_SIZE",\s*"(\d+)"\)\)', content)
            if pool_size_match and pool_size_match.group(1) == "5":
                print("  ✅ DB_POOL_SIZE=5 (default)")
            else:
                if pool_size_match:
                    print(f"  ❌ DB_POOL_SIZE default is {pool_size_match.group(1)}, expected 5")
                else:
                    print("  ❌ DB_POOL_SIZE default not found")
                all_passed = False
            
            max_overflow_match = re.search(r'DB_MAX_OVERFLOW:\s*int\s*=\s*int\(os\.getenv\("DB_MAX_OVERFLOW",\s*"(\d+)"\)\)', content)
            if max_overflow_match and max_overflow_match.group(1) == "10":
                print("  ✅ DB_MAX_OVERFLOW=10 (default)")
            else:
                if max_overflow_match:
                    print(f"  ❌ DB_MAX_OVERFLOW default is {max_overflow_match.group(1)}, expected 10")
                else:
                    print("  ❌ DB_MAX_OVERFLOW default not found")
                all_passed = False
            
            connect_timeout_match = re.search(r'DB_CONNECT_TIMEOUT:\s*int\s*=\s*int\(os\.getenv\("DB_CONNECT_TIMEOUT",\s*"(\d+)"\)\)', content)
            if connect_timeout_match and connect_timeout_match.group(1) == "5":
                print("  ✅ DB_CONNECT_TIMEOUT=5 (default)")
            else:
                if connect_timeout_match:
                    print(f"  ⚠️  DB_CONNECT_TIMEOUT default is {connect_timeout_match.group(1)}, expected 5")
                else:
                    print("  ❌ DB_CONNECT_TIMEOUT default not found")
                all_passed = False
            
            pool_recycle_match = re.search(r'DB_POOL_RECYCLE:\s*int\s*=\s*int\(os\.getenv\("DB_POOL_RECYCLE",\s*"(\d+)"\)\)', content)
            if pool_recycle_match and pool_recycle_match.group(1) == "300":
                print("  ✅ DB_POOL_RECYCLE=300 (default)")
            else:
                if pool_recycle_match:
                    print(f"  ⚠️  DB_POOL_RECYCLE default is {pool_recycle_match.group(1)}, expected 300")
                else:
                    print("  ❌ DB_POOL_RECYCLE default not found")
                all_passed = False
        else:
            # Test database engine files
            # Test 1: pool_size default = 5 (handles both lowercase and UPPERCASE variable names)
            pool_size_match = re.search(r'(?:pool_size|POOL_SIZE)\s*=\s*int\(os\.getenv\("DB_POOL_SIZE",\s*"(\d+)"\)\)', content)
            if pool_size_match and pool_size_match.group(1) == "5":
                print("  ✅ pool_size=5 (default)")
            else:
                if pool_size_match:
                    print(f"  ❌ pool_size default is {pool_size_match.group(1)}, expected 5")
                else:
                    print("  ❌ pool_size default not found")
                all_passed = False
            
            # Test 2: max_overflow default = 10 (handles both lowercase and UPPERCASE variable names)
            max_overflow_match = re.search(r'(?:max_overflow|MAX_OVERFLOW)\s*=\s*int\(os\.getenv\("DB_(?:POOL_)?MAX_OVERFLOW",\s*"(\d+)"\)\)', content)
            if max_overflow_match and max_overflow_match.group(1) == "10":
                print("  ✅ max_overflow=10 (default)")
            else:
                if max_overflow_match:
                    print(f"  ❌ max_overflow default is {max_overflow_match.group(1)}, expected 10")
                else:
                    print("  ❌ max_overflow default not found")
                all_passed = False
            
            # Test 3: pool_pre_ping=True
            has_pre_ping = bool(re.search(r'pool_pre_ping\s*=\s*True', content))
            if has_pre_ping:
                print("  ✅ pool_pre_ping=True")
            else:
                print("  ❌ pool_pre_ping=True MISSING")
                all_passed = False
            
            # Test 4: pool_recycle=300 (default, handles both lowercase and UPPERCASE variable names)
            pool_recycle_match = re.search(r'(?:pool_recycle|POOL_RECYCLE)\s*=\s*int\(os\.getenv\("DB_POOL_RECYCLE",\s*"(\d+)"\)\)', content)
            if pool_recycle_match and pool_recycle_match.group(1) == "300":
                print("  ✅ pool_recycle=300 (default)")
            else:
                if pool_recycle_match:
                    print(f"  ⚠️  pool_recycle default is {pool_recycle_match.group(1)}, expected 300")
                else:
                    print("  ❌ pool_recycle default not found")
                all_passed = False
            
            # Test 5: connect_timeout=5 (default, handles both lowercase and UPPERCASE variable names)
            connect_timeout_match = re.search(r'(?:connect_timeout|CONNECT_TIMEOUT)\s*=\s*int\(os\.getenv\("DB_CONNECT_TIMEOUT",\s*"(\d+)"\)\)', content)
            if connect_timeout_match and connect_timeout_match.group(1) == "5":
                print("  ✅ connect_timeout=5 (default)")
            else:
                if connect_timeout_match:
                    print(f"  ⚠️  connect_timeout default is {connect_timeout_match.group(1)}, expected 5")
                else:
                    print("  ❌ connect_timeout default not found")
                all_passed = False
            
            # Test 6: sslmode="require" in connect_args
            has_sslmode = bool(re.search(r'"sslmode"\s*:\s*"require"', content))
            if has_sslmode:
                print('  ✅ connect_args={"sslmode": "require"}')
            else:
                print('  ❌ connect_args={"sslmode": "require"} MISSING')
                all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED - Production engine configuration verified")
        print("\nThis prevents:")
        print("  • Hanging requests (pool_pre_ping + timeouts)")
        print("  • DNS stalls (connect_timeout=5)")
        print("  • Dead connections (pool_recycle=300)")
        return True
    else:
        print("❌ SOME TESTS FAILED - Review configuration")
        return False


def test_requirements_summary():
    """Print summary of production engine requirements."""
    print("\n" + "=" * 80)
    print("PRODUCTION ENGINE REQUIREMENTS")
    print("=" * 80)
    print("""
Required Configuration (as per problem statement):
  engine = create_engine(
      DATABASE_URL,
      pool_size=5,              # Adequate for production load
      max_overflow=10,          # Burst capacity for traffic spikes
      pool_pre_ping=True,       # Validate connections before use
      pool_recycle=300,         # Recycle connections every 5 minutes
      connect_args={
          "connect_timeout": 5, # Handle cold starts and DNS stalls
          "sslmode": "require", # Force SSL encryption
      }
  )

Benefits:
  ✓ Prevents hanging requests
  ✓ Prevents DNS stalls
  ✓ Prevents dead connections
  ✓ Production-ready pool sizing
  ✓ Burst capacity for traffic spikes
""")
    print("=" * 80)


if __name__ == "__main__":
    test_requirements_summary()
    success = test_production_engine_config()
    exit(0 if success else 1)

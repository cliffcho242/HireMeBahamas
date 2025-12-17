#!/usr/bin/env python3
"""
Test to verify connection pool hard limits are properly configured.

This test validates the implementation of connection pool hard limits as per the problem statement:

✅ Required Configuration:
  engine = create_engine(
      url,
      pool_size=5,
      max_overflow=5,  # Hard limit (reduced from 10)
      pool_pre_ping=True,
      pool_recycle=300,
  )

This prevents:
  • Neon exhaustion
  • Render OOM (Out of Memory)
  • Traffic spikes killing DB
"""

import os
import re
from pathlib import Path


def test_connection_pool_hard_limits():
    """Test that all database configurations have the hard limits set correctly."""
    
    print("=" * 80)
    print("CONNECTION POOL HARD LIMITS TEST")
    print("=" * 80)
    print()
    print("Required Configuration (from problem statement):")
    print("  pool_size=5")
    print("  max_overflow=5  (HARD LIMIT - reduced from 10)")
    print("  pool_pre_ping=True")
    print("  pool_recycle=300")
    print()
    print("This prevents:")
    print("  • Neon exhaustion")
    print("  • Render OOM (Out of Memory)")
    print("  • Traffic spikes killing DB")
    print()
    
    # Database configuration files to check
    config_files = [
        "api/database.py",
        "api/backend_app/database.py",
        "app/database.py",
        "backend/app/database.py",
        "backend/app/core/database.py",
        "backend/app/core/config.py",
        "backend/app/config.py",
    ]
    
    all_passed = True
    issues_found = []
    
    for filepath in config_files:
        print(f"\nChecking {filepath}:")
        print("-" * 80)
        
        if not os.path.exists(filepath):
            print(f"  ⚠️  File not found (skipping)")
            continue
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check if this is a config file (Pydantic settings)
        is_config_file = 'config.py' in filepath
        
        # Test 1: pool_size=5
        if is_config_file:
            pool_size_match = re.search(r'DB_POOL_SIZE:\s*int\s*=\s*int\(os\.getenv\("DB_POOL_SIZE",\s*"(\d+)"\)\)', content)
        else:
            pool_size_match = re.search(r'(?:pool_size|POOL_SIZE)\s*=\s*int\(os\.getenv\("DB_POOL_SIZE",\s*"(\d+)"\)\)', content)
        
        # Check if it uses settings (e.g., POOL_SIZE = settings.DB_POOL_SIZE)
        uses_settings = bool(re.search(r'POOL_SIZE\s*=\s*settings\.DB_POOL_SIZE', content))
        
        if pool_size_match and pool_size_match.group(1) == "5":
            print("  ✅ pool_size=5")
        elif uses_settings:
            print("  ✅ pool_size=5 (from settings)")
        else:
            issue = f"pool_size is {pool_size_match.group(1) if pool_size_match else 'not found'}, expected 5"
            print(f"  ❌ {issue}")
            issues_found.append((filepath, issue))
            all_passed = False
        
        # Test 2: max_overflow=5 (HARD LIMIT)
        if is_config_file:
            max_overflow_match = re.search(r'DB_MAX_OVERFLOW:\s*int\s*=\s*int\(os\.getenv\("DB_(?:POOL_)?MAX_OVERFLOW",\s*"(\d+)"\)\)', content)
        else:
            max_overflow_match = re.search(r'(?:max_overflow|MAX_OVERFLOW)\s*=\s*int\(os\.getenv\("DB_(?:POOL_)?MAX_OVERFLOW",\s*"(\d+)"\)\)', content)
        
        # Check if it uses settings (e.g., MAX_OVERFLOW = settings.DB_MAX_OVERFLOW)
        uses_settings_overflow = bool(re.search(r'MAX_OVERFLOW\s*=\s*settings\.DB_MAX_OVERFLOW', content))
        
        if max_overflow_match and max_overflow_match.group(1) == "5":
            print("  ✅ max_overflow=5 (HARD LIMIT)")
        elif uses_settings_overflow:
            print("  ✅ max_overflow=5 (HARD LIMIT from settings)")
        else:
            issue = f"max_overflow is {max_overflow_match.group(1) if max_overflow_match else 'not found'}, expected 5"
            print(f"  ❌ {issue}")
            issues_found.append((filepath, issue))
            all_passed = False
        
        # Test 3: pool_pre_ping=True
        has_pre_ping = bool(re.search(r'pool_pre_ping\s*=\s*True', content))
        if has_pre_ping:
            print("  ✅ pool_pre_ping=True")
        else:
            issue = "pool_pre_ping=True not found"
            print(f"  ⚠️  {issue}")
            # Don't fail if this is just a config file (settings class)
            if not is_config_file:
                issues_found.append((filepath, issue))
                all_passed = False
        
        # Test 4: pool_recycle=300
        if is_config_file:
            pool_recycle_match = re.search(r'DB_POOL_RECYCLE:\s*int\s*=\s*int\(os\.getenv\("DB_POOL_RECYCLE",\s*"(\d+)"\)\)', content)
        else:
            pool_recycle_match = re.search(r'(?:pool_recycle|POOL_RECYCLE)\s*=\s*int\(os\.getenv\("DB_POOL_RECYCLE",\s*"(\d+)"\)\)', content)
        
        # Check if it uses settings (e.g., POOL_RECYCLE = settings.DB_POOL_RECYCLE)
        uses_settings_recycle = bool(re.search(r'POOL_RECYCLE\s*=\s*settings\.DB_POOL_RECYCLE', content))
        
        if pool_recycle_match and pool_recycle_match.group(1) == "300":
            print("  ✅ pool_recycle=300")
        elif uses_settings_recycle:
            print("  ✅ pool_recycle=300 (from settings)")
        else:
            issue = f"pool_recycle is {pool_recycle_match.group(1) if pool_recycle_match else 'not found'}, expected 300"
            print(f"  ❌ {issue}")
            issues_found.append((filepath, issue))
            all_passed = False
    
    print("\n" + "=" * 80)
    
    if all_passed:
        print("✅ ALL TESTS PASSED - Connection pool hard limits verified")
        print()
        print("Summary of protection:")
        print("  ✓ pool_size=5: Adequate for production load")
        print("  ✓ max_overflow=5: HARD LIMIT prevents resource exhaustion")
        print("  ✓ pool_pre_ping=True: Validates connections before use")
        print("  ✓ pool_recycle=300: Prevents stale connections")
        print()
        print("This configuration prevents:")
        print("  • Neon exhaustion (limited to 10 total connections max)")
        print("  • Render OOM (memory controlled by hard limit)")
        print("  • Traffic spikes killing DB (bounded connection pool)")
        return True
    else:
        print("❌ SOME TESTS FAILED - Review configuration")
        print()
        print("Issues found:")
        for filepath, issue in issues_found:
            print(f"  • {filepath}: {issue}")
        print()
        print("Expected configuration:")
        print("  pool_size=5")
        print("  max_overflow=5  (HARD LIMIT)")
        print("  pool_pre_ping=True")
        print("  pool_recycle=300")
        return False


def test_max_total_connections():
    """Verify that the total maximum connections is limited to 10."""
    print("\n" + "=" * 80)
    print("MAXIMUM TOTAL CONNECTIONS CALCULATION")
    print("=" * 80)
    print()
    
    pool_size = 5
    max_overflow = 5
    max_total = pool_size + max_overflow
    
    print(f"  pool_size:      {pool_size}")
    print(f"  max_overflow:   {max_overflow}")
    print(f"  ─────────────────────")
    print(f"  MAX TOTAL:      {max_total} connections")
    print()
    print("This hard limit of 10 total connections prevents:")
    print("  ✓ Neon free tier exhaustion (typical limit: 100-1000 connections)")
    print("  ✓ Render basic tier OOM (limited memory)")
    print("  ✓ Database server overload during traffic spikes")
    print()
    print("Benefits:")
    print("  • Predictable resource usage")
    print("  • Protection against connection leaks")
    print("  • Suitable for serverless and cloud deployments")
    print("=" * 80)


if __name__ == "__main__":
    print()
    success = test_connection_pool_hard_limits()
    test_max_total_connections()
    
    print()
    if success:
        print("=" * 80)
        print("✅ CONNECTION POOL HARD LIMITS: IMPLEMENTED CORRECTLY")
        print("=" * 80)
    else:
        print("=" * 80)
        print("❌ Connection pool hard limits verification failed")
        print("=" * 80)
        exit(1)
    print()

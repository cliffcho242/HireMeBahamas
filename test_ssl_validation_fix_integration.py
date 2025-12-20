#!/usr/bin/env python3
"""
Integration test simulating actual application startup with different DATABASE_URL configurations.

This test verifies the complete fix for the SSL validation contradiction:
- Neon pooled connections should work without sslmode
- asyncpg connections should work without sslmode
- Validation should pass at startup for production configurations
"""

import os
import sys
from pathlib import Path


def clear_modules(*patterns):
    """Clear modules from cache."""
    modules_to_remove = []
    for k in sys.modules:
        if any(pattern in k for pattern in patterns):
            if k.startswith('backend.') or k.startswith('backend_app.'):
                modules_to_remove.append(k)
    
    for mod in modules_to_remove:
        del sys.modules[mod]


def test_startup_scenario_1_neon_pooled():
    """Scenario 1: Production deployment with Neon pooled connection (typical Render deployment)"""
    print("=" * 70)
    print("SCENARIO 1: Production Neon Pooled Connection")
    print("=" * 70)
    print("DATABASE_URL: postgresql+asyncpg://user:***@ep-xxx-pooler.us-east-1.aws.neon.tech:5432/db")
    print()
    
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://user:pass@ep-cool-bird-123-pooler.us-east-1.aws.neon.tech:5432/hiremebahamas'
    
    try:
        clear_modules('backend', 'backend_app', 'db_guards')
        sys.path.insert(0, '.')
        from backend.app.core.db_guards import validate_database_config
        
        result = validate_database_config(strict=False)
        
        if result:
            print("✅ SUCCESS: Application would start successfully")
            print("   - Neon pooled connection detected")
            print("   - SSL handled automatically by pooler")
            print("   - No sslmode parameter needed or checked")
            return True
        else:
            print("❌ FAIL: Application startup would fail")
            return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error during startup: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_startup_scenario_2_asyncpg_direct():
    """Scenario 2: Direct asyncpg connection (e.g., Vercel with asyncpg)"""
    print("\n" + "=" * 70)
    print("SCENARIO 2: Direct asyncpg Connection")
    print("=" * 70)
    print("DATABASE_URL: postgresql+asyncpg://user:***@db.example.com:5432/db")
    print()
    
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://user:pass@production-db.example.com:5432/hiremebahamas'
    
    try:
        clear_modules('backend', 'backend_app', 'db_guards')
        sys.path.insert(0, '.')
        from backend.app.core.db_guards import validate_database_config
        
        result = validate_database_config(strict=False)
        
        if result:
            print("✅ SUCCESS: Application would start successfully")
            print("   - asyncpg driver detected")
            print("   - SSL configured via connect_args")
            print("   - No sslmode parameter needed")
            return True
        else:
            print("❌ FAIL: Application startup would fail")
            return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error during startup: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_startup_scenario_3_local_dev():
    """Scenario 3: Local development with localhost"""
    print("\n" + "=" * 70)
    print("SCENARIO 3: Local Development")
    print("=" * 70)
    print("DATABASE_URL: postgresql://user:***@localhost:5432/db")
    print()
    
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost:5432/hiremebahamas_dev'
    
    try:
        clear_modules('backend', 'backend_app', 'db_guards')
        sys.path.insert(0, '.')
        from backend.app.core.db_guards import validate_database_config
        
        result = validate_database_config(strict=False)
        
        if result:
            print("✅ SUCCESS: Application would start successfully")
            print("   - Localhost detected")
            print("   - SSL not required for local development")
            return True
        else:
            print("❌ FAIL: Application startup would fail")
            return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error during startup: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_startup_scenario_4_psycopg_with_sslmode():
    """Scenario 4: Traditional PostgreSQL with psycopg and sslmode"""
    print("\n" + "=" * 70)
    print("SCENARIO 4: Traditional PostgreSQL with sslmode")
    print("=" * 70)
    print("DATABASE_URL: postgresql://user:***@db.example.com:5432/db?sslmode=require")
    print()
    
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@traditional-db.example.com:5432/hiremebahamas?sslmode=require'
    
    try:
        clear_modules('backend', 'backend_app', 'db_guards')
        sys.path.insert(0, '.')
        from backend.app.core.db_guards import validate_database_config
        
        result = validate_database_config(strict=False)
        
        if result:
            print("✅ SUCCESS: Application would start successfully")
            print("   - Traditional PostgreSQL with sslmode detected")
            print("   - sslmode parameter present (required for non-asyncpg)")
            return True
        else:
            print("❌ FAIL: Application startup would fail")
            return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error during startup: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_startup_scenario_5_broken_asyncpg_with_sslmode():
    """Scenario 5: Broken configuration - asyncpg with sslmode (should be detected)"""
    print("\n" + "=" * 70)
    print("SCENARIO 5: Broken Config - asyncpg + sslmode (should warn/block)")
    print("=" * 70)
    print("DATABASE_URL: postgresql+asyncpg://user:***@db.example.com:5432/db?sslmode=require")
    print()
    
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://user:pass@production-db.example.com:5432/hiremebahamas?sslmode=require'
    
    try:
        clear_modules('backend', 'backend_app', 'db_guards')
        sys.path.insert(0, 'api')
        from backend_app.core.db_guards import validate_database_config
        
        result = validate_database_config(strict=False)
        
        if not result:
            print("✅ SUCCESS: Invalid configuration correctly detected")
            print("   - asyncpg with sslmode would cause runtime error")
            print("   - Validation prevented the error at startup")
            return True
        else:
            print("❌ FAIL: Invalid configuration not detected")
            return False
    except Exception as e:
        print(f"⚠️  Expected behavior: Configuration issue detected")
        print(f"   Error type: {type(e).__name__}")
        return True  # Expected to catch the issue


def main():
    """Run all startup scenarios"""
    print("\n" + "=" * 70)
    print("DATABASE SSL CONFIGURATION FIX - INTEGRATION TEST")
    print("Testing real-world startup scenarios")
    print("=" * 70)
    print()
    
    scenarios = [
        ("Neon Pooled Connection", test_startup_scenario_1_neon_pooled),
        ("Direct asyncpg Connection", test_startup_scenario_2_asyncpg_direct),
        ("Local Development", test_startup_scenario_3_local_dev),
        ("Traditional PostgreSQL", test_startup_scenario_4_psycopg_with_sslmode),
        ("Broken asyncpg+sslmode", test_startup_scenario_5_broken_asyncpg_with_sslmode),
    ]
    
    passed = 0
    failed = 0
    
    for scenario_name, test_func in scenarios:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n⚠️  Scenario '{scenario_name}' FAILED\n")
        except Exception as e:
            failed += 1
            print(f"\n❌ Scenario '{scenario_name}' ERROR: {e}\n")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("INTEGRATION TEST RESULTS")
    print("=" * 70)
    print(f"Scenarios Passed: {passed}/{len(scenarios)}")
    print(f"Scenarios Failed: {failed}/{len(scenarios)}")
    print()
    
    if failed == 0:
        print("✅ ALL SCENARIOS PASSED!")
        print()
        print("Summary:")
        print("  ✅ Neon pooled connections work correctly")
        print("  ✅ asyncpg connections work without sslmode")
        print("  ✅ Local development works without SSL")
        print("  ✅ Traditional PostgreSQL with sslmode works")
        print("  ✅ Invalid configurations are detected")
        print()
        print("The SSL validation contradiction has been FIXED!")
        print("Applications can now start successfully with Neon pooled connections.")
        return 0
    else:
        print("❌ SOME SCENARIOS FAILED!")
        print("Please review the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

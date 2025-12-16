#!/usr/bin/env python3
"""
Test suite for deployment status checker

This test validates the deployment status checker's ability to:
1. Detect DATABASE_URL pattern errors
2. Validate environment variables
3. Check configuration files
4. Output JSON correctly
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Get the script path
SCRIPT_PATH = Path(__file__).parent / "check_deployment_status.py"


def run_checker(env_vars=None, args=None):
    """Run the deployment status checker with given environment and arguments"""
    cmd = [sys.executable, str(SCRIPT_PATH)]
    if args:
        cmd.extend(args)
    
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env
    )
    
    return result


def test_database_url_pattern_error():
    """Test detection of DATABASE_URL missing database name"""
    print("\n🧪 Test 1: DATABASE_URL pattern error detection")
    
    # Test with missing database name
    result = run_checker(
        env_vars={"DATABASE_URL": "postgresql://user:pass@host:5432/"},
        args=["--json"]
    )
    
    try:
        data = json.loads(result.stdout)
        
        # Check that status is offline
        assert data["status"] == "offline", "Status should be offline"
        
        # Check for DATABASE_URL critical issue
        db_checks = [c for c in data["checks"] if c["name"] == "DATABASE_URL" and c["category"] == "database"]
        assert len(db_checks) > 0, "Should have DATABASE_URL check"
        assert db_checks[0]["status"] == "critical", "DATABASE_URL should be critical"
        assert "database name" in db_checks[0]["message"].lower(), "Should mention database name missing"
        
        print("   ✅ Correctly detected missing database name")
        print(f"   ✅ Status: {db_checks[0]['status']}")
        print(f"   ✅ Message: {db_checks[0]['message']}")
        return True
    except Exception as e:
        print(f"   ❌ Test failed: {str(e)}")
        return False


def test_valid_database_url():
    """Test validation of correct DATABASE_URL"""
    print("\n🧪 Test 2: Valid DATABASE_URL detection")
    
    result = run_checker(
        env_vars={"DATABASE_URL": "postgresql://user:pass@host:5432/mydb?sslmode=require"},
        args=["--json"]
    )
    
    try:
        data = json.loads(result.stdout)
        
        # Check for DATABASE_URL ok status
        db_checks = [c for c in data["checks"] if c["name"] == "DATABASE_URL" and c["category"] == "database"]
        assert len(db_checks) > 0, "Should have DATABASE_URL check"
        assert db_checks[0]["status"] == "ok", "DATABASE_URL should be ok"
        
        print("   ✅ Correctly validated DATABASE_URL")
        print(f"   ✅ Status: {db_checks[0]['status']}")
        return True
    except Exception as e:
        print(f"   ❌ Test failed: {str(e)}")
        return False


def test_missing_sslmode():
    """Test that missing SSL mode is handled automatically (no longer causes warning)"""
    print("\n🧪 Test 3: Missing SSL mode is handled automatically")
    
    result = run_checker(
        env_vars={"DATABASE_URL": "postgresql://user:pass@host:5432/mydb"},
        args=["--json"]
    )
    
    try:
        data = json.loads(result.stdout)
        
        # Check for DATABASE_URL check
        db_checks = [c for c in data["checks"] if c["name"] == "DATABASE_URL" and c["category"] == "database"]
        assert len(db_checks) > 0, "Should have DATABASE_URL check"
        # After removing redundant validation, missing sslmode should not cause warnings
        # The ensure_sslmode() function adds it automatically
        assert db_checks[0]["status"] in ["ok", "info"], "Missing sslmode should be OK (added automatically)"
        
        print("   ✅ Missing SSL mode is handled automatically (no warning needed)")
        print(f"   ✅ Status: {db_checks[0]['status']}")
        return True
    except Exception as e:
        print(f"   ❌ Test failed: {str(e)}")
        return False


def test_json_output_structure():
    """Test JSON output structure"""
    print("\n🧪 Test 4: JSON output structure")
    
    result = run_checker(args=["--json"])
    
    try:
        data = json.loads(result.stdout)
        
        # Check required keys
        assert "status" in data, "Should have status key"
        assert "deployment_info" in data, "Should have deployment_info key"
        assert "checks" in data, "Should have checks key"
        assert "summary" in data, "Should have summary key"
        
        # Check summary structure
        summary = data["summary"]
        assert "total_checks" in summary, "Summary should have total_checks"
        assert "critical" in summary, "Summary should have critical count"
        assert "errors" in summary, "Summary should have errors count"
        assert "warnings" in summary, "Summary should have warnings count"
        assert "ok" in summary, "Summary should have ok count"
        
        print("   ✅ JSON structure is valid")
        print(f"   ✅ Total checks: {summary['total_checks']}")
        print(f"   ✅ Critical: {summary['critical']}, Errors: {summary['errors']}, Warnings: {summary['warnings']}, OK: {summary['ok']}")
        return True
    except Exception as e:
        print(f"   ❌ Test failed: {str(e)}")
        return False


def test_configuration_validation():
    """Test configuration file validation"""
    print("\n🧪 Test 5: Configuration file validation")
    
    result = run_checker(args=["--json"])
    
    try:
        data = json.loads(result.stdout)
        
        # Check for config checks
        config_checks = [c for c in data["checks"] if c["category"] == "config"]
        assert len(config_checks) > 0, "Should have configuration checks"
        
        # Should find vercel.json in the repository
        vercel_check = [c for c in config_checks if "vercel.json" in c["name"]]
        assert len(vercel_check) > 0, "Should check vercel.json"
        
        print("   ✅ Configuration validation working")
        print(f"   ✅ Found {len(config_checks)} configuration checks")
        return True
    except Exception as e:
        print(f"   ❌ Test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("🧪 Deployment Status Checker Test Suite")
    print("="*60)
    
    if not SCRIPT_PATH.exists():
        print(f"\n❌ Script not found at: {SCRIPT_PATH}")
        return 1
    
    tests = [
        test_database_url_pattern_error,
        test_valid_database_url,
        test_missing_sslmode,
        test_json_output_structure,
        test_configuration_validation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ Test crashed: {str(e)}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 Test Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*60)
    
    if failed == 0:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

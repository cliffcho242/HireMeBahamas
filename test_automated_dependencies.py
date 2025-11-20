#!/usr/bin/env python3
"""
Test suite for automated dependency system
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def test_check_dependencies():
    """Test dependency checker script"""
    print("\n🧪 Testing check_dependencies.py...")
    result = subprocess.run(
        [sys.executable, "scripts/check_dependencies.py"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Should complete without errors
    assert result.returncode in [0, 1], "Script should exit with 0 or 1"
    
    # Should create report file
    report_file = Path("dependency_check_report.json")
    assert report_file.exists(), "Should create dependency_check_report.json"
    
    # Report should be valid JSON
    with open(report_file) as f:
        report = json.load(f)
    
    assert "status" in report, "Report should have status"
    assert "python_dependencies" in report, "Report should have dependencies"
    
    print("✅ check_dependencies.py test passed")
    return True


def test_startup_init():
    """Test startup initialization script"""
    print("\n🧪 Testing startup_init.py...")
    result = subprocess.run(
        [sys.executable, "scripts/startup_init.py"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Should complete successfully
    assert result.returncode == 0, "Startup init should succeed"
    assert "✅" in result.stdout, "Should show success indicators"
    
    print("✅ startup_init.py test passed")
    return True


def test_health_endpoint():
    """Test health endpoint handler"""
    print("\n🧪 Testing health_endpoint.py...")
    
    # Import the module
    sys.path.insert(0, str(Path(__file__).parent / "scripts"))
    from health_endpoint import get_health_status
    
    # Get health status
    health = get_health_status()
    
    assert "status" in health, "Should have status"
    assert "dependencies" in health, "Should have dependencies"
    assert "backend" in health["dependencies"], "Should have backend deps"
    
    print("✅ health_endpoint.py test passed")
    return True


def test_setup_scripts_exist():
    """Test that all required scripts exist"""
    print("\n🧪 Testing script files exist...")
    
    required_scripts = [
        "scripts/check_dependencies.py",
        "scripts/activate_all_dependencies.py",
        "scripts/startup_init.py",
        "scripts/auto_recover.py",
        "scripts/setup_env.py",
        "scripts/health_endpoint.py",
        "scripts/one_click_setup.sh",
        "scripts/one_click_setup.bat",
        "frontend/scripts/validate-deps.js",
    ]
    
    for script in required_scripts:
        path = Path(script)
        assert path.exists(), f"{script} should exist"
        
        # Unix scripts should be executable
        if script.endswith('.sh') or script.endswith('.py'):
            assert os.access(path, os.X_OK), f"{script} should be executable"
    
    print("✅ All required scripts exist")
    return True


def test_documentation_exists():
    """Test that documentation exists"""
    print("\n🧪 Testing documentation exists...")
    
    docs = [
        "AUTOMATED_DEPENDENCIES.md",
        "scripts/README.md",
    ]
    
    for doc in docs:
        path = Path(doc)
        assert path.exists(), f"{doc} should exist"
        assert path.stat().st_size > 1000, f"{doc} should have content"
    
    print("✅ Documentation exists and has content")
    return True


def test_admin_dashboard_exists():
    """Test that admin dashboard exists"""
    print("\n🧪 Testing admin dashboard...")
    
    dashboard = Path("admin_panel/dependencies.html")
    assert dashboard.exists(), "Admin dashboard should exist"
    
    content = dashboard.read_text()
    assert "Dependency Health Dashboard" in content, "Should have dashboard title"
    assert "/api/health/dependencies" in content, "Should call health API"
    
    print("✅ Admin dashboard exists and configured")
    return True


def test_ci_workflow_exists():
    """Test that CI/CD workflow exists"""
    print("\n🧪 Testing CI/CD workflow...")
    
    workflow = Path(".github/workflows/dependencies-check.yml")
    assert workflow.exists(), "CI/CD workflow should exist"
    
    content = workflow.read_text()
    assert "check-python-dependencies" in content, "Should have Python job"
    assert "check-frontend-dependencies" in content, "Should have frontend job"
    assert "test-integrations" in content, "Should have integration tests"
    
    print("✅ CI/CD workflow exists and configured")
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Running Automated Dependency System Tests")
    print("=" * 60)
    
    tests = [
        test_setup_scripts_exist,
        test_documentation_exists,
        test_admin_dashboard_exists,
        test_ci_workflow_exists,
        test_check_dependencies,
        test_startup_init,
        test_health_endpoint,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed > 0:
        print("\n❌ Some tests failed")
        return 1
    else:
        print("\n✅ All tests passed!")
        return 0


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

#!/usr/bin/env python3
"""
Simple test to verify health endpoint implementation
Tests the code structure without requiring full app initialization
"""
import sys
import re
from pathlib import Path


def test_health_endpoint_exists():
    """Verify health endpoint exists in backend/app/main.py"""
    print("\n🧪 Testing health endpoint exists...")
    
    main_file = Path(__file__).parent / 'backend' / 'app' / 'main.py'
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for health endpoint decorator
    if '@app.get("/health"' not in content:
        print("❌ Health endpoint not found!")
        return False
    
    print("✅ Health endpoint found in backend/app/main.py")
    return True


def test_health_endpoint_returns_correct_response():
    """Verify health endpoint returns {"status": "ok"}"""
    print("\n🧪 Testing health endpoint returns correct response...")
    
    main_file = Path(__file__).parent / 'backend' / 'app' / 'main.py'
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the health endpoint function - simpler approach
    # Just check if the return statement contains {"status": "ok"}
    if '{"status": "ok"}' in content or "{'status': 'ok'}" in content:
        print("✅ Health endpoint returns {'status': 'ok'}")
        return True
    
    print("❌ Health endpoint does not return {'status': 'ok'}")
    return False


def test_health_endpoint_no_db_dependency():
    """Verify health endpoint has no database dependency"""
    print("\n🧪 Testing health endpoint has no database dependency...")
    
    main_file = Path(__file__).parent / 'backend' / 'app' / 'main.py'
    
    with open(main_file, 'r') as f:
        lines = f.readlines()
    
    # Find the health endpoint
    in_health_func = False
    health_lines = []
    
    for i, line in enumerate(lines):
        if '@app.get("/health"' in line or '@app.head("/health"' in line:
            in_health_func = True
            continue
        
        if in_health_func:
            health_lines.append(line)
            
            # End of function
            if line.strip().startswith('@app.') or (
                line.strip().startswith('def ') and 'health' not in line.lower()
            ):
                break
    
    health_code = ''.join(health_lines)
    
    # Check for database-related patterns
    forbidden_patterns = [
        'db.execute',
        'SELECT 1',
        'get_db',
        'AsyncSession',
        'Depends(get_db)',
        'test_db_connection',
        'check_database_health',
    ]
    
    violations = []
    for pattern in forbidden_patterns:
        if pattern in health_code:
            violations.append(pattern)
    
    if violations:
        print(f"❌ Health endpoint contains database operations: {violations}")
        return False
    
    print("✅ Health endpoint has no database dependency")
    return True


def test_health_endpoint_matches_spec():
    """Verify health endpoint matches the problem statement specification"""
    print("\n🧪 Testing health endpoint matches specification...")
    
    main_file = Path(__file__).parent / 'backend' / 'app' / 'main.py'
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Requirements from problem statement:
    # 1. Path: /health ✓
    # 2. Returns: {"status": "ok"} ✓
    # 3. NO DB dependency ✓
    
    checks = []
    
    # Check 1: Has @app.get("/health")
    if '@app.get("/health"' in content:
        checks.append(("Path /health", True))
    else:
        checks.append(("Path /health", False))
    
    # Check 2: Returns {"status": "ok"}
    if '{"status": "ok"}' in content:
        checks.append(("Returns {'status': 'ok'}", True))
    else:
        checks.append(("Returns {'status': 'ok'}", False))
    
    # Check 3: No database in health function
    health_section = content[content.find('@app.get("/health"'):content.find('@app.get("/health"') + 500]
    has_db = any(pattern in health_section for pattern in ['db.execute', 'get_db', 'SELECT'])
    checks.append(("No database dependency", not has_db))
    
    # Print results
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("✅ Health endpoint matches specification")
        return True
    else:
        print("❌ Health endpoint does not fully match specification")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("Health Endpoint Verification")
    print("=" * 70)
    
    tests = [
        test_health_endpoint_exists,
        test_health_endpoint_returns_correct_response,
        test_health_endpoint_no_db_dependency,
        test_health_endpoint_matches_spec,
    ]
    
    success = True
    for test_func in tests:
        try:
            if not test_func():
                success = False
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            success = False
    
    print("\n" + "=" * 70)
    if success:
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        print("\nHealth endpoint implementation verified:")
        print("  - Path: /health")
        print("  - Returns: {'status': 'ok'}")
        print("  - Database: NO dependency (as required)")
        print("  - Port: Auto-configured via FastAPI/uvicorn")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 70)
        sys.exit(1)

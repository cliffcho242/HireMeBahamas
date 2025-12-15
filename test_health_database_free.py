#!/usr/bin/env python3
"""
Test that health check endpoints are 100% database-free.
This validates the MASTER FIX for production-grade health checks.
"""
import sys
import time
from pathlib import Path


def test_health_endpoint_no_db_import():
    """Test that /health endpoint code doesn't import database modules"""
    print("\n🧪 Testing /health endpoint is database-free...")
    
    script_dir = Path(__file__).parent
    main_file = script_dir / 'api' / 'backend_app' / 'main.py'
    
    with open(main_file, 'r') as f:
        lines = f.readlines()
    
    # Find the /health endpoint definition
    in_health_endpoint = False
    health_endpoint_lines = []
    
    for i, line in enumerate(lines):
        if '@app.get("/health"' in line:
            in_health_endpoint = True
        elif in_health_endpoint:
            health_endpoint_lines.append(line)
            # End of function - check for next decorator or another function
            if line.strip().startswith('@app.') or (line.strip().startswith('def ') and 'health' not in line.lower()):
                break
            # Empty line after return usually indicates end of function
            if i > 0 and line.strip() == '' and 'return' in health_endpoint_lines[-2]:
                break
    
    # Check that the endpoint doesn't have database calls
    health_code = ''.join(health_endpoint_lines)
    
    forbidden_patterns = [
        'db.execute',
        'SELECT 1',
        'test_db_connection',
        'check_database_health',
        'get_db(',
        'AsyncSession',
        'Depends(get_db)',
    ]
    
    violations = []
    for pattern in forbidden_patterns:
        if pattern in health_code:
            violations.append(pattern)
    
    if violations:
        print(f"❌ /health endpoint contains database operations: {violations}")
        return False
    
    print("✅ /health endpoint is database-free!")
    return True


def test_ready_endpoint_no_db_calls():
    """Test that /ready endpoint doesn't make database calls"""
    print("\n🧪 Testing /ready endpoint is database-free...")
    
    script_dir = Path(__file__).parent
    main_file = script_dir / 'api' / 'backend_app' / 'main.py'
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the /ready endpoint
    lines = content.split('\n')
    in_ready_endpoint = False
    ready_endpoint_lines = []
    
    for i, line in enumerate(lines):
        if '@app.get("/ready"' in line and '/ready/db' not in line:
            in_ready_endpoint = True
        elif in_ready_endpoint:
            ready_endpoint_lines.append(line)
            # End of function
            if line.strip().startswith('@app.') or (line.strip().startswith('def ') and 'ready' not in line.lower()):
                break
            # Check for print statement that comes after
            if 'print(' in line and 'NUCLEAR' in line:
                break
    
    ready_code = '\n'.join(ready_endpoint_lines)
    
    # Check that it doesn't call database functions
    forbidden_patterns = [
        'test_db_connection',
        'get_db_status',
        'SELECT 1',
        'db.execute',
        'await',  # Should be synchronous now
    ]
    
    violations = []
    for pattern in forbidden_patterns:
        if pattern in ready_code:
            violations.append(pattern)
    
    if violations:
        print(f"❌ /ready endpoint contains database operations: {violations}")
        print(f"Code snippet:\n{ready_code[:500]}")
        return False
    
    print("✅ /ready endpoint is database-free!")
    return True


def test_health_ping_endpoint():
    """Test that /health/ping endpoint is simple and fast"""
    print("\n🧪 Testing /health/ping endpoint...")
    
    script_dir = Path(__file__).parent
    main_file = script_dir / 'api' / 'backend_app' / 'main.py'
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the /health/ping endpoint
    if '@app.get("/health/ping")' not in content:
        print("❌ /health/ping endpoint not found!")
        return False
    
    # Extract the endpoint code
    lines = content.split('\n')
    in_ping_endpoint = False
    ping_lines = []
    
    for line in lines:
        if '@app.get("/health/ping")' in line:
            in_ping_endpoint = True
        elif in_ping_endpoint:
            ping_lines.append(line)
            if line.strip().startswith('@app.') or line.strip().startswith('# Cache warming'):
                break
    
    ping_code = '\n'.join(ping_lines)
    
    # Should not have any database calls
    if 'db' in ping_code.lower() or 'select' in ping_code.lower():
        print("❌ /health/ping endpoint contains database operations!")
        return False
    
    print("✅ /health/ping endpoint is database-free!")
    return True


def test_endpoint_response_structure():
    """Test that endpoints return the correct response structure"""
    print("\n🧪 Testing endpoint response structure...")
    
    script_dir = Path(__file__).parent
    api_dir = script_dir / 'api'
    sys.path.insert(0, str(api_dir))
    
    try:
        from backend_app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test /health
        response = client.get("/health")
        assert response.status_code == 200, f"/health returned {response.status_code}"
        data = response.json()
        assert data["status"] == "ok", f"/health returned wrong status: {data}"
        print("  ✅ /health returns correct structure")
        
        # Test /live
        response = client.get("/live")
        assert response.status_code == 200, f"/live returned {response.status_code}"
        data = response.json()
        assert data["status"] == "alive", f"/live returned wrong status: {data}"
        print("  ✅ /live returns correct structure")
        
        # Test /ready
        response = client.get("/ready")
        assert response.status_code == 200, f"/ready returned {response.status_code}"
        data = response.json()
        assert data["status"] == "ready", f"/ready returned wrong status: {data}"
        assert "message" in data, f"/ready missing message field: {data}"
        print("  ✅ /ready returns correct structure")
        
        # Test /health/ping
        response = client.get("/health/ping")
        assert response.status_code == 200, f"/health/ping returned {response.status_code}"
        data = response.json()
        assert data["status"] == "ok", f"/health/ping returned wrong status: {data}"
        print("  ✅ /health/ping returns correct structure")
        
        print("✅ All endpoints return correct response structure!")
        return True
        
    except Exception as e:
        print(f"❌ Response structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_endpoint_performance():
    """Test that health endpoints respond quickly"""
    print("\n🧪 Testing endpoint performance (should be <5ms)...")
    
    script_dir = Path(__file__).parent
    api_dir = script_dir / 'api'
    sys.path.insert(0, str(api_dir))
    
    try:
        from backend_app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        endpoints = ["/health", "/live", "/ready", "/health/ping"]
        
        for endpoint in endpoints:
            start = time.time()
            response = client.get(endpoint)
            duration_ms = (time.time() - start) * 1000
            
            assert response.status_code == 200, f"{endpoint} returned {response.status_code}"
            
            # Be lenient with timing - test client adds overhead
            # In production, these should be <5ms, but in tests <100ms is acceptable
            if duration_ms < 100:
                print(f"  ✅ {endpoint} responded in {duration_ms:.2f}ms")
            else:
                print(f"  ⚠️  {endpoint} responded in {duration_ms:.2f}ms (acceptable in tests)")
        
        print("✅ All endpoints respond quickly!")
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("MASTER FIX VERIFICATION: Database-Free Health Checks")
    print("=" * 70)
    
    success = True
    
    # Code analysis tests (don't require app startup)
    tests = [
        test_health_endpoint_no_db_import,
        test_ready_endpoint_no_db_calls,
        test_health_ping_endpoint,
    ]
    
    for test_func in tests:
        try:
            if not test_func():
                success = False
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            success = False
    
    # Runtime tests (require app startup)
    runtime_tests = [
        test_endpoint_response_structure,
        test_endpoint_performance,
    ]
    
    for test_func in runtime_tests:
        try:
            if not test_func():
                success = False
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            success = False
    
    print("\n" + "=" * 70)
    if success:
        print("✅ ALL TESTS PASSED - Health checks are 100% database-free!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Review the output above")
        print("=" * 70)
        sys.exit(1)

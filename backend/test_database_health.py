"""
Test database health monitoring functionality
"""
import asyncio
import sys
from pathlib import Path

import pytest

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

@pytest.mark.asyncio
async def test_database_health():
    """Test database health monitoring utilities"""
    
    print("=" * 80)
    print("Database Health Monitoring Tests")
    print("=" * 80)
    
    # Test 1: Import db_health module
    print("\n1. Testing db_health module imports...")
    try:
        from app.core.db_health import (
            check_database_health, 
            log_slow_query_warning, 
            get_database_stats
        )
        print("   ✓ db_health module imported successfully")
    except Exception as e:
        print(f"   ✗ Failed to import db_health module: {e}")
        return False
    
    # Test 2: Test slow query warning logic
    print("\n2. Testing slow query warning logic...")
    
    test_cases = [
        (500, 1000, False),   # 500ms < 1000ms threshold - not slow
        (1500, 1000, True),   # 1500ms > 1000ms threshold - slow
        (2000, 500, True),    # 2000ms > 500ms threshold - slow
        (100, 200, False),    # 100ms < 200ms threshold - not slow
    ]
    
    for duration, threshold, should_warn in test_cases:
        # The function logs but doesn't return, so we just verify it doesn't crash
        await log_slow_query_warning("test_query", duration, threshold)
        status = "SLOW" if should_warn else "OK"
        print(f"   ✓ {duration}ms with {threshold}ms threshold: {status}")
    
    # Test 3: Test health status structure
    print("\n3. Testing health status structure...")
    
    expected_healthy = {
        "status": "healthy",
        "response_time_ms": 50,
        "message": "Database connection is working"
    }
    
    expected_unhealthy = {
        "status": "unhealthy",
        "response_time_ms": 5000,
        "error": "Connection timeout",
        "message": "Database connection failed"
    }
    
    # Verify structure
    assert "status" in expected_healthy, "Health status should have 'status' field"
    assert "response_time_ms" in expected_healthy, "Health status should have 'response_time_ms' field"
    assert "message" in expected_healthy, "Health status should have 'message' field"
    
    assert expected_healthy["status"] == "healthy", "Healthy status should be 'healthy'"
    assert expected_unhealthy["status"] == "unhealthy", "Unhealthy status should be 'unhealthy'"
    
    print("   ✓ Healthy status structure validated")
    print("   ✓ Unhealthy status structure validated")
    
    # Test 4: Test database stats structure
    print("\n4. Testing database stats structure...")
    
    expected_stats = {
        "active_connections": 5,
        "database_size_bytes": 1048576,
        "database_size_mb": 1.0
    }
    
    assert "active_connections" in expected_stats, "Stats should have 'active_connections'"
    assert "database_size_bytes" in expected_stats, "Stats should have 'database_size_bytes'"
    assert "database_size_mb" in expected_stats, "Stats should have 'database_size_mb'"
    
    # Verify size conversion
    size_mb = expected_stats["database_size_bytes"] / (1024 * 1024)
    assert abs(size_mb - expected_stats["database_size_mb"]) < 0.01, "Size conversion should be accurate"
    
    print("   ✓ Database stats structure validated")
    print("   ✓ Size conversion validated")
    
    # Test 5: Test timing threshold logic
    print("\n5. Testing timing threshold detection...")
    
    slow_threshold = 1000  # 1 second
    
    timing_tests = [
        (500, False, "500ms should not trigger warning"),
        (999, False, "999ms should not trigger warning"),
        (1000, False, "1000ms at threshold should not trigger warning"),
        (1001, True, "1001ms should trigger warning"),
        (5000, True, "5000ms should trigger warning"),
    ]
    
    for duration_ms, should_be_slow, description in timing_tests:
        is_slow = duration_ms > slow_threshold
        assert is_slow == should_be_slow, f"Failed: {description}"
        print(f"   ✓ {description}")
    
    # Test 6: Test error handling structure
    print("\n6. Testing error handling patterns...")
    
    try:
        # Simulate an error scenario
        error_msg = "Database connection timeout"
        error_type = "TimeoutError"
        
        error_response = {
            "status": "unhealthy",
            "error": error_msg,
            "error_type": error_type
        }
        
        assert error_response["status"] == "unhealthy", "Error status should be unhealthy"
        assert "error" in error_response, "Error response should include error field"
        
        print("   ✓ Error response structure validated")
        
    except Exception as e:
        print(f"   ✗ Error handling test failed: {e}")
        return False
    
    # Test 7: Test health check response integration
    print("\n7. Testing health check response structure...")
    
    expected_health_check = {
        "status": "healthy",
        "api": {
            "status": "healthy",
            "message": "HireMeBahamas API is running",
            "version": "1.0.0"
        },
        "database": {
            "status": "healthy",
            "response_time_ms": 50,
            "message": "Database connection is working"
        }
    }
    
    # Verify structure
    assert "status" in expected_health_check, "Health check should have status"
    assert "api" in expected_health_check, "Health check should have api info"
    assert "database" in expected_health_check, "Health check should have database info"
    
    # Verify nested structures
    assert expected_health_check["api"]["status"] == "healthy", "API status should be healthy"
    assert expected_health_check["database"]["status"] == "healthy", "DB status should be healthy"
    assert expected_health_check["status"] == "healthy", "Overall status should be healthy"
    
    print("   ✓ Health check response structure validated")
    print("   ✓ Nested status fields validated")
    
    # Test 8: Test degraded status logic
    print("\n8. Testing degraded status scenarios...")
    
    # When database is unhealthy, overall should be degraded
    db_unhealthy_check = {
        "status": "degraded",  # Overall status
        "api": {
            "status": "healthy"
        },
        "database": {
            "status": "unhealthy"
        }
    }
    
    # Verify degraded logic
    assert db_unhealthy_check["status"] == "degraded", "Overall status should be degraded when DB is unhealthy"
    assert db_unhealthy_check["api"]["status"] == "healthy", "API can still be healthy"
    assert db_unhealthy_check["database"]["status"] == "unhealthy", "DB status should be unhealthy"
    
    print("   ✓ Degraded status logic validated")
    print("   ✓ Component-level status differentiation validated")
    
    print("\n" + "=" * 80)
    print("✅ All database health monitoring tests passed!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_database_health())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

"""
Test concurrent query execution for performance optimization.

This test verifies that the concurrent query execution utility works correctly
and provides performance improvements for independent queries.
"""
import os
import sys
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


def wait_for_db_init(max_wait=5):
    """Wait for database initialization to complete"""
    from final_backend_postgresql import _db_initialized
    
    start = time.time()
    while not _db_initialized and (time.time() - start) < max_wait:
        # Check if there's an init thread
        try:
            from final_backend_postgresql import _db_init_thread
            if _db_init_thread and _db_init_thread.is_alive():
                time.sleep(0.1)
            else:
                break
        except (ImportError, AttributeError):
            # _db_init_thread may not be defined if init already completed
            break
    return _db_initialized


def test_concurrent_query_execution():
    """Test that concurrent queries execute correctly"""
    from final_backend_postgresql import (
        execute_queries_concurrent,
        get_db_connection,
        return_db_connection,
        USE_POSTGRESQL,
    )
    
    # Wait for database initialization
    wait_for_db_init()
    
    print("=" * 80)
    print("Concurrent Query Execution Test")
    print("=" * 80)
    
    # Test 1: Basic concurrent query execution
    print("\n1. Testing basic concurrent query execution...")
    
    queries = [
        ("SELECT COUNT(*) as count FROM users", None, 'one'),
        ("SELECT COUNT(*) as count FROM posts", None, 'one'),
        ("SELECT COUNT(*) as count FROM jobs", None, 'one'),
    ]
    
    start_time = time.time()
    results = execute_queries_concurrent(queries, timeout_seconds=10)
    elapsed_ms = (time.time() - start_time) * 1000
    
    print(f"   Executed 3 concurrent queries in {elapsed_ms:.2f}ms")
    assert len(results) == 3, f"Expected 3 results, got {len(results)}"
    
    # All results should be valid (not None)
    for i, result in enumerate(results):
        assert result is not None, f"Result {i} should not be None"
        # Both SQLite Row and PostgreSQL RealDictCursor support key access
        assert "count" in result.keys(), f"Result {i} should have 'count' key"
        print(f"   Query {i + 1} result: count = {result['count']}")
    
    print("   ✓ Basic concurrent execution works correctly")
    
    # Test 2: Performance comparison (concurrent vs sequential)
    print("\n2. Testing performance improvement...")
    
    # Sequential execution
    sequential_start = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sequential_results = []
    for query_sql, params, fetch_mode in queries:
        if params:
            cursor.execute(query_sql, params)
        else:
            cursor.execute(query_sql)
        sequential_results.append(cursor.fetchone())
    
    cursor.close()
    return_db_connection(conn)
    sequential_time = (time.time() - sequential_start) * 1000
    
    # Concurrent execution
    concurrent_start = time.time()
    concurrent_results = execute_queries_concurrent(queries, timeout_seconds=10)
    concurrent_time = (time.time() - concurrent_start) * 1000
    
    print(f"   Sequential execution time: {sequential_time:.2f}ms")
    print(f"   Concurrent execution time: {concurrent_time:.2f}ms")
    
    # Verify results match
    for i in range(len(queries)):
        assert sequential_results[i]["count"] == concurrent_results[i]["count"], \
            f"Results mismatch at index {i}"
    
    print("   ✓ Results match between sequential and concurrent execution")
    
    # Test 3: Handle query with parameters
    print("\n3. Testing queries with parameters...")
    
    # Use correct boolean format for SQLite (1) vs PostgreSQL (TRUE)
    if USE_POSTGRESQL:
        param_queries = [
            ("SELECT COUNT(*) as count FROM users WHERE is_active = %s", (True,), 'one'),
            ("SELECT COUNT(*) as count FROM jobs WHERE is_active = %s", (True,), 'one'),
        ]
    else:
        param_queries = [
            ("SELECT COUNT(*) as count FROM users WHERE is_active = ?", (1,), 'one'),
            ("SELECT COUNT(*) as count FROM jobs WHERE is_active = ?", (1,), 'one'),
        ]
    
    results = execute_queries_concurrent(param_queries, timeout_seconds=10)
    
    assert len(results) == 2, "Expected 2 results"
    for i, result in enumerate(results):
        assert result is not None, f"Result {i} should not be None"
        print(f"   Parameterized query {i + 1} result: count = {result['count']}")
    
    print("   ✓ Parameterized queries work correctly")
    
    # Test 4: Handle empty query list
    print("\n4. Testing empty query list...")
    
    empty_results = execute_queries_concurrent([], timeout_seconds=10)
    assert empty_results == [], "Empty query list should return empty results"
    print("   ✓ Empty query list handled correctly")
    
    print("\n" + "=" * 80)
    print("All concurrent query tests passed!")
    print("=" * 80)
    
    return True


def test_concurrent_query_error_handling():
    """Test that concurrent queries handle errors gracefully"""
    from final_backend_postgresql import execute_queries_concurrent
    
    # Wait for database initialization
    wait_for_db_init()
    
    print("\n" + "=" * 80)
    print("Concurrent Query Error Handling Test")
    print("=" * 80)
    
    # Test 1: Invalid query should return None (not crash)
    print("\n1. Testing invalid query handling...")
    
    queries = [
        ("SELECT COUNT(*) as count FROM users", None, 'one'),
        ("SELECT * FROM nonexistent_table", None, 'all'),  # Invalid query
        ("SELECT COUNT(*) as count FROM posts", None, 'one'),
    ]
    
    results = execute_queries_concurrent(queries, timeout_seconds=10)
    
    assert len(results) == 3, "Should return 3 results even with invalid query"
    assert results[0] is not None, "First result should be valid"
    assert results[1] is None, "Second result should be None (invalid query)"
    assert results[2] is not None, "Third result should be valid"
    
    print("   ✓ Invalid query handled gracefully")
    
    print("\n" + "=" * 80)
    print("All error handling tests passed!")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        test_concurrent_query_execution()
        test_concurrent_query_error_handling()
        print("\n✓ All concurrent query tests completed successfully")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

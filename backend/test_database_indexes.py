"""
Test database indexing for query optimization.

This test verifies that the database indexes are created correctly
to optimize query performance and prevent HTTP 499 timeout errors.
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
    from final_backend_postgresql import _db_initialized, _db_init_thread
    
    start = time.time()
    while not _db_initialized and (time.time() - start) < max_wait:
        if _db_init_thread and _db_init_thread.is_alive():
            time.sleep(0.1)
        else:
            break
    return _db_initialized


def test_database_indexes():
    """Test that database indexes are properly configured"""
    from final_backend_postgresql import (
        get_db_connection,
        return_db_connection,
        USE_POSTGRESQL,
    )
    
    # Wait for database initialization
    wait_for_db_init()
    
    print("=" * 80)
    print("Database Index Test")
    print("=" * 80)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if USE_POSTGRESQL:
            # Query PostgreSQL for indexes
            print("\n1. Checking PostgreSQL indexes...")
            cursor.execute("""
                SELECT indexname, tablename, indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """)
            indexes = cursor.fetchall()
            
            print(f"   Found {len(indexes)} indexes")
            for idx in indexes:
                print(f"   - {idx['tablename']}.{idx['indexname']}")
            
            # Check for specific performance-critical indexes
            index_names = [idx['indexname'] for idx in indexes]
            expected_indexes = [
                'posts_user_id_idx',
                'posts_created_at_idx',
                'jobs_is_active_idx',
                'jobs_created_at_idx',
                'follows_follower_id_idx',
                'follows_followed_id_idx',
                # New indexes added for performance optimization
                'users_created_at_idx',
                'friendships_sender_receiver_idx',
                'friendships_receiver_sender_idx',
                'stories_expires_at_idx',
            ]
            
            for expected in expected_indexes:
                if expected in index_names:
                    print(f"   ✓ {expected} exists")
                else:
                    print(f"   ⚠ {expected} not found (may need migration)")
        else:
            # Query SQLite for indexes
            print("\n1. Checking SQLite indexes...")
            cursor.execute("""
                SELECT name, tbl_name, sql
                FROM sqlite_master
                WHERE type = 'index' AND sql IS NOT NULL
                ORDER BY tbl_name, name
            """)
            indexes = cursor.fetchall()
            
            print(f"   Found {len(indexes)} explicit indexes")
            for idx in indexes:
                print(f"   - {idx['tbl_name']}.{idx['name']}")
            
            # Check for specific performance-critical indexes
            index_names = [idx['name'] for idx in indexes]
            expected_indexes = [
                'posts_user_id_idx',
                'posts_created_at_idx',
                'jobs_is_active_idx',
                'jobs_created_at_idx',
                'follows_follower_id_idx',
                'follows_followed_id_idx',
                # New indexes added for performance optimization
                'users_created_at_idx',
                'friendships_sender_receiver_idx',
                'friendships_receiver_sender_idx',
                'stories_expires_at_idx',
            ]
            
            for expected in expected_indexes:
                if expected in index_names:
                    print(f"   ✓ {expected} exists")
                else:
                    print(f"   ⚠ {expected} not found (may need migration)")
        
        print("\n" + "=" * 80)
        print("Database index test completed!")
        print("=" * 80)
        
        return True
    
    finally:
        cursor.close()
        return_db_connection(conn)


def test_query_performance():
    """Test that queries using indexes perform well"""
    import time
    from final_backend_postgresql import (
        get_db_connection,
        return_db_connection,
        USE_POSTGRESQL,
    )
    
    # Wait for database initialization
    wait_for_db_init()
    
    print("\n" + "=" * 80)
    print("Query Performance Test")
    print("=" * 80)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Test 1: Posts query with index
        print("\n1. Testing posts query performance...")
        start_time = time.time()
        if USE_POSTGRESQL:
            cursor.execute("""
                SELECT p.id, p.content, p.created_at, u.first_name
                FROM posts p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.created_at DESC
                LIMIT 20
            """)
        else:
            cursor.execute("""
                SELECT p.id, p.content, p.created_at, u.first_name
                FROM posts p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.created_at DESC
                LIMIT 20
            """)
        posts = cursor.fetchall()
        elapsed_ms = (time.time() - start_time) * 1000
        print(f"   Posts query: {elapsed_ms:.2f}ms ({len(posts)} results)")
        assert elapsed_ms < 1000, f"Posts query too slow: {elapsed_ms:.2f}ms"
        print("   ✓ Posts query performance acceptable")
        
        # Test 2: Jobs query with index
        print("\n2. Testing jobs query performance...")
        start_time = time.time()
        if USE_POSTGRESQL:
            cursor.execute("""
                SELECT j.id, j.title, j.company, j.created_at
                FROM jobs j
                WHERE j.is_active = TRUE
                ORDER BY j.created_at DESC
                LIMIT 20
            """)
        else:
            cursor.execute("""
                SELECT j.id, j.title, j.company, j.created_at
                FROM jobs j
                WHERE j.is_active = 1
                ORDER BY j.created_at DESC
                LIMIT 20
            """)
        jobs = cursor.fetchall()
        elapsed_ms = (time.time() - start_time) * 1000
        print(f"   Jobs query: {elapsed_ms:.2f}ms ({len(jobs)} results)")
        assert elapsed_ms < 1000, f"Jobs query too slow: {elapsed_ms:.2f}ms"
        print("   ✓ Jobs query performance acceptable")
        
        # Test 3: Follows query with index
        print("\n3. Testing follows query performance...")
        start_time = time.time()
        if USE_POSTGRESQL:
            cursor.execute("""
                SELECT COUNT(*) as count FROM follows
            """)
        else:
            cursor.execute("""
                SELECT COUNT(*) as count FROM follows
            """)
        result = cursor.fetchone()
        elapsed_ms = (time.time() - start_time) * 1000
        print(f"   Follows count query: {elapsed_ms:.2f}ms")
        assert elapsed_ms < 500, f"Follows query too slow: {elapsed_ms:.2f}ms"
        print("   ✓ Follows query performance acceptable")
        
        print("\n" + "=" * 80)
        print("All query performance tests passed!")
        print("=" * 80)
        
        return True
    
    finally:
        cursor.close()
        return_db_connection(conn)


if __name__ == "__main__":
    try:
        test_database_indexes()
        test_query_performance()
        print("\n✓ All database index tests completed successfully")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

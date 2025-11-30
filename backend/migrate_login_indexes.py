"""
Database migration script to add performance indexes for login optimization.

This migration adds indexes that significantly reduce query time for:
1. User lookup by email (indexed email with case-insensitive function)
2. User lookup by phone
3. User lookup by ID (for cache validation)

Run this migration CONCURRENTLY to avoid blocking reads/writes on production.
"""
import os
import sys

# SQL statements for PostgreSQL indexes
# These are designed to be run CONCURRENTLY to avoid locking the table
POSTGRESQL_INDEX_STATEMENTS = [
    # Case-insensitive email index for faster login lookups
    # This is the PRIMARY performance optimization for login
    """
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_lower 
    ON users (lower(email));
    """,
    
    # Phone number index for phone-based login
    """
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_phone 
    ON users (phone) WHERE phone IS NOT NULL;
    """,
    
    # Combined email and is_active index for even faster login
    # This is particularly useful when filtering by active status during login
    """
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_active 
    ON users (email, is_active);
    """,
    
    # Index on created_at for recently registered users queries
    """
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created_at 
    ON users (created_at DESC);
    """,
]

# SQLite doesn't support CONCURRENTLY, use regular CREATE INDEX
SQLITE_INDEX_STATEMENTS = [
    """
    CREATE INDEX IF NOT EXISTS idx_users_email_lower ON users (email);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_users_phone ON users (phone);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_users_email_active ON users (email, is_active);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_users_created_at ON users (created_at);
    """,
]


def run_migration():
    """Run the index migration."""
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    from final_backend_postgresql import (
        get_db_connection,
        return_db_connection,
        USE_POSTGRESQL,
    )
    
    print("=" * 80)
    print("Running login performance index migration...")
    print("=" * 80)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if USE_POSTGRESQL:
            print("\nApplying PostgreSQL indexes (CONCURRENTLY)...")
            statements = POSTGRESQL_INDEX_STATEMENTS
        else:
            print("\nApplying SQLite indexes...")
            statements = SQLITE_INDEX_STATEMENTS
        
        for statement in statements:
            try:
                # Extract index name for logging
                if "idx_" in statement:
                    index_name = statement.split("idx_")[1].split()[0].strip()
                else:
                    index_name = "unknown"
                
                print(f"\nCreating index: idx_{index_name}...")
                cursor.execute(statement)
                conn.commit()
                print(f"  ✓ idx_{index_name} created successfully")
            except Exception as e:
                error_msg = str(e).lower()
                if "already exists" in error_msg or "duplicate" in error_msg:
                    print(f"  ⚠ Index already exists (skipping)")
                else:
                    print(f"  ✗ Error: {e}")
                    # Continue with other indexes even if one fails
                    conn.rollback()
        
        print("\n" + "=" * 80)
        print("Index migration completed!")
        print("=" * 80)
        
        # Verify indexes
        print("\nVerifying indexes...")
        if USE_POSTGRESQL:
            cursor.execute("""
                SELECT indexname, tablename
                FROM pg_indexes
                WHERE schemaname = 'public' 
                AND tablename = 'users'
                AND indexname LIKE 'idx_%'
                ORDER BY indexname
            """)
        else:
            cursor.execute("""
                SELECT name, tbl_name
                FROM sqlite_master
                WHERE type = 'index' 
                AND tbl_name = 'users'
                AND name LIKE 'idx_%'
                ORDER BY name
            """)
        
        indexes = cursor.fetchall()
        print(f"\nFound {len(indexes)} custom indexes on users table:")
        for idx in indexes:
            idx_name = idx['indexname'] if USE_POSTGRESQL else idx['name']
            print(f"  - {idx_name}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        return False
    finally:
        cursor.close()
        return_db_connection(conn)


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)

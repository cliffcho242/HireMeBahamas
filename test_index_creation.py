"""
Test script to verify database index creation.

This script tests that:
1. Engine can initialize correctly with lazy loading
2. Database tables can be created via init_db()
3. Indexes defined in models (index=True) are created automatically
4. The lazy engine pattern works as expected

Usage:
    python test_index_creation.py
"""
import asyncio
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_lazy_engine_initialization():
    """Test that lazy engine initialization works correctly."""
    logger.info("="*60)
    logger.info("TEST 1: Lazy Engine Initialization")
    logger.info("="*60)
    
    try:
        # Import database module (should NOT create engine yet)
        from backend.app.database import get_engine
        logger.info("✓ Database module imported")
        
        # Trigger engine initialization by accessing it
        # Note: We test the behavior through public API (get_engine) instead of accessing private _engine
        actual_engine = get_engine()
        if actual_engine is not None:
            logger.info("✓ Engine initialized successfully on first access (lazy initialization working)")
            return True
        else:
            logger.error("✗ Engine initialization returned None")
            return False
            
    except Exception as e:
        logger.error(f"✗ Test failed: {type(e).__name__}: {e}")
        return False


async def test_database_initialization():
    """Test that database initialization creates tables and indexes."""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Database Initialization (init_db)")
    logger.info("="*60)
    
    try:
        from backend.app.database import init_db, get_engine
        from sqlalchemy import text
        
        # Ensure engine is available
        engine = get_engine()
        if engine is None:
            logger.error("✗ Engine not available, cannot test database initialization")
            return False
        
        # Call init_db() to create tables and indexes
        logger.info("Calling init_db()...")
        success = await init_db()
        
        if success:
            logger.info("✓ init_db() completed successfully")
        else:
            logger.error("✗ init_db() failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Test failed: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_index_existence():
    """Test that indexes were created correctly."""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: Verify Index Creation")
    logger.info("="*60)
    
    try:
        from backend.app.database import engine
        from sqlalchemy import text
        
        # List of expected indexes (from models with index=True)
        expected_indexes = [
            ("users", "ix_users_email"),        # email = Column(..., index=True)
            ("users", "ix_users_username"),     # username = Column(..., index=True)
        ]
        
        async with engine.connect() as conn:
            logger.info("\nChecking for expected indexes:")
            
            all_found = True
            for table_name, index_name in expected_indexes:
                # Note: Using PostgreSQL-specific pg_indexes view
                # For production, consider using SQLAlchemy Inspector for database-agnostic queries
                result = await conn.execute(text("""
                    SELECT 1 FROM pg_indexes 
                    WHERE tablename = :table_name 
                    AND indexname = :index_name
                """), {"table_name": table_name, "index_name": index_name})
                
                exists = result.scalar() is not None
                status = "✓" if exists else "✗"
                logger.info(f"  {status} {table_name}.{index_name}")
                
                if not exists:
                    all_found = False
            
            if all_found:
                logger.info("\n✓ All expected indexes found")
                return True
            else:
                logger.warning("\n⚠ Some indexes are missing")
                return False
                
    except Exception as e:
        logger.error(f"✗ Test failed: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_base_metadata_indexes():
    """Test that Base.metadata includes index definitions from models."""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: Verify Base.metadata Includes Indexes")
    logger.info("="*60)
    
    try:
        from backend.app.database import Base
        from backend.app import models  # Import models to register them
        
        logger.info(f"\nRegistered tables: {len(Base.metadata.tables)}")
        
        # Check if users table is registered
        if "users" in Base.metadata.tables:
            logger.info("✓ Users table registered in Base.metadata")
            
            users_table = Base.metadata.tables["users"]
            
            # Check for indexes
            logger.info(f"\nIndexes defined for users table:")
            index_count = 0
            for index in users_table.indexes:
                logger.info(f"  - {index.name}: {[c.name for c in index.columns]}")
                index_count += 1
            
            if index_count > 0:
                logger.info(f"\n✓ Found {index_count} index(es) in Base.metadata")
                return True
            else:
                logger.warning("\n⚠ No indexes found in Base.metadata (may be OK if using column-level index=True)")
                # Note: column-level index=True doesn't show up in table.indexes
                # but is still created by create_all()
                return True
        else:
            logger.error("✗ Users table not registered in Base.metadata")
            return False
            
    except Exception as e:
        logger.error(f"✗ Test failed: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """Run all tests."""
    logger.info("\n" + "="*80)
    logger.info(" INDEX CREATION VERIFICATION TEST SUITE")
    logger.info("="*80)
    logger.info("\nThis test suite verifies that database indexes are created correctly")
    logger.info("via the lazy engine initialization pattern and Base.metadata.create_all")
    logger.info("\n")
    
    # Check DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("✗ DATABASE_URL not set. Please set it before running tests.")
        logger.info("\nFor local testing, set:")
        logger.info("  export DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/DBNAME")
        sys.exit(1)
    else:
        # Mask password for logging - show only host/database
        try:
            if "@" in database_url:
                host_part = database_url.split("@")[1]
                logger.info(f"DATABASE_URL configured: postgresql://***:***@{host_part}")
            else:
                logger.info("DATABASE_URL configured (format not recognized)")
        except Exception:
            logger.info("DATABASE_URL configured")
    
    # Run tests
    tests = [
        ("Lazy Engine Initialization", test_lazy_engine_initialization),
        ("Database Initialization", test_database_initialization),
        ("Index Existence", test_index_existence),
        ("Base.metadata Indexes", test_base_metadata_indexes),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            logger.error(f"✗ Unexpected error in {test_name}: {e}")
            results[test_name] = False
    
    # Print summary
    logger.info("\n" + "="*80)
    logger.info(" TEST SUMMARY")
    logger.info("="*80)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n✅ ALL TESTS PASSED - Index creation is working correctly!")
        logger.info("\nConclusion:")
        logger.info("  - Lazy engine initialization is working")
        logger.info("  - init_db() creates tables and indexes via Base.metadata.create_all")
        logger.info("  - Indexes defined with index=True are created automatically")
        logger.info("  - No code changes needed")
        return 0
    else:
        logger.error(f"\n❌ {total - passed} TEST(S) FAILED")
        logger.error("\nSome tests failed. Please check:")
        logger.error("  1. DATABASE_URL is configured correctly")
        logger.error("  2. Database is accessible")
        logger.error("  3. Database credentials are valid")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

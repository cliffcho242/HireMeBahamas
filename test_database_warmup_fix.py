"""
Test to verify database warmup coroutine fix.

This test ensures that:
1. init_db() is properly awaited and returns a boolean
2. warmup_db() is called without an engine parameter
3. The background_init() function works correctly
"""
import asyncio
import logging
from unittest.mock import patch, AsyncMock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_background_init_success():
    """Test that background_init properly awaits init_db and calls warmup_db."""
    logger.info("Testing background_init with successful initialization...")
    
    # Mock init_db to return True (success)
    # Mock warmup_db to return True (success)
    with patch('app.database.init_db', new_callable=AsyncMock) as mock_init_db, \
         patch('app.database.warmup_db', new_callable=AsyncMock) as mock_warmup_db:
        
        mock_init_db.return_value = True
        mock_warmup_db.return_value = True
        
        # Import and call background_init
        from app.main import background_init
        await background_init()
        
        # Verify init_db was called (awaited)
        mock_init_db.assert_called_once()
        
        # Verify warmup_db was called without parameters (since init_db succeeded)
        mock_warmup_db.assert_called_once_with()
        
    logger.info("✓ background_init correctly awaits init_db and calls warmup_db")


async def test_background_init_failed_init():
    """Test that warmup_db is not called when init_db fails."""
    logger.info("Testing background_init when init_db fails...")
    
    # Mock init_db to return False (failure)
    with patch('app.database.init_db', new_callable=AsyncMock) as mock_init_db, \
         patch('app.database.warmup_db', new_callable=AsyncMock) as mock_warmup_db:
        
        mock_init_db.return_value = False
        
        # Import and call background_init
        from app.main import background_init
        await background_init()
        
        # Verify init_db was called
        mock_init_db.assert_called_once()
        
        # Verify warmup_db was NOT called (since init_db failed)
        mock_warmup_db.assert_not_called()
        
    logger.info("✓ warmup_db is not called when init_db fails")


async def test_background_init_exception_handling():
    """Test that exceptions in background_init are properly caught."""
    logger.info("Testing background_init exception handling...")
    
    # Mock init_db to raise an exception
    with patch('app.database.init_db', new_callable=AsyncMock) as mock_init_db:
        
        mock_init_db.side_effect = Exception("Database connection failed")
        
        # Import and call background_init
        from app.main import background_init
        
        # Should not raise exception (it's caught and logged)
        try:
            await background_init()
            logger.info("✓ Exception was caught and handled gracefully")
        except Exception as e:
            logger.error(f"✗ Exception was not caught: {e}")
            raise


async def test_init_db_returns_bool():
    """Test that init_db returns a boolean, not a coroutine."""
    logger.info("Testing that init_db returns a boolean...")
    
    from app.database import init_db
    
    # Call init_db with await
    result = await init_db()
    
    # Verify result is a boolean
    assert isinstance(result, bool), f"Expected bool, got {type(result)}"
    logger.info(f"✓ init_db returned {result} (type: {type(result).__name__})")


async def test_warmup_db_no_engine_parameter():
    """Test that warmup_db can be called without engine parameter."""
    logger.info("Testing that warmup_db works without engine parameter...")
    
    from app.database import warmup_db
    
    # Call warmup_db without any parameters
    result = await warmup_db()
    
    # Verify result is a boolean
    assert isinstance(result, bool), f"Expected bool, got {type(result)}"
    logger.info(f"✓ warmup_db returned {result} (type: {type(result).__name__})")


async def main():
    """Run all tests."""
    logger.info("=" * 70)
    logger.info("Database Warmup Fix Tests")
    logger.info("=" * 70)
    
    tests = [
        ("background_init success", test_background_init_success),
        ("background_init with failed init", test_background_init_failed_init),
        ("background_init exception handling", test_background_init_exception_handling),
        ("init_db returns boolean", test_init_db_returns_bool),
        ("warmup_db without engine parameter", test_warmup_db_no_engine_parameter),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            logger.info(f"\n[TEST] {name}")
            await test_func()
            passed += 1
            logger.info(f"[PASS] {name}")
        except Exception as e:
            failed += 1
            logger.error(f"[FAIL] {name}: {e}", exc_info=True)
    
    logger.info("\n" + "=" * 70)
    logger.info(f"Results: {passed} passed, {failed} failed")
    logger.info("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

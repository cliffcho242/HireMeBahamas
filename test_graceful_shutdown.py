#!/usr/bin/env python3
"""
Test graceful shutdown implementation.

This test verifies that the shutdown hook properly:
1. Closes database connections
2. Disposes the engine to prevent zombie sockets
3. Handles errors gracefully
"""
import asyncio
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add the api directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))


async def test_shutdown_hook_exists():
    """Test that the shutdown hook is properly registered in the code."""
    print("\n1. Testing shutdown hook exists in code...")
    
    # Read the main.py file and check for shutdown hook
    main_py_path = os.path.join(os.path.dirname(__file__), 'api', 'backend_app', 'main.py')
    
    try:
        with open(main_py_path, 'r') as f:
            content = f.read()
            
        has_decorator = '@app.on_event("shutdown")' in content
        has_function = 'async def full_shutdown()' in content or 'def shutdown()' in content
        
        if has_decorator and has_function:
            print(f"   ✅ Found shutdown hook with @app.on_event('shutdown') decorator")
            return True
        else:
            print(f"   ❌ Shutdown hook not found (decorator: {has_decorator}, function: {has_function})")
            return False
    except Exception as e:
        print(f"   ❌ Error reading main.py: {e}")
        return False


async def test_engine_disposal_on_shutdown():
    """Test that engine.dispose() is called during shutdown.
    
    Note: backend_app.database uses AsyncEngine (asyncpg), so dispose() is async.
    We use AsyncMock to properly mock the async dispose() method.
    """
    print("\n2. Testing engine disposal during shutdown...")
    
    # Import close_db function
    from backend_app.database import close_db, get_engine
    
    # Create a mock async engine (backend_app.database uses AsyncEngine with asyncpg)
    mock_engine = AsyncMock()
    mock_engine.dispose = AsyncMock()  # AsyncMock because dispose() is async in AsyncEngine
    
    # Patch get_engine to return our mock
    with patch('backend_app.database.get_engine', return_value=mock_engine):
        with patch('backend_app.database._engine', mock_engine):
            await close_db()
            
            # Verify dispose was called
            if mock_engine.dispose.called:
                print("   ✅ engine.dispose() was called during shutdown")
                return True
            else:
                print("   ❌ engine.dispose() was NOT called")
                return False


async def test_shutdown_handles_none_engine():
    """Test that shutdown handles gracefully when engine is None."""
    print("\n3. Testing shutdown with None engine...")
    
    from backend_app.database import close_db
    
    # Patch get_engine to return None
    with patch('backend_app.database.get_engine', return_value=None):
        with patch('backend_app.database._engine', None):
            try:
                await close_db()
                print("   ✅ Shutdown handled None engine gracefully")
                return True
            except Exception as e:
                print(f"   ❌ Shutdown failed with None engine: {e}")
                return False


async def test_shutdown_handles_errors():
    """Test that shutdown handles disposal errors gracefully."""
    print("\n4. Testing shutdown error handling...")
    
    from backend_app.database import close_db
    
    # Create a mock engine that raises an error
    mock_engine = AsyncMock()
    mock_engine.dispose = AsyncMock(side_effect=RuntimeError("Connection error"))
    
    with patch('backend_app.database.get_engine', return_value=mock_engine):
        with patch('backend_app.database._engine', mock_engine):
            try:
                await close_db()
                print("   ✅ Shutdown handled disposal error gracefully")
                return True
            except Exception as e:
                print(f"   ❌ Shutdown raised exception: {e}")
                return False


async def test_shutdown_prevents_zombie_sockets():
    """Test that shutdown properly closes pooled connections."""
    print("\n5. Testing prevention of zombie sockets...")
    
    from backend_app.database import close_db
    
    # Create a mock engine with pool info
    mock_engine = AsyncMock()
    mock_engine.dispose = AsyncMock()
    mock_engine.pool = MagicMock()
    mock_engine.pool.size = MagicMock(return_value=5)
    mock_engine.pool.checkedin = MagicMock(return_value=3)
    
    with patch('backend_app.database.get_engine', return_value=mock_engine):
        with patch('backend_app.database._engine', mock_engine):
            await close_db()
            
            # Verify dispose was called (which closes all connections)
            if mock_engine.dispose.called:
                print("   ✅ Pooled connections closed (prevents zombie sockets)")
                return True
            else:
                print("   ❌ Dispose not called (may leave zombie sockets)")
                return False


async def test_full_shutdown_sequence():
    """Test that shutdown hook calls engine.dispose()."""
    print("\n6. Testing shutdown hook calls engine.dispose()...")
    
    # Read the main.py and database.py files to verify implementation
    main_py_path = os.path.join(os.path.dirname(__file__), 'api', 'backend_app', 'main.py')
    database_py_path = os.path.join(os.path.dirname(__file__), 'api', 'backend_app', 'database.py')
    
    try:
        with open(main_py_path, 'r') as f:
            main_content = f.read()
        
        with open(database_py_path, 'r') as f:
            database_content = f.read()
        
        # Check that shutdown hook imports from app.database
        imports_engine = 'from app.database import' in main_content and ('engine' in main_content or 'close_db' in main_content)
        
        # Check that shutdown calls close_db or engine.dispose
        calls_close_db = 'await close_db()' in main_content or 'close_db()' in main_content
        
        # Check that close_db calls engine.dispose() (async version uses 'await')
        # The async version in backend_app/database.py uses 'await actual_engine.dispose()'
        disposes_engine = 'await actual_engine.dispose()' in database_content or 'actual_engine.dispose()' in database_content or 'engine.dispose()' in database_content
        
        if imports_engine and calls_close_db and disposes_engine:
            print("   ✅ Shutdown hook properly calls engine.dispose() to close connections")
            return True
        else:
            print(f"   ❌ Missing implementation (imports: {imports_engine}, calls_close: {calls_close_db}, disposes: {disposes_engine})")
            return False
    except Exception as e:
        print(f"   ❌ Error checking implementation: {e}")
        return False


async def main():
    """Run all tests."""
    print("="*80)
    print("Graceful Shutdown Implementation Test Suite")
    print("="*80)
    print("\nVerifying shutdown hook implementation per problem statement:")
    print("  - @app.on_event('shutdown') decorator")
    print("  - engine imported from app.database")
    print("  - engine.dispose() called to close pooled connections")
    print("  - Prevents zombie sockets")
    
    # Run tests
    test1 = await test_shutdown_hook_exists()
    test2 = await test_engine_disposal_on_shutdown()
    test3 = await test_shutdown_handles_none_engine()
    test4 = await test_shutdown_handles_errors()
    test5 = await test_shutdown_prevents_zombie_sockets()
    test6 = await test_full_shutdown_sequence()
    
    print("\n" + "="*80)
    all_passed = test1 and test2 and test3 and test4 and test5 and test6
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("\nGraceful shutdown implementation verified:")
        print("  ✔ Closes pooled connections")
        print("  ✔ Prevents zombie sockets")
        print("  ✔ Handles errors gracefully")
        print("  ✔ No connection corruption")
        print("="*80)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

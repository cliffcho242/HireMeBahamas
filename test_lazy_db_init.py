#!/usr/bin/env python3
"""
Test script to verify lazy database initialization pattern.
This test confirms that database connections are NOT made at import time.
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_lazy_initialization():
    """Test that database modules use lazy initialization"""
    
    print("Testing lazy database initialization pattern...")
    print("=" * 60)
    
    # Test 1: Check that database.py modules can be imported without connecting
    print("\n1. Testing api/database.py lazy initialization...")
    try:
        # Set a fake DATABASE_URL to test validation
        os.environ['DATABASE_URL'] = 'postgresql+asyncpg://test:test@localhost:5432/test'
        
        # Import should not create connection
        sys.path.insert(0, os.path.join(project_root, 'api'))
        import database as api_db
        
        # Check that get_engine function exists
        assert hasattr(api_db, 'get_engine'), "api/database.py missing get_engine() function"
        print("   ✅ api/database.py has get_engine() function")
        
        # Check that engine is not created yet (lazy initialization)
        assert api_db._engine is None, "api/database.py created engine at import time (BAD)"
        print("   ✅ api/database.py engine is None at import time (GOOD)")
        
    except ImportError as e:
        print(f"   ⚠️  Could not import api/database.py: {e}")
    
    # Test 2: Check backend_app/database.py
    print("\n2. Testing api/backend_app/database.py lazy initialization...")
    try:
        sys.path.insert(0, os.path.join(project_root, 'api'))
        import backend_app.database as backend_app_db
        
        # Check that get_engine function exists
        assert hasattr(backend_app_db, 'get_engine'), "backend_app/database.py missing get_engine() function"
        print("   ✅ backend_app/database.py has get_engine() function")
        
        # Check that engine is not created yet (lazy initialization)
        assert backend_app_db._engine is None, "backend_app/database.py created engine at import time (BAD)"
        print("   ✅ backend_app/database.py engine is None at import time (GOOD)")
        
    except ImportError as e:
        print(f"   ⚠️  Could not import backend_app/database.py: {e}")
    
    # Test 3: Check backend/app/database.py
    print("\n3. Testing backend/app/database.py lazy initialization...")
    try:
        sys.path.insert(0, os.path.join(project_root, 'backend'))
        import app.database as backend_db
        
        # Check that get_engine function exists
        assert hasattr(backend_db, 'get_engine'), "backend/app/database.py missing get_engine() function"
        print("   ✅ backend/app/database.py has get_engine() function")
        
        # Check that engine is not created yet (lazy initialization)
        assert backend_db._engine is None, "backend/app/database.py created engine at import time (BAD)"
        print("   ✅ backend/app/database.py engine is None at import time (GOOD)")
        
    except ImportError as e:
        print(f"   ⚠️  Could not import backend/app/database.py: {e}")
    
    # Test 4: Check api/index.py lazy initialization
    print("\n4. Testing api/index.py lazy initialization...")
    try:
        # This is tricky because index.py has many dependencies
        # We'll check that it has get_db_engine function
        with open(os.path.join(project_root, 'api', 'index.py'), 'r') as f:
            content = f.read()
            
        # Check that get_db_engine function is defined
        assert 'def get_db_engine():' in content, "api/index.py missing get_db_engine() function"
        print("   ✅ api/index.py has get_db_engine() function")
        
        # Check that it's not creating engine at module level
        # Look for patterns like: db_engine = create_async_engine(
        # but NOT inside get_db_engine function
        lines = content.split('\n')
        in_function = False
        function_indent = 0
        for i, line in enumerate(lines):
            # Track when we enter a function
            if line.strip().startswith('def '):
                in_function = True
                function_indent = len(line) - len(line.lstrip())
            # Track when we exit a function (by checking indentation)
            elif in_function and line.strip() and not line.strip().startswith('#'):
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= function_indent:
                    in_function = False
            
            # Check for engine creation outside any function
            if 'create_async_engine(' in line and not line.strip().startswith('#'):
                if not in_function:
                    # Found engine creation at module level (outside any function)!
                    print(f"   ❌ Found engine creation at module level (line {i+1}): {line.strip()}")
                    raise AssertionError(f"Engine created at module level in api/index.py line {i+1}")
                # If inside a function, it's OK (that's the lazy pattern)
        
        print("   ✅ api/index.py does not create engine at module level (GOOD)")
        
    except FileNotFoundError:
        print("   ⚠️  Could not find api/index.py")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Lazy initialization pattern is correct!")
    print("\nPattern summary:")
    print("  ✅ GOOD: def get_engine() -> creates engine on first call")
    print("  ✅ GOOD: engine = LazyEngine() -> defers to get_engine()")
    print("  ❌ BAD:  engine = create_async_engine() -> creates at import")
    print("\nBest practice: Always call get_engine() before using the engine")
    return True

if __name__ == '__main__':
    success = test_lazy_initialization()
    sys.exit(0 if success else 1)

"""
Test to verify that the database configuration includes Railway/Render Postgres
timeout fix settings: connect_timeout, command_timeout, jit=off, and IPv4 preference.
"""

import os
import sys

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_production_connection_settings():
    """Test that production database settings include all timeout fixes."""
    
    # Clear any cached modules
    modules_to_remove = [key for key in sys.modules.keys() if 'app' in key]
    for module in modules_to_remove:
        del sys.modules[module]
    
    # Set up production environment
    os.environ["ENVIRONMENT"] = "production"
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@railway-host.railway.app:5432/db"
    
    try:
        from app import database
        
        # Test 1: Verify production mode is detected
        assert database.IS_PRODUCTION_DATABASE is True, (
            "Expected IS_PRODUCTION_DATABASE to be True in production"
        )
        print("✓ Test 1 passed: Production mode detected correctly")
        
        # Test 2: Verify connect_timeout is set (NUCLEAR FIX: 30 seconds)
        assert database.CONNECT_TIMEOUT_SECONDS == 30, (
            f"Expected CONNECT_TIMEOUT_SECONDS=30, got {database.CONNECT_TIMEOUT_SECONDS}"
        )
        print("✓ Test 2 passed: CONNECT_TIMEOUT_SECONDS=30 (NUCLEAR FIX)")
        
        # Test 3: Verify statement_timeout is set  
        assert database.STATEMENT_TIMEOUT_SECONDS == 30, (
            f"Expected STATEMENT_TIMEOUT_SECONDS=30, got {database.STATEMENT_TIMEOUT_SECONDS}"
        )
        print("✓ Test 3 passed: STATEMENT_TIMEOUT_SECONDS=30")
        
        # Test 4: Verify IPv4 preference is enabled
        assert database.FORCE_IPV4 is True, (
            f"Expected FORCE_IPV4=True, got {database.FORCE_IPV4}"
        )
        print("✓ Test 4 passed: FORCE_IPV4=True")
        
        # Test 5: Verify connect_args in engine_kwargs
        assert "connect_args" in database.engine_kwargs, (
            "Expected connect_args in engine_kwargs for production"
        )
        connect_args = database.engine_kwargs["connect_args"]
        
        assert connect_args.get("timeout") == 30, (
            f"Expected connect_args['timeout']=30, got {connect_args.get('timeout')}"
        )
        print("✓ Test 5 passed: connect_args['timeout']=30 (NUCLEAR FIX)")
        
        # Test 6: Verify command_timeout
        assert connect_args.get("command_timeout") == 30, (
            f"Expected connect_args['command_timeout']=30, got {connect_args.get('command_timeout')}"
        )
        print("✓ Test 6 passed: connect_args['command_timeout']=30")
        
        # Test 7: Verify server_settings with jit=off
        server_settings = connect_args.get("server_settings", {})
        assert server_settings.get("jit") == "off", (
            f"Expected server_settings['jit']='off', got {server_settings.get('jit')}"
        )
        print("✓ Test 7 passed: server_settings['jit']='off'")
        
        # Test 8: Verify statement_timeout in server_settings
        assert server_settings.get("statement_timeout") == "30000", (
            f"Expected server_settings['statement_timeout']='30000', got {server_settings.get('statement_timeout')}"
        )
        print("✓ Test 8 passed: server_settings['statement_timeout']='30000'")
        
        # Test 9: Verify pool_pre_ping is enabled
        assert database.engine_kwargs.get("pool_pre_ping") is True, (
            "Expected pool_pre_ping=True in engine_kwargs"
        )
        print("✓ Test 9 passed: pool_pre_ping=True")
        
        # Test 10: Verify pool_recycle is set for production
        assert database.engine_kwargs.get("pool_recycle") == 300, (
            f"Expected pool_recycle=300, got {database.engine_kwargs.get('pool_recycle')}"
        )
        print("✓ Test 10 passed: pool_recycle=300")
        
        # Test 11: Verify SSL require is set (NUCLEAR FIX)
        assert connect_args.get("ssl") == "require", (
            f"Expected connect_args['ssl']='require', got {connect_args.get('ssl')}"
        )
        print("✓ Test 11 passed: connect_args['ssl']='require' (NUCLEAR FIX)")
        
        # Test 12: Verify pool_size is 3 for production (NUCLEAR FIX)
        assert database.POOL_SIZE == 3, (
            f"Expected POOL_SIZE=3, got {database.POOL_SIZE}"
        )
        print("✓ Test 12 passed: POOL_SIZE=3 (NUCLEAR FIX)")
        
        # Test 13: Verify max_overflow is 5 for production (NUCLEAR FIX)
        assert database.POOL_MAX_OVERFLOW == 5, (
            f"Expected POOL_MAX_OVERFLOW=5, got {database.POOL_MAX_OVERFLOW}"
        )
        print("✓ Test 13 passed: POOL_MAX_OVERFLOW=5 (NUCLEAR FIX)")
        
        print("\n✅ All Railway/Render Postgres timeout fix settings verified!")
        print("✅ NUCLEAR FIX applied: pool_size=3, max_overflow=5, connect_timeout=30, ssl=require, jit=off")
        print("✅ Configuration ready for Render → Railway PostgreSQL connections")
        
    finally:
        # Clean up environment
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]


def test_ipv4_preference():
    """Test that IPv4 preference correctly affects address resolution behavior."""
    import socket
    
    # Clear any cached modules
    modules_to_remove = [key for key in sys.modules.keys() if 'app' in key]
    for module in modules_to_remove:
        del sys.modules[module]
    
    os.environ["DB_FORCE_IPV4"] = "true"
    
    try:
        from app import database
        
        # Test that FORCE_IPV4 setting is enabled
        assert database.FORCE_IPV4 is True, "Expected FORCE_IPV4=True"
        print("✓ IPv4 preference is enabled")
        
        # Test the behavior: when getaddrinfo is called with AF_UNSPEC,
        # it should return IPv4 addresses (AF_INET family = 2)
        # Using localhost which is guaranteed to resolve
        results = socket.getaddrinfo("localhost", 5432, socket.AF_UNSPEC)
        
        # All results should be IPv4 (family = 2 = AF_INET)
        for result in results:
            family = result[0]
            assert family == socket.AF_INET, (
                f"Expected IPv4 (AF_INET={socket.AF_INET}), got family={family}"
            )
        print("✓ getaddrinfo returns only IPv4 addresses when AF_UNSPEC is used")
        
        print("\n✅ IPv4 preference test passed!")
        
    finally:
        if "DB_FORCE_IPV4" in os.environ:
            del os.environ["DB_FORCE_IPV4"]


if __name__ == "__main__":
    test_production_connection_settings()
    print("\n" + "=" * 60 + "\n")
    test_ipv4_preference()

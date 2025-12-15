"""
Test to verify database timeout configuration changes
"""
import os
import sys

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
api_dir = os.path.join(os.path.dirname(__file__), 'api')
sys.path.insert(0, backend_dir)
sys.path.insert(0, api_dir)


def test_backend_database_config():
    """Test backend/app/database.py configuration"""
    from backend.app import database
    
    # Verify CONNECT_TIMEOUT is set to 5 seconds (default)
    assert database.CONNECT_TIMEOUT == 5, f"Expected CONNECT_TIMEOUT=5, got {database.CONNECT_TIMEOUT}"
    
    # Verify POOL_SIZE is set to 5 (default)
    assert database.POOL_SIZE == 5, f"Expected POOL_SIZE=5, got {database.POOL_SIZE}"
    
    # Verify MAX_OVERFLOW is set to 10 (default)
    assert database.MAX_OVERFLOW == 10, f"Expected MAX_OVERFLOW=10, got {database.MAX_OVERFLOW}"
    
    print("✓ backend/app/database.py configuration verified")
    print(f"  - CONNECT_TIMEOUT: {database.CONNECT_TIMEOUT}s")
    print(f"  - POOL_SIZE: {database.POOL_SIZE}")
    print(f"  - MAX_OVERFLOW: {database.MAX_OVERFLOW}")


def test_api_backend_app_database_config():
    """Test api/backend_app/database.py configuration"""
    from backend_app import database
    
    # Verify CONNECT_TIMEOUT is set to 5 seconds (default)
    assert database.CONNECT_TIMEOUT == 5, f"Expected CONNECT_TIMEOUT=5, got {database.CONNECT_TIMEOUT}"
    
    # Verify POOL_SIZE is set to 5 (default)
    assert database.POOL_SIZE == 5, f"Expected POOL_SIZE=5, got {database.POOL_SIZE}"
    
    # Verify MAX_OVERFLOW is set to 10 (default)
    assert database.MAX_OVERFLOW == 10, f"Expected MAX_OVERFLOW=10, got {database.MAX_OVERFLOW}"
    
    print("✓ api/backend_app/database.py configuration verified")
    print(f"  - CONNECT_TIMEOUT: {database.CONNECT_TIMEOUT}s")
    print(f"  - POOL_SIZE: {database.POOL_SIZE}")
    print(f"  - MAX_OVERFLOW: {database.MAX_OVERFLOW}")


def test_gunicorn_config():
    """Test gunicorn.conf.py configuration"""
    # Import gunicorn config
    gunicorn_conf_path = os.path.join(os.path.dirname(__file__), 'gunicorn.conf.py')
    
    # Read and execute the config file to get variables
    config_vars = {}
    with open(gunicorn_conf_path, 'r') as f:
        exec(f.read(), config_vars)
    
    # Verify workers is set to 2 (default)
    workers = config_vars.get('workers', 0)
    assert workers == 2, f"Expected workers=2, got {workers}"
    
    # Verify threads is set to 4 (default)
    threads = config_vars.get('threads', 0)
    assert threads == 4, f"Expected threads=4, got {threads}"
    
    # Verify timeout is set to 60 (default)
    timeout = config_vars.get('timeout', 0)
    assert timeout == 60, f"Expected timeout=60, got {timeout}"
    
    # Verify keepalive is set to 5 (default)
    keepalive = config_vars.get('keepalive', 0)
    assert keepalive == 5, f"Expected keepalive=5, got {keepalive}"
    
    print("✓ gunicorn.conf.py configuration verified")
    print(f"  - workers: {workers}")
    print(f"  - threads: {threads}")
    print(f"  - timeout: {timeout}s")
    print(f"  - keepalive: {keepalive}s")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Database and Gunicorn Configuration Changes")
    print("=" * 60)
    print()
    
    try:
        test_backend_database_config()
        print()
    except Exception as e:
        print(f"✗ backend/app/database.py test failed: {e}")
        print()
    
    try:
        test_api_backend_app_database_config()
        print()
    except Exception as e:
        print(f"✗ api/backend_app/database.py test failed: {e}")
        print()
    
    try:
        test_gunicorn_config()
        print()
    except Exception as e:
        print(f"✗ gunicorn.conf.py test failed: {e}")
        print()
    
    print("=" * 60)
    print("All configuration tests completed!")
    print("=" * 60)

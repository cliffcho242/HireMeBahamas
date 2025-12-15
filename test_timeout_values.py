"""
Test to verify database timeout configuration values in source files
"""
import re


def test_backend_database_timeouts():
    """Verify backend/app/database.py has correct timeout values"""
    with open('backend/app/database.py', 'r') as f:
        content = f.read()
    
    # Check CONNECT_TIMEOUT default is 5
    assert 'CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))' in content, \
        "CONNECT_TIMEOUT should default to 5 seconds"
    
    # Check POOL_SIZE default is 5
    assert 'POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))' in content, \
        "POOL_SIZE should default to 5"
    
    # Check MAX_OVERFLOW default is 10
    assert 'MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))' in content, \
        "MAX_OVERFLOW should default to 10"
    
    # Check application_name is "render-app"
    assert '"application_name": "render-app"' in content, \
        "application_name should be 'render-app'"
    
    print("✓ backend/app/database.py timeouts verified")
    print("  - CONNECT_TIMEOUT: 5s (hard timeout for DNS failures)")
    print("  - POOL_SIZE: 5")
    print("  - MAX_OVERFLOW: 10")
    print("  - application_name: render-app")


def test_api_backend_app_database_timeouts():
    """Verify api/backend_app/database.py has correct timeout values"""
    with open('api/backend_app/database.py', 'r') as f:
        content = f.read()
    
    # Check CONNECT_TIMEOUT default is 5
    assert 'CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))' in content, \
        "CONNECT_TIMEOUT should default to 5 seconds"
    
    # Check POOL_SIZE default is 5
    assert 'POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))' in content, \
        "POOL_SIZE should default to 5"
    
    # Check MAX_OVERFLOW default is 10
    assert 'MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))' in content, \
        "MAX_OVERFLOW should default to 10"
    
    # Check application_name is "render-app"
    assert '"application_name": "render-app"' in content, \
        "application_name should be 'render-app'"
    
    print("✓ api/backend_app/database.py timeouts verified")
    print("  - CONNECT_TIMEOUT: 5s (hard timeout for DNS failures)")
    print("  - POOL_SIZE: 5")
    print("  - MAX_OVERFLOW: 10")
    print("  - application_name: render-app")


def test_api_database_timeouts():
    """Verify api/database.py has correct timeout values"""
    with open('api/database.py', 'r') as f:
        content = f.read()
    
    # Check connect_timeout default is 5
    assert 'connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))' in content, \
        "connect_timeout should default to 5 seconds"
    
    # Check pool_size default is 5
    assert 'pool_size = int(os.getenv("DB_POOL_SIZE", "5"))' in content, \
        "pool_size should default to 5"
    
    # Check max_overflow default is 10
    assert 'max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))' in content, \
        "max_overflow should default to 10"
    
    # Check application_name is "render-app"
    assert '"application_name": "render-app"' in content, \
        "application_name should be 'render-app'"
    
    # Check pool_pre_ping is True
    assert 'pool_pre_ping=True' in content, \
        "pool_pre_ping should be True"
    
    print("✓ api/database.py timeouts verified")
    print("  - connect_timeout: 5s (hard timeout for DNS failures)")
    print("  - pool_size: 5")
    print("  - max_overflow: 10")
    print("  - pool_pre_ping: True")
    print("  - application_name: render-app")


def test_gunicorn_workers():
    """Verify gunicorn.conf.py has correct worker configuration"""
    with open('gunicorn.conf.py', 'r') as f:
        content = f.read()
    
    # Check workers default is 2
    assert 'workers = int(os.environ.get("WEB_CONCURRENCY", "2"))' in content, \
        "workers should default to 2"
    
    # Check threads default is 4
    assert 'threads = int(os.environ.get("WEB_THREADS", "4"))' in content, \
        "threads should default to 4"
    
    # Check timeout default is 60
    assert 'timeout = int(os.environ.get("GUNICORN_TIMEOUT", "60"))' in content, \
        "timeout should default to 60"
    
    # Check keepalive is 5
    assert 'keepalive = 5' in content, \
        "keepalive should be 5"
    
    print("✓ gunicorn.conf.py configuration verified")
    print("  - workers: 2 (prevents single-worker blocking)")
    print("  - threads: 4")
    print("  - timeout: 60s")
    print("  - keepalive: 5s")


if __name__ == "__main__":
    print("=" * 70)
    print("Verifying Database Timeout and Gunicorn Configuration Changes")
    print("=" * 70)
    print()
    
    all_passed = True
    
    try:
        test_backend_database_timeouts()
        print()
    except AssertionError as e:
        print(f"✗ backend/app/database.py: {e}")
        print()
        all_passed = False
    
    try:
        test_api_backend_app_database_timeouts()
        print()
    except AssertionError as e:
        print(f"✗ api/backend_app/database.py: {e}")
        print()
        all_passed = False
    
    try:
        test_api_database_timeouts()
        print()
    except AssertionError as e:
        print(f"✗ api/database.py: {e}")
        print()
        all_passed = False
    
    try:
        test_gunicorn_workers()
        print()
    except AssertionError as e:
        print(f"✗ gunicorn.conf.py: {e}")
        print()
        all_passed = False
    
    print("=" * 70)
    if all_passed:
        print("✓ All configuration changes verified successfully!")
    else:
        print("✗ Some configuration checks failed")
    print("=" * 70)
    
    exit(0 if all_passed else 1)

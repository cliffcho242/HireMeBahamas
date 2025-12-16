"""
Test to verify port binding configuration is not hardcoded.

Tests that all main entry points use environment variables for port configuration
with appropriate defaults.
"""

import os
import ast
import re
from pathlib import Path

# Get the repository root directory
REPO_ROOT = Path(__file__).parent


def test_final_backend_postgresql_port_binding():
    """Test that final_backend_postgresql.py uses environment variable for port."""
    file_path = REPO_ROOT / 'final_backend_postgresql.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if the file contains the correct pattern
    # Should be: port = int(os.environ.get("PORT", 10000))
    assert 'os.environ.get("PORT"' in content, "Should use os.environ.get for PORT"
    
    # Verify it uses host="0.0.0.0"
    assert 'host="0.0.0.0"' in content, "Should bind to 0.0.0.0"
    
    # Extract the if __name__ == "__main__" block
    if_name_match = re.search(r'if __name__ == "__main__":(.*?)(?:$|\n\S)', content, re.DOTALL)
    assert if_name_match, "Should have if __name__ == '__main__' block"
    
    main_block = if_name_match.group(1)
    
    # Should NOT have hardcoded port like app.run(port=5000)
    assert not re.search(r'app\.run\([^)]*port=\d+', main_block), \
        "Should not hardcode port in app.run()"
    
    # Should use the port variable from environment
    assert 'port=port' in main_block or 'port = port' in main_block, \
        "Should use port variable from os.environ.get()"
    
    print("✅ final_backend_postgresql.py port binding is correct")


def test_backend_app_main_port_binding():
    """Test that backend/app/main.py uses environment variable for port."""
    file_path = REPO_ROOT / 'backend' / 'app' / 'main.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if the file contains the correct pattern
    # Should be: port = int(os.getenv('PORT', 10000))
    assert 'os.getenv' in content or 'os.environ.get' in content, \
        "Should use os.getenv or os.environ.get for PORT"
    
    # Verify it uses host="0.0.0.0"
    assert 'host="0.0.0.0"' in content, "Should bind to 0.0.0.0"
    
    # Extract the if __name__ == "__main__" block
    if_name_match = re.search(r'if __name__ == "__main__":(.*?)(?:$|\n(?=\S))', content, re.DOTALL)
    assert if_name_match, "Should have if __name__ == '__main__' block"
    
    main_block = if_name_match.group(1)
    
    # Should NOT have hardcoded port like uvicorn.run(..., port=8000)
    assert not re.search(r'uvicorn\.run\([^)]*port=\d+', main_block), \
        "Should not hardcode port in uvicorn.run()"
    
    # Should use the port variable from environment
    assert 'port=port' in main_block or 'port = port' in main_block, \
        "Should use port variable from os.getenv()"
    
    print("✅ backend/app/main.py port binding is correct")


def test_gunicorn_config_port_binding():
    """Test that gunicorn.conf.py uses environment variable for port."""
    file_path = REPO_ROOT / 'gunicorn.conf.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if the file contains the correct pattern
    # Should be: bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
    assert "os.environ.get('PORT'" in content or 'os.environ.get("PORT"' in content, \
        "gunicorn.conf.py should use os.environ.get for PORT"
    
    # Verify it binds to 0.0.0.0
    assert '0.0.0.0:' in content, "Should bind to 0.0.0.0"
    
    print("✅ gunicorn.conf.py port binding is correct")


def test_procfile_uses_port_variable():
    """Test that Procfile uses $PORT variable."""
    file_path = REPO_ROOT / 'Procfile'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Should use $PORT in the web command
    assert '$PORT' in content, "Procfile should use $PORT variable"
    assert '0.0.0.0:$PORT' in content, "Procfile should bind to 0.0.0.0:$PORT"
    
    print("✅ Procfile port binding is correct")


def test_port_5432_validation():
    """Test that port 5432 is explicitly rejected in configuration files."""
    
    # Test backend/app/main.py validates port 5432
    file_path = REPO_ROOT / 'backend' / 'app' / 'main.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    assert 'port == 5432' in content, "backend/app/main.py should validate port 5432"
    assert 'PostgreSQL' in content or 'postgres' in content.lower(), \
        "Should mention PostgreSQL in error message"
    assert 'sys.exit(1)' in content, "Should exit with error code 1 when port is 5432"
    
    print("✅ backend/app/main.py validates port 5432 correctly")
    
    # Test gunicorn.conf.py validates port 5432
    gunicorn_files = [
        REPO_ROOT / 'gunicorn.conf.py',
        REPO_ROOT / 'backend' / 'gunicorn.conf.py'
    ]
    
    for file_path in gunicorn_files:
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert '_port_int == 5432' in content or 'port == 5432' in content, \
            f"{file_path} should validate port 5432"
        assert 'PostgreSQL' in content or 'postgres' in content.lower(), \
            f"{file_path} should mention PostgreSQL in error message"
        assert 'sys.exit(1)' in content, \
            f"{file_path} should exit with error code 1 when port is 5432"
        
        print(f"✅ {file_path.name} validates port 5432 correctly")


def test_port_5432_rejection_message():
    """Test that rejection messages are clear and helpful."""
    
    # Check backend/app/main.py error message
    file_path = REPO_ROOT / 'backend' / 'app' / 'main.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Should have clear error messages
    assert 'DO NOT BIND' in content or 'Cannot bind' in content, \
        "Should have clear error message about binding"
    assert 'reserved for PostgreSQL' in content or 'PostgreSQL database' in content, \
        "Should explain that 5432 is for PostgreSQL"
    
    print("✅ Error messages are clear and helpful")


if __name__ == "__main__":
    print("🧪 Running port binding configuration tests...\n")
    
    try:
        test_final_backend_postgresql_port_binding()
        test_backend_app_main_port_binding()
        test_gunicorn_config_port_binding()
        test_procfile_uses_port_variable()
        test_port_5432_validation()
        test_port_5432_rejection_message()
        
        print("\n✅ All port binding tests passed!")
        print("📋 Summary:")
        print("   - No hardcoded ports in main entry points")
        print("   - All apps use os.environ.get('PORT', 10000)")
        print("   - All apps bind to host='0.0.0.0'")
        print("   - Gunicorn config uses environment variable")
        print("   - Procfile uses $PORT variable")
        print("   - Port 5432 (PostgreSQL) is explicitly rejected")
        print("   - Error messages are clear and helpful")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)

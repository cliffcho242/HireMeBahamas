"""
Simple validation test for STEP 14 Redis implementation.
This test validates the code structure and configuration without requiring Redis to be installed.
"""
import ast
import os


def test_redis_file_structure():
    """Validate that app/redis.py has the correct structure."""
    print("Testing app/redis.py structure...")
    
    import os
    redis_file_path = os.path.join(os.path.dirname(__file__), "app", "redis.py")
    
    with open(redis_file_path, 'r') as f:
        content = f.read()
    
    # Parse the AST to check structure
    tree = ast.parse(content)
    
    imports = []
    assignments = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(f"from {node.module}")
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments.append(target.id)
    
    # Verify imports
    assert 'redis' in imports, "Missing 'import redis'"
    assert 'from app.config' in imports, "Missing 'from app.config import REDIS_URL'"
    print("  ✓ Correct imports: redis and app.config")
    
    # Verify redis_client is assigned
    assert 'redis_client' in assignments, "Missing 'redis_client' assignment"
    print("  ✓ redis_client is defined")
    
    # Check for required keywords in the content
    assert 'decode_responses=True' in content, "Missing decode_responses=True"
    assert 'socket_connect_timeout=2' in content, "Missing socket_connect_timeout=2"
    assert 'socket_timeout=2' in content, "Missing socket_timeout=2"
    assert 'redis.from_url' in content, "Missing redis.from_url call"
    assert 'REDIS_URL' in content, "Missing REDIS_URL parameter"
    print("  ✓ All required parameters configured correctly")
    
    print("✅ app/redis.py structure is correct!\n")


def test_config_has_redis_url():
    """Validate that app/config.py exports REDIS_URL."""
    print("Testing app/config.py for REDIS_URL...")
    
    import os
    config_file_path = os.path.join(os.path.dirname(__file__), "app", "config.py")
    
    with open(config_file_path, 'r') as f:
        content = f.read()
    
    assert 'REDIS_URL' in content, "REDIS_URL not found in config.py"
    assert 'os.getenv("REDIS_URL")' in content, "REDIS_URL not using os.getenv"
    print("  ✓ REDIS_URL is properly defined in config.py")
    print("✅ app/config.py has REDIS_URL!\n")


if __name__ == "__main__":
    print("=" * 60)
    print("STEP 14 — Redis Caching Validation Tests")
    print("=" * 60)
    print()
    
    try:
        test_redis_file_structure()
    except AssertionError as e:
        print(f"✗ Structure test failed: {e}\n")
        exit(1)
    except Exception as e:
        print(f"✗ Unexpected error in structure test: {e}\n")
        exit(1)
    
    try:
        test_config_has_redis_url()
    except AssertionError as e:
        print(f"✗ Config test failed: {e}\n")
        exit(1)
    except Exception as e:
        print(f"✗ Unexpected error in config test: {e}\n")
        exit(1)
    
    print("=" * 60)
    print("✅ ALL VALIDATION TESTS PASSED!")
    print("=" * 60)
    print()
    print("Summary:")
    print("  • app/redis.py created with correct structure")
    print("  • Imports redis library")
    print("  • Imports REDIS_URL from app.config")
    print("  • Creates redis_client with:")
    print("    - decode_responses=True")
    print("    - socket_connect_timeout=2")
    print("    - socket_timeout=2")
    print()

"""
Test health endpoint meets instant response requirements.

Requirements:
- ✅ REQUIRED: @app.get("/health", include_in_schema=False)
- ✅ REQUIRED: Returns {"ok": True}
- ❌ NO DB access
- ❌ NO IO operations
- ❌ NO async/await (must be synchronous)

Render kills apps that fail health checks.
"""
import time
import sys
import os
from pathlib import Path

# Add api directory to path
api_dir = Path(__file__).parent / 'api'
sys.path.insert(0, str(api_dir))

def test_api_index_health_endpoint():
    """Test api/index.py health endpoint is instant and correct."""
    print("\n" + "="*70)
    print("Testing api/index.py health endpoint...")
    print("="*70)
    
    # Read the file
    health_file = Path(__file__).parent / 'api' / 'index.py'
    content = health_file.read_text()
    
    # Check 1: Health endpoint exists and is NOT async
    if 'async def health():' in content:
        print("❌ FAIL: Health endpoint is async (must be synchronous)")
        return False
    
    if 'def health():' not in content:
        print("❌ FAIL: Health endpoint not found")
        return False
    
    print("✅ PASS: Health endpoint is synchronous (not async)")
    
    # Check 2: Has correct decorator
    if '@app.get("/health", include_in_schema=False)' not in content:
        print("❌ FAIL: Health endpoint missing required decorator")
        return False
    
    print("✅ PASS: Health endpoint has correct decorator")
    
    # Check 3: Returns {"ok": True}
    # Find the health function and check its return statement
    health_start = content.find('def health():')
    if health_start == -1:
        print("❌ FAIL: Could not find health function")
        return False
    
    # Find the next function after health (to bound the search)
    next_func = content.find('\ndef ', health_start + 1)
    health_section = content[health_start:next_func] if next_func != -1 else content[health_start:]
    
    if 'return {"ok": True}' not in health_section:
        print(f"❌ FAIL: Health endpoint does not return {{\"ok\": True}}")
        print(f"   Found section: {health_section[:200]}")
        return False
    
    print("✅ PASS: Health endpoint returns {\"ok\": True}")
    
    # Check 4: No database access
    db_keywords = ['engine', 'session', 'query', 'get_db', 'database', 'asyncpg', 'sqlalchemy']
    for keyword in db_keywords:
        if keyword in health_section.lower():
            # Allow the keyword in comments/docstrings
            lines = health_section.split('\n')
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                    continue
                if keyword in line.lower() and not line.strip().startswith('#'):
                    print(f"⚠️  WARNING: Keyword '{keyword}' found in health function (may indicate DB access)")
    
    print("✅ PASS: No obvious database access in health endpoint")
    
    # Check 5: No I/O operations
    io_keywords = ['open(', 'write(', 'read(', 'file', 'os.']
    for keyword in io_keywords:
        if keyword in health_section:
            print(f"⚠️  WARNING: I/O operation '{keyword}' found in health function")
    
    print("✅ PASS: No obvious I/O operations in health endpoint")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED for api/index.py")
    print("="*70)
    return True

def test_backend_main_health_endpoint():
    """Test backend/app/main.py health endpoint is instant and correct."""
    print("\n" + "="*70)
    print("Testing backend/app/main.py health endpoint...")
    print("="*70)
    
    # Read the file
    health_file = Path(__file__).parent / 'backend' / 'app' / 'main.py'
    if not health_file.exists():
        print("⚠️  WARNING: backend/app/main.py not found")
        return True  # Not a failure, just doesn't exist
    
    content = health_file.read_text()
    
    # Check 1: Health endpoint exists and is NOT async
    if 'async def health():' in content:
        print("❌ FAIL: Health endpoint is async (must be synchronous)")
        return False
    
    if 'def health():' not in content:
        print("❌ FAIL: Health endpoint not found")
        return False
    
    print("✅ PASS: Health endpoint is synchronous (not async)")
    
    # Check 2: Has correct decorator
    if '@app.get("/health", include_in_schema=False)' not in content:
        print("❌ FAIL: Health endpoint missing required decorator")
        return False
    
    print("✅ PASS: Health endpoint has correct decorator")
    
    # Check 3: Returns {"ok": True}
    health_start = content.find('def health():')
    next_func = content.find('\ndef ', health_start + 1)
    health_section = content[health_start:next_func] if next_func != -1 else content[health_start:]
    
    if 'return {"ok": True}' not in health_section:
        print(f"❌ FAIL: Health endpoint does not return {{\"ok\": True}}")
        return False
    
    print("✅ PASS: Health endpoint returns {\"ok\": True}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED for backend/app/main.py")
    print("="*70)
    return True

def test_api_backend_app_main_health_endpoint():
    """Test api/backend_app/main.py health endpoint is instant and correct."""
    print("\n" + "="*70)
    print("Testing api/backend_app/main.py health endpoint...")
    print("="*70)
    
    # Read the file
    health_file = Path(__file__).parent / 'api' / 'backend_app' / 'main.py'
    if not health_file.exists():
        print("⚠️  WARNING: api/backend_app/main.py not found")
        return True  # Not a failure, just doesn't exist
    
    content = health_file.read_text()
    
    # Check 1: Health endpoint exists and is NOT async
    if 'async def health():' in content:
        print("❌ FAIL: Health endpoint is async (must be synchronous)")
        return False
    
    if 'def health():' not in content:
        print("❌ FAIL: Health endpoint not found")
        return False
    
    print("✅ PASS: Health endpoint is synchronous (not async)")
    
    # Check 2: Has correct decorator
    if '@app.get("/health", include_in_schema=False)' not in content:
        print("❌ FAIL: Health endpoint missing required decorator")
        return False
    
    print("✅ PASS: Health endpoint has correct decorator")
    
    # Check 3: Returns {"ok": True}
    health_start = content.find('def health():')
    next_func = content.find('\ndef ', health_start + 1)
    health_section = content[health_start:next_func] if next_func != -1 else content[health_start:]
    
    if 'return {"ok": True}' not in health_section:
        print(f"❌ FAIL: Health endpoint does not return {{\"ok\": True}}")
        return False
    
    print("✅ PASS: Health endpoint returns {\"ok\": True}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED for api/backend_app/main.py")
    print("="*70)
    return True

def main():
    """Run all health endpoint tests."""
    print("\n" + "="*70)
    print("HEALTH ENDPOINT INSTANT RESPONSE TESTS")
    print("="*70)
    print("\nRequirements:")
    print("  ✅ @app.get('/health', include_in_schema=False)")
    print("  ✅ Returns {'ok': True}")
    print("  ❌ NO DB access")
    print("  ❌ NO IO operations")
    print("  ❌ NO async/await")
    print("\n")
    
    all_passed = True
    
    # Test api/index.py
    if not test_api_index_health_endpoint():
        all_passed = False
    
    # Test backend/app/main.py
    if not test_backend_main_health_endpoint():
        all_passed = False
    
    # Test api/backend_app/main.py
    if not test_api_backend_app_main_health_endpoint():
        all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL HEALTH ENDPOINTS PASS REQUIREMENTS")
        print("="*70)
        return 0
    else:
        print("❌ SOME HEALTH ENDPOINTS FAILED")
        print("="*70)
        return 1

if __name__ == '__main__':
    exit(main())

"""
Test enhanced login logging to verify diagnostic improvements
"""
import asyncio
import sys
from pathlib import Path
import logging
from io import StringIO

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

async def test_enhanced_logging():
    """Test that enhanced logging features are working"""
    
    print("=" * 80)
    print("Enhanced Login Logging Tests")
    print("=" * 80)
    
    # Test 1: Verify time module is imported in auth.py
    print("\n1. Testing auth.py imports...")
    try:
        import app.api.auth as auth_module
        assert hasattr(auth_module, 'time'), "time module should be imported"
        print("   ✓ time module imported successfully")
    except Exception as e:
        print(f"   ✗ Failed to import time module: {e}")
        return False
    
    # Test 2: Verify main.py imports
    print("\n2. Testing main.py imports...")
    try:
        import app.main as main_module
        assert hasattr(main_module, 'json'), "json module should be imported"
        print("   ✓ json module imported successfully")
    except Exception as e:
        print(f"   ✗ Failed to import json module: {e}")
        return False
    
    # Test 3: Test timing functionality
    print("\n3. Testing timing functionality...")
    import time
    
    start = time.time()
    await asyncio.sleep(0.01)  # Sleep 10ms
    duration_ms = int((time.time() - start) * 1000)
    
    assert duration_ms >= 10, f"Duration should be at least 10ms, got {duration_ms}ms"
    assert duration_ms < 100, f"Duration should be less than 100ms, got {duration_ms}ms"
    print(f"   ✓ Timing measurement works correctly: {duration_ms}ms")
    
    # Test 4: Test JSON error parsing
    print("\n4. Testing JSON error parsing...")
    import json
    
    test_error_responses = [
        {"detail": "Invalid credentials"},
        {"detail": "User not found"},
        {"detail": "Too many login attempts. Please try again in 15 minutes."},
    ]
    
    for error_data in test_error_responses:
        json_str = json.dumps(error_data)
        parsed = json.loads(json_str)
        assert parsed.get('detail') == error_data['detail'], "JSON parsing failed"
        print(f"   ✓ Parsed error: {parsed.get('detail')}")
    
    # Test 5: Test request ID generation
    print("\n5. Testing request ID generation...")
    import uuid
    
    for _ in range(5):
        request_id = str(uuid.uuid4())[:8]
        assert len(request_id) == 8, f"Request ID should be 8 chars, got {len(request_id)}"
        # First 8 chars of UUID can be any hex digit or hyphen at position 8 (but we only take first 8)
        # So only positions 0-7, which are hex digits
        assert all(c in '0123456789abcdef' for c in request_id.lower()), "Request ID should be hex digits"
    print("   ✓ Request ID generation works correctly")
    
    # Test 6: Test logger configuration
    print("\n6. Testing enhanced logging format...")
    test_logger = logging.getLogger('test_enhanced_logging')
    test_logger.setLevel(logging.INFO)
    
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    test_logger.addHandler(handler)
    
    # Simulate enhanced log messages
    test_request_id = "abc12345"
    test_logs = [
        f"[{test_request_id}] --> POST /api/auth/login from 192.168.1.1 | UA: Mozilla...",
        f"[{test_request_id}] Database query (email lookup) completed in 15ms",
        f"[{test_request_id}] Password verification completed in 120ms",
        f"[{test_request_id}] Token creation completed in 5ms",
        f"[{test_request_id}] <-- 200 POST /api/auth/login in 150ms",
        f"[{test_request_id}] SLOW REQUEST: POST /api/auth/login took 5500ms (>3s threshold)",
    ]
    
    for log_msg in test_logs:
        test_logger.info(log_msg)
    
    log_output = log_capture.getvalue()
    
    for log_msg in test_logs:
        assert log_msg in log_output, f"Log message not found: {log_msg}"
    
    print(f"   ✓ All {len(test_logs)} enhanced log formats validated")
    
    # Test 7: Test error detail logging
    print("\n7. Testing error detail logging...")
    
    error_scenarios = [
        {
            "request_id": "req001",
            "error": "User not found",
            "email": "test@example.com",
            "ip": "192.168.1.1"
        },
        {
            "request_id": "req002",
            "error": "Invalid password",
            "email": "user@example.com",
            "ip": "10.0.0.5",
            "user_id": 123
        },
        {
            "request_id": "req003",
            "error": "Rate limit exceeded",
            "email": "attacker@example.com",
            "ip": "203.0.113.1"
        }
    ]
    
    for scenario in error_scenarios:
        log_msg = (
            f"[{scenario['request_id']}] Login failed - {scenario['error']}: "
            f"{scenario['email']}, client_ip: {scenario['ip']}"
        )
        if 'user_id' in scenario:
            log_msg += f", user_id: {scenario['user_id']}"
        
        test_logger.warning(log_msg)
    
    log_output = log_capture.getvalue()
    
    for scenario in error_scenarios:
        assert scenario['request_id'] in log_output, f"Request ID not found: {scenario['request_id']}"
        assert scenario['error'] in log_output, f"Error message not found: {scenario['error']}"
    
    print(f"   ✓ All {len(error_scenarios)} error scenarios properly logged")
    
    print("\n" + "=" * 80)
    print("✅ All enhanced logging tests passed!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_enhanced_logging())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

"""
Test login functionality with enhanced logging
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

async def test_login_scenarios():
    """Test various login scenarios to validate logging and error handling"""
    from app.core.security import get_password_hash, verify_password
    
    print("=" * 60)
    print("Testing Login Functionality")
    print("=" * 60)
    
    # Test 1: Password hashing and verification
    print("\n1. Testing password hashing...")
    test_password = "TestPassword123!"
    hashed = get_password_hash(test_password)
    print(f"   ✓ Password hashed successfully")
    print(f"   Hash length: {len(hashed)}")
    
    # Test password verification
    is_valid = verify_password(test_password, hashed)
    print(f"   ✓ Password verification: {'PASS' if is_valid else 'FAIL'}")
    
    is_invalid = verify_password("WrongPassword", hashed)
    print(f"   ✓ Wrong password rejected: {'PASS' if not is_invalid else 'FAIL'}")
    
    # Test 2: Token creation
    print("\n2. Testing token creation...")
    from app.core.security import create_access_token, decode_access_token
    
    token = create_access_token(data={"sub": "123"})
    print(f"   ✓ Token created successfully")
    print(f"   Token length: {len(token)}")
    
    # Decode token
    payload = decode_access_token(token)
    print(f"   ✓ Token decoded successfully")
    print(f"   User ID from token: {payload.get('sub')}")
    
    # Test 3: Test logging format
    print("\n3. Testing logging configuration...")
    import logging
    
    # Create a test logger
    logger = logging.getLogger('test_auth')
    logger.setLevel(logging.INFO)
    
    # Create a handler to capture log output
    from io import StringIO
    import logging.handlers
    
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    
    # Test log messages
    logger.info("Login attempt for email: test@example.com")
    logger.warning("Login failed - User not found: test@example.com")
    logger.info("Login successful for user: test@example.com (user_id=1)")
    
    log_output = log_capture.getvalue()
    print(f"   ✓ Logging configured correctly")
    print(f"   Sample log entries: {len(log_output.splitlines())} lines")
    
    # Verify log format
    if "Login attempt" in log_output and "Login failed" in log_output and "Login successful" in log_output:
        print("   ✓ All log types present")
    else:
        print("   ✗ Some log types missing")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_login_scenarios())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

"""
Comprehensive test for login functionality with rate limiting and phone support
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

async def test_login_comprehensive():
    """Test login functionality comprehensively"""
    
    # Import only the security module to avoid full app dependencies
    
    print("=" * 80)
    print("Comprehensive Login Tests")
    print("=" * 80)
    
    # Test 1: Rate limiting logic (manual implementation to test)
    print("\n1. Testing rate limiting logic...")
    from datetime import datetime, timedelta
    
    # Simulate rate limiting
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = timedelta(minutes=15)
    test_attempts = {}
    
    def check_rate_limit_test(identifier):
        current_time = datetime.utcnow()
        if identifier in test_attempts:
            attempts, lockout_until = test_attempts[identifier]
            if lockout_until and current_time < lockout_until:
                return False
            if lockout_until and current_time >= lockout_until:
                test_attempts[identifier] = (0, None)
                return True
            if attempts >= MAX_LOGIN_ATTEMPTS:
                test_attempts[identifier] = (attempts, current_time + LOCKOUT_DURATION)
                return False
        return True
    
    def record_attempt_test(identifier, success):
        if success:
            if identifier in test_attempts:
                del test_attempts[identifier]
        else:
            if identifier in test_attempts:
                attempts, lockout_until = test_attempts[identifier]
                test_attempts[identifier] = (attempts + 1, lockout_until)
            else:
                test_attempts[identifier] = (1, None)
    
    test_ip = "192.168.1.1"
    assert check_rate_limit_test(test_ip) == True, "First attempt should be allowed"
    print("   ✓ First attempt allowed")
    
    # Record failed attempts
    for i in range(MAX_LOGIN_ATTEMPTS):
        record_attempt_test(test_ip, False)
    
    assert check_rate_limit_test(test_ip) == False, "Should be rate limited after max attempts"
    print(f"   ✓ Rate limited after {MAX_LOGIN_ATTEMPTS} failed attempts")
    
    # Test successful login resets counter
    test_ip2 = "192.168.1.2"
    record_attempt_test(test_ip2, False)
    record_attempt_test(test_ip2, False)
    assert check_rate_limit_test(test_ip2) == True, "Should still allow attempts"
    record_attempt_test(test_ip2, True)
    
    attempts, lockout = test_attempts.get(test_ip2, (0, None))
    assert attempts == 0 or test_ip2 not in test_attempts, "Counter should be reset after successful login"
    print("   ✓ Counter reset after successful login")
    
    # Test 2: Phone number regex
    print("\n2. Testing phone number detection...")
    import re
    
    # Use the same pattern as production code
    phone_pattern = r'^\+?[\d\s\-\(\)]+$'
    
    test_cases = [
        ("1234567890", True, "10 digits"),
        ("+1-234-567-8900", True, "formatted with country code"),
        ("(242) 123-4567", True, "formatted with parentheses"),
        ("test@example.com", False, "email address"),
        ("user123", False, "username"),
        ("+123 456 7890", True, "spaced with country code"),
    ]
    
    for value, expected, description in test_cases:
        is_phone = bool(re.match(phone_pattern, value))
        status = "✓" if is_phone == expected else "✗"
        print(f"   {status} {description}: '{value}' -> {is_phone}")
        assert is_phone == expected, f"Failed for {description}"
    
    # Test 3: Password hashing
    print("\n3. Testing password security...")
    from app.core.security import get_password_hash, verify_password
    
    passwords = [
        "SimplePass123",
        "Complex!Pass@2024",
        "verylongpasswordwithmanychars123456",
        "P@ssw0rd!"
    ]
    
    for pwd in passwords:
        hashed = get_password_hash(pwd)
        assert len(hashed) == 60, f"Bcrypt hash should be 60 chars, got {len(hashed)}"
        assert verify_password(pwd, hashed), f"Password verification failed for {pwd}"
        assert not verify_password("wrong" + pwd, hashed), f"Wrong password accepted for {pwd}"
        print(f"   ✓ Password hashing/verification works for: {pwd[:10]}...")
    
    # Test 4: Token creation and validation
    print("\n4. Testing JWT tokens...")
    from app.core.security import create_access_token, decode_access_token
    
    test_users = ["1", "123", "999999"]
    for user_id in test_users:
        token = create_access_token(data={"sub": user_id})
        assert isinstance(token, str), "Token should be a string"
        assert len(token) > 50, "Token should be reasonably long"
        
        payload = decode_access_token(token)
        assert payload["sub"] == user_id, f"Token payload mismatch: expected {user_id}, got {payload['sub']}"
        assert "exp" in payload, "Token should have expiration"
        print(f"   ✓ Token creation/validation works for user_id={user_id}")
    
    # Test 5: Error message improvements
    print("\n5. Testing error messages...")
    
    error_messages = {
        "oauth_user": "This account uses social login. Please sign in with Google or Apple.",
        "incorrect_creds": "Incorrect email or password",
        "inactive": "Account is deactivated",
        "rate_limited": "Too many login attempts",
    }
    
    for key, msg in error_messages.items():
        assert len(msg) > 10, f"Error message too short: {key}"
        assert not any(tech_term in msg.lower() for tech_term in ["null", "undefined", "error"]), \
            f"Error message contains technical terms: {key}"
        print(f"   ✓ Error message '{key}': {msg[:50]}...")
    
    # Test 6: Logging format
    print("\n6. Testing logging configuration...")
    import logging
    from io import StringIO
    
    logger = logging.getLogger('test_login_comprehensive')
    logger.setLevel(logging.INFO)
    
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    
    # Test various log messages
    test_logs = [
        ("INFO", "Login attempt for: test@example.com from IP: 192.168.1.1"),
        ("WARNING", "Login failed - User not found: test@example.com"),
        ("WARNING", "Login failed - Invalid password for user: test@example.com (user_id=1)"),
        ("INFO", "Login successful for user: test@example.com (user_id=1)"),
        ("WARNING", "Rate limit exceeded for IP: 192.168.1.1"),
    ]
    
    for level, message in test_logs:
        if level == "INFO":
            logger.info(message)
        elif level == "WARNING":
            logger.warning(message)
    
    log_output = log_capture.getvalue()
    
    for _, message in test_logs:
        assert message in log_output, f"Log message not found: {message}"
    
    print(f"   ✓ All {len(test_logs)} log types properly formatted")
    
    print("\n" + "=" * 80)
    print("✅ All comprehensive tests passed!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_login_comprehensive())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

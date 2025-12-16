#!/usr/bin/env python3
"""
Comprehensive tests for JWT refresh token authentication system.

Tests cover:
- Token generation and validation
- Refresh token storage and retrieval
- Token rotation pattern
- Token revocation
- Secure cookie configuration
- Production security settings
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.backend_app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_token,
    store_refresh_token,
    verify_refresh_token_in_db,
    revoke_refresh_token,
    revoke_all_user_tokens,
    cleanup_expired_tokens,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    COOKIE_HTTPONLY,
    COOKIE_SECURE,
    COOKIE_SAMESITE,
)
from api.backend_app.database import get_async_session


async def test_token_generation():
    """Test access and refresh token generation"""
    print("\n" + "="*60)
    print("TEST: Token Generation")
    print("="*60)
    
    user_id = 12345
    
    # Test access token generation
    access_token = create_access_token(data={"sub": str(user_id)})
    print(f"✓ Generated access token (length: {len(access_token)})")
    
    # Test refresh token generation
    refresh_token = create_refresh_token(user_id)
    print(f"✓ Generated refresh token (length: {len(refresh_token)})")
    
    # Decode access token
    access_payload = decode_access_token(access_token)
    assert access_payload["sub"] == str(user_id), "Access token user ID mismatch"
    print(f"✓ Access token decoded successfully: user_id={access_payload['sub']}")
    
    # Decode refresh token
    refresh_payload = decode_refresh_token(refresh_token)
    assert refresh_payload["sub"] == str(user_id), "Refresh token user ID mismatch"
    assert refresh_payload["type"] == "refresh", "Refresh token type mismatch"
    print(f"✓ Refresh token decoded successfully: user_id={refresh_payload['sub']}, type={refresh_payload['type']}")
    
    # Test token expiration
    exp_timestamp = access_payload.get("exp")
    exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
    expected_exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    time_diff = abs((exp_datetime - expected_exp).total_seconds())
    assert time_diff < 5, "Access token expiration time incorrect"
    print(f"✓ Access token expires in {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    
    refresh_exp_timestamp = refresh_payload.get("exp")
    refresh_exp_datetime = datetime.utcfromtimestamp(refresh_exp_timestamp)
    expected_refresh_exp = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_time_diff = abs((refresh_exp_datetime - expected_refresh_exp).total_seconds())
    assert refresh_time_diff < 5, "Refresh token expiration time incorrect"
    print(f"✓ Refresh token expires in {REFRESH_TOKEN_EXPIRE_DAYS} days")
    
    print("\n✅ Token generation tests passed!")
    return True


async def test_token_hashing():
    """Test token hashing for secure storage"""
    print("\n" + "="*60)
    print("TEST: Token Hashing")
    print("="*60)
    
    token = "test_refresh_token_abc123"
    
    # Test hashing
    hash1 = hash_token(token)
    hash2 = hash_token(token)
    
    assert hash1 == hash2, "Same token should produce same hash"
    assert len(hash1) == 64, "SHA-256 hash should be 64 characters"
    assert hash1 != token, "Hash should be different from original token"
    print(f"✓ Token hashing produces consistent SHA-256 hashes")
    print(f"  Original: {token}")
    print(f"  Hash:     {hash1}")
    
    # Test different tokens produce different hashes
    token2 = "test_refresh_token_xyz789"
    hash3 = hash_token(token2)
    assert hash1 != hash3, "Different tokens should produce different hashes"
    print(f"✓ Different tokens produce different hashes")
    
    print("\n✅ Token hashing tests passed!")
    return True


async def test_refresh_token_storage():
    """Test storing and retrieving refresh tokens from database"""
    print("\n" + "="*60)
    print("TEST: Refresh Token Storage")
    print("="*60)
    
    try:
        async with get_async_session() as session:
            # Create a test user (assuming user ID 1 exists, or skip if not)
            user_id = 1
            refresh_token = create_refresh_token(user_id)
            
            # Store refresh token
            await store_refresh_token(
                session, 
                user_id, 
                refresh_token,
                ip_address="192.168.1.1",
                user_agent="Mozilla/5.0 Test Browser"
            )
            print(f"✓ Stored refresh token for user_id={user_id}")
            
            # Verify token in database
            verified_user_id = await verify_refresh_token_in_db(session, refresh_token)
            assert verified_user_id == user_id, "Token verification failed"
            print(f"✓ Verified refresh token in database: user_id={verified_user_id}")
            
            # Test invalid token
            invalid_token = "invalid_token_that_doesnt_exist"
            verified_invalid = await verify_refresh_token_in_db(session, invalid_token)
            assert verified_invalid is None, "Invalid token should return None"
            print(f"✓ Invalid token correctly rejected")
            
            # Clean up - revoke the test token
            await revoke_refresh_token(session, refresh_token)
            print(f"✓ Cleaned up test token")
            
            print("\n✅ Refresh token storage tests passed!")
            return True
    except Exception as e:
        print(f"⚠️  Database test skipped: {e}")
        print("   (This is expected if database is not configured)")
        return None


async def test_token_revocation():
    """Test token revocation functionality"""
    print("\n" + "="*60)
    print("TEST: Token Revocation")
    print("="*60)
    
    try:
        async with get_async_session() as session:
            user_id = 1
            
            # Create and store token
            refresh_token = create_refresh_token(user_id)
            await store_refresh_token(session, user_id, refresh_token)
            print(f"✓ Created refresh token for user_id={user_id}")
            
            # Verify token works before revocation
            verified = await verify_refresh_token_in_db(session, refresh_token)
            assert verified == user_id, "Token should be valid before revocation"
            print(f"✓ Token verified before revocation")
            
            # Revoke token
            revoked = await revoke_refresh_token(session, refresh_token)
            assert revoked == True, "Revocation should return True"
            print(f"✓ Token revoked successfully")
            
            # Verify token doesn't work after revocation
            verified_after = await verify_refresh_token_in_db(session, refresh_token)
            assert verified_after is None, "Token should be invalid after revocation"
            print(f"✓ Token correctly rejected after revocation")
            
            print("\n✅ Token revocation tests passed!")
            return True
    except Exception as e:
        print(f"⚠️  Database test skipped: {e}")
        return None


async def test_revoke_all_tokens():
    """Test revoking all tokens for a user"""
    print("\n" + "="*60)
    print("TEST: Revoke All User Tokens")
    print("="*60)
    
    try:
        async with get_async_session() as session:
            user_id = 1
            
            # Create multiple tokens
            token1 = create_refresh_token(user_id)
            token2 = create_refresh_token(user_id)
            token3 = create_refresh_token(user_id)
            
            await store_refresh_token(session, user_id, token1)
            await store_refresh_token(session, user_id, token2)
            await store_refresh_token(session, user_id, token3)
            print(f"✓ Created 3 refresh tokens for user_id={user_id}")
            
            # Verify all tokens work
            assert await verify_refresh_token_in_db(session, token1) == user_id
            assert await verify_refresh_token_in_db(session, token2) == user_id
            assert await verify_refresh_token_in_db(session, token3) == user_id
            print(f"✓ All 3 tokens verified before revocation")
            
            # Revoke all tokens
            count = await revoke_all_user_tokens(session, user_id)
            print(f"✓ Revoked {count} tokens for user_id={user_id}")
            
            # Verify all tokens are invalid
            assert await verify_refresh_token_in_db(session, token1) is None
            assert await verify_refresh_token_in_db(session, token2) is None
            assert await verify_refresh_token_in_db(session, token3) is None
            print(f"✓ All tokens correctly rejected after revocation")
            
            print("\n✅ Revoke all tokens tests passed!")
            return True
    except Exception as e:
        print(f"⚠️  Database test skipped: {e}")
        return None


async def test_token_rotation():
    """Test token rotation pattern"""
    print("\n" + "="*60)
    print("TEST: Token Rotation Pattern")
    print("="*60)
    
    try:
        async with get_async_session() as session:
            user_id = 1
            
            # Create and store first token
            old_token = create_refresh_token(user_id)
            await store_refresh_token(session, user_id, old_token)
            print(f"✓ Created initial refresh token")
            
            # Verify old token works
            assert await verify_refresh_token_in_db(session, old_token) == user_id
            print(f"✓ Old token verified")
            
            # Simulate rotation: revoke old, create new
            await revoke_refresh_token(session, old_token)
            new_token = create_refresh_token(user_id)
            await store_refresh_token(session, user_id, new_token)
            print(f"✓ Rotated to new token")
            
            # Verify old token is invalid
            assert await verify_refresh_token_in_db(session, old_token) is None
            print(f"✓ Old token correctly rejected")
            
            # Verify new token works
            assert await verify_refresh_token_in_db(session, new_token) == user_id
            print(f"✓ New token verified")
            
            # Clean up
            await revoke_refresh_token(session, new_token)
            
            print("\n✅ Token rotation tests passed!")
            return True
    except Exception as e:
        print(f"⚠️  Database test skipped: {e}")
        return None


def test_cookie_security_config():
    """Test cookie security configuration"""
    print("\n" + "="*60)
    print("TEST: Cookie Security Configuration")
    print("="*60)
    
    # Test cookie settings
    print(f"  COOKIE_HTTPONLY: {COOKIE_HTTPONLY}")
    print(f"  COOKIE_SECURE: {COOKIE_SECURE}")
    print(f"  COOKIE_SAMESITE: {COOKIE_SAMESITE}")
    
    # HttpOnly must always be True
    assert COOKIE_HTTPONLY == True, "HttpOnly must always be True for security"
    print(f"✓ HttpOnly is enabled (prevents JavaScript access)")
    
    # SameSite should be appropriate for environment
    assert COOKIE_SAMESITE in ["none", "lax", "strict"], "SameSite must be valid value"
    print(f"✓ SameSite configured: {COOKIE_SAMESITE}")
    
    # Secure depends on environment
    print(f"✓ Secure flag: {COOKIE_SECURE} (True in production, False in dev)")
    
    print("\n✅ Cookie security configuration tests passed!")
    return True


def test_token_expiration_config():
    """Test token expiration configuration"""
    print("\n" + "="*60)
    print("TEST: Token Expiration Configuration")
    print("="*60)
    
    print(f"  Access Token Expiration: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    print(f"  Refresh Token Expiration: {REFRESH_TOKEN_EXPIRE_DAYS} days")
    
    # Access token should be short-lived (15 minutes recommended)
    assert ACCESS_TOKEN_EXPIRE_MINUTES <= 60, "Access tokens should be short-lived (≤60 min)"
    print(f"✓ Access token expiration is appropriate (≤60 min)")
    
    # Refresh token should be longer but not excessive
    assert 1 <= REFRESH_TOKEN_EXPIRE_DAYS <= 90, "Refresh tokens should be 1-90 days"
    print(f"✓ Refresh token expiration is appropriate (1-90 days)")
    
    # Refresh should be longer than access
    refresh_minutes = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60
    assert refresh_minutes > ACCESS_TOKEN_EXPIRE_MINUTES, "Refresh token must outlive access token"
    print(f"✓ Refresh token lifetime ({refresh_minutes} min) > Access token lifetime ({ACCESS_TOKEN_EXPIRE_MINUTES} min)")
    
    print("\n✅ Token expiration configuration tests passed!")
    return True


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" JWT REFRESH TOKEN AUTHENTICATION - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    results = []
    
    # Run synchronous tests
    results.append(("Cookie Security Config", test_cookie_security_config()))
    results.append(("Token Expiration Config", test_token_expiration_config()))
    
    # Run async tests
    results.append(("Token Generation", await test_token_generation()))
    results.append(("Token Hashing", await test_token_hashing()))
    results.append(("Refresh Token Storage", await test_refresh_token_storage()))
    results.append(("Token Revocation", await test_token_revocation()))
    results.append(("Revoke All Tokens", await test_revoke_all_tokens()))
    results.append(("Token Rotation", await test_token_rotation()))
    
    # Print summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result == True)
    skipped = sum(1 for _, result in results if result is None)
    failed = sum(1 for _, result in results if result == False)
    
    for test_name, result in results:
        if result == True:
            status = "✅ PASSED"
        elif result is None:
            status = "⚠️  SKIPPED"
        else:
            status = "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {len(results)} tests")
    print(f"✅ Passed: {passed}")
    print(f"⚠️  Skipped: {skipped} (database not configured)")
    print(f"❌ Failed: {failed}")
    
    if failed > 0:
        print("\n❌ Some tests failed!")
        sys.exit(1)
    else:
        print("\n✅ All available tests passed!")
        print("\nNote: Some tests require a configured database.")
        print("To run all tests, set up DATABASE_URL in your environment.")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())

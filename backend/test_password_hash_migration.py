"""
Test password hash migration functionality.

This test verifies that:
1. Old high-round password hashes are detected correctly
2. Hash upgrade logic is triggered appropriately
3. Bcrypt rounds are correctly extracted from hashes
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


def test_get_bcrypt_rounds_from_hash():
    """Test that bcrypt rounds are correctly extracted from password hashes."""
    from final_backend_postgresql import _get_bcrypt_rounds_from_hash
    
    # Test with 10 rounds hash
    hash_10 = "$2b$10$abcdefghijklmnopqrstuOexamplehashvalue"
    assert _get_bcrypt_rounds_from_hash(hash_10) == 10, "Should detect 10 rounds"
    
    # Test with 12 rounds hash
    hash_12 = "$2b$12$abcdefghijklmnopqrstuOexamplehashvalue"
    assert _get_bcrypt_rounds_from_hash(hash_12) == 12, "Should detect 12 rounds"
    
    # Test with 14 rounds hash
    hash_14 = "$2b$14$abcdefghijklmnopqrstuOexamplehashvalue"
    assert _get_bcrypt_rounds_from_hash(hash_14) == 14, "Should detect 14 rounds"
    
    # Test with $2a$ variant (older bcrypt)
    hash_2a = "$2a$12$abcdefghijklmnopqrstuOexamplehashvalue"
    assert _get_bcrypt_rounds_from_hash(hash_2a) == 12, "Should detect 12 rounds for $2a$ variant"
    
    # Test with invalid hash format
    invalid_hash = "not_a_bcrypt_hash"
    assert _get_bcrypt_rounds_from_hash(invalid_hash) == 0, "Should return 0 for invalid hash"
    
    # Test with empty string
    assert _get_bcrypt_rounds_from_hash("") == 0, "Should return 0 for empty string"


def test_should_upgrade_password_hash():
    """Test that hash upgrade detection works correctly."""
    from final_backend_postgresql import (
        _should_upgrade_password_hash,
        BCRYPT_ROUNDS,
        PASSWORD_HASH_MIGRATION_ENABLED
    )
    
    # Skip test if migration is disabled
    if not PASSWORD_HASH_MIGRATION_ENABLED:
        print("  Skipping (migration disabled)")
        return
    
    # Hash with more rounds than current setting should be upgraded
    if BCRYPT_ROUNDS == 10:
        old_hash = "$2b$12$abcdefghijklmnopqrstuOexamplehashvalue"
        assert _should_upgrade_password_hash(old_hash) is True, \
            "12-round hash should be upgraded when BCRYPT_ROUNDS=10"
        
        # Hash with same or fewer rounds should NOT be upgraded
        current_hash = "$2b$10$abcdefghijklmnopqrstuOexamplehashvalue"
        assert _should_upgrade_password_hash(current_hash) is False, \
            "10-round hash should NOT be upgraded when BCRYPT_ROUNDS=10"
        
        newer_hash = "$2b$08$abcdefghijklmnopqrstuOexamplehashvalue"
        assert _should_upgrade_password_hash(newer_hash) is False, \
            "8-round hash should NOT be upgraded when BCRYPT_ROUNDS=10"


def test_bcrypt_rounds_extraction_with_real_hashes():
    """Test with real bcrypt-generated hashes."""
    import bcrypt
    from final_backend_postgresql import _get_bcrypt_rounds_from_hash
    
    # Generate real hashes with different rounds
    password = b"test_password123"
    
    # 10 rounds
    hash_10 = bcrypt.hashpw(password, bcrypt.gensalt(rounds=10)).decode('utf-8')
    assert _get_bcrypt_rounds_from_hash(hash_10) == 10, \
        f"Should detect 10 rounds in {hash_10[:15]}..."
    
    # 12 rounds (only test if not too slow)
    hash_12 = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12)).decode('utf-8')
    assert _get_bcrypt_rounds_from_hash(hash_12) == 12, \
        f"Should detect 12 rounds in {hash_12[:15]}..."


def test_password_hash_migration_config():
    """Test that password hash migration configuration is correct."""
    from final_backend_postgresql import (
        PASSWORD_HASH_MIGRATION_ENABLED,
        BCRYPT_ROUNDS
    )
    
    # Migration should be enabled by default
    assert PASSWORD_HASH_MIGRATION_ENABLED is True, \
        "Password hash migration should be enabled by default"
    
    # BCRYPT_ROUNDS should be 10 by default (optimized for performance)
    assert BCRYPT_ROUNDS == 10, \
        f"BCRYPT_ROUNDS should be 10, got {BCRYPT_ROUNDS}"


def test_connection_warmup_function_exists():
    """Test that connection warmup function is defined."""
    from final_backend_postgresql import _warmup_connection_pool
    
    # Function should exist and be callable
    assert callable(_warmup_connection_pool), \
        "_warmup_connection_pool should be a callable function"


if __name__ == "__main__":
    print("Running password hash migration tests...")
    
    print("\n1. Testing _get_bcrypt_rounds_from_hash...")
    test_get_bcrypt_rounds_from_hash()
    print("   ✓ Passed")
    
    print("\n2. Testing _should_upgrade_password_hash...")
    test_should_upgrade_password_hash()
    print("   ✓ Passed")
    
    print("\n3. Testing bcrypt rounds extraction with real hashes...")
    test_bcrypt_rounds_extraction_with_real_hashes()
    print("   ✓ Passed")
    
    print("\n4. Testing password hash migration config...")
    test_password_hash_migration_config()
    print("   ✓ Passed")
    
    print("\n5. Testing connection warmup function exists...")
    test_connection_warmup_function_exists()
    print("   ✓ Passed")
    
    print("\n" + "=" * 50)
    print("All password hash migration tests passed!")
    print("=" * 50)

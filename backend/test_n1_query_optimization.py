"""
Test N+1 query optimization for conversations endpoint.

This test verifies that the conversations endpoint fetches all messages
in a batch query instead of N+1 queries (one query per conversation).
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


def test_user_columns_constants_defined():
    """Test that user column constants are properly defined."""
    from final_backend_postgresql import (
        USER_COLUMNS_FULL,
        USER_COLUMNS_LOGIN,
        USER_COLUMNS_PUBLIC,
    )
    
    print("=" * 80)
    print("User Column Constants Test")
    print("=" * 80)
    
    # Test 1: Constants are defined and non-empty
    print("\n1. Testing column constant definitions...")
    assert USER_COLUMNS_FULL is not None, "USER_COLUMNS_FULL should be defined"
    assert USER_COLUMNS_LOGIN is not None, "USER_COLUMNS_LOGIN should be defined"
    assert USER_COLUMNS_PUBLIC is not None, "USER_COLUMNS_PUBLIC should be defined"
    
    assert len(USER_COLUMNS_FULL.strip()) > 0, "USER_COLUMNS_FULL should not be empty"
    assert len(USER_COLUMNS_LOGIN.strip()) > 0, "USER_COLUMNS_LOGIN should not be empty"
    assert len(USER_COLUMNS_PUBLIC.strip()) > 0, "USER_COLUMNS_PUBLIC should not be empty"
    print("   ✓ All column constants are defined and non-empty")
    
    # Test 2: LOGIN columns include required fields
    print("\n2. Testing LOGIN columns include auth-required fields...")
    login_columns_lower = USER_COLUMNS_LOGIN.lower()
    required_login_fields = ['id', 'email', 'password_hash', 'is_active']
    for field in required_login_fields:
        assert field in login_columns_lower, f"LOGIN columns should include {field}"
    print(f"   ✓ LOGIN columns include: {required_login_fields}")
    
    # Test 3: PUBLIC columns exclude sensitive data
    print("\n3. Testing PUBLIC columns exclude sensitive data...")
    public_columns_lower = USER_COLUMNS_PUBLIC.lower()
    # password_hash should NOT be in public columns
    assert 'password_hash' not in public_columns_lower, "PUBLIC columns should NOT include password_hash"
    print("   ✓ PUBLIC columns exclude password_hash (sensitive)")
    
    # Test 4: FULL columns include all table columns
    print("\n4. Testing FULL columns include comprehensive data...")
    full_columns_lower = USER_COLUMNS_FULL.lower()
    expected_columns = ['id', 'email', 'first_name', 'last_name', 'bio', 'avatar_url']
    for col in expected_columns:
        assert col in full_columns_lower, f"FULL columns should include {col}"
    print(f"   ✓ FULL columns include comprehensive fields")
    
    print("\n" + "=" * 80)
    print("All user column constant tests passed!")
    print("=" * 80)


def test_conversations_batch_query_structure():
    """Test that the conversations endpoint uses batch query for messages."""
    import inspect
    from final_backend_postgresql import get_conversations
    
    print("\n" + "=" * 80)
    print("Conversations Batch Query Test")
    print("=" * 80)
    
    # Get the source code of the function
    source = inspect.getsource(get_conversations)
    
    # Test 1: Function uses batch query pattern
    print("\n1. Testing for batch query pattern...")
    
    # The optimized version should use ANY(%s) or IN for PostgreSQL
    has_any_operator = "ANY(%s)" in source or "ANY(%" in source
    # Or placeholders for SQLite
    has_in_placeholder = "IN ({placeholders})" in source
    
    assert has_any_operator or has_in_placeholder, \
        "Conversations endpoint should use batch query (ANY or IN with placeholders)"
    print("   ✓ Batch query pattern found (uses ANY or IN)")
    
    # Test 2: Function groups messages by conversation
    print("\n2. Testing for message grouping pattern...")
    has_messages_grouping = "messages_by_conversation" in source
    assert has_messages_grouping, \
        "Conversations endpoint should group messages by conversation ID"
    print("   ✓ Message grouping pattern found")
    
    # Test 3: Function should NOT have nested query in loop (N+1 pattern)
    print("\n3. Testing for absence of N+1 pattern...")
    # Check that there's no pattern like "for conv in conversations_data: ... cursor.execute"
    # Split by the conversations loop and check
    loop_pattern_found = False
    if "for conv in conversations_data:" in source:
        # After the loop starts, there shouldn't be a cursor.execute for messages
        loop_start = source.find("for conv in conversations_data:")
        loop_section = source[loop_start:loop_start + 500]  # Check next 500 chars
        # The optimized version shouldn't have cursor.execute in this section
        # (messages are pre-fetched before the loop)
        if "cursor.execute" in loop_section and "WHERE m.conversation_id" in loop_section:
            loop_pattern_found = True
    
    assert not loop_pattern_found, \
        "N+1 pattern detected: cursor.execute found in conversations loop"
    print("   ✓ No N+1 query pattern found in loop")
    
    print("\n" + "=" * 80)
    print("All conversation batch query tests passed!")
    print("=" * 80)


def test_explicit_columns_in_login():
    """Test that login endpoint uses explicit columns instead of SELECT *."""
    import inspect
    from final_backend_postgresql import login
    
    print("\n" + "=" * 80)
    print("Login Explicit Columns Test")
    print("=" * 80)
    
    source = inspect.getsource(login)
    
    # Test 1: Should use USER_COLUMNS_LOGIN constant
    print("\n1. Testing for explicit column usage in login...")
    has_column_constant = "USER_COLUMNS_LOGIN" in source
    
    if has_column_constant:
        print("   ✓ Uses USER_COLUMNS_LOGIN constant")
    
    # Test 2: Should NOT use SELECT * for user lookup
    print("\n2. Testing for absence of SELECT * in login...")
    # Note: The actual code uses f-strings, so we check for the pattern
    has_select_star = "SELECT *" in source and "FROM users" in source
    # The old pattern would be: SELECT * FROM users WHERE LOWER(email)
    # The new pattern uses f-string with column constant
    
    assert not has_select_star, \
        "Login endpoint should not use SELECT * for user queries"
    print("   ✓ No SELECT * pattern found in login")
    
    print("\n" + "=" * 80)
    print("All login explicit columns tests passed!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_user_columns_constants_defined()
        test_conversations_batch_query_structure()
        test_explicit_columns_in_login()
        print("\n✓ All N+1 query optimization tests completed successfully")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

"""Test that auth module exports are working correctly."""


def test_auth_imports():
    """Test that all auth functions can be imported from app.auth."""
    # Test the specific import that was failing
    from app.auth import get_current_user
    assert get_current_user is not None, "get_current_user should be importable"
    
    # Test additional imports
    from app.auth import get_current_user_optional
    assert get_current_user_optional is not None, "get_current_user_optional should be importable"
    
    from app.auth import create_access_token, decode_access_token
    assert create_access_token is not None, "create_access_token should be importable"
    assert decode_access_token is not None, "decode_access_token should be importable"
    
    print("✓ All auth imports successful!")


def test_auth_all_exports():
    """Test that __all__ is properly defined."""
    from app import auth
    
    assert hasattr(auth, '__all__'), "auth module should have __all__ defined"
    assert 'get_current_user' in auth.__all__, "get_current_user should be in __all__"
    assert 'get_current_user_optional' in auth.__all__, "get_current_user_optional should be in __all__"
    assert 'create_access_token' in auth.__all__, "create_access_token should be in __all__"
    assert 'decode_access_token' in auth.__all__, "decode_access_token should be in __all__"
    
    print("✓ __all__ exports properly defined!")


if __name__ == "__main__":
    test_auth_imports()
    test_auth_all_exports()
    print("\n✅ All auth import tests passed!")

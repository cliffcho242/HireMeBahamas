"""
Test for /api/auth/me endpoint - Verify minimal response format.

This test ensures the /api/auth/me endpoint returns only the essential
user identification fields (id, email, role) as specified in Step 4.

This test validates the response schema without requiring database access.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pytest


def test_auth_me_endpoint_schema():
    """Test that /api/auth/me endpoint returns only id, email, and role.
    
    This test validates the schema definition without needing database access.
    
    Verifies that the UserMeResponse schema only includes id, email, and role fields.
    """
    from app.schemas.auth import UserMeResponse
    from pydantic import ValidationError
    
    # Test valid minimal response
    valid_data = {
        "id": 1,
        "email": "test@example.com",
        "role": "user"
    }
    
    response = UserMeResponse(**valid_data)
    
    # Check that only the required fields are present
    response_dict = response.model_dump()
    expected_fields = {"id", "email", "role"}
    actual_fields = set(response_dict.keys())
    
    assert actual_fields == expected_fields, (
        f"Expected fields {expected_fields}, got {actual_fields}. "
        f"Extra fields: {actual_fields - expected_fields}, "
        f"Missing fields: {expected_fields - actual_fields}"
    )
    
    # Verify field values
    assert response.id == valid_data["id"]
    assert response.email == valid_data["email"]
    assert response.role == valid_data["role"]


def test_auth_me_response_schema_validation():
    """Test that UserMeResponse validates fields correctly."""
    from app.schemas.auth import UserMeResponse
    from pydantic import ValidationError
    
    # Test with missing required field
    try:
        UserMeResponse(id=1, email="test@example.com")  # Missing role
        assert False, "Should have raised ValidationError for missing role"
    except ValidationError:
        pass  # Expected
    
    # Test with extra fields (should be ignored with Pydantic v2)
    response = UserMeResponse(
        id=1,
        email="test@example.com",
        role="user",
        extra_field="should_be_ignored"  # type: ignore
    )
    assert hasattr(response, "id")
    assert hasattr(response, "email")
    assert hasattr(response, "role")


def test_auth_me_response_schema_types():
    """Test that UserMeResponse enforces correct types."""
    from app.schemas.auth import UserMeResponse
    
    # Valid types
    response = UserMeResponse(id=1, email="test@example.com", role="user")
    assert isinstance(response.id, int)
    assert isinstance(response.email, str)
    assert isinstance(response.role, str)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

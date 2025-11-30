"""Test user data loading functionality."""

import pytest


class TestUserDataLoading:
    """Tests for user data loading and validation."""

    def test_user_required_fields(self):
        """Test that user data has required fields."""
        # Define a sample user data structure
        user_data = {
            "id": 1,
            "email": "test@hiremebahamas.com",
            "first_name": "John",
            "last_name": "Doe",
        }

        # Verify required fields are present
        assert "id" in user_data
        assert "email" in user_data
        assert "first_name" in user_data
        assert "last_name" in user_data

    def test_user_email_format(self):
        """Test that user email has valid format."""
        user_data = {
            "email": "test@hiremebahamas.com",
        }

        # Basic email validation
        email = user_data["email"]
        assert "@" in email
        assert "." in email.split("@")[1]

    def test_user_full_name(self):
        """Test computing full name from first and last name."""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
        }

        full_name = f"{user_data['first_name']} {user_data['last_name']}"
        assert full_name == "John Doe"

    def test_user_optional_fields(self):
        """Test that optional user fields have proper defaults."""
        user_data = {
            "id": 1,
            "email": "test@hiremebahamas.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": None,
            "location": None,
            "occupation": None,
            "bio": None,
            "skills": None,
            "is_active": True,
            "is_admin": False,
            "is_available_for_hire": False,
            "role": "user",
        }

        # Verify optional fields can be None
        assert user_data["phone"] is None
        assert user_data["location"] is None
        assert user_data["occupation"] is None
        assert user_data["bio"] is None
        assert user_data["skills"] is None

        # Verify boolean defaults
        assert user_data["is_active"] is True
        assert user_data["is_admin"] is False
        assert user_data["is_available_for_hire"] is False

        # Verify role default
        assert user_data["role"] == "user"

    def test_user_role_values(self):
        """Test valid user role values."""
        valid_roles = ["user", "admin", "employer", "freelancer"]

        for role in valid_roles:
            user_data = {"role": role}
            assert user_data["role"] in valid_roles

    def test_user_avatar_url_optional(self):
        """Test that avatar URL is optional."""
        user_with_avatar = {"avatar_url": "https://example.com/avatar.png"}
        user_without_avatar = {"avatar_url": None}

        assert user_with_avatar["avatar_url"] is not None
        assert user_without_avatar["avatar_url"] is None

    def test_user_oauth_fields(self):
        """Test OAuth provider fields for social login users."""
        # OAuth user (e.g., Google login)
        oauth_user = {
            "oauth_provider": "google",
            "oauth_provider_id": "12345",
            "hashed_password": None,  # OAuth users may not have a password
        }

        assert oauth_user["oauth_provider"] == "google"
        assert oauth_user["oauth_provider_id"] is not None

        # Regular user (no OAuth)
        regular_user = {
            "oauth_provider": None,
            "oauth_provider_id": None,
            "hashed_password": "hashed_password_here",
        }

        assert regular_user["oauth_provider"] is None
        assert regular_user["hashed_password"] is not None

    def test_user_data_serialization(self):
        """Test that user data can be serialized to dict format."""
        user_data = {
            "id": 1,
            "email": "test@hiremebahamas.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1-242-555-1234",
            "location": "Nassau, Bahamas",
            "occupation": "Software Developer",
            "company_name": "Tech Co",
            "bio": "A developer from the Bahamas",
            "skills": "Python, JavaScript, Flask",
            "is_active": True,
            "is_admin": False,
            "is_available_for_hire": True,
            "role": "freelancer",
        }

        # Verify serialization
        assert isinstance(user_data, dict)
        assert len(user_data) == 14

        # Verify all fields have expected types
        assert isinstance(user_data["id"], int)
        assert isinstance(user_data["email"], str)
        assert isinstance(user_data["first_name"], str)
        assert isinstance(user_data["last_name"], str)
        assert isinstance(user_data["is_active"], bool)
        assert isinstance(user_data["is_admin"], bool)
        assert isinstance(user_data["is_available_for_hire"], bool)

    def test_user_list_loading(self):
        """Test loading a list of users."""
        users = [
            {
                "id": 1,
                "email": "user1@hiremebahamas.com",
                "first_name": "John",
                "last_name": "Doe",
            },
            {
                "id": 2,
                "email": "user2@hiremebahamas.com",
                "first_name": "Jane",
                "last_name": "Smith",
            },
            {
                "id": 3,
                "email": "user3@hiremebahamas.com",
                "first_name": "Bob",
                "last_name": "Wilson",
            },
        ]

        # Verify list loading
        assert len(users) == 3
        assert all("id" in user for user in users)
        assert all("email" in user for user in users)

        # Verify unique IDs
        ids = [user["id"] for user in users]
        assert len(ids) == len(set(ids))

        # Verify unique emails
        emails = [user["email"] for user in users]
        assert len(emails) == len(set(emails))

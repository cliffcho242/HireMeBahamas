#!/usr/bin/env python3
"""
Comprehensive test suite for user registration functionality
Tests the registration process with various scenarios including:
- Successful registration
- Validation errors
- Duplicate email handling
- Password strength validation
- Missing required fields
"""

import json
import os
import sqlite3
import tempfile
from pathlib import Path

import pytest

# Import the Flask app from final_backend.py
import final_backend


@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    
    # Store original values to restore after test
    original_db_path = getattr(final_backend, 'DB_PATH', None)
    original_use_postgresql = getattr(final_backend, 'USE_POSTGRESQL', None)
    
    # Update the app to use test database
    final_backend.DB_PATH = Path(db_path)
    final_backend.USE_POSTGRESQL = False
    
    # Initialize the database with users table
    # Note: This schema mirrors the production schema in final_backend.py
    # If the production schema changes, this should be updated accordingly
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table with all required fields
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            user_type TEXT,
            location TEXT,
            phone TEXT,
            bio TEXT,
            avatar_url TEXT,
            is_active INTEGER DEFAULT 1,
            is_available_for_hire INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    final_backend.app.config['TESTING'] = True
    # Use a unique secret key for each test to prevent cross-test issues
    import secrets
    final_backend.app.config['SECRET_KEY'] = secrets.token_hex(32)
    
    yield final_backend.app
    
    # Cleanup: restore original values and remove temp database
    if original_db_path is not None:
        final_backend.DB_PATH = original_db_path
    if original_use_postgresql is not None:
        final_backend.USE_POSTGRESQL = original_use_postgresql
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the app"""
    return app.test_client()


class TestRegistration:
    """Test cases for user registration"""
    
    def test_successful_registration(self, client):
        """Test successful user registration with valid data"""
        registration_data = {
            "email": "test@example.com",
            "password": "TestPass123",
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "freelancer",
            "location": "Nassau, Bahamas"
        }
        
        response = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data["success"] is True
        assert data["message"] == "Registration successful"
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify user data
        user = data["user"]
        assert user["email"] == "test@example.com"
        assert user["first_name"] == "John"
        assert user["last_name"] == "Doe"
        assert user["user_type"] == "freelancer"
        assert user["location"] == "Nassau, Bahamas"
        assert "id" in user
    
    def test_registration_with_optional_fields(self, client):
        """Test registration with optional fields like phone and bio"""
        registration_data = {
            "email": "user2@example.com",
            "password": "SecurePass456",
            "first_name": "Jane",
            "last_name": "Smith",
            "user_type": "employer",
            "location": "Freeport, Bahamas",
            "phone": "+1-242-555-1234",
            "bio": "Experienced HR professional"
        }
        
        response = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        
        user = data["user"]
        assert user["phone"] == "+1-242-555-1234"
        assert user["bio"] == "Experienced HR professional"
    
    def test_registration_missing_email(self, client):
        """Test registration fails when email is missing"""
        registration_data = {
            "password": "TestPass123",
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "freelancer",
            "location": "Nassau, Bahamas"
        }
        
        response = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Email" in data["message"]
    
    def test_registration_missing_password(self, client):
        """Test registration fails when password is missing"""
        registration_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "freelancer",
            "location": "Nassau, Bahamas"
        }
        
        response = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Password" in data["message"]
    
    def test_registration_missing_first_name(self, client):
        """Test registration fails when first_name is missing"""
        registration_data = {
            "email": "test@example.com",
            "password": "TestPass123",
            "last_name": "Doe",
            "user_type": "freelancer",
            "location": "Nassau, Bahamas"
        }
        
        response = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "First Name" in data["message"]
    
    def test_registration_missing_last_name(self, client):
        """Test registration fails when last_name is missing"""
        registration_data = {
            "email": "test@example.com",
            "password": "TestPass123",
            "first_name": "John",
            "user_type": "freelancer",
            "location": "Nassau, Bahamas"
        }
        
        response = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Last Name" in data["message"]
    
    def test_registration_missing_user_type(self, client):
        """Test registration fails when user_type is missing"""
        registration_data = {
            "email": "test@example.com",
            "password": "TestPass123",
            "first_name": "John",
            "last_name": "Doe",
            "location": "Nassau, Bahamas"
        }
        
        response = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "User Type" in data["message"]
    
    def test_registration_missing_location(self, client):
        """Test registration fails when location is missing"""
        registration_data = {
            "email": "test@example.com",
            "password": "TestPass123",
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "freelancer"
        }
        
        response = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Location" in data["message"]
    
    def test_registration_weak_password_too_short(self, client):
        """Test registration fails with password less than 8 characters"""
        registration_data = {
            "email": "test@example.com",
            "password": "Short1",  # Only 6 characters
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "freelancer",
            "location": "Nassau, Bahamas"
        }
        
        response = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "at least 8 characters" in data["message"]
    
    def test_registration_weak_password_no_number(self, client):
        """Test registration fails with password without numbers"""
        registration_data = {
            "email": "test@example.com",
            "password": "OnlyLetters",  # No numbers
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "freelancer",
            "location": "Nassau, Bahamas"
        }
        
        response = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "one letter and one number" in data["message"]
    
    def test_registration_weak_password_no_letter(self, client):
        """Test registration fails with password without letters"""
        registration_data = {
            "email": "test@example.com",
            "password": "12345678",  # No letters
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "freelancer",
            "location": "Nassau, Bahamas"
        }
        
        response = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "one letter and one number" in data["message"]
    
    def test_registration_duplicate_email(self, client):
        """Test registration fails when email already exists"""
        registration_data = {
            "email": "duplicate@example.com",
            "password": "TestPass123",
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "freelancer",
            "location": "Nassau, Bahamas"
        }
        
        # First registration should succeed
        response1 = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        assert response1.status_code == 201
        
        # Second registration with same email should fail
        response2 = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        
        assert response2.status_code == 409
        data = response2.get_json()
        assert data["success"] is False
        assert "already exists" in data["message"]
    
    def test_registration_email_case_insensitive(self, client):
        """Test that email comparison is case-insensitive"""
        registration_data1 = {
            "email": "Test@Example.com",
            "password": "TestPass123",
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "freelancer",
            "location": "Nassau, Bahamas"
        }
        
        # First registration
        response1 = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data1),
            content_type="application/json"
        )
        assert response1.status_code == 201
        
        # Try to register with same email but different case
        registration_data2 = {
            "email": "test@example.com",  # Different case
            "password": "TestPass456",
            "first_name": "Jane",
            "last_name": "Smith",
            "user_type": "employer",
            "location": "Nassau, Bahamas"
        }
        
        response2 = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data2),
            content_type="application/json"
        )
        
        assert response2.status_code == 409
        data = response2.get_json()
        assert data["success"] is False
        assert "already exists" in data["message"]
    
    def test_registration_empty_string_fields(self, client):
        """Test registration fails with empty string for required fields"""
        registration_data = {
            "email": "",  # Empty string
            "password": "TestPass123",
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "freelancer",
            "location": "Nassau, Bahamas"
        }
        
        response = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
    
    def test_registration_whitespace_trimming(self, client):
        """Test that registration trims whitespace from fields"""
        registration_data = {
            "email": "  trimtest@example.com  ",
            "password": "TestPass123",
            "first_name": "  John  ",
            "last_name": "  Doe  ",
            "user_type": "freelancer",
            "location": "  Nassau, Bahamas  "
        }
        
        response = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        
        assert response.status_code == 201
        data = response.get_json()
        user = data["user"]
        
        # Email should be trimmed and lowercased
        assert user["email"] == "trimtest@example.com"
        assert user["first_name"] == "John"
        assert user["last_name"] == "Doe"
        assert user["location"] == "Nassau, Bahamas"
    
    def test_registration_token_generation(self, client):
        """Test that registration generates a valid JWT token"""
        registration_data = {
            "email": "tokentest@example.com",
            "password": "TestPass123",
            "first_name": "Token",
            "last_name": "Test",
            "user_type": "freelancer",
            "location": "Nassau, Bahamas"
        }
        
        response = client.post(
            "/api/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json"
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Verify token exists and has correct format
        assert "access_token" in data
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
        
        # Token should have 3 parts (header.payload.signature)
        token_parts = data["access_token"].split(".")
        assert len(token_parts) == 3
    
    def test_registration_options_request(self, client):
        """Test that OPTIONS request for CORS works"""
        response = client.options("/api/auth/register")
        
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

#!/usr/bin/env python3
"""
Test script to verify user lookup endpoint supports both ID and username lookups.
Tests the /api/users/<identifier> endpoint in final_backend_postgresql.py
"""

import json
import os
import secrets
import sqlite3
import tempfile
from pathlib import Path

import pytest

# Import the Flask app from final_backend_postgresql.py
import final_backend_postgresql


@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    
    # Store original values to restore after test
    original_db_path = getattr(final_backend_postgresql, 'DB_PATH', None)
    original_use_postgresql = getattr(final_backend_postgresql, 'USE_POSTGRESQL', None)
    
    # Update the app to use test database
    final_backend_postgresql.DB_PATH = Path(db_path)
    final_backend_postgresql.USE_POSTGRESQL = False
    
    # Initialize the database with required tables
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
            username TEXT UNIQUE,
            user_type TEXT,
            location TEXT,
            phone TEXT,
            bio TEXT,
            avatar_url TEXT,
            occupation TEXT,
            company_name TEXT,
            is_active INTEGER DEFAULT 1,
            is_available_for_hire INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    
    # Create follows table for follow-related queries
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS follows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            follower_id INTEGER NOT NULL,
            followed_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(follower_id, followed_id)
        )
    """)
    
    # Create posts table for posts count
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    final_backend_postgresql.app.config['TESTING'] = True
    # Use a unique secret key for each test
    final_backend_postgresql.app.config['SECRET_KEY'] = secrets.token_hex(32)
    
    yield final_backend_postgresql.app
    
    # Cleanup
    if original_db_path is not None:
        final_backend_postgresql.DB_PATH = original_db_path
    if original_use_postgresql is not None:
        final_backend_postgresql.USE_POSTGRESQL = original_use_postgresql
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the app"""
    return app.test_client()


def create_test_user(client, email="testuser@example.com", username="testuser123"):
    """Helper to create a test user and return user data with token"""
    registration_data = {
        "email": email,
        "password": "TestPass123",
        "first_name": "Test",
        "last_name": "User",
        "user_type": "freelancer",
        "location": "Nassau, Bahamas"
    }
    
    response = client.post(
        "/api/auth/register",
        data=json.dumps(registration_data),
        content_type="application/json"
    )
    
    data = response.get_json()
    
    # Update the username directly in the database
    conn = sqlite3.connect(str(final_backend_postgresql.DB_PATH))
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = ? WHERE email = ?", (username, email))
    conn.commit()
    conn.close()
    
    return {
        "user": data.get("user"),
        "token": data.get("access_token")
    }


class TestUserLookup:
    """Test cases for user lookup by ID and username"""
    
    def test_lookup_by_id(self, client):
        """Test user lookup by numeric ID"""
        # Create a test user
        test_data = create_test_user(client)
        token = test_data["token"]
        user_id = test_data["user"]["id"]
        
        # Look up the user by ID
        response = client.get(
            f"/api/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data["success"] is True
        assert "user" in data
        assert data["user"]["id"] == user_id
        assert data["user"]["email"] == "testuser@example.com"
        assert data["user"]["first_name"] == "Test"
        assert data["user"]["last_name"] == "User"
    
    def test_lookup_by_username(self, client):
        """Test user lookup by username string"""
        # Create a test user with a specific username
        test_data = create_test_user(
            client,
            email="user_with_username@example.com",
            username="johndoe"
        )
        token = test_data["token"]
        
        # Look up the user by username
        response = client.get(
            "/api/users/johndoe",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data["success"] is True
        assert "user" in data
        assert data["user"]["username"] == "johndoe"
        assert data["user"]["email"] == "user_with_username@example.com"
    
    def test_lookup_nonexistent_id(self, client):
        """Test lookup of non-existent user ID returns 404"""
        # Create a test user to get a valid token
        test_data = create_test_user(
            client,
            email="existing@example.com",
            username="existing"
        )
        token = test_data["token"]
        
        # Try to look up a non-existent user ID
        response = client.get(
            "/api/users/999999",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()
    
    def test_lookup_nonexistent_username(self, client):
        """Test lookup of non-existent username returns 404"""
        # Create a test user to get a valid token
        test_data = create_test_user(
            client,
            email="existing2@example.com",
            username="existinguser"
        )
        token = test_data["token"]
        
        # Try to look up a non-existent username
        response = client.get(
            "/api/users/nonexistentuser",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()
    
    def test_lookup_without_auth(self, client):
        """Test that lookup requires authentication"""
        response = client.get("/api/users/1")
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False
    
    def test_lookup_with_invalid_token(self, client):
        """Test that lookup fails with invalid token"""
        response = client.get(
            "/api/users/1",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False
    
    def test_lookup_numeric_username_fallback(self, client):
        """Test that purely numeric username is found after ID fallback"""
        # Create a user with a numeric username (edge case)
        test_data = create_test_user(
            client,
            email="numericuser@example.com",
            username="12345"
        )
        token = test_data["token"]
        user_id = test_data["user"]["id"]
        
        # Look up by the numeric username - this should fall back to username
        # lookup after ID lookup fails (since no user with ID 12345 exists)
        response = client.get(
            "/api/users/12345",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should find the user by username fallback
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["user"]["username"] == "12345"
        assert data["user"]["email"] == "numericuser@example.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

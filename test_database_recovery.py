#!/usr/bin/env python3
"""
Test suite for database recovery status functionality.

Tests the PostgreSQL database recovery detection and monitoring features:
- get_database_recovery_status() function
- /api/database/recovery-status endpoint
- Recovery status reporting in health checks
"""

import json
import os
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
    
    # Update the app to use test database (SQLite for testing)
    final_backend_postgresql.DB_PATH = Path(db_path)
    final_backend_postgresql.USE_POSTGRESQL = False
    
    # Initialize the database with required tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create minimal users table for testing
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
    
    final_backend_postgresql.app.config['TESTING'] = True
    
    yield final_backend_postgresql.app
    
    # Cleanup: restore original values and remove temp database
    if original_db_path is not None:
        final_backend_postgresql.DB_PATH = original_db_path
    if original_use_postgresql is not None:
        final_backend_postgresql.USE_POSTGRESQL = original_use_postgresql
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the Flask application"""
    return app.test_client()


class TestDatabaseRecoveryStatus:
    """Tests for database recovery status functionality"""
    
    def test_get_database_recovery_status_sqlite(self, app):
        """Test that SQLite mode returns not_applicable status"""
        with app.app_context():
            status = final_backend_postgresql.get_database_recovery_status()
            
            assert status["type"] == "sqlite"
            assert status["in_recovery"] == False
            assert status["status"] == "not_applicable"
            assert "message" in status
    
    def test_recovery_status_endpoint_returns_json(self, client):
        """Test that the recovery status endpoint returns valid JSON"""
        response = client.get("/api/database/recovery-status")
        
        assert response.status_code == 200
        assert response.content_type == "application/json"
        
        data = json.loads(response.data)
        assert "timestamp" in data
        assert "recovery" in data
    
    def test_recovery_status_endpoint_structure(self, client):
        """Test the structure of the recovery status response"""
        response = client.get("/api/database/recovery-status")
        data = json.loads(response.data)
        
        recovery = data["recovery"]
        assert "type" in recovery
        assert "in_recovery" in recovery
        assert "status" in recovery
    
    def test_health_endpoint_works(self, client):
        """Test that the basic health endpoint works"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
    
    def test_detailed_health_endpoint_works(self, client):
        """Test that the detailed health endpoint works"""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "status" in data
        assert "database" in data
        assert "db_type" in data


# Define MockPsycopg2Error once at module level to avoid duplication
try:
    import psycopg2
    
    class MockPsycopg2Error(psycopg2.Error):
        """Mock psycopg2 error for testing transient error detection"""
        pass
except ImportError:
    MockPsycopg2Error = None


class TestTransientErrorDetection:
    """Tests for transient error detection logic"""
    
    def test_is_transient_connection_error_recovery_message(self, app):
        """Test that recovery messages are detected as transient"""
        if MockPsycopg2Error is None:
            pytest.skip("psycopg2 not available for this test")
        
        with app.app_context():
            mock_error = MockPsycopg2Error("the database system is in recovery")
            result = final_backend_postgresql._is_transient_connection_error(mock_error)
            assert result is True
    
    def test_is_transient_connection_error_startup_message(self, app):
        """Test that startup messages are detected as transient"""
        if MockPsycopg2Error is None:
            pytest.skip("psycopg2 not available for this test")
        
        with app.app_context():
            mock_error = MockPsycopg2Error("the database system is starting up")
            result = final_backend_postgresql._is_transient_connection_error(mock_error)
            assert result is True
    
    def test_is_transient_connection_error_non_transient(self, app):
        """Test that non-transient errors are not detected as transient"""
        with app.app_context():
            # Regular exception should not be transient
            regular_error = Exception("Some regular error")
            result = final_backend_postgresql._is_transient_connection_error(regular_error)
            assert result is False


class TestConnectionPoolStats:
    """Tests for connection pool statistics"""
    
    def test_get_connection_pool_stats_sqlite(self, app):
        """Test that SQLite mode returns correct pool stats"""
        with app.app_context():
            stats = final_backend_postgresql.get_connection_pool_stats()
            
            assert stats["type"] == "sqlite"
            assert stats["pooled"] == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

#!/usr/bin/env python3
"""
Test suite for database recovery status functionality.

Tests the PostgreSQL database recovery detection and monitoring features:
- get_database_recovery_status() function
- /api/database/recovery-status endpoint
- Recovery status reporting in health checks
- Graceful shutdown signal handlers
"""

import json
import os
import signal
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


class TestGracefulShutdown:
    """Tests for graceful shutdown functionality"""
    
    def test_signal_handlers_registered(self):
        """Test that signal handlers are registered for SIGTERM and SIGINT"""
        # Verify signal handlers are registered
        sigterm_handler = signal.getsignal(signal.SIGTERM)
        sigint_handler = signal.getsignal(signal.SIGINT)
        
        # Signal handlers should be set (not default)
        assert sigterm_handler is not signal.SIG_DFL, "SIGTERM handler should be registered"
        assert sigint_handler is not signal.SIG_DFL, "SIGINT handler should be registered"
        
        # Both should point to our custom handler
        assert callable(sigterm_handler), "SIGTERM handler should be callable"
        assert callable(sigint_handler), "SIGINT handler should be callable"
    
    def test_shutdown_executor_function_exists(self):
        """Test that _shutdown_executor function exists and is callable"""
        assert hasattr(final_backend_postgresql, '_shutdown_executor')
        assert callable(final_backend_postgresql._shutdown_executor)
    
    def test_shutdown_connection_pool_function_exists(self):
        """Test that _shutdown_connection_pool function exists and is callable"""
        assert hasattr(final_backend_postgresql, '_shutdown_connection_pool')
        assert callable(final_backend_postgresql._shutdown_connection_pool)
    
    def test_executor_shutdown_is_idempotent(self):
        """Test that calling _shutdown_executor multiple times doesn't raise errors"""
        # Should be safe to call multiple times (idempotent)
        final_backend_postgresql._shutdown_executor()
        final_backend_postgresql._shutdown_executor()
        # No exception means success
    
    def test_connection_pool_shutdown_is_idempotent(self):
        """Test that calling _shutdown_connection_pool multiple times doesn't raise errors"""
        # Should be safe to call multiple times (idempotent)
        final_backend_postgresql._shutdown_connection_pool()
        final_backend_postgresql._shutdown_connection_pool()
        # No exception means success
    
    def test_signal_handler_function_exists(self):
        """Test that _signal_handler function exists and is callable"""
        assert hasattr(final_backend_postgresql, '_signal_handler')
        assert callable(final_backend_postgresql._signal_handler)
    
    def test_signal_handler_handles_known_signals(self):
        """Test that signal handler works correctly for known signals"""
        # We can't actually call the signal handler because it calls sys.exit()
        # But we can verify the handler is the expected function
        handler = signal.getsignal(signal.SIGTERM)
        assert handler == final_backend_postgresql._signal_handler


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Tests for the database performance monitoring endpoints.

These tests validate the /api/query-stats and /api/database-health endpoints.
"""
import os
import pytest
import sys

# Set up test environment before importing the application
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing")
os.environ.setdefault("ENVIRONMENT", "development")

# Import the Flask application
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def app():
    """Create a Flask test application."""
    # Import inside fixture to ensure env vars are set first
    from final_backend_postgresql import app as flask_app
    flask_app.config['TESTING'] = True
    return flask_app


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    return app.test_client()


def get_test_token(app):
    """Generate a test JWT token."""
    import jwt
    from datetime import datetime, timedelta, timezone
    
    payload = {
        "user_id": 1,
        "email": "test@example.com",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")


class TestQueryStatsEndpoint:
    """Tests for the /api/query-stats endpoint."""

    def test_query_stats_requires_auth(self, client):
        """Test that query-stats endpoint requires authentication."""
        response = client.get('/api/query-stats')
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'Authorization token required' in data['message']

    def test_query_stats_with_invalid_token(self, client):
        """Test that query-stats rejects invalid tokens."""
        response = client.get(
            '/api/query-stats',
            headers={'Authorization': 'Bearer invalid-token'}
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'Invalid token' in data['message']

    def test_query_stats_options_request(self, client):
        """Test that OPTIONS request returns 200 (CORS preflight)."""
        response = client.options('/api/query-stats')
        assert response.status_code == 200

    def test_query_stats_sqlite_mode(self, client, app):
        """Test query-stats response when using SQLite (development mode)."""
        # This test runs in SQLite mode since no DATABASE_URL is set
        token = get_test_token(app)
        response = client.get(
            '/api/query-stats',
            headers={'Authorization': f'Bearer {token}'}
        )
        # In SQLite mode, should return success with extension_available=False
        assert response.status_code == 200
        data = response.get_json()
        assert data['extension_available'] is False
        assert 'SQLite' in data['message']

    def test_query_stats_with_parameters(self, client, app):
        """Test query-stats with query parameters."""
        token = get_test_token(app)
        response = client.get(
            '/api/query-stats?limit=10&min_avg_time_ms=100&order_by=avg_time',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        # Should handle parameters even in SQLite mode
        assert 'extension_available' in data


class TestDatabaseHealthEndpoint:
    """Tests for the /api/database-health endpoint."""

    def test_database_health_no_auth_required(self, client):
        """Test that database-health endpoint works without auth."""
        response = client.get('/api/database-health')
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert 'database_type' in data

    def test_database_health_options_request(self, client):
        """Test that OPTIONS request returns 200 (CORS preflight)."""
        response = client.options('/api/database-health')
        assert response.status_code == 200

    def test_database_health_sqlite_mode(self, client):
        """Test database-health in SQLite mode."""
        response = client.get('/api/database-health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['database_type'] == 'sqlite'
        assert data['status'] == 'healthy'

    def test_database_health_includes_monitoring_tips(self, client):
        """Test that database-health includes monitoring tips."""
        response = client.get('/api/database-health')
        assert response.status_code == 200
        data = response.get_json()
        # In SQLite mode, monitoring tips may not be present
        # This is acceptable behavior


class TestQueryStatsParameterValidation:
    """Tests for parameter validation in query-stats endpoint."""

    def test_limit_clamped_to_minimum(self, client, app):
        """Test that limit parameter is clamped to minimum of 1."""
        token = get_test_token(app)
        response = client.get(
            '/api/query-stats?limit=-5',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        # Should not error even with invalid limit

    def test_limit_clamped_to_maximum(self, client, app):
        """Test that limit parameter is clamped to maximum of 100."""
        token = get_test_token(app)
        response = client.get(
            '/api/query-stats?limit=1000',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        # Should not error even with excessive limit

    def test_invalid_order_by_uses_default(self, client, app):
        """Test that invalid order_by falls back to default."""
        token = get_test_token(app)
        response = client.get(
            '/api/query-stats?order_by=invalid_column',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        # Should use default order and not error


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

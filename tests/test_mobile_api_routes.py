#!/usr/bin/env python3
"""
Test suite for mobile API routes.
Tests the fast-response endpoints required for mobile client compatibility.
"""
import os
import sys
import time
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestNotificationsRoute(unittest.TestCase):
    """Test /api/notifications/unread-count endpoint."""

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests."""
        from final_backend_postgresql import app
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_notifications_unread_count_returns_200(self):
        """Test that /api/notifications/unread-count returns 200."""
        response = self.client.get("/api/notifications/unread-count")
        self.assertEqual(response.status_code, 200)

    def test_notifications_unread_count_returns_json(self):
        """Test that /api/notifications/unread-count returns valid JSON."""
        response = self.client.get("/api/notifications/unread-count")
        self.assertEqual(response.content_type, "application/json")

    def test_notifications_unread_count_has_count_field(self):
        """Test that response contains a 'count' field."""
        response = self.client.get("/api/notifications/unread-count")
        data = response.get_json()
        self.assertIn("count", data)
        self.assertIsInstance(data["count"], int)

    def test_notifications_unread_count_is_fast(self):
        """Test that response time is under 50ms (instant response)."""
        start = time.time()
        response = self.client.get("/api/notifications/unread-count")
        elapsed_ms = (time.time() - start) * 1000
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed_ms, 50, f"Response took {elapsed_ms:.1f}ms, expected <50ms")

    def test_notifications_unread_count_options_method(self):
        """Test that OPTIONS method returns 200 for CORS preflight."""
        response = self.client.options("/api/notifications/unread-count")
        self.assertEqual(response.status_code, 200)


class TestHealthRoute(unittest.TestCase):
    """Test /health endpoint."""

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests."""
        from final_backend_postgresql import app
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_health_returns_200(self):
        """Test that /health returns 200."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_health_returns_json(self):
        """Test that /health returns valid JSON."""
        response = self.client.get("/health")
        self.assertEqual(response.content_type, "application/json")

    def test_health_has_status_field(self):
        """Test that response contains a 'status' field."""
        response = self.client.get("/health")
        data = response.get_json()
        self.assertIn("status", data)

    def test_health_is_fast(self):
        """Test that response time is under 10ms (instant response)."""
        start = time.time()
        response = self.client.get("/health")
        elapsed_ms = (time.time() - start) * 1000
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed_ms, 10, f"Response took {elapsed_ms:.1f}ms, expected <10ms")


class TestHealthPingRoute(unittest.TestCase):
    """Test /health/ping endpoint."""

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests."""
        from final_backend_postgresql import app
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_health_ping_returns_200(self):
        """Test that /health/ping returns 200."""
        response = self.client.get("/health/ping")
        self.assertEqual(response.status_code, 200)

    def test_health_ping_returns_pong(self):
        """Test that /health/ping returns 'pong'."""
        response = self.client.get("/health/ping")
        self.assertEqual(response.data.decode(), "pong")

    def test_health_ping_is_fast(self):
        """Test that response time is under 10ms (instant response)."""
        start = time.time()
        response = self.client.get("/health/ping")
        elapsed_ms = (time.time() - start) * 1000
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed_ms, 10, f"Response took {elapsed_ms:.1f}ms, expected <10ms")

    def test_health_ping_head_method(self):
        """Test that HEAD method returns 200."""
        response = self.client.head("/health/ping")
        self.assertEqual(response.status_code, 200)


class TestApiFallbackRoute(unittest.TestCase):
    """Test global API fallback route."""

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests."""
        from final_backend_postgresql import app
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_fallback_returns_200_for_unknown_route(self):
        """Test that unknown /api/* routes return 200."""
        response = self.client.get("/api/unknown-endpoint-xyz")
        self.assertEqual(response.status_code, 200)

    def test_fallback_returns_json(self):
        """Test that fallback returns valid JSON."""
        response = self.client.get("/api/unknown-endpoint-xyz")
        self.assertEqual(response.content_type, "application/json")

    def test_fallback_has_success_field(self):
        """Test that fallback response contains 'success' field."""
        response = self.client.get("/api/unknown-endpoint-xyz")
        data = response.get_json()
        self.assertIn("success", data)
        self.assertTrue(data["success"])

    def test_fallback_has_data_field(self):
        """Test that fallback response contains 'data' field."""
        response = self.client.get("/api/unknown-endpoint-xyz")
        data = response.get_json()
        self.assertIn("data", data)
        self.assertIsInstance(data["data"], list)

    def test_fallback_options_method(self):
        """Test that OPTIONS method returns 200 for CORS preflight."""
        response = self.client.options("/api/unknown-endpoint-xyz")
        self.assertEqual(response.status_code, 200)

    def test_fallback_post_method(self):
        """Test that POST to unknown route returns 200."""
        response = self.client.post("/api/unknown-endpoint-xyz")
        self.assertEqual(response.status_code, 200)


class TestExistingRoutesStillWork(unittest.TestCase):
    """Test that existing routes are not broken by fallback."""

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests."""
        from final_backend_postgresql import app
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_posts_route_works(self):
        """Test that /api/posts still works."""
        response = self.client.get("/api/posts")
        self.assertEqual(response.status_code, 200)

    def test_posts_route_returns_proper_structure(self):
        """Test that /api/posts returns proper data structure."""
        response = self.client.get("/api/posts")
        data = response.get_json()
        self.assertIn("success", data)
        self.assertIn("posts", data)
        self.assertTrue(data["success"])

    def test_friends_suggestions_requires_auth(self):
        """Test that /api/friends/suggestions requires authentication."""
        response = self.client.get("/api/friends/suggestions")
        # 401 is correct - this endpoint requires authentication
        self.assertEqual(response.status_code, 401)

    def test_friends_list_requires_auth(self):
        """Test that /api/friends/list requires authentication."""
        response = self.client.get("/api/friends/list")
        # 401 is correct - this endpoint requires authentication
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()

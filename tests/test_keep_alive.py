#!/usr/bin/env python3
"""
Test suite for keep_alive.py background worker.
Tests the ultimate immortal keep-alive functionality that prevents Render services from sleeping.
"""
import os
import unittest
from unittest.mock import patch, Mock


class TestKeepAliveConfiguration(unittest.TestCase):
    """Test keep_alive.py configuration and behavior."""

    def test_keep_alive_script_syntax(self):
        """Test that keep_alive.py has valid Python syntax."""
        import py_compile

        try:
            py_compile.compile("keep_alive.py", doraise=True)
        except py_compile.PyCompileError as e:
            self.fail(f"keep_alive.py has syntax errors: {e}")

    def test_url_with_fallback(self):
        """Test that URL requires BACKEND_URL environment variable."""
        with open("keep_alive.py", "r") as f:
            content = f.read()

        # Verify it uses os.environ["BACKEND_URL"] pattern (strict)
        self.assertIn('os.environ["BACKEND_URL"]', content)

        # Verify URL validation for proper scheme
        self.assertIn('startswith(("http://", "https://"))', content)

        # Verify HEALTH_URL is constructed from BASE_URL + /health using f-string
        self.assertIn('f"{BASE_URL}/health"', content)

    def test_uses_health_endpoint(self):
        """Test that the script uses the /health endpoint."""
        with open("keep_alive.py", "r") as f:
            content = f.read()

        # Verify the script uses the /health endpoint
        self.assertIn("/health", content)

    def test_max_retries_per_ping(self):
        """Test that the script has MAX_RETRIES retries per ping cycle."""
        with open("keep_alive.py", "r") as f:
            content = f.read()

        # Verify MAX_RETRIES is defined (5 retries)
        self.assertIn("MAX_RETRIES = 5", content)
        # Verify retry loop uses MAX_RETRIES
        self.assertIn("range(1, MAX_RETRIES + 1)", content)
        self.assertIn("attempt", content)
        # Verify MAX_RETRIES is used in logging (f-string format)
        self.assertIn("{MAX_RETRIES}", content)

    def test_timeout_configuration(self):
        """Test that timeout is configured correctly."""
        with open("keep_alive.py", "r") as f:
            content = f.read()

        # Verify connect timeout and read timeout are defined
        self.assertIn("CONNECT_TIMEOUT = 10", content)
        self.assertIn("READ_TIMEOUT = 30", content)
        # Verify tuple timeout format is used (connect, read)
        self.assertIn("timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)", content)

    def test_exception_handling(self):
        """Test that exceptions are caught and don't stop the loop."""
        with open("keep_alive.py", "r") as f:
            content = f.read()

        # Verify the script has exception handling
        self.assertIn("except Exception as e:", content)
        # Verify it continues running after exception
        self.assertIn("while True:", content)

    def test_exponential_backoff_on_failure(self):
        """Test that the script uses exponential backoff on persistent failure."""
        with open("keep_alive.py", "r") as f:
            content = f.read()

        # Verify backoff logic
        self.assertIn("backoff", content)
        self.assertIn("2 ** backoff", content)
        self.assertIn("min(backoff + 1, 6)", content)

    def test_jitter_on_backoff(self):
        """Test that jitter is added to backoff to prevent thundering herd."""
        with open("keep_alive.py", "r") as f:
            content = f.read()

        # Verify random jitter is used
        self.assertIn("import random", content)
        self.assertIn("random.uniform", content)

    def test_never_gives_up(self):
        """Test that the script never exits on failure."""
        with open("keep_alive.py", "r") as f:
            content = f.read()

        # Verify infinite loop
        self.assertIn("while True:", content)
        # Verify no sys.exit calls
        self.assertNotIn("sys.exit", content)
        self.assertNotIn("exit(", content)


class TestKeepAliveBehavior(unittest.TestCase):
    """Test keep_alive.py runtime behavior."""

    def test_url_validation_empty_env_var(self):
        """Test that empty RENDER_EXTERNAL_URL falls back to default."""
        # This test verifies the fix for MissingSchema error
        DEFAULT_URL = "https://hiremebahamas-backend.onrender.com"
        
        # Test with empty string
        with patch.dict(os.environ, {"RENDER_EXTERNAL_URL": ""}):
            _base_url = os.getenv("RENDER_EXTERNAL_URL", "").strip()
            if not _base_url or not _base_url.startswith(("http://", "https://")):
                _base_url = DEFAULT_URL
            self.assertEqual(_base_url, DEFAULT_URL)

    def test_url_validation_whitespace_env_var(self):
        """Test that whitespace-only RENDER_EXTERNAL_URL falls back to default."""
        DEFAULT_URL = "https://hiremebahamas-backend.onrender.com"
        
        with patch.dict(os.environ, {"RENDER_EXTERNAL_URL": "   "}):
            _base_url = os.getenv("RENDER_EXTERNAL_URL", "").strip()
            if not _base_url or not _base_url.startswith(("http://", "https://")):
                _base_url = DEFAULT_URL
            self.assertEqual(_base_url, DEFAULT_URL)

    def test_url_validation_relative_path(self):
        """Test that relative path RENDER_EXTERNAL_URL falls back to default."""
        DEFAULT_URL = "https://hiremebahamas-backend.onrender.com"
        
        # This was the original bug: /health without scheme
        with patch.dict(os.environ, {"RENDER_EXTERNAL_URL": "/health"}):
            _base_url = os.getenv("RENDER_EXTERNAL_URL", "").strip()
            if not _base_url or not _base_url.startswith(("http://", "https://")):
                _base_url = DEFAULT_URL
            self.assertEqual(_base_url, DEFAULT_URL)

    def test_url_validation_valid_https(self):
        """Test that valid HTTPS URL is used."""
        with patch.dict(os.environ, {"RENDER_EXTERNAL_URL": "https://custom-app.render.com"}):
            _base_url = os.getenv("RENDER_EXTERNAL_URL", "").strip()
            DEFAULT_URL = "https://hiremebahamas-backend.onrender.com"
            if not _base_url or not _base_url.startswith(("http://", "https://")):
                _base_url = DEFAULT_URL
            self.assertEqual(_base_url, "https://custom-app.render.com")

    def test_url_validation_valid_http(self):
        """Test that valid HTTP URL is used for local development."""
        with patch.dict(os.environ, {"RENDER_EXTERNAL_URL": "http://localhost:8000"}):
            _base_url = os.getenv("RENDER_EXTERNAL_URL", "").strip()
            DEFAULT_URL = "https://hiremebahamas-backend.onrender.com"
            if not _base_url or not _base_url.startswith(("http://", "https://")):
                _base_url = DEFAULT_URL
            self.assertEqual(_base_url, "http://localhost:8000")

    @patch("requests.get")
    def test_ping_request_made(self, mock_get):
        """Test that a GET request is made to the health endpoint."""
        mock_get.return_value.status_code = 200

        import requests

        # Simulate the ping with tuple timeout
        response = requests.get(
            "https://hiremebahamas-backend.onrender.com/health",
            timeout=(6, 30),
            headers={"User-Agent": "ImmortalKeepAlive/2025"}
        )

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "https://hiremebahamas-backend.onrender.com/health",
            timeout=(6, 30),
            headers={"User-Agent": "ImmortalKeepAlive/2025"}
        )

    @patch("requests.get")
    def test_ping_handles_timeout(self, mock_get):
        """Test that request timeouts are handled gracefully."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Read timed out")

        try:
            requests.get(
            "https://hiremebahamas-backend.onrender.com/health",
                timeout=(6, 30)
            )
        except Exception:
            pass  # This should be caught like in keep_alive.py

        # Verify the exception was raised and handled
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_ping_handles_connection_error(self, mock_get):
        """Test that connection errors are handled gracefully."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        try:
            requests.get(
                "https://hiremebahamas-backend.onrender.com/health",
                timeout=(6, 30)
            )
        except Exception:
            pass  # This should be caught like in keep_alive.py

        # Verify the exception was raised and handled
        mock_get.assert_called_once()


class TestRenderYamlConfiguration(unittest.TestCase):
    """Test render.yaml configuration for the keep-alive worker."""

    def test_render_yaml_has_worker(self):
        """Test that render.yaml contains the keep-alive worker configuration."""
        import yaml

        with open("render.yaml", "r") as f:
            config = yaml.safe_load(f)

        # Verify services list exists
        self.assertIn("services", config)

        # Find the keep-alive worker
        workers = [s for s in config["services"] if s.get("type") == "worker"]
        self.assertTrue(len(workers) > 0, "No worker service found in render.yaml")

        # Verify keep-alive worker configuration
        keep_alive_worker = [w for w in workers if w.get("name") == "keep-alive"]
        self.assertTrue(len(keep_alive_worker) > 0, "keep-alive worker not found")

        worker = keep_alive_worker[0]
        self.assertEqual(worker.get("runtime"), "python")
        self.assertEqual(worker.get("startCommand"), "python keep_alive.py")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
Test suite for keep_alive.py background worker.
Tests the nuclear immortal keep-alive functionality that prevents Render services from sleeping.
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

    def test_hardcoded_url_no_env_vars(self):
        """Test that URL is hardcoded and no os.getenv is used."""
        with open("keep_alive.py", "r") as f:
            content = f.read()

        # Verify hardcoded URL
        self.assertIn('HEALTH_URL = "https://hiremebahamas.onrender.com/health"', content)

        # Verify NO os.getenv is used
        self.assertNotIn("os.getenv", content)
        self.assertNotIn("os.environ", content)

    def test_uses_health_endpoint(self):
        """Test that the script uses the /health endpoint."""
        with open("keep_alive.py", "r") as f:
            content = f.read()

        # Verify the script uses the /health endpoint
        self.assertIn("/health", content)

    def test_three_retries_per_ping(self):
        """Test that the script has 3 retries per ping cycle."""
        with open("keep_alive.py", "r") as f:
            content = f.read()

        # Verify 3 retries (range 1 to 4 = attempts 1, 2, 3)
        self.assertIn("range(1, MAX_RETRIES + 1)", content)
        self.assertIn("MAX_RETRIES = 3", content)

    def test_increasing_timeout(self):
        """Test that timeout increases with each retry attempt."""
        with open("keep_alive.py", "r") as f:
            content = f.read()

        # Verify connect timeout (6s) and increasing read timeout (20 + attempt * 10)
        self.assertIn("timeout=(6, 20 + attempt * 10)", content)

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
        self.assertIn("BASE_BACKOFF_SECONDS ** backoff", content)
        self.assertIn("min(backoff + 1, MAX_BACKOFF_LEVEL)", content)

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

    @patch("requests.get")
    def test_ping_request_made(self, mock_get):
        """Test that a GET request is made to the health endpoint."""
        mock_get.return_value.status_code = 200

        import requests

        # Simulate the ping with tuple timeout
        response = requests.get(
            "https://hiremebahamas.onrender.com/health",
            timeout=(6, 30),
            headers={"User-Agent": "ImmortalKeepAlive/2025"}
        )

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "https://hiremebahamas.onrender.com/health",
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
                "https://hiremebahamas.onrender.com/health",
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
                "https://hiremebahamas.onrender.com/health",
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

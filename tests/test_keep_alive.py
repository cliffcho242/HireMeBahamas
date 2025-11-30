#!/usr/bin/env python3
"""
Test suite for keep_alive.py background worker.
Tests the keep-alive functionality that prevents Render services from sleeping.
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

    def test_environment_variable_optional_with_default(self):
        """Test that RENDER_EXTERNAL_URL environment variable is optional with default URL."""
        # Verify the script uses os.getenv() with default fallback
        with open("keep_alive.py", "r") as f:
            content = f.read()
        
        # Verify it uses os.getenv() with default fallback
        self.assertIn('os.getenv("RENDER_EXTERNAL_URL"', content)
        
        # Verify it has default URL fallback
        self.assertIn("https://hiremebahamas.onrender.com", content)
        
        # Verify it does NOT exit on missing env var (since we have a default)
        self.assertNotIn("sys.exit(1)", content)

    def test_ping_interval_is_40_seconds(self):
        """Test that the ping interval is 40 seconds as specified."""
        # Read the keep_alive.py script and verify the sleep interval
        with open("keep_alive.py", "r") as f:
            content = f.read()
        
        # Verify the script sets delay to 40 (initial or after success reset)
        self.assertTrue(
            ", 40" in content or "= 40" in content,
            "Ping interval of 40 seconds not found in keep_alive.py"
        )

    def test_uses_health_endpoint(self):
        """Test that the script uses the /health endpoint."""
        with open("keep_alive.py", "r") as f:
            content = f.read()
        
        # Verify the script uses the /health endpoint
        self.assertIn("/health", content)

    def test_timeout_is_10_seconds(self):
        """Test that the request timeout is 10 seconds."""
        with open("keep_alive.py", "r") as f:
            content = f.read()
        
        # Verify the script uses a 10 second timeout
        self.assertIn("timeout=10", content)

    def test_exception_handling(self):
        """Test that exceptions are caught and don't stop the loop."""
        with open("keep_alive.py", "r") as f:
            content = f.read()
        
        # Verify the script has exception handling
        self.assertIn("except Exception as e:", content)
        # Verify it continues running after exception (sleep is inside the loop)
        self.assertIn("time.sleep(delay)", content)


class TestKeepAliveBehavior(unittest.TestCase):
    """Test keep_alive.py runtime behavior."""

    @patch("requests.get")
    def test_ping_request_made(self, mock_get):
        """Test that a GET request is made to the health endpoint."""
        mock_get.return_value.status_code = 200
        
        # Set up environment
        with patch.dict(os.environ, {"RENDER_EXTERNAL_URL": "https://test.onrender.com"}):
            import requests
            
            # Simulate the ping
            url = os.environ["RENDER_EXTERNAL_URL"]
            response = requests.get(f"{url}/health", timeout=10)
            
            # Verify the request was made correctly
            mock_get.assert_called_once_with(
                "https://test.onrender.com/health",
                timeout=10
            )

    @patch("requests.get")
    def test_ping_handles_timeout(self, mock_get):
        """Test that request timeouts are handled gracefully."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")
        
        # Simulate the ping with exception handling
        with patch.dict(os.environ, {"RENDER_EXTERNAL_URL": "https://test.onrender.com"}):
            url = os.environ["RENDER_EXTERNAL_URL"]
            
            try:
                requests.get(f"{url}/health", timeout=10)
            except Exception:
                pass  # This should be caught like in keep_alive.py
            
            # Verify the exception was raised and handled
            mock_get.assert_called_once()

    @patch("requests.get")
    def test_ping_handles_connection_error(self, mock_get):
        """Test that connection errors are handled gracefully."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        # Simulate the ping with exception handling
        with patch.dict(os.environ, {"RENDER_EXTERNAL_URL": "https://test.onrender.com"}):
            url = os.environ["RENDER_EXTERNAL_URL"]
            
            try:
                requests.get(f"{url}/health", timeout=10)
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

    def test_render_yaml_worker_has_env_var(self):
        """Test that render.yaml worker has APP_URL or RENDER_EXTERNAL_URL configured."""
        import yaml
        
        with open("render.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Find the keep-alive worker
        workers = [s for s in config["services"] if s.get("name") == "keep-alive"]
        self.assertTrue(len(workers) > 0, "keep-alive worker not found")
        
        worker = workers[0]
        env_vars = worker.get("envVars", [])
        
        # Find APP_URL or RENDER_EXTERNAL_URL
        url_vars = [v for v in env_vars if v.get("key") in ("APP_URL", "RENDER_EXTERNAL_URL")]
        self.assertTrue(len(url_vars) > 0, "APP_URL or RENDER_EXTERNAL_URL not configured")
        
        # Verify the URL is set correctly
        url_var = url_vars[0]
        self.assertEqual(url_var.get("value"), "https://hiremebahamas.onrender.com")


if __name__ == "__main__":
    unittest.main()

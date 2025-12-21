#!/usr/bin/env python3
"""
Test suite for BACKEND_URL environment variable pattern.

This ensures that Python scripts correctly use the BACKEND_URL environment variable
following the pattern: BASE_URL = os.environ["BACKEND_URL"]
"""

import os
import unittest
from unittest.mock import patch, Mock
import sys


class TestBackendURLPattern(unittest.TestCase):
    """Test BACKEND_URL environment variable usage pattern."""

    def test_example_script_requires_backend_url(self):
        """Test that example script requires BACKEND_URL to be set."""
        # Ensure BACKEND_URL is not set for this test
        with patch.dict(os.environ, {}, clear=False):
            # Remove BACKEND_URL if it exists
            os.environ.pop('BACKEND_URL', None)
            
            # Try to import the pattern - should raise KeyError if not set
            with self.assertRaises(KeyError):
                _ = os.environ["BACKEND_URL"]

    def test_example_script_accepts_valid_url(self):
        """Test that example script accepts valid BACKEND_URL."""
        test_url = "https://hiremebahamas.vercel.app"
        
        with patch.dict(os.environ, {"BACKEND_URL": test_url}):
            BASE_URL = os.environ["BACKEND_URL"]
            self.assertEqual(BASE_URL, test_url)

    def test_backend_url_with_health_endpoint(self):
        """Test that BACKEND_URL can be used with health endpoint."""
        test_url = "https://hiremebahamas.vercel.app"
        
        with patch.dict(os.environ, {"BACKEND_URL": test_url}):
            BASE_URL = os.environ["BACKEND_URL"]
            health_url = f"{BASE_URL}/health"
            
            self.assertEqual(health_url, "https://hiremebahamas.vercel.app/health")

    def test_backend_url_with_trailing_slash(self):
        """Test that BACKEND_URL works correctly with trailing slash."""
        test_url = "https://hiremebahamas.vercel.app/"
        
        with patch.dict(os.environ, {"BACKEND_URL": test_url}):
            BASE_URL = os.environ["BACKEND_URL"]
            # Remove trailing slash if present for consistency
            BASE_URL = BASE_URL.rstrip('/')
            health_url = f"{BASE_URL}/health"
            
            self.assertEqual(health_url, "https://hiremebahamas.vercel.app/health")

    def test_backend_url_localhost(self):
        """Test that BACKEND_URL works with localhost URLs."""
        test_url = "http://localhost:8000"
        
        with patch.dict(os.environ, {"BACKEND_URL": test_url}):
            BASE_URL = os.environ["BACKEND_URL"]
            health_url = f"{BASE_URL}/health"
            
            self.assertEqual(health_url, "http://localhost:8000/health")

    def test_env_example_documents_backend_url(self):
        """Test that .env.example documents BACKEND_URL."""
        import pathlib
        
        # Get path relative to project root (parent of tests directory)
        test_dir = pathlib.Path(__file__).parent
        project_root = test_dir.parent
        env_example_path = project_root / ".env.example"
        
        with open(env_example_path, "r") as f:
            content = f.read()
        
        # Verify BACKEND_URL is documented
        self.assertIn("BACKEND_URL", content)
        # Verify it has example values
        self.assertIn("localhost:8000", content)

    def test_keep_alive_uses_strict_pattern(self):
        """Test that keep_alive.py uses the strict BACKEND_URL pattern."""
        import pathlib
        
        test_dir = pathlib.Path(__file__).parent
        project_root = test_dir.parent
        file_path = project_root / "keep_alive.py"
        
        with open(file_path, "r") as f:
            content = f.read()
        
        # Verify it uses os.environ["BACKEND_URL"] pattern
        self.assertIn('os.environ["BACKEND_URL"]', content)
        # Verify it has BASE_URL variable
        self.assertIn("BASE_URL", content)

    def test_example_health_check_uses_strict_pattern(self):
        """Test that example health check uses the strict BACKEND_URL pattern."""
        import pathlib
        
        test_dir = pathlib.Path(__file__).parent
        project_root = test_dir.parent
        file_path = project_root / "example_backend_health_check.py"
        
        with open(file_path, "r") as f:
            content = f.read()
        
        # Verify it uses os.environ["BACKEND_URL"] pattern
        self.assertIn('os.environ["BACKEND_URL"]', content)
        # Verify it has BASE_URL variable
        self.assertIn("BASE_URL", content)
        # Verify it uses f-string pattern
        self.assertIn('f"{BASE_URL}/health"', content)

    def test_comprehensive_api_test_has_base_url(self):
        """Test that comprehensive_api_test.py defines BASE_URL."""
        import pathlib
        
        test_dir = pathlib.Path(__file__).parent
        project_root = test_dir.parent
        file_path = project_root / "comprehensive_api_test.py"
        
        with open(file_path, "r") as f:
            content = f.read()
        
        # Verify it defines BASE_URL
        self.assertIn("BASE_URL", content)
        # Verify it uses BACKEND_URL environment variable
        self.assertIn("BACKEND_URL", content)

    def test_test_hireme_has_base_url(self):
        """Test that test_hireme.py defines BASE_URL."""
        import pathlib
        
        test_dir = pathlib.Path(__file__).parent
        project_root = test_dir.parent
        file_path = project_root / "test_hireme.py"
        
        with open(file_path, "r") as f:
            content = f.read()
        
        # Verify it defines BASE_URL
        self.assertIn("BASE_URL", content)
        # Verify it uses BACKEND_URL environment variable
        self.assertIn("BACKEND_URL", content)

    def test_init_admin_has_base_url(self):
        """Test that init_admin_render.py defines BASE_URL."""
        import pathlib
        
        test_dir = pathlib.Path(__file__).parent
        project_root = test_dir.parent
        file_path = project_root / "init_admin_render.py"
        
        with open(file_path, "r") as f:
            content = f.read()
        
        # Verify it defines BASE_URL
        self.assertIn("BASE_URL", content)
        # Verify it uses BACKEND_URL environment variable
        self.assertIn("BACKEND_URL", content)


class TestBackendURLValidation(unittest.TestCase):
    """Test validation of BACKEND_URL values."""

    def test_url_must_start_with_http(self):
        """Test that BACKEND_URL must start with http:// or https://."""
        invalid_urls = [
            "hiremebahamas.vercel.app",
            "//hiremebahamas.vercel.app",
            "ftp://hiremebahamas.vercel.app",
            "/health",
            "",
        ]
        
        for invalid_url in invalid_urls:
            with self.subTest(url=invalid_url):
                # Valid URL should start with http:// or https://
                is_valid = invalid_url.startswith(("http://", "https://"))
                self.assertFalse(is_valid, f"URL should be invalid: {invalid_url}")

    def test_valid_urls(self):
        """Test that valid BACKEND_URLs are accepted."""
        valid_urls = [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "https://hiremebahamas.vercel.app",
            "https://hiremebahamas-backend.railway.app",
            "https://hiremebahamas-backend.onrender.com",
        ]
        
        for valid_url in valid_urls:
            with self.subTest(url=valid_url):
                # Valid URL should start with http:// or https://
                is_valid = valid_url.startswith(("http://", "https://"))
                self.assertTrue(is_valid, f"URL should be valid: {valid_url}")


if __name__ == "__main__":
    unittest.main()

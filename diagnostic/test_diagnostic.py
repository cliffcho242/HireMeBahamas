#!/usr/bin/env python3
"""
Basic tests for the Vercel connection diagnostic tool
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add parent directory to path to import the diagnostic module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from diagnostic.check_vercel_connection import VercelDiagnostic, DiagnosticResult


class TestDiagnosticResult(unittest.TestCase):
    """Test DiagnosticResult class"""
    
    def test_create_result(self):
        """Test creating a diagnostic result"""
        result = DiagnosticResult(
            name="Test Check",
            passed=True,
            message="Test passed",
            duration_ms=100,
            details={"key": "value"}
        )
        
        self.assertEqual(result.name, "Test Check")
        self.assertTrue(result.passed)
        self.assertEqual(result.message, "Test passed")
        self.assertEqual(result.duration_ms, 100)
        self.assertEqual(result.details, {"key": "value"})
    
    def test_create_result_without_optional_fields(self):
        """Test creating a diagnostic result without optional fields"""
        result = DiagnosticResult(
            name="Test Check",
            passed=False,
            message="Test failed"
        )
        
        self.assertEqual(result.name, "Test Check")
        self.assertFalse(result.passed)
        self.assertEqual(result.message, "Test failed")
        self.assertIsNone(result.duration_ms)
        self.assertEqual(result.details, {})


class TestVercelDiagnostic(unittest.TestCase):
    """Test VercelDiagnostic class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.url = "https://test.vercel.app"
        self.diagnostic = VercelDiagnostic(self.url, verbose=False)
    
    def test_initialization(self):
        """Test diagnostic initialization"""
        self.assertEqual(self.diagnostic.url, "https://test.vercel.app")
        self.assertFalse(self.diagnostic.verbose)
        self.assertIsNone(self.diagnostic.output_file)
        self.assertEqual(len(self.diagnostic.results), 0)
    
    def test_url_normalization(self):
        """Test URL is normalized (trailing slash removed)"""
        diagnostic = VercelDiagnostic("https://test.vercel.app/")
        self.assertEqual(diagnostic.url, "https://test.vercel.app")
    
    def test_verbose_mode(self):
        """Test verbose mode"""
        diagnostic = VercelDiagnostic(self.url, verbose=True)
        self.assertTrue(diagnostic.verbose)
    
    def test_output_file(self):
        """Test output file setting"""
        diagnostic = VercelDiagnostic(self.url, output_file="test.txt")
        self.assertEqual(diagnostic.output_file, "test.txt")
    
    def test_check_json_response(self):
        """Test JSON response validation"""
        # Mock response with valid JSON
        mock_response = Mock()
        mock_response.json.return_value = {"status": "ok"}
        
        is_valid, data = self.diagnostic._check_json_response(mock_response)
        self.assertTrue(is_valid)
        self.assertEqual(data, {"status": "ok"})
    
    def test_check_json_response_invalid(self):
        """Test JSON response validation with invalid JSON"""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        is_valid, data = self.diagnostic._check_json_response(mock_response)
        self.assertFalse(is_valid)
        self.assertIsNone(data)
    
    @patch('diagnostic.check_vercel_connection.requests.Session')
    def test_session_creation(self, mock_session_class):
        """Test that session is created with retry logic"""
        diagnostic = VercelDiagnostic(self.url)
        self.assertIsNotNone(diagnostic.session)


class TestCommandLineInterface(unittest.TestCase):
    """Test command-line interface"""
    
    def test_url_validation(self):
        """Test URL validation in main function"""
        from diagnostic.check_vercel_connection import main
        
        # Test invalid URL (no protocol)
        with patch('sys.argv', ['script', '--url', 'invalid-url']):
            with patch('sys.stdout', new=StringIO()):
                exit_code = main()
                # Should return error code 1
                self.assertEqual(exit_code, 1)
    
    def test_help_option(self):
        """Test help option"""
        from diagnostic.check_vercel_connection import main
        
        with patch('sys.argv', ['script', '--help']):
            with self.assertRaises(SystemExit) as cm:
                main()
            # Help should exit with code 0
            self.assertEqual(cm.exception.code, 0)


class TestMockResponse(unittest.TestCase):
    """Test with mocked HTTP responses"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.url = "https://test.vercel.app"
        self.diagnostic = VercelDiagnostic(self.url, verbose=False)
    
    @patch('diagnostic.check_vercel_connection.requests.Session.get')
    def test_successful_health_check(self, mock_get):
        """Test successful health check"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "backend": "available",
            "database": "connected",
            "platform": "vercel-serverless"
        }
        mock_get.return_value = mock_response
        
        # This would normally make a request
        response, error = self.diagnostic._make_request("/api/health")
        
        self.assertIsNotNone(response)
        self.assertIsNone(error)
        self.assertEqual(response.status_code, 200)
    
    @patch('diagnostic.check_vercel_connection.requests.Session.get')
    def test_failed_health_check(self, mock_get):
        """Test failed health check"""
        # Mock failed response
        mock_get.side_effect = Exception("Connection error")
        
        response, error = self.diagnostic._make_request("/api/health")
        
        self.assertIsNone(response)
        self.assertIsNotNone(error)
        self.assertIsInstance(error, Exception)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestDiagnosticResult))
    suite.addTests(loader.loadTestsFromTestCase(TestVercelDiagnostic))
    suite.addTests(loader.loadTestsFromTestCase(TestCommandLineInterface))
    suite.addTests(loader.loadTestsFromTestCase(TestMockResponse))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())

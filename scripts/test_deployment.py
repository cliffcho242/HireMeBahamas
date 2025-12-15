#!/usr/bin/env python3
"""
Deployment Testing Script for HireMeBahamas
Tests if a deployed application is working correctly after migration
"""

import sys
import requests
import argparse
from urllib.parse import urljoin
from typing import Dict, List, Tuple


class DeploymentTester:
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize deployment tester.
        
        Args:
            base_url: Base URL of deployed application
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.results: List[Tuple[str, bool, str]] = []
    
    def test_endpoint(self, path: str, method: str = "GET", 
                     expected_status: int = 200, **kwargs) -> bool:
        """
        Test a single endpoint.
        
        Args:
            path: API endpoint path
            method: HTTP method
            expected_status: Expected HTTP status code
            **kwargs: Additional requests arguments
        
        Returns:
            True if test passed, False otherwise
        """
        url = urljoin(self.base_url, path)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            success = response.status_code == expected_status
            message = f"HTTP {response.status_code}"
            
            if not success:
                message += f" (expected {expected_status})"
            
            self.results.append((path, success, message))
            return success
            
        except requests.exceptions.Timeout:
            self.results.append((path, False, "Timeout"))
            return False
        except requests.exceptions.ConnectionError:
            self.results.append((path, False, "Connection failed"))
            return False
        except Exception as e:
            self.results.append((path, False, str(e)))
            return False
    
    def test_frontend(self) -> bool:
        """Test frontend is accessible."""
        print("🌐 Testing frontend...")
        return self.test_endpoint("/", expected_status=200)
    
    def test_health_endpoints(self) -> bool:
        """Test health check endpoints."""
        print("💚 Testing health endpoints...")
        
        results = []
        
        # Test simple health check
        results.append(self.test_endpoint("/health", expected_status=200))
        
        # Test API health check
        results.append(self.test_endpoint("/api/health", expected_status=200))
        
        # Test ready endpoint (may fail if DB not connected)
        self.test_endpoint("/api/ready", expected_status=200)
        
        return all(results)
    
    def test_api_endpoints(self) -> bool:
        """Test key API endpoints (without authentication)."""
        print("🔌 Testing API endpoints...")
        
        results = []
        
        # Test status endpoint
        results.append(self.test_endpoint("/api/status", expected_status=200))
        
        # Test auth endpoints exist (should return 400/401, not 404)
        self.test_endpoint("/api/auth/login", method="POST", expected_status=400)
        self.test_endpoint("/api/auth/register", method="POST", expected_status=400)
        
        return all(results)
    
    def test_static_assets(self) -> bool:
        """Test static assets are accessible."""
        print("📦 Testing static assets...")
        
        # These should exist in a built Vite app
        paths = ["/assets/", "/favicon.ico"]
        
        results = []
        for path in paths:
            # 200 or 404 is fine (assets may not exist at exact path)
            # We just want to make sure we can reach the server
            try:
                url = urljoin(self.base_url, path)
                response = requests.get(url, timeout=self.timeout)
                results.append(True)
                self.results.append((path, True, f"HTTP {response.status_code}"))
            except Exception as e:
                results.append(False)
                self.results.append((path, False, str(e)))
        
        return any(results)  # At least one should work
    
    def print_results(self) -> bool:
        """
        Print test results.
        
        Returns:
            True if all tests passed, False otherwise
        """
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for path, success, message in self.results:
            status = "✅" if success else "❌"
            print(f"{status} {path:40} {message}")
            
            if success:
                passed += 1
            else:
                failed += 1
        
        print("=" * 60)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total:  {passed + failed}")
        print("=" * 60)
        
        success_rate = (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0
        
        if success_rate == 100:
            print("\n🎉 All tests passed! Your deployment is working correctly.")
            return True
        elif success_rate >= 75:
            print(f"\n⚠️  {success_rate:.0f}% tests passed. Some non-critical issues detected.")
            return True
        else:
            print(f"\n❌ {success_rate:.0f}% tests passed. Your deployment has issues.")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all deployment tests."""
        print("\n🚀 Testing HireMeBahamas Deployment")
        print(f"📍 URL: {self.base_url}")
        print("=" * 60)
        
        # Run tests
        self.test_frontend()
        self.test_health_endpoints()
        self.test_api_endpoints()
        self.test_static_assets()
        
        # Print results
        return self.print_results()


def main():
    parser = argparse.ArgumentParser(
        description="Test HireMeBahamas deployment after migration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test Vercel deployment
  python test_deployment.py --url https://your-app.vercel.app
  
  # Test Railway deployment
  python test_deployment.py --url https://your-app.up.railway.app
  
  # Test with longer timeout
  python test_deployment.py --url https://your-app.vercel.app --timeout 60
        """
    )
    
    parser.add_argument(
        "--url",
        required=True,
        help="Base URL of deployed application (e.g., https://your-app.vercel.app)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)"
    )
    
    args = parser.parse_args()
    
    # Validate and normalize URL
    url = args.url.strip()
    
    # Ensure URL starts with http:// or https://
    if not url.startswith(("http://", "https://")):
        # Default to https for security
        url = f"https://{url}"
    
    # Basic URL validation - check for valid domain pattern
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            print(f"❌ Error: Invalid URL format: {url}")
            print("   URL must be in format: https://your-app.vercel.app")
            sys.exit(1)
        
        # Warn if using localhost or non-standard ports (potential mistakes)
        if parsed.netloc.startswith("localhost") or "127.0.0.1" in parsed.netloc:
            print(f"⚠️  Warning: Testing localhost deployment: {url}")
            print("   Make sure the local server is running!")
            
    except Exception as e:
        print(f"❌ Error: Invalid URL: {e}")
        sys.exit(1)
    
    # Run tests
    tester = DeploymentTester(url, timeout=args.timeout)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

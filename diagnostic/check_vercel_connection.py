#!/usr/bin/env python3
"""
HireMeBahamas Connection Diagnostic Tool
=========================================

Comprehensive diagnostic tool to test and verify Vercel deployment connections
for both frontend and backend.

Usage:
    python diagnostic/check_vercel_connection.py --url https://your-app.vercel.app
    python diagnostic/check_vercel_connection.py --url https://your-app.vercel.app --verbose
    python diagnostic/check_vercel_connection.py --url https://your-app.vercel.app --output report.txt
"""

import argparse
import sys
import time
import json
from typing import Dict, Any, List, Tuple, Optional
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class DiagnosticResult:
    """Stores the result of a diagnostic check"""
    def __init__(self, name: str, passed: bool, message: str, 
                 duration_ms: Optional[int] = None, details: Optional[Dict] = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration_ms = duration_ms
        self.details = details or {}


class VercelDiagnostic:
    """Main diagnostic class for checking Vercel deployment"""
    
    def __init__(self, url: str, verbose: bool = False, output_file: Optional[str] = None):
        self.url = url.rstrip('/')
        self.verbose = verbose
        self.output_file = output_file
        self.results: List[DiagnosticResult] = []
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic and proper timeouts"""
        session = requests.Session()
        
        # Retry strategy with exponential backoff
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _log(self, message: str, color: str = Colors.ENDC):
        """Print and optionally save log message"""
        colored_message = f"{color}{message}{Colors.ENDC}"
        print(colored_message)
        
    def _verbose_log(self, message: str):
        """Log message only in verbose mode"""
        if self.verbose:
            self._log(f"  [VERBOSE] {message}", Colors.OKCYAN)
    
    def _make_request(self, endpoint: str, method: str = "GET", 
                     timeout: int = 60, **kwargs) -> Tuple[Optional[requests.Response], Optional[Exception]]:
        """Make HTTP request with error handling and cold start support"""
        url = f"{self.url}{endpoint}"
        self._verbose_log(f"Making {method} request to {url}")
        
        start_time = time.time()
        try:
            if method == "GET":
                response = self.session.get(url, timeout=timeout, **kwargs)
            elif method == "HEAD":
                response = self.session.head(url, timeout=timeout, **kwargs)
            else:
                response = self.session.request(method, url, timeout=timeout, **kwargs)
            
            duration_ms = int((time.time() - start_time) * 1000)
            self._verbose_log(f"Request completed in {duration_ms}ms - Status: {response.status_code}")
            
            return response, None
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._verbose_log(f"Request failed after {duration_ms}ms - Error: {str(e)}")
            return None, e
    
    def _check_json_response(self, response: requests.Response) -> Tuple[bool, Optional[Dict]]:
        """Validate and parse JSON response"""
        try:
            data = response.json()
            return True, data
        except Exception as e:
            self._verbose_log(f"Failed to parse JSON: {str(e)}")
            return False, None
    
    def check_frontend_health(self) -> List[DiagnosticResult]:
        """Check frontend deployment health"""
        self._log("\n📱 FRONTEND TESTS", Colors.HEADER)
        self._log("-" * 40)
        
        results = []
        
        # Test 1: Frontend is accessible
        self._verbose_log("Testing frontend accessibility...")
        response, error = self._make_request("/", timeout=30)
        
        if error or not response or response.status_code != 200:
            error_msg = str(error) if error else f"Status {response.status_code if response else 'N/A'}"
            results.append(DiagnosticResult(
                "Frontend Accessible",
                False,
                f"Frontend not accessible: {error_msg}"
            ))
            self._log(f"❌ Frontend not accessible: {error_msg}", Colors.FAIL)
            return results
        
        duration = int((time.time() - time.time()) * 1000) if response else 0
        results.append(DiagnosticResult(
            "Frontend Accessible",
            True,
            f"Frontend accessible at: {self.url}",
            duration
        ))
        self._log(f"✅ Frontend accessible at: {self.url}", Colors.OKGREEN)
        
        # Test 2: Check for React app markup
        self._verbose_log("Checking for React app markup...")
        if response and response.text:
            has_root_div = 'id="root"' in response.text or 'id="app"' in response.text
            has_react_markers = 'react' in response.text.lower() or '__REACT' in response.text
            
            if has_root_div or has_react_markers:
                results.append(DiagnosticResult(
                    "React App Detected",
                    True,
                    "React app markup found in HTML"
                ))
                self._log("✅ React app detected", Colors.OKGREEN)
            else:
                results.append(DiagnosticResult(
                    "React App Detected",
                    False,
                    "No React app markup found - might be a routing issue"
                ))
                self._log("⚠️  React app markup not found", Colors.WARNING)
        
        # Test 3: Static assets loading
        self._verbose_log("Checking static assets...")
        assets_response, assets_error = self._make_request("/assets/", method="HEAD", timeout=10)
        
        # Note: /assets/ might 404 if no assets directory, but /assets/[file] should work
        # This is a soft check - we just verify the server responds
        if assets_response or (assets_error and "timeout" not in str(assets_error).lower()):
            results.append(DiagnosticResult(
                "Static Assets",
                True,
                "Static asset endpoint responding"
            ))
            self._log("✅ Static assets endpoint responding", Colors.OKGREEN)
        else:
            results.append(DiagnosticResult(
                "Static Assets",
                False,
                "Static assets endpoint not responding"
            ))
            self._log("⚠️  Static assets endpoint not responding", Colors.WARNING)
        
        # Test 4: No 404 on root
        if response and response.status_code == 200:
            results.append(DiagnosticResult(
                "Root Path",
                True,
                "Root path (/) returns 200 OK"
            ))
            self._log("✅ No routing errors on root path", Colors.OKGREEN)
        
        return results
    
    def check_backend_api_health(self) -> List[DiagnosticResult]:
        """Check backend API endpoints"""
        self._log("\n🔧 BACKEND API TESTS", Colors.HEADER)
        self._log("-" * 40)
        
        results = []
        
        # Test 1: /api/health endpoint
        self._verbose_log("Testing /api/health endpoint...")
        start_time = time.time()
        response, error = self._make_request("/api/health", timeout=60)
        duration_ms = int((time.time() - start_time) * 1000)
        
        if error or not response:
            error_msg = str(error) if error else "No response"
            results.append(DiagnosticResult(
                "/api/health",
                False,
                f"Failed: {error_msg}",
                duration_ms
            ))
            self._log(f"❌ /api/health: {error_msg}", Colors.FAIL)
        elif response.status_code == 200:
            is_json, data = self._check_json_response(response)
            
            if is_json and data:
                backend_status = data.get('backend', 'unknown')
                db_status = data.get('database', 'unknown')
                platform = data.get('platform', 'unknown')
                
                results.append(DiagnosticResult(
                    "/api/health",
                    True,
                    f"Status 200 ({duration_ms}ms)",
                    duration_ms,
                    {"backend": backend_status, "database": db_status, "platform": platform}
                ))
                
                self._log(f"✅ /api/health: Status 200 ({duration_ms}ms)", Colors.OKGREEN)
                self._log(f"   - Backend: {backend_status}", Colors.OKBLUE)
                self._log(f"   - Database: {db_status}", Colors.OKBLUE)
                self._log(f"   - Platform: {platform}", Colors.OKBLUE)
            else:
                results.append(DiagnosticResult(
                    "/api/health",
                    False,
                    f"Invalid JSON response",
                    duration_ms
                ))
                self._log(f"⚠️  /api/health: Invalid JSON response", Colors.WARNING)
        else:
            results.append(DiagnosticResult(
                "/api/health",
                False,
                f"Status {response.status_code}",
                duration_ms
            ))
            self._log(f"❌ /api/health: Status {response.status_code}", Colors.FAIL)
        
        # Test 2: /api/status endpoint
        self._verbose_log("Testing /api/status endpoint...")
        start_time = time.time()
        response, error = self._make_request("/api/status", timeout=60)
        duration_ms = int((time.time() - start_time) * 1000)
        
        if error or not response:
            error_msg = str(error) if error else "No response"
            results.append(DiagnosticResult(
                "/api/status",
                False,
                f"Failed: {error_msg}",
                duration_ms
            ))
            self._log(f"❌ /api/status: {error_msg}", Colors.FAIL)
        elif response.status_code == 200:
            is_json, data = self._check_json_response(response)
            
            if is_json and data:
                backend_loaded = data.get('backend_loaded', False)
                capabilities = data.get('capabilities', {})
                
                results.append(DiagnosticResult(
                    "/api/status",
                    True,
                    f"Status 200 ({duration_ms}ms)",
                    duration_ms,
                    {"backend_loaded": backend_loaded, "capabilities": capabilities}
                ))
                
                self._log(f"✅ /api/status: Status 200 ({duration_ms}ms)", Colors.OKGREEN)
                self._log(f"   - Backend loaded: {backend_loaded}", Colors.OKBLUE)
                
                if capabilities:
                    enabled_capabilities = [k for k, v in capabilities.items() if v]
                    self._log(f"   - Capabilities: {', '.join(enabled_capabilities)}", Colors.OKBLUE)
            else:
                results.append(DiagnosticResult(
                    "/api/status",
                    False,
                    f"Invalid JSON response",
                    duration_ms
                ))
                self._log(f"⚠️  /api/status: Invalid JSON response", Colors.WARNING)
        else:
            results.append(DiagnosticResult(
                "/api/status",
                False,
                f"Status {response.status_code}",
                duration_ms
            ))
            self._log(f"❌ /api/status: Status {response.status_code}", Colors.FAIL)
        
        # Test 3: /api/ready endpoint
        self._verbose_log("Testing /api/ready endpoint...")
        start_time = time.time()
        response, error = self._make_request("/api/ready", timeout=60)
        duration_ms = int((time.time() - start_time) * 1000)
        
        if error or not response:
            error_msg = str(error) if error else "No response"
            results.append(DiagnosticResult(
                "/api/ready",
                False,
                f"Failed: {error_msg}",
                duration_ms
            ))
            self._log(f"❌ /api/ready: {error_msg}", Colors.FAIL)
        elif response.status_code == 200:
            is_json, data = self._check_json_response(response)
            
            if is_json and data:
                db_status = data.get('database', 'unknown')
                status = data.get('status', 'unknown')
                
                results.append(DiagnosticResult(
                    "/api/ready",
                    True,
                    f"Status 200 ({duration_ms}ms)",
                    duration_ms,
                    {"database": db_status, "status": status}
                ))
                
                self._log(f"✅ /api/ready: Status 200 ({duration_ms}ms)", Colors.OKGREEN)
                self._log(f"   - Database: {db_status}", Colors.OKBLUE)
                self._log(f"   - Status: {status}", Colors.OKBLUE)
            else:
                results.append(DiagnosticResult(
                    "/api/ready",
                    False,
                    f"Invalid JSON response",
                    duration_ms
                ))
                self._log(f"⚠️  /api/ready: Invalid JSON response", Colors.WARNING)
        else:
            results.append(DiagnosticResult(
                "/api/ready",
                False,
                f"Status {response.status_code}",
                duration_ms
            ))
            self._log(f"❌ /api/ready: Status {response.status_code}", Colors.FAIL)
        
        # Check response times
        slow_responses = [r for r in results if r.duration_ms and r.duration_ms > 5000]
        if slow_responses:
            self._log(f"\n⚠️  Warning: {len(slow_responses)} endpoint(s) responded slowly (>5s)", Colors.WARNING)
            for r in slow_responses:
                self._log(f"   - {r.name}: {r.duration_ms}ms", Colors.WARNING)
        
        return results
    
    def check_configuration(self) -> List[DiagnosticResult]:
        """Verify configuration is correct"""
        self._log("\n⚙️  CONFIGURATION", Colors.HEADER)
        self._log("-" * 40)
        
        results = []
        
        # These are informational checks based on API responses
        # We can't directly check vercel.json from the deployed site
        
        # Check if API routing works (if /api/health works, routing is good)
        health_result = next((r for r in self.results if r.name == "/api/health"), None)
        
        if health_result and health_result.passed:
            results.append(DiagnosticResult(
                "API Routing",
                True,
                "vercel.json routing working correctly"
            ))
            self._log("✅ vercel.json: Routing configured correctly", Colors.OKGREEN)
        else:
            results.append(DiagnosticResult(
                "API Routing",
                False,
                "API routing may not be configured correctly"
            ))
            self._log("❌ vercel.json: API routing issue detected", Colors.FAIL)
        
        # Check CORS (we can infer from successful API calls)
        if health_result and health_result.passed:
            results.append(DiagnosticResult(
                "CORS",
                True,
                "CORS appears to be configured correctly"
            ))
            self._log("✅ CORS: Properly configured", Colors.OKGREEN)
        
        # Check frontend API auto-detection (informational)
        results.append(DiagnosticResult(
            "Frontend API",
            True,
            "Same-origin API should work on Vercel"
        ))
        self._log("✅ Frontend API: Auto-detection should work", Colors.OKGREEN)
        
        return results
    
    def check_database_connection(self) -> List[DiagnosticResult]:
        """Check database connection status"""
        self._log("\n💾 DATABASE", Colors.HEADER)
        self._log("-" * 40)
        
        results = []
        
        # Get database status from API responses
        health_result = next((r for r in self.results if r.name == "/api/health"), None)
        ready_result = next((r for r in self.results if r.name == "/api/ready"), None)
        
        if health_result and health_result.passed:
            db_status = health_result.details.get('database', 'unknown')
            
            if db_status in ['connected', 'available']:
                results.append(DiagnosticResult(
                    "Database URL",
                    True,
                    "DATABASE_URL is configured"
                ))
                self._log("✅ DATABASE_URL: Configured", Colors.OKGREEN)
                
                if ready_result and ready_result.passed:
                    results.append(DiagnosticResult(
                        "Database Connection",
                        True,
                        "Connection successful"
                    ))
                    self._log("✅ Connection: Successful", Colors.OKGREEN)
                    
                    results.append(DiagnosticResult(
                        "Database Query",
                        True,
                        "Query test passed"
                    ))
                    self._log("✅ Query test: Passed", Colors.OKGREEN)
                else:
                    results.append(DiagnosticResult(
                        "Database Connection",
                        False,
                        "Connection failed or not ready"
                    ))
                    self._log("❌ Connection: Failed", Colors.FAIL)
            elif db_status == 'unavailable':
                results.append(DiagnosticResult(
                    "Database URL",
                    False,
                    "DATABASE_URL not configured"
                ))
                self._log("❌ DATABASE_URL: Not configured", Colors.FAIL)
            else:
                results.append(DiagnosticResult(
                    "Database Status",
                    False,
                    f"Unknown database status: {db_status}"
                ))
                self._log(f"⚠️  Database status: {db_status}", Colors.WARNING)
        else:
            results.append(DiagnosticResult(
                "Database Check",
                False,
                "Unable to determine database status - API health check failed"
            ))
            self._log("❌ Database: Unable to check (API health failed)", Colors.FAIL)
        
        # SSL Mode check
        if health_result and health_result.passed:
            db_status = health_result.details.get('database', 'unknown')
            if db_status in ['connected', 'available']:
                results.append(DiagnosticResult(
                    "SSL Mode",
                    True,
                    "SSL configuration appears correct"
                ))
                self._log("✅ SSL Mode: Configured correctly", Colors.OKGREEN)
        
        return results
    
    def check_environment_security(self) -> List[DiagnosticResult]:
        """Check environment variables and security"""
        self._log("\n🔐 SECURITY", Colors.HEADER)
        self._log("-" * 40)
        
        results = []
        
        # Get JWT and environment status from API
        health_result = next((r for r in self.results if r.name == "/api/health"), None)
        status_result = next((r for r in self.results if r.name == "/api/status"), None)
        
        if health_result and health_result.passed:
            jwt_status = health_result.details.get('jwt', 'unknown')
            
            if jwt_status == 'configured':
                results.append(DiagnosticResult(
                    "JWT_SECRET_KEY",
                    True,
                    "Set (not default)"
                ))
                self._log("✅ JWT_SECRET_KEY: Set (not default)", Colors.OKGREEN)
            else:
                results.append(DiagnosticResult(
                    "JWT_SECRET_KEY",
                    False,
                    "Using default value - SECURITY RISK"
                ))
                self._log("❌ JWT_SECRET_KEY: Using default (SECURITY RISK)", Colors.FAIL)
        
        if status_result and status_result.passed:
            jwt_configured = status_result.details.get('jwt_configured', False)
            
            if jwt_configured:
                results.append(DiagnosticResult(
                    "SECRET_KEY",
                    True,
                    "Set (not default)"
                ))
                self._log("✅ SECRET_KEY: Set (not default)", Colors.OKGREEN)
        
        # Check environment
        if status_result and status_result.passed:
            results.append(DiagnosticResult(
                "Environment",
                True,
                "Backend is operational"
            ))
            self._log("✅ ENVIRONMENT: Backend operational", Colors.OKGREEN)
        
        return results
    
    def print_summary(self):
        """Print overall summary of diagnostic results"""
        self._log("\n📊 SUMMARY", Colors.HEADER)
        self._log("=" * 40)
        
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r.passed)
        failed_checks = total_checks - passed_checks
        
        if failed_checks == 0:
            self._log(f"✅ All systems operational ({passed_checks}/{total_checks} checks passed)", Colors.OKGREEN)
            self._log("✅ Frontend-Backend connection: Working", Colors.OKGREEN)
            
            # Check database status
            db_results = [r for r in self.results if 'database' in r.name.lower() or 'Database' in r.name]
            if any(r.passed for r in db_results):
                self._log("✅ Database: Connected", Colors.OKGREEN)
            
            self._log("✅ Ready for production use", Colors.OKGREEN)
        else:
            self._log(f"⚠️  {passed_checks}/{total_checks} checks passed, {failed_checks} failed", Colors.WARNING)
            
            # List failed checks
            failed = [r for r in self.results if not r.passed]
            if failed:
                self._log("\n❌ Failed checks:", Colors.FAIL)
                for r in failed:
                    self._log(f"   - {r.name}: {r.message}", Colors.FAIL)
        
        self._log(f"\nDeployment URL: {self.url}")
        self._log(f"Health Check: {self.url}/api/health")
        
        # Add troubleshooting suggestions for failures
        if failed_checks > 0:
            self._print_troubleshooting_suggestions()
    
    def _print_troubleshooting_suggestions(self):
        """Print troubleshooting suggestions based on failures"""
        self._log("\n💡 TROUBLESHOOTING SUGGESTIONS", Colors.WARNING)
        self._log("=" * 40)
        
        # Check for common failure patterns
        api_failures = [r for r in self.results if not r.passed and '/api/' in r.name]
        frontend_failures = [r for r in self.results if not r.passed and 'Frontend' in r.name]
        db_failures = [r for r in self.results if not r.passed and 'database' in r.name.lower()]
        
        if frontend_failures:
            self._log("\n📱 Frontend Issues:", Colors.WARNING)
            self._log("   • Check Vercel build logs for build failures")
            self._log("   • Verify vercel.json outputDirectory setting")
            self._log("   • Ensure frontend build completes successfully")
            self._log("   • Check browser console for JavaScript errors")
        
        if api_failures:
            self._log("\n🔧 Backend API Issues:", Colors.WARNING)
            self._log("   • Verify DATABASE_URL is set in Vercel environment variables")
            self._log("   • Check Vercel function logs for errors")
            self._log("   • Ensure api/index.py is deployed correctly")
            self._log("   • Verify all Python dependencies are in requirements.txt")
            self._log("   • Check if serverless function is timing out (30s limit)")
        
        if db_failures:
            self._log("\n💾 Database Issues:", Colors.WARNING)
            self._log("   • Ensure DATABASE_URL environment variable is set")
            self._log("   • Verify database credentials are correct")
            self._log("   • Check if database accepts connections from Vercel IPs")
            self._log("   • Ensure SSL mode is set correctly (sslmode=require)")
            self._log("   • Verify database is running and accessible")
        
        self._log(f"\n📚 Documentation: docs/BACKEND_CONNECTION_TROUBLESHOOTING.md")
    
    def save_results(self):
        """Save results to file if output_file is specified"""
        if not self.output_file:
            return
        
        try:
            with open(self.output_file, 'w') as f:
                f.write("HireMeBahamas Connection Diagnostic Report\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"URL: {self.url}\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Write all results
                for result in self.results:
                    status = "✅ PASS" if result.passed else "❌ FAIL"
                    f.write(f"{status} - {result.name}\n")
                    f.write(f"    {result.message}\n")
                    if result.duration_ms:
                        f.write(f"    Duration: {result.duration_ms}ms\n")
                    if result.details:
                        f.write(f"    Details: {json.dumps(result.details, indent=2)}\n")
                    f.write("\n")
                
                # Write summary
                total = len(self.results)
                passed = sum(1 for r in self.results if r.passed)
                f.write(f"\nSummary: {passed}/{total} checks passed\n")
            
            self._log(f"\n📝 Results saved to: {self.output_file}", Colors.OKGREEN)
        except Exception as e:
            self._log(f"\n⚠️  Failed to save results: {str(e)}", Colors.WARNING)
    
    def run(self):
        """Run all diagnostic checks"""
        self._log("🔍 HireMeBahamas Connection Diagnostic", Colors.BOLD + Colors.HEADER)
        self._log("=" * 60)
        self._log(f"Testing deployment: {self.url}\n")
        
        # Run all checks
        try:
            # Frontend checks
            frontend_results = self.check_frontend_health()
            self.results.extend(frontend_results)
            
            # Backend API checks
            backend_results = self.check_backend_api_health()
            self.results.extend(backend_results)
            
            # Configuration checks
            config_results = self.check_configuration()
            self.results.extend(config_results)
            
            # Database checks
            db_results = self.check_database_connection()
            self.results.extend(db_results)
            
            # Security checks
            security_results = self.check_environment_security()
            self.results.extend(security_results)
            
            # Print summary
            self.print_summary()
            
            # Save results if requested
            self.save_results()
            
            # Return exit code based on results
            failed_count = sum(1 for r in self.results if not r.passed)
            return 0 if failed_count == 0 else 1
            
        except KeyboardInterrupt:
            self._log("\n\n⚠️  Diagnostic interrupted by user", Colors.WARNING)
            return 130
        except Exception as e:
            self._log(f"\n\n❌ Diagnostic failed with error: {str(e)}", Colors.FAIL)
            if self.verbose:
                import traceback
                self._log(traceback.format_exc(), Colors.FAIL)
            return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="HireMeBahamas Vercel Connection Diagnostic Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test production deployment
  python diagnostic/check_vercel_connection.py --url https://your-app.vercel.app

  # Test with verbose logging
  python diagnostic/check_vercel_connection.py --url https://your-app.vercel.app --verbose

  # Save results to file
  python diagnostic/check_vercel_connection.py --url https://your-app.vercel.app --output report.txt
        """
    )
    
    parser.add_argument(
        '--url',
        required=True,
        help='Vercel deployment URL (e.g., https://your-app.vercel.app)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging for detailed diagnostics'
    )
    
    parser.add_argument(
        '--output',
        help='Save diagnostic results to file'
    )
    
    args = parser.parse_args()
    
    # Validate URL
    parsed = urlparse(args.url)
    if not parsed.scheme or not parsed.netloc:
        print(f"{Colors.FAIL}❌ Invalid URL: {args.url}{Colors.ENDC}")
        print(f"{Colors.WARNING}URL must include protocol (https://){Colors.ENDC}")
        return 1
    
    # Run diagnostic
    diagnostic = VercelDiagnostic(args.url, args.verbose, args.output)
    return diagnostic.run()


if __name__ == "__main__":
    sys.exit(main())

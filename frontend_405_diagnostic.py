#!/usr/bin/env python3
"""
Frontend 405 Error Diagnostic Tool
Specifically analyzes frontend authentication issues causing 405 errors
"""

import json
import requests
import time
from pathlib import Path
import re
from typing import Dict, List, Optional
import logging


class Frontend405Diagnostics:
    """Frontend-specific 405 error diagnostics"""

    def __init__(self):
        self.workspace_root = Path(".")
        self.frontend_dir = self.workspace_root / "frontend"
        self.api_base = "https://hiremebahamas-backend.railway.app"

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.issues = []

    def analyze_api_configuration(self) -> None:
        """Analyze frontend API configuration"""
        self.logger.info("🔍 Analyzing frontend API configuration...")

        # Check api.ts configuration
        api_file = self.frontend_dir / "src" / "services" / "api.ts"
        if api_file.exists():
            self._analyze_api_service(api_file)

        # Check environment configuration
        self._check_environment_config()

        # Check Vite configuration
        vite_config = self.frontend_dir / "vite.config.ts"
        if vite_config.exists():
            self._analyze_vite_config(vite_config)

    def _analyze_api_service(self, api_file: Path) -> None:
        """Analyze the main API service file"""
        try:
            with open(api_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check base URL configuration
            base_url_match = re.search(r'baseURL:\s*[\'"]([^\'"]+)[\'"]', content)
            if base_url_match:
                base_url = base_url_match.group(1)
                self.logger.info(f"Found API base URL: {base_url}")

                # Test if base URL is accessible
                self._test_base_url(base_url)

            # Check authentication endpoints
            auth_endpoints = re.findall(
                r'\.post\([\'"]([^\'"]*auth[^\'"]*)[\'"]', content
            )
            for endpoint in auth_endpoints:
                self.logger.info(f"Found auth endpoint: {endpoint}")

            # Check for proper error handling
            if "response.interceptors.response.use" not in content:
                self.issues.append(
                    {
                        "type": "warning",
                        "message": "Missing response interceptor for error handling",
                        "file": str(api_file),
                        "fix": "Add response interceptor to handle 405 and other errors",
                    }
                )

        except Exception as e:
            self.logger.error(f"Error analyzing API service: {e}")

    def _test_base_url(self, base_url: str) -> None:
        """Test if the base URL is accessible"""
        try:
            # Test health endpoint
            health_url = f"{base_url}/health"
            response = requests.get(health_url, timeout=10)

            if response.status_code == 200:
                self.logger.info(f"✅ Base URL accessible: {base_url}")
            else:
                self.issues.append(
                    {
                        "type": "error",
                        "message": f"Base URL health check failed: {response.status_code}",
                        "fix": "Check backend deployment status",
                    }
                )

        except requests.exceptions.RequestException as e:
            self.issues.append(
                {
                    "type": "critical",
                    "message": f"Cannot reach base URL {base_url}: {e}",
                    "fix": "Verify backend URL and deployment",
                }
            )

    def _check_environment_config(self) -> None:
        """Check environment configuration"""
        env_files = [
            self.frontend_dir / ".env",
            self.frontend_dir / ".env.local",
            self.frontend_dir / ".env.production",
        ]

        for env_file in env_files:
            if env_file.exists():
                with open(env_file, "r") as f:
                    content = f.read()

                if "VITE_API_URL" in content:
                    api_url = re.search(r"VITE_API_URL\s*=\s*([^\n]+)", content)
                    if api_url:
                        url = api_url.group(1).strip("'\"")
                        self.logger.info(f"Environment API URL: {url}")

    def _analyze_vite_config(self, vite_config: Path) -> None:
        """Analyze Vite configuration for proxy settings"""
        try:
            with open(vite_config, "r") as f:
                content = f.read()

            # Check for proxy configuration
            if "proxy" in content:
                self.logger.info("Found proxy configuration in Vite config")
            else:
                self.issues.append(
                    {
                        "type": "info",
                        "message": "No proxy configuration found in Vite config",
                        "fix": "Consider adding proxy for development",
                    }
                )

        except Exception as e:
            self.logger.error(f"Error analyzing Vite config: {e}")

    def test_authentication_flow(self) -> None:
        """Test the complete authentication flow"""
        self.logger.info("🔐 Testing authentication flow...")

        test_credentials = {
            "email": "admin@hiremebahamas.com",
            "password": "AdminPass123!",
        }

        # Test login endpoint
        self._test_login_endpoint(test_credentials)

        # Test CORS preflight
        self._test_cors_preflight()

    def _test_login_endpoint(self, credentials: Dict) -> None:
        """Test login endpoint specifically"""
        endpoints_to_test = [
            f"{self.api_base}/api/auth/login",
            f"{self.api_base}/auth/login",
        ]

        for endpoint in endpoints_to_test:
            try:
                self.logger.info(f"Testing login endpoint: {endpoint}")

                # Test POST request
                response = requests.post(
                    endpoint,
                    json=credentials,
                    headers={
                        "Content-Type": "application/json",
                        "Origin": "https://hiremebahamas.vercel.app",
                    },
                    timeout=30,
                )

                if response.status_code == 405:
                    self.issues.append(
                        {
                            "type": "critical",
                            "message": f"405 Method Not Allowed on {endpoint}",
                            "details": f"Response: {response.text}",
                            "fix": "Check backend route definition and allowed methods",
                        }
                    )
                elif response.status_code == 200:
                    self.logger.info(f"✅ Login endpoint working: {endpoint}")
                else:
                    self.logger.info(f"Login endpoint response: {response.status_code}")

            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed for {endpoint}: {e}")

    def _test_cors_preflight(self) -> None:
        """Test CORS preflight request"""
        endpoint = f"{self.api_base}/api/auth/login"

        try:
            # Send OPTIONS request (CORS preflight)
            response = requests.options(
                endpoint,
                headers={
                    "Origin": "https://hiremebahamas.vercel.app",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type",
                },
                timeout=10,
            )

            if response.status_code == 405:
                self.issues.append(
                    {
                        "type": "critical",
                        "message": "CORS preflight failing with 405 error",
                        "fix": "Backend needs to handle OPTIONS requests",
                    }
                )
            elif response.status_code == 200:
                # Check CORS headers
                cors_headers = [
                    "Access-Control-Allow-Origin",
                    "Access-Control-Allow-Methods",
                    "Access-Control-Allow-Headers",
                ]

                missing_headers = [h for h in cors_headers if h not in response.headers]
                if missing_headers:
                    self.issues.append(
                        {
                            "type": "warning",
                            "message": f"Missing CORS headers: {missing_headers}",
                            "fix": "Add missing CORS headers to OPTIONS response",
                        }
                    )
                else:
                    self.logger.info("✅ CORS preflight working correctly")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"CORS preflight test failed: {e}")

    def analyze_authentication_components(self) -> None:
        """Analyze React authentication components"""
        self.logger.info("⚛️ Analyzing authentication components...")

        # Find authentication-related components
        auth_components = []
        src_dir = self.frontend_dir / "src"

        if src_dir.exists():
            for component_file in src_dir.rglob("*.tsx"):
                if any(
                    keyword in component_file.name.lower()
                    for keyword in ["login", "auth", "signup", "register"]
                ):
                    auth_components.append(component_file)

        for component in auth_components:
            self._analyze_auth_component(component)

    def _analyze_auth_component(self, component_file: Path) -> None:
        """Analyze individual authentication component"""
        try:
            with open(component_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for API calls
            api_calls = re.findall(r"authAPI\.(login|register)", content)
            if api_calls:
                self.logger.info(
                    f"Found API calls in {component_file.name}: {api_calls}"
                )

            # Check for error handling
            if "catch" not in content and "error" not in content.lower():
                self.issues.append(
                    {
                        "type": "warning",
                        "message": f"Component {component_file.name} may lack error handling",
                        "file": str(component_file),
                        "fix": "Add try-catch and error state handling",
                    }
                )

        except Exception as e:
            self.logger.error(f"Error analyzing component {component_file}: {e}")

    def generate_fix_script(self) -> None:
        """Generate automatic fix script"""
        fix_script_path = self.workspace_root / "fix_405_errors.py"

        with open(fix_script_path, "w") as f:
            f.write(
                '''#!/usr/bin/env python3
"""
Automated 405 Error Fix Script
Generated by Frontend 405 Diagnostics
"""

import json
from pathlib import Path

def fix_api_configuration():
    """Fix API configuration issues"""
    frontend_dir = Path("frontend")
    api_file = frontend_dir / "src" / "services" / "api.ts"
    
    if api_file.exists():
        with open(api_file, 'r') as f:
            content = f.read()
            
        # Add better error handling for 405 errors
        if 'status === 405' not in content:
            error_handler = """
    // Handle 405 Method Not Allowed errors
    if (error.response?.status === 405) {
      console.error('405 Method Not Allowed:', {
        url: error.config?.url,
        method: error.config?.method,
        message: 'Check backend route configuration'
      });
      
      // Show user-friendly error
      throw new Error('Service temporarily unavailable. Please try again.');
    }
"""
            # Insert before existing error handling
            content = content.replace(
                'console.error(\'API Error:\',',
                error_handler + '\\n    console.error(\'API Error:\','
            )
            
        with open(api_file, 'w') as f:
            f.write(content)
            
        print("✅ Updated API error handling")

def main():
    print("🔧 Applying 405 error fixes...")
    fix_api_configuration()
    print("✅ Fix script completed")

if __name__ == "__main__":
    main()
'''
            )

        self.logger.info(f"📄 Generated fix script: {fix_script_path}")

    def run_diagnostics(self) -> None:
        """Run complete frontend diagnostics"""
        self.logger.info("🚀 Starting Frontend 405 Diagnostics...")

        self.analyze_api_configuration()
        self.test_authentication_flow()
        self.analyze_authentication_components()
        self.generate_fix_script()

        # Generate report
        self._generate_report()

    def _generate_report(self) -> None:
        """Generate diagnostic report"""
        report_path = self.workspace_root / "FRONTEND_405_REPORT.md"

        with open(report_path, "w") as f:
            f.write("# Frontend 405 Error Diagnostic Report\\n\\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")

            if not self.issues:
                f.write("## ✅ No Issues Found\\n\\n")
                f.write("The frontend appears to be configured correctly.\\n")
            else:
                # Group issues by type
                critical = [i for i in self.issues if i.get("type") == "critical"]
                errors = [i for i in self.issues if i.get("type") == "error"]
                warnings = [i for i in self.issues if i.get("type") == "warning"]

                f.write(f"## Summary\\n\\n")
                f.write(f"- 🔴 Critical: {len(critical)}\\n")
                f.write(f"- ❌ Errors: {len(errors)}\\n")
                f.write(f"- ⚠️ Warnings: {len(warnings)}\\n\\n")

                for issue_type, issues, icon in [
                    ("Critical Issues", critical, "🔴"),
                    ("Errors", errors, "❌"),
                    ("Warnings", warnings, "⚠️"),
                ]:
                    if issues:
                        f.write(f"## {icon} {issue_type}\\n\\n")
                        for issue in issues:
                            f.write(f"### {issue['message']}\\n\\n")
                            if "file" in issue:
                                f.write(f"**File:** `{issue['file']}`\\n")
                            if "details" in issue:
                                f.write(f"**Details:** {issue['details']}\\n")
                            if "fix" in issue:
                                f.write(f"**Fix:** {issue['fix']}\\n")
                            f.write("\\n")

            f.write("## Next Steps\\n\\n")
            f.write("1. Run `python fix_405_errors.py` to apply automatic fixes\\n")
            f.write("2. Check backend deployment status\\n")
            f.write("3. Test authentication in browser developer tools\\n")
            f.write("4. Monitor network requests for 405 errors\\n")

        self.logger.info(f"📄 Report saved: {report_path}")


def main():
    """Main function"""
    diagnostics = Frontend405Diagnostics()
    diagnostics.run_diagnostics()

    print("\\n✅ Frontend diagnostics complete!")
    print("📄 Check FRONTEND_405_REPORT.md for detailed analysis")


if __name__ == "__main__":
    main()

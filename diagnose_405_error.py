#!/usr/bin/env python3
"""
Main 405 Error Diagnosis and Fix Tool
Uses IntelliSense and live testing to diagnose and fix 405 errors
"""

import json
import logging
import requests
import time
from pathlib import Path
from typing import Dict, List
import subprocess
import sys


class Main405Diagnostics:
    """Main diagnostic orchestrator"""

    def __init__(self):
        self.workspace_root = Path(".")
        self.api_base = "https://hiremebahamas-backend.railway.app"
        self.local_api = "http://localhost:5000"

        # Setup logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
        )
        self.logger = logging.getLogger(__name__)

        self.diagnosis_results = {
            "backend_status": None,
            "frontend_config": None,
            "route_analysis": None,
            "live_tests": None,
        }

    def check_backend_status(self) -> Dict:
        """Check backend deployment and health status"""
        self.logger.info("🚀 Checking backend status...")

        status = {"health_check": False, "endpoints_tested": [], "issues": []}

        # Test health endpoint
        try:
            response = requests.get(f"{self.api_base}/health", timeout=30)
            if response.status_code == 200:
                status["health_check"] = True
                self.logger.info("✅ Backend health check passed")
            else:
                status["issues"].append(f"Health check failed: {response.status_code}")

        except requests.exceptions.RequestException as e:
            status["issues"].append(f"Cannot reach backend: {e}")

        # Test authentication endpoints
        auth_endpoints = ["/api/auth/login", "/auth/login"]
        test_data = {"email": "test@example.com", "password": "test123"}

        for endpoint in auth_endpoints:
            url = f"{self.api_base}{endpoint}"
            endpoint_status = {"url": url, "methods": {}}

            # Test OPTIONS (CORS preflight)
            try:
                options_response = requests.options(url, timeout=10)
                endpoint_status["methods"]["OPTIONS"] = options_response.status_code

                if options_response.status_code == 405:
                    status["issues"].append(f"405 on OPTIONS {endpoint}")

            except requests.exceptions.RequestException as e:
                endpoint_status["methods"]["OPTIONS"] = f"Error: {e}"

            # Test POST
            try:
                post_response = requests.post(
                    url,
                    json=test_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10,
                )
                endpoint_status["methods"]["POST"] = post_response.status_code

                if post_response.status_code == 405:
                    status["issues"].append(f"405 on POST {endpoint}")

            except requests.exceptions.RequestException as e:
                endpoint_status["methods"]["POST"] = f"Error: {e}"

            status["endpoints_tested"].append(endpoint_status)

        return status

    def analyze_frontend_config(self) -> Dict:
        """Analyze frontend configuration"""
        self.logger.info("⚛️ Analyzing frontend configuration...")

        config = {
            "api_service_found": False,
            "base_url": None,
            "environment_vars": [],
            "issues": [],
        }

        # Check API service file
        api_file = self.workspace_root / "frontend" / "src" / "services" / "api.ts"
        if api_file.exists():
            config["api_service_found"] = True

            try:
                with open(api_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract base URL
                import re

                base_url_match = re.search(r'baseURL:\s*[\'"]([^\'"]+)[\'"]', content)
                if base_url_match:
                    config["base_url"] = base_url_match.group(1)

                # Check for proper error handling
                if "405" not in content:
                    config["issues"].append("No specific 405 error handling found")

            except Exception as e:
                config["issues"].append(f"Error reading API service: {e}")
        else:
            config["issues"].append("API service file not found")

        # Check environment files
        env_files = [
            self.workspace_root / "frontend" / ".env",
            self.workspace_root / "frontend" / ".env.local",
        ]

        for env_file in env_files:
            if env_file.exists():
                try:
                    with open(env_file, "r") as f:
                        content = f.read()
                        lines = [
                            line.strip() for line in content.split("\n") if line.strip()
                        ]
                        config["environment_vars"].extend(lines)
                except Exception as e:
                    config["issues"].append(f"Error reading {env_file.name}: {e}")

        return config

    def analyze_backend_routes(self) -> Dict:
        """Analyze backend route definitions"""
        self.logger.info("🔍 Analyzing backend routes...")

        analysis = {"files_analyzed": 0, "routes_found": [], "issues": []}

        # Find Python backend files
        backend_files = []
        for pattern in ["*backend*.py", "*server*.py", "*app*.py", "*main*.py"]:
            backend_files.extend(self.workspace_root.glob(pattern))
            backend_files.extend(self.workspace_root.rglob(pattern))

        # Remove duplicates and filter
        backend_files = list(set(backend_files))
        backend_files = [f for f in backend_files if f.is_file()]

        for file_path in backend_files[:10]:  # Limit to first 10 files
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                analysis["files_analyzed"] += 1

                # Find route definitions
                import re

                route_patterns = [
                    r'@app\.route\([\'"]([^\'"]+)[\'"].*methods\s*=\s*\[([^\]]+)\]',
                    r'@app\.route\([\'"]([^\'"]+)[\'"]',
                ]

                for pattern in route_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if isinstance(match, tuple) and len(match) >= 1:
                            route_path = match[0]
                            methods = match[1] if len(match) > 1 else "GET"

                            if "auth" in route_path.lower():
                                route_info = {
                                    "path": route_path,
                                    "methods": methods,
                                    "file": str(file_path.name),
                                }
                                analysis["routes_found"].append(route_info)

                                # Check for potential issues
                                if "POST" in methods and "OPTIONS" not in methods:
                                    analysis["issues"].append(
                                        f"Route {route_path} in {file_path.name} "
                                        f"has POST but no OPTIONS method"
                                    )

            except Exception as e:
                analysis["issues"].append(f"Error analyzing {file_path.name}: {e}")

        return analysis

    def perform_live_tests(self) -> Dict:
        """Perform live API tests"""
        self.logger.info("🧪 Performing live API tests...")

        tests = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests_performed": [],
            "critical_issues": [],
            "recommendations": [],
        }

        # Test 1: Direct API calls
        test_endpoints = [
            f"{self.api_base}/api/auth/login",
            f"{self.api_base}/auth/login",
        ]

        for endpoint in test_endpoints:
            test_result = self._test_endpoint_thoroughly(endpoint)
            tests["tests_performed"].append(test_result)

            if any("405" in str(result) for result in test_result.values()):
                tests["critical_issues"].append(f"405 error detected on {endpoint}")

        # Test 2: CORS from browser context
        cors_test = self._test_cors_from_frontend()
        tests["tests_performed"].append({"cors_test": cors_test})

        # Generate recommendations
        if tests["critical_issues"]:
            tests["recommendations"].extend(
                [
                    "Check backend route definitions",
                    "Verify CORS configuration",
                    "Ensure backend deployment is complete",
                    "Test with direct curl commands",
                ]
            )
        else:
            tests["recommendations"].append("No critical issues found")

        return tests

    def _test_endpoint_thoroughly(self, endpoint: str) -> Dict:
        """Test an endpoint with multiple methods"""
        results = {"endpoint": endpoint}

        # Test OPTIONS
        try:
            response = requests.options(endpoint, timeout=10)
            results["OPTIONS"] = response.status_code
        except Exception as e:
            results["OPTIONS"] = f"Error: {e}"

        # Test POST
        try:
            test_data = {"email": "test@example.com", "password": "test123"}
            response = requests.post(
                endpoint,
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            results["POST"] = response.status_code
        except Exception as e:
            results["POST"] = f"Error: {e}"

        # Test GET (should probably return 405)
        try:
            response = requests.get(endpoint, timeout=10)
            results["GET"] = response.status_code
        except Exception as e:
            results["GET"] = f"Error: {e}"

        return results

    def _test_cors_from_frontend(self) -> Dict:
        """Test CORS as it would happen from frontend"""
        endpoint = f"{self.api_base}/api/auth/login"

        cors_test = {
            "preflight_request": None,
            "actual_request": None,
            "cors_headers_present": False,
        }

        # Simulate CORS preflight
        try:
            preflight_response = requests.options(
                endpoint,
                headers={
                    "Origin": "https://hiremebahamas.vercel.app",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type",
                },
                timeout=10,
            )

            cors_test["preflight_request"] = preflight_response.status_code

            # Check for CORS headers
            cors_headers = [
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Methods",
                "Access-Control-Allow-Headers",
            ]

            cors_test["cors_headers_present"] = all(
                header in preflight_response.headers for header in cors_headers
            )

        except Exception as e:
            cors_test["preflight_request"] = f"Error: {e}"

        return cors_test

    def generate_fix_recommendations(self) -> List[str]:
        """Generate specific fix recommendations based on diagnosis"""
        recommendations = []

        # Analyze results and generate recommendations
        backend_status = self.diagnosis_results.get("backend_status", {})
        frontend_config = self.diagnosis_results.get("frontend_config", {})
        route_analysis = self.diagnosis_results.get("route_analysis", {})
        live_tests = self.diagnosis_results.get("live_tests", {})

        # Backend recommendations
        if backend_status and backend_status.get("issues"):
            recommendations.append("🚀 Backend Issues:")
            for issue in backend_status["issues"]:
                if "405" in issue:
                    recommendations.append("   - Add OPTIONS method to auth routes")
                    recommendations.append("   - Verify CORS configuration")

        # Frontend recommendations
        if frontend_config and frontend_config.get("issues"):
            recommendations.append("⚛️ Frontend Issues:")
            for issue in frontend_config["issues"]:
                if "405" in issue:
                    recommendations.append("   - Add 405 error handling to API service")

        # Route analysis recommendations
        if route_analysis and route_analysis.get("issues"):
            recommendations.append("🔍 Route Issues:")
            for issue in route_analysis["issues"]:
                recommendations.append(f"   - {issue}")

        if not recommendations:
            recommendations.append("✅ No major issues detected")

        return recommendations

    def run_complete_diagnosis(self) -> None:
        """Run complete 405 error diagnosis"""
        self.logger.info("🔍 Starting Complete 405 Error Diagnosis...")

        # Run all diagnostic phases
        self.diagnosis_results["backend_status"] = self.check_backend_status()
        self.diagnosis_results["frontend_config"] = self.analyze_frontend_config()
        self.diagnosis_results["route_analysis"] = self.analyze_backend_routes()
        self.diagnosis_results["live_tests"] = self.perform_live_tests()

        # Generate recommendations
        recommendations = self.generate_fix_recommendations()

        # Create comprehensive report
        self._create_comprehensive_report(recommendations)

        # Create automated fix script
        self._create_fix_script()

    def _create_comprehensive_report(self, recommendations: List[str]) -> None:
        """Create comprehensive diagnostic report"""
        report_path = self.workspace_root / "COMPLETE_405_DIAGNOSIS.md"

        with open(report_path, "w") as f:
            f.write("# 🔍 Complete 405 Error Diagnosis Report\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Executive Summary
            total_issues = sum(
                len(result.get("issues", []))
                for result in self.diagnosis_results.values()
                if isinstance(result, dict)
            )

            f.write("## Executive Summary\n\n")
            if total_issues == 0:
                f.write("✅ **No critical issues detected**\n\n")
            else:
                f.write(f"⚠️ **{total_issues} issues detected**\n\n")

            # Backend Status
            backend = self.diagnosis_results["backend_status"]
            f.write("## 🚀 Backend Status\n\n")
            f.write(
                f"- Health Check: {'✅ Pass' if backend.get('health_check') else '❌ Fail'}\n"
            )
            f.write(f"- Endpoints Tested: {len(backend.get('endpoints_tested', []))}\n")
            f.write(f"- Issues Found: {len(backend.get('issues', []))}\n\n")

            if backend.get("issues"):
                f.write("### Backend Issues:\n")
                for issue in backend["issues"]:
                    f.write(f"- {issue}\n")
                f.write("\n")

            # Frontend Configuration
            frontend = self.diagnosis_results["frontend_config"]
            f.write("## ⚛️ Frontend Configuration\n\n")
            f.write(
                f"- API Service Found: {'✅' if frontend.get('api_service_found') else '❌'}\n"
            )
            f.write(f"- Base URL: {frontend.get('base_url', 'Not configured')}\n")
            f.write(
                f"- Environment Variables: {len(frontend.get('environment_vars', []))}\n\n"
            )

            # Route Analysis
            routes = self.diagnosis_results["route_analysis"]
            f.write("## 🔍 Route Analysis\n\n")
            f.write(f"- Files Analyzed: {routes.get('files_analyzed', 0)}\n")
            f.write(f"- Auth Routes Found: {len(routes.get('routes_found', []))}\n\n")

            if routes.get("routes_found"):
                f.write("### Auth Routes:\n")
                for route in routes["routes_found"]:
                    f.write(
                        f"- `{route['path']}` ({route['methods']}) in {route['file']}\n"
                    )
                f.write("\n")

            # Live Tests
            tests = self.diagnosis_results["live_tests"]
            f.write("## 🧪 Live Test Results\n\n")
            f.write(f"- Tests Performed: {len(tests.get('tests_performed', []))}\n")
            f.write(f"- Critical Issues: {len(tests.get('critical_issues', []))}\n\n")

            # Recommendations
            f.write("## 🔧 Recommendations\n\n")
            for rec in recommendations:
                f.write(f"{rec}\n")

            f.write("\n## Next Steps\n\n")
            f.write("1. Run `python apply_405_fixes.py` to apply automated fixes\n")
            f.write("2. Check backend deployment logs\n")
            f.write("3. Test authentication in browser\n")
            f.write("4. Monitor network requests in DevTools\n")

        self.logger.info(f"📄 Comprehensive report saved: {report_path}")

    def _create_fix_script(self) -> None:
        """Create automated fix script"""
        fix_script_path = self.workspace_root / "apply_405_fixes.py"

        fix_script_content = '''#!/usr/bin/env python3
"""
Automated 405 Error Fix Script
Applies fixes based on diagnosis results
"""

import json
from pathlib import Path
import re

def fix_backend_routes():
    """Fix backend route issues"""
    print("🔧 Fixing backend routes...")
    
    # Add OPTIONS method to auth routes
    backend_files = list(Path(".").rglob("*backend*.py"))
    
    for file_path in backend_files:
        if file_path.is_file():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Fix routes missing OPTIONS
                fixed_content = re.sub(
                    r"methods\\s*=\\s*\\['POST'\\]",
                    "methods=['POST', 'OPTIONS']",
                    content
                )
                
                if fixed_content != content:
                    with open(file_path, 'w') as f:
                        f.write(fixed_content)
                    print(f"✅ Fixed routes in {file_path.name}")
                    
            except Exception as e:
                print(f"❌ Error fixing {file_path.name}: {e}")

def fix_frontend_api():
    """Fix frontend API configuration"""
    print("🔧 Fixing frontend API...")
    
    api_file = Path("frontend/src/services/api.ts")
    if api_file.exists():
        try:
            with open(api_file, 'r') as f:
                content = f.read()
                
            # Add 405 error handling
            if "status === 405" not in content:
                error_handler = """
    // Handle 405 Method Not Allowed
    if (error.response?.status === 405) {
      console.error('405 Method Not Allowed:', error.config?.url);
      throw new Error('Service configuration issue. Please try again later.');
    }
"""
                
                # Insert before existing error handling
                content = content.replace(
                    "console.error('API Error:'",
                    error_handler + "\\n    console.error('API Error:'"
                )
                
                with open(api_file, 'w') as f:
                    f.write(content)
                    
                print("✅ Added 405 error handling to frontend")
                
        except Exception as e:
            print(f"❌ Error fixing frontend API: {e}")

def main():
    """Apply all fixes"""
    print("🚀 Applying 405 error fixes...")
    
    fix_backend_routes()
    fix_frontend_api()
    
    print("✅ Fix application completed!")
    print("Please test the authentication flow again.")

if __name__ == "__main__":
    main()
'''

        with open(fix_script_path, "w") as f:
            f.write(fix_script_content)

        self.logger.info(f"🔧 Fix script created: {fix_script_path}")


def main():
    """Main function"""
    print("🔍 Starting Complete 405 Error Diagnosis...")
    print("This will analyze backend, frontend, and perform live tests.")

    diagnostics = Main405Diagnostics()
    diagnostics.run_complete_diagnosis()

    print("\n✅ Complete diagnosis finished!")
    print("📄 Check COMPLETE_405_DIAGNOSIS.md for full report")
    print("🔧 Run python apply_405_fixes.py to apply fixes")


if __name__ == "__main__":
    main()

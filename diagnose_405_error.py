#!/usr/bin/env python3
"""
HireMeBahamas 405 Error Diagnostic Tool
Uses IntelliSense and automated testing to diagnose login/signup issues
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HireBahamas405Diagnostics:
    def __init__(self):
        self.backend_url = "https://hiremebahamas.onrender.com"
        self.results = []
        self.issues_found = []
        
    def log_result(self, test_name: str, status: str, details: str = "", data: Any = None):
        """Log diagnostic results"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test": test_name,
            "status": status,
            "details": details,
            "data": data
        }
        self.results.append(result)
        
        # Print with colors
        status_colors = {
            "PASS": "\033[92m✅",  # Green
            "FAIL": "\033[91m❌",  # Red
            "WARN": "\033[93m⚠️",   # Yellow
            "INFO": "\033[94mℹ️"    # Blue
        }
        
        color = status_colors.get(status, "")
        reset = "\033[0m"
        
        print(f"{color} {test_name}: {status}{reset}")
        if details:
            print(f"   {details}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        print()

    def test_backend_health(self) -> bool:
        """Test if backend is responding"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Backend Health Check", 
                    "PASS", 
                    f"Backend is healthy (status: {data.get('status')})", 
                    data
                )
                return True
            else:
                self.log_result(
                    "Backend Health Check", 
                    "FAIL", 
                    f"Unexpected status code: {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Backend Health Check", 
                "FAIL", 
                f"Connection failed: {str(e)}"
            )
            self.issues_found.append("Backend connection failed - service may be down")
            return False

    def test_cors_preflight(self) -> bool:
        """Test CORS preflight OPTIONS request"""
        try:
            headers = {
                'Origin': 'https://hiremebahamas.vercel.app',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type,Authorization'
            }
            
            response = requests.options(
                f"{self.backend_url}/api/auth/login", 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                cors_headers = {
                    'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                    'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                    'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
                }
                
                self.log_result(
                    "CORS Preflight Check", 
                    "PASS", 
                    "OPTIONS request successful", 
                    cors_headers
                )
                
                # Check if CORS headers are properly set
                if not cors_headers['Access-Control-Allow-Origin']:
                    self.issues_found.append("Missing Access-Control-Allow-Origin header")
                if not cors_headers['Access-Control-Allow-Methods']:
                    self.issues_found.append("Missing Access-Control-Allow-Methods header")
                    
                return True
            else:
                self.log_result(
                    "CORS Preflight Check", 
                    "FAIL", 
                    f"OPTIONS request failed with status: {response.status_code}",
                    {"status_code": response.status_code, "headers": dict(response.headers)}
                )
                self.issues_found.append(f"CORS preflight failed - {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "CORS Preflight Check", 
                "FAIL", 
                f"CORS preflight failed: {str(e)}"
            )
            self.issues_found.append("CORS preflight request failed")
            return False

    def test_login_endpoint_methods(self) -> Dict[str, bool]:
        """Test different HTTP methods on login endpoint"""
        methods_results = {}
        login_data = {
            "email": "admin@hiremebahamas.com",
            "password": "AdminPass123!"
        }
        
        # Test GET (should fail)
        try:
            response = requests.get(f"{self.backend_url}/api/auth/login", timeout=10)
            if response.status_code == 405:
                self.log_result(
                    "Login GET Method Check", 
                    "PASS", 
                    "Correctly rejects GET requests with 405"
                )
                methods_results['GET'] = True
            else:
                self.log_result(
                    "Login GET Method Check", 
                    "WARN", 
                    f"Unexpected response to GET: {response.status_code}"
                )
                methods_results['GET'] = False
        except Exception as e:
            self.log_result(
                "Login GET Method Check", 
                "FAIL", 
                f"GET request failed: {str(e)}"
            )
            methods_results['GET'] = False

        # Test POST (should succeed)
        try:
            response = requests.post(
                f"{self.backend_url}/api/auth/login", 
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Login POST Method Check", 
                    "PASS", 
                    "POST request successful",
                    response.json()
                )
                methods_results['POST'] = True
            elif response.status_code == 405:
                self.log_result(
                    "Login POST Method Check", 
                    "FAIL", 
                    "POST request returned 405 - This is the problem!",
                    {"status_code": response.status_code, "response": response.text}
                )
                self.issues_found.append("Login endpoint returns 405 for POST requests")
                methods_results['POST'] = False
            else:
                self.log_result(
                    "Login POST Method Check", 
                    "WARN", 
                    f"POST request returned unexpected status: {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                methods_results['POST'] = False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Login POST Method Check", 
                "FAIL", 
                f"POST request failed: {str(e)}"
            )
            methods_results['POST'] = False

        return methods_results

    def test_signup_endpoint(self) -> bool:
        """Test signup endpoint"""
        signup_data = {
            "email": f"test_{int(time.time())}@hirebahamas.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "freelancer",
            "location": "Nassau"
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/auth/register", 
                json=signup_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 201:
                self.log_result(
                    "Signup Endpoint Check", 
                    "PASS", 
                    "Registration successful",
                    response.json()
                )
                return True
            elif response.status_code == 405:
                self.log_result(
                    "Signup Endpoint Check", 
                    "FAIL", 
                    "Registration endpoint returns 405",
                    {"status_code": response.status_code, "response": response.text}
                )
                self.issues_found.append("Registration endpoint returns 405 for POST requests")
                return False
            else:
                self.log_result(
                    "Signup Endpoint Check", 
                    "WARN", 
                    f"Registration returned unexpected status: {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Signup Endpoint Check", 
                "FAIL", 
                f"Registration request failed: {str(e)}"
            )
            return False

    def test_endpoint_routing(self) -> None:
        """Test various endpoint variations to identify routing issues"""
        endpoints_to_test = [
            "/api/auth/login",
            "/auth/login",  # Alternative route
            "/login",       # Simple route
            "/api/login"    # Different API structure
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.post(
                    f"{self.backend_url}{endpoint}",
                    json={"email": "admin@hiremebahamas.com", "password": "AdminPass123!"},
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
                
                self.log_result(
                    f"Endpoint Route Test ({endpoint})", 
                    "INFO" if response.status_code == 200 else "WARN", 
                    f"Status: {response.status_code}",
                    {"endpoint": endpoint, "status": response.status_code}
                )
                
            except Exception as e:
                self.log_result(
                    f"Endpoint Route Test ({endpoint})", 
                    "FAIL", 
                    f"Request failed: {str(e)}"
                )

    def analyze_network_headers(self) -> None:
        """Analyze request/response headers for issues"""
        try:
            # Test with different user agents and headers
            test_headers = [
                {"User-Agent": "Mozilla/5.0 (Chrome/91.0.4472.124)"},
                {"User-Agent": "HireMeBahamas-Frontend/1.0"},
                {"Origin": "https://hiremebahamas.vercel.app"},
                {"Referer": "https://hiremebahamas.vercel.app/login"}
            ]
            
            for headers in test_headers:
                response = requests.post(
                    f"{self.backend_url}/api/auth/login",
                    json={"email": "admin@hiremebahamas.com", "password": "AdminPass123!"},
                    headers={**headers, 'Content-Type': 'application/json'},
                    timeout=10
                )
                
                self.log_result(
                    "Header Analysis", 
                    "INFO", 
                    f"Headers {headers} -> Status: {response.status_code}",
                    {"request_headers": headers, "response_status": response.status_code}
                )
                
        except Exception as e:
            self.log_result(
                "Header Analysis", 
                "FAIL", 
                f"Header analysis failed: {str(e)}"
            )

    def generate_recommendations(self) -> List[str]:
        """Generate specific recommendations based on findings"""
        recommendations = []
        
        if not self.issues_found:
            recommendations.append("✅ No major issues detected. The 405 error might be intermittent or client-side.")
            recommendations.append("🔍 Check browser network tab during login attempt for detailed error info.")
            recommendations.append("🔄 Try clearing browser cache and cookies.")
            
        else:
            recommendations.append("🔧 Issues found that need fixing:")
            for issue in self.issues_found:
                recommendations.append(f"  • {issue}")
                
            # Specific fixes based on common issues
            if any("CORS" in issue for issue in self.issues_found):
                recommendations.append("🌐 CORS Fix: Add proper CORS headers to backend")
                recommendations.append("   - Access-Control-Allow-Origin: *")
                recommendations.append("   - Access-Control-Allow-Methods: GET, POST, OPTIONS")
                recommendations.append("   - Access-Control-Allow-Headers: Content-Type, Authorization")
                
            if any("405" in issue for issue in self.issues_found):
                recommendations.append("🔗 Route Fix: Check backend route configuration")
                recommendations.append("   - Ensure /api/auth/login accepts POST method")
                recommendations.append("   - Verify Flask route decorator: @app.route('/api/auth/login', methods=['POST', 'OPTIONS'])")
                
            if any("connection" in issue.lower() for issue in self.issues_found):
                recommendations.append("🔌 Connection Fix: Backend deployment issue")
                recommendations.append("   - Check Render.com deployment status")
                recommendations.append("   - Verify environment variables are set")
                recommendations.append("   - Check backend logs for startup errors")
        
        return recommendations

    def run_full_diagnostic(self) -> None:
        """Run complete diagnostic suite"""
        print("🔍 HireMeBahamas 405 Error Diagnostic Tool")
        print("=" * 60)
        
        # Run all tests
        print("1. Testing backend connectivity...")
        backend_ok = self.test_backend_health()
        
        print("2. Testing CORS configuration...")
        cors_ok = self.test_cors_preflight()
        
        print("3. Testing login endpoint methods...")
        methods_results = self.test_login_endpoint_methods()
        
        print("4. Testing signup endpoint...")
        signup_ok = self.test_signup_endpoint()
        
        print("5. Testing endpoint routing...")
        self.test_endpoint_routing()
        
        print("6. Analyzing network headers...")
        self.analyze_network_headers()
        
        # Generate summary report
        print("\n" + "=" * 60)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 60)
        
        print(f"Backend Health: {'✅ PASS' if backend_ok else '❌ FAIL'}")
        print(f"CORS Configuration: {'✅ PASS' if cors_ok else '❌ FAIL'}")
        print(f"Login POST Method: {'✅ PASS' if methods_results.get('POST') else '❌ FAIL'}")
        print(f"Signup Endpoint: {'✅ PASS' if signup_ok else '❌ FAIL'}")
        
        print("\n🎯 RECOMMENDATIONS:")
        recommendations = self.generate_recommendations()
        for rec in recommendations:
            print(rec)
        
        # Save detailed results
        with open('405_diagnostic_results.json', 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "backend_health": backend_ok,
                    "cors_ok": cors_ok,
                    "login_post_ok": methods_results.get('POST', False),
                    "signup_ok": signup_ok
                },
                "issues": self.issues_found,
                "recommendations": recommendations,
                "detailed_results": self.results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: 405_diagnostic_results.json")
        print("=" * 60)

def main():
    diagnostics = HireBahamas405Diagnostics()
    diagnostics.run_full_diagnostic()

if __name__ == "__main__":
    main()
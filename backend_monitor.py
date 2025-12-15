#!/usr/bin/env python3
"""Real-time backend request monitor"""

import json
import time
from threading import Thread

import requests


class BackendMonitor:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8008"
        self.monitoring = False

    def test_login_continuously(self):
        """Test login endpoint every few seconds"""
        while self.monitoring:
            try:
                response = requests.post(
                    f"{self.base_url}/api/auth/login",
                    json={"email": "admin@hirebahamas.com", "password": "admin123"},
                    timeout=5,
                )

                print(
                    f"[{time.strftime('%H:%M:%S')}] Login test - Status: {response.status_code}"
                )

                if response.status_code != 200:
                    print(f"  ❌ Error: {response.text}")
                else:
                    print(f"  ✅ Success: Login working")

            except requests.exceptions.ConnectionError:
                print(f"[{time.strftime('%H:%M:%S')}] ❌ Backend not responding")
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] ❌ Error: {e}")

            time.sleep(5)

    def check_cors_headers(self):
        """Check CORS configuration"""
        try:
            print("\n=== CORS Configuration Check ===")

            # Test from different origins
            origins_to_test = [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://localhost:3002",
                "http://localhost:3003",
            ]

            for origin in origins_to_test:
                try:
                    response = requests.options(
                        f"{self.base_url}/api/auth/login",
                        headers={
                            "Origin": origin,
                            "Access-Control-Request-Method": "POST",
                            "Access-Control-Request-Headers": "Content-Type",
                        },
                    )

                    cors_origin = response.headers.get(
                        "Access-Control-Allow-Origin", "Not set"
                    )
                    cors_methods = response.headers.get(
                        "Access-Control-Allow-Methods", "Not set"
                    )

                    print(f"Origin {origin}:")
                    print(f"  Status: {response.status_code}")
                    print(f"  Allowed Origin: {cors_origin}")
                    print(f"  Allowed Methods: {cors_methods}")
                    print()

                except Exception as e:
                    print(f"Origin {origin}: Error - {e}")

        except Exception as e:
            print(f"CORS check error: {e}")

    def test_endpoints(self):
        """Test all available endpoints"""
        print("\n=== Endpoint Tests ===")

        endpoints = [
            ("GET", "/health", None),
            (
                "POST",
                "/api/auth/login",
                {"email": "admin@hirebahamas.com", "password": "admin123"},
            ),
            (
                "GET",
                "/api/auth/profile",
                None,
            ),  # This will fail without token but we can see the response
        ]

        for method, endpoint, data in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                print(f"Testing {method} {endpoint}...")

                if method == "GET":
                    response = requests.get(url, timeout=10)
                elif method == "POST":
                    response = requests.post(url, json=data, timeout=10)

                print(f"  Status: {response.status_code}")
                print(
                    f"  Response: {response.text[:200]}{'...' if len(response.text) > 200 else ''}"
                )
                print()

            except Exception as e:
                print(f"  Error: {e}")
                print()

    def run_diagnostics(self):
        """Run complete diagnostics"""
        print("🔍 Starting Backend Diagnostics...")
        print("=" * 50)

        self.test_endpoints()
        self.check_cors_headers()

        print("\n📊 Starting continuous monitoring...")
        print("Press Ctrl+C to stop")

        self.monitoring = True
        try:
            self.test_login_continuously()
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            self.monitoring = False


if __name__ == "__main__":
    monitor = BackendMonitor()
    monitor.run_diagnostics()

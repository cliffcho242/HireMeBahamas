#!/usr/bin/env python3
"""
🚀 Automated Login Fix - Find and Fix All Issues
This script automatically detects and fixes all login-related problems
"""
import json
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import bcrypt
import requests


class LoginFixAutomator:
    def __init__(self):
        self.base_path = Path("C:/Users/Dell/OneDrive/Desktop/HireBahamas")
        self.issues_found = []
        self.fixes_applied = []

    def log(self, message, level="INFO"):
        """Enhanced logging with colors"""
        colors = {
            "INFO": "🔍",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "FIX": "🔧",
        }
        print(f"{colors.get(level, '📝')} {message}")

    def test_backend_endpoints(self):
        """Test all backend endpoints"""
        self.log("Testing backend endpoints...")

        endpoints_to_test = [
            "http://127.0.0.1:8008/health",
            "http://127.0.0.1:8008/auth/login",
            "http://127.0.0.1:8008/api/auth/login",
        ]

        working_endpoints = []

        for endpoint in endpoints_to_test:
            try:
                if "login" in endpoint:
                    # Test with POST for login endpoints
                    response = requests.post(
                        endpoint, json={"email": "test", "password": "test"}, timeout=3
                    )
                    # Any response means endpoint exists (even if 401)
                    if response.status_code in [200, 401, 422]:
                        working_endpoints.append(endpoint)
                        self.log(f"Endpoint working: {endpoint}", "SUCCESS")
                    else:
                        self.log(
                            f"Endpoint returned {response.status_code}: {endpoint}",
                            "WARNING",
                        )
                else:
                    # Test with GET for health endpoint
                    response = requests.get(endpoint, timeout=3)
                    if response.status_code == 200:
                        working_endpoints.append(endpoint)
                        self.log(f"Endpoint working: {endpoint}", "SUCCESS")
            except requests.exceptions.ConnectionError:
                self.log(f"Endpoint not responding: {endpoint}", "ERROR")
                self.issues_found.append(f"Backend endpoint not responding: {endpoint}")
            except Exception as e:
                self.log(f"Endpoint error {endpoint}: {e}", "ERROR")

        return working_endpoints

    def fix_api_endpoints(self):
        """Fix API endpoint mismatches"""
        self.log("Checking API endpoint configurations...", "FIX")

        # Check backend routes
        backend_file = self.base_path / "facebook_like_backend.py"
        if backend_file.exists():
            with open(backend_file, "r") as f:
                backend_content = f.read()

            # Check if /api/auth/login exists
            if (
                "/api/auth/login" not in backend_content
                and "/auth/login" in backend_content
            ):
                self.log(
                    "Found endpoint mismatch - backend has /auth/login but frontend expects /api/auth/login",
                    "WARNING",
                )
                self.issues_found.append("API endpoint mismatch")

                # Add the missing endpoint
                if "@app.route('/auth/login'" in backend_content:
                    # Add duplicate route for /api/auth/login
                    login_route_pattern = (
                        r"@app\.route\('/auth/login'[^}]+\n    return [^}]+\n}"
                    )
                    import re

                    # Find the login function
                    login_func_start = backend_content.find("@app.route('/auth/login'")
                    if login_func_start != -1:
                        # Find the function definition and add alias
                        new_route = "\n@app.route('/api/auth/login', methods=['POST'])\ndef api_login():\n    return login()\n"

                        # Insert after the existing login function
                        login_func_end = backend_content.find(
                            "\n@app.route", login_func_start + 1
                        )
                        if login_func_end == -1:
                            login_func_end = len(backend_content)

                        new_content = (
                            backend_content[:login_func_end]
                            + new_route
                            + backend_content[login_func_end:]
                        )

                        with open(backend_file, "w") as f:
                            f.write(new_content)

                        self.log("Added /api/auth/login endpoint alias", "FIX")
                        self.fixes_applied.append("Added API endpoint alias")

                        return True
        return False

    def test_database_integrity(self):
        """Test database structure and admin account"""
        self.log("Testing database integrity...")

        db_paths = [
            self.base_path / "hirebahamas.db",
            self.base_path / "backend" / "hirebahamas.db",
        ]

        all_good = True

        for db_path in db_paths:
            if db_path.exists():
                self.log(f"Checking database: {db_path}")
                try:
                    conn = sqlite3.connect(str(db_path))
                    cursor = conn.cursor()

                    # Check table structure
                    cursor.execute("PRAGMA table_info(users)")
                    columns = [col[1] for col in cursor.fetchall()]

                    if "password_hash" not in columns:
                        self.log(f"Missing password_hash column in {db_path}", "ERROR")
                        self.issues_found.append(f"Database schema issue: {db_path}")
                        all_good = False
                        continue

                    # Check admin user
                    cursor.execute(
                        "SELECT id, email, password_hash FROM users WHERE email = ?",
                        ("admin@hirebahamas.com",),
                    )
                    admin_user = cursor.fetchone()

                    if not admin_user:
                        self.log(f"No admin user in {db_path}", "ERROR")
                        self.issues_found.append(f"Missing admin user: {db_path}")
                        all_good = False
                    else:
                        # Test password hash
                        try:
                            password_check = bcrypt.checkpw(
                                "admin123".encode(), admin_user[2].encode()
                            )
                            if not password_check:
                                self.log(
                                    f"Invalid admin password hash in {db_path}", "ERROR"
                                )
                                self.issues_found.append(
                                    f"Corrupted admin password: {db_path}"
                                )
                                all_good = False
                            else:
                                self.log(f"Admin user OK in {db_path}", "SUCCESS")
                        except Exception as e:
                            self.log(
                                f"Password verification error in {db_path}: {e}",
                                "ERROR",
                            )
                            self.issues_found.append(f"Password hash error: {db_path}")
                            all_good = False

                    conn.close()

                except Exception as e:
                    self.log(f"Database error {db_path}: {e}", "ERROR")
                    self.issues_found.append(f"Database access error: {db_path}")
                    all_good = False

        return all_good

    def fix_database_issues(self):
        """Fix all database issues"""
        self.log("Fixing database issues...", "FIX")

        # Run the ultimate database fix
        fix_script = self.base_path / "ultimate_database_fix.py"
        if fix_script.exists():
            try:
                result = subprocess.run(
                    [
                        "C:/Users/Dell/OneDrive/Desktop/HireBahamas/.venv/Scripts/python.exe",
                        str(fix_script),
                    ],
                    capture_output=True,
                    text=True,
                    cwd=str(self.base_path),
                )

                if result.returncode == 0:
                    self.log("Database fix completed successfully", "SUCCESS")
                    self.fixes_applied.append("Database schema and admin user fixed")
                    return True
                else:
                    self.log(f"Database fix failed: {result.stderr}", "ERROR")

            except Exception as e:
                self.log(f"Failed to run database fix: {e}", "ERROR")

        return False

    def restart_backend(self):
        """Restart backend server"""
        self.log("Restarting backend server...", "FIX")

        # Kill existing processes
        try:
            subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
            time.sleep(2)
        except:
            pass

        # Start new backend
        try:
            backend_script = self.base_path / "facebook_like_backend.py"
            cmd = [
                "C:/Users/Dell/OneDrive/Desktop/HireBahamas/.venv/Scripts/python.exe",
                str(backend_script),
            ]

            # Start in background
            process = subprocess.Popen(cmd, cwd=str(self.base_path))

            # Wait for startup
            time.sleep(5)

            # Test if it's running
            try:
                response = requests.get("http://127.0.0.1:8008/health", timeout=5)
                if response.status_code == 200:
                    self.log("Backend restarted successfully", "SUCCESS")
                    self.fixes_applied.append("Backend server restarted")
                    return True
            except:
                pass

        except Exception as e:
            self.log(f"Failed to restart backend: {e}", "ERROR")

        return False

    def test_full_login_flow(self):
        """Test complete login flow"""
        self.log("Testing complete login flow...")

        # Test both endpoints
        endpoints = [
            "http://127.0.0.1:8008/auth/login",
            "http://127.0.0.1:8008/api/auth/login",
        ]

        login_data = {"email": "admin@hirebahamas.com", "password": "admin123"}

        for endpoint in endpoints:
            try:
                response = requests.post(endpoint, json=login_data, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("token"):
                        self.log(f"Login successful at {endpoint}", "SUCCESS")
                        return True
                    else:
                        self.log(
                            f"Login response missing token at {endpoint}", "WARNING"
                        )
                else:
                    self.log(
                        f"Login failed at {endpoint}: {response.status_code} - {response.text}",
                        "ERROR",
                    )

            except Exception as e:
                self.log(f"Login test error at {endpoint}: {e}", "ERROR")

        return False

    def run_automated_fix(self):
        """Run complete automated fix process"""
        self.log("🚀 Starting Automated Login Fix Process", "INFO")
        self.log("=" * 60, "INFO")

        # Step 1: Test backend endpoints
        working_endpoints = self.test_backend_endpoints()

        # Step 2: Fix API endpoint issues
        if not any("/api/auth/login" in ep for ep in working_endpoints):
            self.fix_api_endpoints()

        # Step 3: Test database
        db_ok = self.test_database_integrity()
        if not db_ok:
            self.fix_database_issues()

        # Step 4: Restart backend to apply fixes
        if self.fixes_applied:
            self.restart_backend()

        # Step 5: Final test
        time.sleep(3)
        login_working = self.test_full_login_flow()

        # Summary
        self.log("=" * 60, "INFO")
        self.log("🎯 AUTOMATED FIX SUMMARY", "INFO")
        self.log("=" * 60, "INFO")

        self.log(f"Issues Found: {len(self.issues_found)}", "INFO")
        for issue in self.issues_found:
            self.log(f"  - {issue}", "WARNING")

        self.log(f"Fixes Applied: {len(self.fixes_applied)}", "INFO")
        for fix in self.fixes_applied:
            self.log(f"  - {fix}", "SUCCESS")

        if login_working:
            self.log("🎉 LOGIN SYSTEM FULLY OPERATIONAL!", "SUCCESS")
            self.log(
                "✅ Admin Credentials: admin@hirebahamas.com / admin123", "SUCCESS"
            )
            self.log("✅ Frontend: http://localhost:3000", "SUCCESS")
            self.log("✅ Backend: http://127.0.0.1:8008", "SUCCESS")
        else:
            self.log("❌ LOGIN SYSTEM STILL HAS ISSUES", "ERROR")
            self.log(
                "Please check the errors above and try manual troubleshooting", "ERROR"
            )

        return login_working


if __name__ == "__main__":
    fixer = LoginFixAutomator()
    success = fixer.run_automated_fix()
    sys.exit(0 if success else 1)

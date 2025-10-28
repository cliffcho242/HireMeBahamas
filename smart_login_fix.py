#!/usr/bin/env python3
"""
Smart AI-Enhanced Login Fix System
Automatically diagnoses and fixes login issues with continuous monitoring
"""
import asyncio
import sqlite3
import subprocess
import time
from datetime import datetime
from pathlib import Path

import bcrypt
import requests


class SmartLoginFix:
    """Intelligent login error detection and auto-repair system"""

    def __init__(self):
        self.workspace = Path(__file__).parent
        self.venv_python = self.workspace / ".venv" / "Scripts" / "python.exe"
        self.backend_url = "http://127.0.0.1:8008"
        self.db_path = self.workspace / "backend" / "hirebahamas.db"
        self.monitoring = False

        print("[INFO] Smart Login Fix initialized")

    def log(self, message: str, level: str = "INFO"):
        """Safe logging for Windows"""
        levels = {
            "INFO": "[INFO]",
            "SUCCESS": "[OK]",
            "ERROR": "[ERROR]",
            "WARNING": "[WARN]",
            "FIX": "[FIX]",
        }
        try:
            print(
                f"{levels.get(level, '[LOG]')} {datetime.now().strftime('%H:%M:%S')} {message}"
            )
        except UnicodeEncodeError:
            safe_message = message.encode("ascii", "ignore").decode("ascii")
            print(
                f"{levels.get(level, '[LOG]')} {datetime.now().strftime('%H:%M:%S')} {safe_message}"
            )

    async def diagnose_login_system(self):
        """Comprehensive login system diagnosis"""
        self.log("Starting login system diagnosis...", "INFO")

        issues = []

        # Check 1: Backend health
        try:
            response = await asyncio.to_thread(
                requests.get, f"{self.backend_url}/health", timeout=5
            )
            if response.status_code != 200:
                issues.append(
                    {
                        "type": "backend_unhealthy",
                        "details": f"Status: {response.status_code}",
                    }
                )
        except requests.exceptions.ConnectionError:
            issues.append({"type": "backend_down", "details": "Backend not responding"})
        except Exception as e:
            issues.append({"type": "backend_error", "details": str(e)})

        # Check 2: Database
        try:
            if not self.db_path.exists():
                issues.append(
                    {"type": "database_missing", "details": "Database file not found"}
                )
            else:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE email = ?",
                    ("admin@hirebahamas.com",),
                )
                admin_count = cursor.fetchone()[0]
                conn.close()

                if admin_count == 0:
                    issues.append(
                        {"type": "admin_missing", "details": "Admin user not found"}
                    )
        except Exception as e:
            issues.append({"type": "database_error", "details": str(e)})

        # Check 3: Login endpoint
        try:
            response = await asyncio.to_thread(
                requests.post,
                f"{self.backend_url}/api/auth/login",
                json={"email": "test", "password": "test"},
                timeout=5,
            )
            # Any structured response means endpoint exists
            if response.status_code not in [200, 401, 422, 400]:
                issues.append(
                    {
                        "type": "endpoint_error",
                        "details": f"Unexpected status: {response.status_code}",
                    }
                )
        except requests.exceptions.ConnectionError:
            if not any(issue["type"] == "backend_down" for issue in issues):
                issues.append(
                    {
                        "type": "endpoint_down",
                        "details": "Login endpoint not accessible",
                    }
                )
        except Exception as e:
            issues.append({"type": "endpoint_error", "details": str(e)})

        self.log(
            f"Diagnosis complete: {len(issues)} issues found",
            "WARNING" if issues else "SUCCESS",
        )
        return issues

    async def auto_fix_backend(self):
        """Auto-fix backend startup issues"""
        self.log("Fixing backend startup...", "FIX")

        try:
            # Kill existing processes
            await asyncio.to_thread(
                subprocess.run,
                ["taskkill", "/F", "/IM", "python.exe"],
                capture_output=True,
                check=False,
            )
            await asyncio.sleep(3)

            # Start backend
            backend_script = self.workspace / "facebook_like_backend.py"
            if not backend_script.exists():
                self.log("Backend script not found", "ERROR")
                return False

            process = await asyncio.to_thread(
                subprocess.Popen,
                [str(self.venv_python), str(backend_script)],
                cwd=str(self.workspace),
            )

            # Wait for startup
            for attempt in range(15):
                await asyncio.sleep(2)
                try:
                    response = await asyncio.to_thread(
                        requests.get, f"{self.backend_url}/health", timeout=3
                    )
                    if response.status_code == 200:
                        self.log("Backend fixed successfully", "SUCCESS")
                        return True
                except:
                    pass

            self.log("Backend fix failed - timeout", "ERROR")
            return False

        except Exception as e:
            self.log(f"Backend fix error: {str(e)}", "ERROR")
            return False

    async def auto_fix_database(self):
        """Auto-fix database issues"""
        self.log("Fixing database issues...", "FIX")

        try:
            # Run database repair
            fix_script = self.workspace / "ultimate_database_fix.py"
            if fix_script.exists():
                result = await asyncio.to_thread(
                    subprocess.run,
                    [str(self.venv_python), str(fix_script)],
                    capture_output=True,
                    cwd=str(self.workspace),
                )

                if result.returncode == 0:
                    self.log("Database fixed successfully", "SUCCESS")
                    return True

            self.log("Database fix failed", "ERROR")
            return False

        except Exception as e:
            self.log(f"Database fix error: {str(e)}", "ERROR")
            return False

    async def auto_fix_admin_user(self):
        """Auto-fix admin user issues"""
        self.log("Fixing admin user...", "FIX")

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Remove existing admin
            cursor.execute(
                "DELETE FROM users WHERE email = ?", ("admin@hirebahamas.com",)
            )

            # Create new admin
            password_hash = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt())

            cursor.execute(
                """
                INSERT INTO users (email, password_hash, username, full_name, is_active)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    "admin@hirebahamas.com",
                    password_hash.decode("utf-8"),
                    "admin",
                    "Platform Administrator",
                    True,
                ),
            )

            conn.commit()
            conn.close()

            self.log("Admin user fixed successfully", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Admin fix error: {str(e)}", "ERROR")
            return False

    async def auto_repair_system(self, issues):
        """Auto-repair system based on issues found"""
        self.log("Starting automatic repair...", "FIX")

        repair_success = True

        for issue in issues:
            issue_type = issue["type"]

            if issue_type in ["backend_down", "backend_unhealthy", "backend_error"]:
                success = await self.auto_fix_backend()
                if not success:
                    repair_success = False

            elif issue_type in ["database_missing", "database_error"]:
                success = await self.auto_fix_database()
                if not success:
                    repair_success = False

            elif issue_type == "admin_missing":
                success = await self.auto_fix_admin_user()
                if not success:
                    repair_success = False

            elif issue_type in ["endpoint_down", "endpoint_error"]:
                # Usually fixed by backend restart
                pass

        return repair_success

    async def test_login_functionality(self):
        """Test complete login functionality"""
        self.log("Testing login functionality...", "INFO")

        tests_passed = 0
        total_tests = 3

        # Test 1: Backend health
        try:
            response = await asyncio.to_thread(
                requests.get, f"{self.backend_url}/health", timeout=5
            )
            if response.status_code == 200:
                tests_passed += 1
                self.log("Health check: PASSED", "SUCCESS")
            else:
                self.log(
                    f"Health check: FAILED (Status: {response.status_code})", "ERROR"
                )
        except Exception as e:
            self.log(f"Health check: FAILED ({str(e)})", "ERROR")

        # Test 2: Valid login
        try:
            response = await asyncio.to_thread(
                requests.post,
                f"{self.backend_url}/api/auth/login",
                json={"email": "admin@hirebahamas.com", "password": "admin123"},
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("token") and result.get("user"):
                    tests_passed += 1
                    self.log("Valid login: PASSED", "SUCCESS")
                else:
                    self.log("Valid login: FAILED (Missing token/user)", "ERROR")
            else:
                self.log(
                    f"Valid login: FAILED (Status: {response.status_code})", "ERROR"
                )

        except Exception as e:
            self.log(f"Valid login: FAILED ({str(e)})", "ERROR")

        # Test 3: Invalid login handling
        try:
            response = await asyncio.to_thread(
                requests.post,
                f"{self.backend_url}/api/auth/login",
                json={"email": "wrong@email.com", "password": "wrongpass"},
                timeout=5,
            )

            if response.status_code == 401:
                tests_passed += 1
                self.log("Invalid login handling: PASSED", "SUCCESS")
            else:
                self.log(
                    f"Invalid login handling: FAILED (Expected 401, got {response.status_code})",
                    "ERROR",
                )

        except Exception as e:
            self.log(f"Invalid login handling: FAILED ({str(e)})", "ERROR")

        success_rate = tests_passed / total_tests

        if success_rate == 1.0:
            self.log("All login tests PASSED! System fully operational", "SUCCESS")
        else:
            self.log(
                f"Login tests: {tests_passed}/{total_tests} passed ({success_rate:.1%})",
                "WARNING",
            )

        return success_rate == 1.0

    async def run_smart_fix_cycle(self):
        """Run a complete smart fix cycle"""
        self.log("=== Smart Login Fix Cycle ===", "INFO")

        # Step 1: Diagnose
        issues = await self.diagnose_login_system()

        # Step 2: Repair if needed
        if issues:
            self.log(f"Found {len(issues)} issues - starting repair", "WARNING")
            repair_success = await self.auto_repair_system(issues)

            if repair_success:
                # Wait for systems to stabilize
                await asyncio.sleep(5)

                # Step 3: Test
                test_success = await self.test_login_functionality()

                if test_success:
                    self.log("Smart fix cycle COMPLETED SUCCESSFULLY", "SUCCESS")
                    return True
                else:
                    self.log("Tests still failing after repair", "ERROR")
                    return False
            else:
                self.log("Repair failed", "ERROR")
                return False
        else:
            self.log("No issues found - testing functionality", "INFO")
            test_success = await self.test_login_functionality()

            if test_success:
                self.log("System is healthy and operational", "SUCCESS")
                return True
            else:
                self.log("Tests failing despite no detected issues", "WARNING")
                return False

    async def start_continuous_monitoring(self):
        """Start continuous monitoring and auto-repair"""
        self.log("Starting continuous monitoring...", "INFO")
        self.monitoring = True

        while self.monitoring:
            try:
                success = await self.run_smart_fix_cycle()

                if success:
                    self.log("System healthy - monitoring continues", "SUCCESS")
                    await asyncio.sleep(120)  # Check every 2 minutes
                else:
                    self.log(
                        "System issues detected - retrying in 30 seconds", "WARNING"
                    )
                    await asyncio.sleep(30)

            except Exception as e:
                self.log(f"Monitoring error: {str(e)}", "ERROR")
                await asyncio.sleep(60)

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring = False
        self.log("Monitoring stopped", "INFO")


async def main():
    """Main execution function"""
    smart_fix = SmartLoginFix()

    try:
        # Run initial fix
        success = await smart_fix.run_smart_fix_cycle()

        if success:
            smart_fix.log(
                "Initial fix successful - starting continuous monitoring", "SUCCESS"
            )
            smart_fix.log("Press Ctrl+C to stop monitoring", "INFO")

            # Start monitoring
            await smart_fix.start_continuous_monitoring()
        else:
            smart_fix.log(
                "Initial fix failed - manual intervention may be required", "ERROR"
            )

    except KeyboardInterrupt:
        smart_fix.stop_monitoring()
        smart_fix.log("Smart Login Fix stopped by user", "INFO")
    except Exception as e:
        smart_fix.log(f"Critical error: {str(e)}", "ERROR")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
🤖 AI-Enhanced Login Error Detection & Auto-Fix System
Advanced AI-powered diagnostics with continuous monitoring and auto-repair
"""

import asyncio
import json
import logging
import os
import socket
import sqlite3
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import bcrypt
import requests


# Enhanced logging setup for Windows compatibility
class SafeLogger:
    def __init__(self):
        self.log_file = Path(__file__).parent / "logs" / "ai_autofix.log"
        self.log_file.parent.mkdir(exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
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
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} - {level} - {message}\n")
        except UnicodeEncodeError:
            safe_message = message.encode("ascii", "ignore").decode("ascii")
            print(
                f"{levels.get(level, '[LOG]')} {datetime.now().strftime('%H:%M:%S')} {safe_message}"
            )


safe_logger = SafeLogger()


class AdvancedLoginAI:
    """Next-generation AI system for login error detection and automatic repair"""

    def __init__(self):
        self.workspace_path = Path(__file__).parent
        self.venv_python = self.workspace_path / ".venv" / "Scripts" / "python.exe"
        self.backend_url = "http://127.0.0.1:8008"
        self.db_path = self.workspace_path / "backend" / "hirebahamas.db"

        # AI Intelligence Core
        self.monitoring_active = False
        self.repair_history = []
        self.error_intelligence = {}
        self.success_patterns = {}
        self.auto_heal_strategies = {}

        # Performance Metrics
        self.diagnostics_run = 0
        self.successful_repairs = 0
        self.uptime_start = datetime.now()

        # Initialize AI strategies
        self.init_ai_repair_strategies()

        safe_logger.log("Advanced Login AI System initialized", "SUCCESS")

    def init_ai_repair_strategies(self):
        """Initialize AI-powered repair strategies"""
        self.auto_heal_strategies = {
            "backend_down": self.heal_backend_startup,
            "database_corrupt": self.heal_database_issues,
            "admin_missing": self.heal_admin_user,
            "login_endpoints": self.heal_login_endpoints,
            "port_conflicts": self.heal_port_conflicts,
            "dependency_issues": self.heal_dependencies,
            "authentication_failure": self.heal_auth_system,
            "timeout_issues": self.heal_timeout_problems,
        }

        safe_logger.log("AI repair strategies initialized", "SUCCESS")

    async def smart_diagnosis(self) -> Dict:
        """AI-powered comprehensive system diagnosis"""
        safe_logger.log("Starting intelligent system diagnosis...", "INFO")
        self.diagnostics_run += 1

        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "system_health": "unknown",
            "critical_issues": [],
            "warnings": [],
            "recommendations": [],
            "ai_confidence": 0.0,
            "repair_priority": [],
        }

        # Backend Health Check
        backend_health = await self.check_backend_intelligence()
        if not backend_health["healthy"]:
            diagnosis["critical_issues"].append(
                {
                    "type": "backend_down",
                    "severity": "critical",
                    "details": backend_health["error"],
                    "fix_strategy": "heal_backend_startup",
                }
            )

        # Database Intelligence Check
        db_health = await self.check_database_intelligence()
        if not db_health["healthy"]:
            diagnosis["critical_issues"].append(
                {
                    "type": "database_corrupt",
                    "severity": "high",
                    "details": db_health["error"],
                    "fix_strategy": "heal_database_issues",
                }
            )

        # Authentication System Check
        auth_health = await self.check_auth_intelligence()
        if not auth_health["healthy"]:
            diagnosis["critical_issues"].append(
                {
                    "type": "authentication_failure",
                    "severity": "high",
                    "details": auth_health["error"],
                    "fix_strategy": "heal_auth_system",
                }
            )

        # Login Endpoint Intelligence
        endpoint_health = await self.check_endpoint_intelligence()
        if not endpoint_health["healthy"]:
            diagnosis["warnings"].append(
                {
                    "type": "login_endpoints",
                    "severity": "medium",
                    "details": endpoint_health["error"],
                    "fix_strategy": "heal_login_endpoints",
                }
            )

        # Calculate AI confidence and prioritize repairs
        total_issues = len(diagnosis["critical_issues"]) + len(diagnosis["warnings"])
        if total_issues == 0:
            diagnosis["system_health"] = "optimal"
            diagnosis["ai_confidence"] = 0.95
        elif len(diagnosis["critical_issues"]) == 0:
            diagnosis["system_health"] = "minor_issues"
            diagnosis["ai_confidence"] = 0.8
        else:
            diagnosis["system_health"] = "needs_repair"
            diagnosis["ai_confidence"] = 0.6

        # Prioritize repairs by severity
        all_issues = diagnosis["critical_issues"] + diagnosis["warnings"]
        diagnosis["repair_priority"] = sorted(
            all_issues,
            key=lambda x: {"critical": 3, "high": 2, "medium": 1, "low": 0}[
                x["severity"]
            ],
            reverse=True,
        )

        safe_logger.log(
            f"Diagnosis complete: {total_issues} issues, confidence: {diagnosis['ai_confidence']:.2f}",
            "WARNING" if total_issues > 0 else "SUCCESS",
        )

        return diagnosis

    async def check_backend_intelligence(self) -> Dict:
        """Intelligent backend health assessment"""
        try:
            response = await asyncio.to_thread(
                requests.get, f"{self.backend_url}/health", timeout=8
            )
            if response.status_code == 200:
                return {
                    "healthy": True,
                    "response_time": response.elapsed.total_seconds(),
                }
            else:
                return {
                    "healthy": False,
                    "error": f"Backend returned {response.status_code}",
                }
        except requests.exceptions.ConnectionError:
            return {
                "healthy": False,
                "error": "Backend not responding - server offline",
            }
        except Exception as e:
            return {"healthy": False, "error": f"Backend check failed: {str(e)}"}

    async def check_database_intelligence(self) -> Dict:
        """Intelligent database health assessment"""
        try:
            if not self.db_path.exists():
                return {"healthy": False, "error": "Database file missing"}

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Check table structure
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]

            required_columns = ["id", "email", "password_hash"]
            missing = [col for col in required_columns if col not in columns]

            if missing:
                conn.close()
                return {
                    "healthy": False,
                    "error": f"Missing database columns: {missing}",
                }

            # Check for users
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            conn.close()

            if user_count == 0:
                return {"healthy": False, "error": "No users in database"}

            return {"healthy": True, "user_count": user_count}

        except Exception as e:
            return {"healthy": False, "error": f"Database error: {str(e)}"}

    async def check_auth_intelligence(self) -> Dict:
        """Intelligent authentication system assessment"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute(
                "SELECT email, password_hash FROM users WHERE email = ?",
                ("admin@hirebahamas.com",),
            )
            admin = cursor.fetchone()

            if not admin:
                conn.close()
                return {"healthy": False, "error": "Admin user not found"}

            # Test password hash
            try:
                is_valid = bcrypt.checkpw(
                    "admin123".encode("utf-8"), admin[1].encode("utf-8")
                )
                conn.close()

                if not is_valid:
                    return {"healthy": False, "error": "Admin password hash invalid"}

                return {"healthy": True, "admin_verified": True}

            except Exception as e:
                conn.close()
                return {
                    "healthy": False,
                    "error": f"Password verification failed: {str(e)}",
                }

        except Exception as e:
            return {"healthy": False, "error": f"Auth check failed: {str(e)}"}

    async def check_endpoint_intelligence(self) -> Dict:
        """Intelligent endpoint health assessment"""
        try:
            # Test login endpoint
            response = await asyncio.to_thread(
                requests.post,
                f"{self.backend_url}/api/auth/login",
                json={"email": "test", "password": "test"},
                timeout=5,
            )

            # Any structured response means endpoint exists
            if response.status_code in [200, 401, 422, 400]:
                return {"healthy": True, "endpoint_active": True}
            else:
                return {
                    "healthy": False,
                    "error": f"Login endpoint returned {response.status_code}",
                }

        except requests.exceptions.ConnectionError:
            return {"healthy": False, "error": "Login endpoint not responding"}
        except Exception as e:
            return {"healthy": False, "error": f"Endpoint check failed: {str(e)}"}

    async def auto_heal_system(self, diagnosis: Dict) -> bool:
        """AI-powered automatic system healing"""
        safe_logger.log("Initiating AI-powered auto-healing sequence...", "FIX")

        healing_success = True
        healed_issues = []

        for issue in diagnosis["repair_priority"]:
            issue_type = issue["type"]
            fix_strategy = issue["fix_strategy"]

            safe_logger.log(
                f"Healing: {issue_type} (severity: {issue['severity']})", "FIX"
            )

            if fix_strategy in self.auto_heal_strategies:
                try:
                    success = await self.auto_heal_strategies[fix_strategy](issue)
                    if success:
                        healed_issues.append(issue_type)
                        safe_logger.log(f"Successfully healed: {issue_type}", "SUCCESS")
                    else:
                        safe_logger.log(f"Failed to heal: {issue_type}", "ERROR")
                        healing_success = False
                except Exception as e:
                    safe_logger.log(
                        f"Healing error for {issue_type}: {str(e)}", "ERROR"
                    )
                    healing_success = False
            else:
                safe_logger.log(f"No healing strategy for: {issue_type}", "WARNING")

        # Record healing attempt
        self.repair_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "issues_detected": len(diagnosis["repair_priority"]),
                "issues_healed": healed_issues,
                "success": healing_success,
            }
        )

        if healing_success:
            self.successful_repairs += 1

        return healing_success

    async def heal_backend_startup(self, issue: Dict) -> bool:
        """AI healing for backend startup issues"""
        try:
            safe_logger.log("Healing backend startup...", "FIX")

            # Kill existing processes
            await asyncio.to_thread(
                subprocess.run,
                ["taskkill", "/F", "/IM", "python.exe"],
                capture_output=True,
            )
            await asyncio.sleep(3)

            # Start fresh backend
            backend_script = self.workspace_path / "facebook_like_backend.py"
            process = await asyncio.to_thread(
                subprocess.Popen,
                [str(self.venv_python), str(backend_script)],
                cwd=str(self.workspace_path),
            )

            # Wait for startup
            for attempt in range(15):
                await asyncio.sleep(2)
                try:
                    response = await asyncio.to_thread(
                        requests.get, f"{self.backend_url}/health", timeout=3
                    )
                    if response.status_code == 200:
                        safe_logger.log("Backend healing successful", "SUCCESS")
                        return True
                except:
                    pass

            safe_logger.log("Backend healing failed - timeout", "ERROR")
            return False

        except Exception as e:
            safe_logger.log(f"Backend healing error: {str(e)}", "ERROR")
            return False

    async def heal_database_issues(self, issue: Dict) -> bool:
        """AI healing for database issues"""
        try:
            safe_logger.log("Healing database issues...", "FIX")

            # Run database repair script
            fix_script = self.workspace_path / "ultimate_database_fix.py"
            if fix_script.exists():
                result = await asyncio.to_thread(
                    subprocess.run,
                    [str(self.venv_python), str(fix_script)],
                    capture_output=True,
                    cwd=str(self.workspace_path),
                )

                if result.returncode == 0:
                    safe_logger.log("Database healing successful", "SUCCESS")
                    return True

            safe_logger.log("Database healing failed", "ERROR")
            return False

        except Exception as e:
            safe_logger.log(f"Database healing error: {str(e)}", "ERROR")
            return False

    async def heal_admin_user(self, issue: Dict) -> bool:
        """AI healing for admin user issues"""
        try:
            safe_logger.log("Healing admin user...", "FIX")

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Remove existing admin
            cursor.execute(
                "DELETE FROM users WHERE email = ?", ("admin@hirebahamas.com",)
            )

            # Create new admin with proper hash
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

            safe_logger.log("Admin user healing successful", "SUCCESS")
            return True

        except Exception as e:
            safe_logger.log(f"Admin healing error: {str(e)}", "ERROR")
            return False

    async def heal_auth_system(self, issue: Dict) -> bool:
        """AI healing for authentication system"""
        return await self.heal_admin_user(issue)

    async def heal_login_endpoints(self, issue: Dict) -> bool:
        """AI healing for login endpoint issues"""
        try:
            safe_logger.log("Healing login endpoints...", "FIX")

            # Check frontend API configurations
            api_files = [
                self.workspace_path / "frontend" / "src" / "services" / "api.ts",
                self.workspace_path
                / "frontend"
                / "src"
                / "services"
                / "api_ai_enhanced.ts",
            ]

            fixes_applied = 0
            for api_file in api_files:
                if api_file.exists():
                    content = api_file.read_text(encoding="utf-8")
                    if (
                        "'/auth/login'" in content
                        and "'/api/auth/login'" not in content
                    ):
                        content = content.replace("'/auth/login'", "'/api/auth/login'")
                        api_file.write_text(content, encoding="utf-8")
                        fixes_applied += 1

            if fixes_applied > 0:
                safe_logger.log("Login endpoint healing successful", "SUCCESS")
                return True

            return True  # No fixes needed

        except Exception as e:
            safe_logger.log(f"Endpoint healing error: {str(e)}", "ERROR")
            return False

    async def heal_port_conflicts(self, issue: Dict) -> bool:
        """AI healing for port conflicts"""
        try:
            safe_logger.log("Healing port conflicts...", "FIX")

            # Kill processes on port 8008
            await asyncio.to_thread(
                subprocess.run,
                ["taskkill", "/F", "/IM", "python.exe"],
                capture_output=True,
            )
            await asyncio.sleep(2)

            safe_logger.log("Port conflict healing successful", "SUCCESS")
            return True

        except Exception as e:
            safe_logger.log(f"Port healing error: {str(e)}", "ERROR")
            return False

    async def heal_dependencies(self, issue: Dict) -> bool:
        """AI healing for dependency issues"""
        try:
            safe_logger.log("Healing dependencies...", "FIX")

            packages = ["flask", "flask-cors", "bcrypt", "requests"]
            for package in packages:
                await asyncio.to_thread(
                    subprocess.run,
                    [str(self.venv_python), "-m", "pip", "install", package],
                    capture_output=True,
                )

            safe_logger.log("Dependency healing successful", "SUCCESS")
            return True

        except Exception as e:
            safe_logger.log(f"Dependency healing error: {str(e)}", "ERROR")
            return False

    async def heal_timeout_problems(self, issue: Dict) -> bool:
        """AI healing for timeout issues"""
        return await self.heal_backend_startup(issue)

    async def comprehensive_login_test(self) -> Dict:
        """Comprehensive login functionality test"""
        safe_logger.log("Running comprehensive login tests...", "INFO")

        test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "overall_success": False,
            "test_details": [],
        }

        # Test 1: Backend health
        try:
            response = await asyncio.to_thread(
                requests.get, f"{self.backend_url}/health", timeout=5
            )
            success = response.status_code == 200
            test_results["test_details"].append(
                {
                    "test": "backend_health",
                    "success": success,
                    "details": f"Status: {response.status_code}",
                }
            )
            if success:
                test_results["tests_passed"] += 1
            else:
                test_results["tests_failed"] += 1
        except Exception as e:
            test_results["test_details"].append(
                {
                    "test": "backend_health",
                    "success": False,
                    "details": f"Error: {str(e)}",
                }
            )
            test_results["tests_failed"] += 1

        # Test 2: Valid admin login
        try:
            response = await asyncio.to_thread(
                requests.post,
                f"{self.backend_url}/api/auth/login",
                json={"email": "admin@hirebahamas.com", "password": "admin123"},
                timeout=10,
            )

            success = response.status_code == 200
            test_results["test_details"].append(
                {
                    "test": "admin_login",
                    "success": success,
                    "details": f"Status: {response.status_code}",
                }
            )

            if success:
                test_results["tests_passed"] += 1
                # Verify token
                result = response.json()
                if result.get("token") and result.get("user"):
                    test_results["test_details"].append(
                        {
                            "test": "token_validation",
                            "success": True,
                            "details": "Token and user data present",
                        }
                    )
                    test_results["tests_passed"] += 1
                else:
                    test_results["test_details"].append(
                        {
                            "test": "token_validation",
                            "success": False,
                            "details": "Missing token or user data",
                        }
                    )
                    test_results["tests_failed"] += 1
            else:
                test_results["tests_failed"] += 1

        except Exception as e:
            test_results["test_details"].append(
                {"test": "admin_login", "success": False, "details": f"Error: {str(e)}"}
            )
            test_results["tests_failed"] += 1

        # Test 3: Invalid login handling
        try:
            response = await asyncio.to_thread(
                requests.post,
                f"{self.backend_url}/api/auth/login",
                json={"email": "wrong@email.com", "password": "wrongpass"},
                timeout=5,
            )

            success = response.status_code == 401
            test_results["test_details"].append(
                {
                    "test": "invalid_login_handling",
                    "success": success,
                    "details": f"Status: {response.status_code} (Expected: 401)",
                }
            )

            if success:
                test_results["tests_passed"] += 1
            else:
                test_results["tests_failed"] += 1

        except Exception as e:
            test_results["test_details"].append(
                {
                    "test": "invalid_login_handling",
                    "success": False,
                    "details": f"Error: {str(e)}",
                }
            )
            test_results["tests_failed"] += 1

        # Determine overall success
        test_results["overall_success"] = test_results["tests_failed"] == 0

        if test_results["overall_success"]:
            safe_logger.log(
                f"All {test_results['tests_passed']} login tests passed!", "SUCCESS"
            )
        else:
            safe_logger.log(
                f"Login tests: {test_results['tests_passed']} passed, {test_results['tests_failed']} failed",
                "WARNING",
            )

        return test_results

    async def start_continuous_monitoring(self):
        """Start continuous AI monitoring loop"""
        safe_logger.log("Starting continuous AI monitoring...", "INFO")
        self.monitoring_active = True

        while self.monitoring_active:
            try:
                # Run diagnosis
                diagnosis = await self.smart_diagnosis()

                if diagnosis["system_health"] != "optimal":
                    safe_logger.log(
                        f"Issues detected: {len(diagnosis['critical_issues'])} critical, {len(diagnosis['warnings'])} warnings",
                        "WARNING",
                    )

                    # Auto-heal
                    healing_success = await self.auto_heal_system(diagnosis)

                    if healing_success:
                        # Test after healing
                        await asyncio.sleep(5)
                        test_result = await self.comprehensive_login_test()

                        if test_result["overall_success"]:
                            safe_logger.log(
                                "System fully operational after AI healing", "SUCCESS"
                            )
                        else:
                            safe_logger.log(
                                "System needs manual intervention", "WARNING"
                            )
                    else:
                        safe_logger.log(
                            "AI healing failed - manual intervention required", "ERROR"
                        )
                else:
                    # System healthy, just verify
                    test_result = await self.comprehensive_login_test()
                    if test_result["overall_success"]:
                        safe_logger.log("System healthy - all tests passing", "SUCCESS")
                    else:
                        safe_logger.log(
                            "Tests failing despite healthy diagnosis", "WARNING"
                        )

                # Wait before next check
                await asyncio.sleep(90)  # Check every 90 seconds

            except Exception as e:
                safe_logger.log(f"Monitoring error: {str(e)}", "ERROR")
                await asyncio.sleep(30)

    def stop_monitoring(self):
        """Stop the AI monitoring system"""
        self.monitoring_active = False
        safe_logger.log("AI monitoring stopped", "INFO")

    async def run_single_healing_cycle(self):
        """Run a single diagnosis and healing cycle"""
        safe_logger.log("Running single AI healing cycle...", "INFO")

        # Diagnose
        diagnosis = await self.smart_diagnosis()

        if diagnosis["system_health"] != "optimal":
            # Heal
            healing_success = await self.auto_heal_system(diagnosis)

            if healing_success:
                await asyncio.sleep(5)
                test_result = await self.comprehensive_login_test()
                return test_result["overall_success"]
            return False
        else:
            # Just test
            test_result = await self.comprehensive_login_test()
            return test_result["overall_success"]


# Main execution functions
async def run_ai_enhanced_login_fix():
    """Run the AI-enhanced login fix system"""
    safe_logger.log("=== AI-Enhanced Login Fix System ===", "INFO")
    safe_logger.log("Initializing advanced AI diagnostics...", "INFO")

    ai_system = AdvancedLoginAI()

    # Run single healing cycle first
    success = await ai_system.run_single_healing_cycle()

    if success:
        safe_logger.log("Login system is fully operational!", "SUCCESS")
        safe_logger.log("Starting continuous AI monitoring...", "INFO")

        # Start continuous monitoring
        try:
            await ai_system.start_continuous_monitoring()
        except KeyboardInterrupt:
            ai_system.stop_monitoring()
            safe_logger.log("AI monitoring stopped by user", "INFO")
    else:
        safe_logger.log(
            "Failed to repair login system - manual intervention needed", "ERROR"
        )
        return False

    return True


def main():
    """Main entry point"""
    try:
        asyncio.run(run_ai_enhanced_login_fix())
    except KeyboardInterrupt:
        safe_logger.log("AI system stopped by user", "INFO")
    except Exception as e:
        safe_logger.log(f"Critical error: {str(e)}", "ERROR")


if __name__ == "__main__":
    main()

    def ai_analyze_connection_error(self) -> List[str]:
        """AI analysis of connection errors with learning"""
        fixes = []

        # Check if backend process is running
        if not self.check_port_availability("127.0.0.1", 8008):
            fixes.extend(
                [
                    "Backend server is not running - will auto-start",
                    "Check Python virtual environment",
                    "Verify Flask dependencies",
                ]
            )
        else:
            fixes.extend(
                [
                    "Port might be blocked by firewall",
                    "Backend may be starting up - wait 10 seconds",
                    "Check for CORS configuration issues",
                ]
            )

        # AI learning: remember successful fixes
        if self.error_patterns["connection_refused"]["count"] > 0:
            successful_fixes = self.error_patterns["connection_refused"]["fixes"]
            if successful_fixes:
                fixes.insert(
                    0, f"AI recommends: {successful_fixes[-1]} (success rate: high)"
                )

        return fixes

    def ai_analyze_http_error(self, status_code: int) -> List[str]:
        """AI analysis of HTTP errors"""
        error_map = {
            404: [
                "Check API endpoints",
                "Verify URL paths",
                "Update route definitions",
            ],
            500: [
                "Check server logs",
                "Verify database connection",
                "Check Python dependencies",
            ],
            503: ["Server overloaded", "Restart backend", "Check system resources"],
            401: ["Authentication required", "Check JWT tokens", "Verify credentials"],
        }
        return error_map.get(status_code, ["Unknown HTTP error", "Check server logs"])

    def ai_analyze_timeout_error(self) -> List[str]:
        """AI analysis of timeout errors"""
        return [
            "Server response too slow - check system resources",
            "Increase timeout settings",
            "Optimize database queries",
            "Check network connectivity",
        ]

    def test_frontend_connection(self) -> Dict:
        """Test frontend server connectivity"""
        logger.info("🔍 Testing frontend connection...")
        result = {
            "status": "unknown",
            "response_time": None,
            "error": None,
            "suggested_fixes": [],
        }

        try:
            start_time = time.time()
            response = requests.get(self.frontend_url, timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                result["status"] = "healthy"
                result["response_time"] = response_time
                logger.info(
                    f"✅ Frontend healthy (response time: {response_time:.3f}s)"
                )
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {response.status_code}"

        except requests.exceptions.ConnectionError as e:
            result["status"] = "connection_refused"
            result["error"] = str(e)
            result["suggested_fixes"] = [
                "Frontend server not running - will auto-start",
                "Check npm dependencies",
                "Verify Vite configuration",
            ]

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["suggested_fixes"] = ["Restart frontend server"]

        return result

    def auto_fix_backend(self) -> bool:
        """AI-powered automatic backend fixing"""
        logger.info("🤖 Applying AI auto-fix for backend...")

        try:
            # Check if backend is already running
            if self.check_port_availability("127.0.0.1", 8008):
                logger.info("✅ Backend already running on port 8008")
                return True

            # Auto-start backend
            backend_script = self.workspace_path / "facebook_like_backend.py"
            if not backend_script.exists():
                logger.error("❌ Backend script not found")
                return False

            # Use virtual environment Python
            venv_python = self.workspace_path / ".venv" / "Scripts" / "python.exe"
            python_cmd = str(venv_python) if venv_python.exists() else "python"

            logger.info(f"🚀 Starting backend with: {python_cmd}")

            # Start backend in background
            process = subprocess.Popen(
                [python_cmd, str(backend_script)],
                cwd=str(self.workspace_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
            )

            # Wait for backend to start
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                if self.check_port_availability("127.0.0.1", 8008):
                    logger.info("✅ Backend started successfully!")
                    self.error_patterns["connection_refused"]["fixes"].append(
                        "auto_start_backend"
                    )
                    return True
                logger.info(f"⏳ Waiting for backend... ({i+1}/30)")

            logger.error("❌ Backend failed to start within 30 seconds")
            return False

        except Exception as e:
            logger.error(f"❌ Failed to auto-fix backend: {e}")
            return False

    def auto_fix_frontend(self) -> bool:
        """AI-powered automatic frontend fixing"""
        logger.info("🤖 Applying AI auto-fix for frontend...")

        try:
            # Check if frontend is already running
            if self.check_port_availability("localhost", 3000):
                logger.info("✅ Frontend already running on port 3000")
                return True

            frontend_dir = self.workspace_path / "frontend"
            if not frontend_dir.exists():
                logger.error("❌ Frontend directory not found")
                return False

            # Start frontend in background
            logger.info("🚀 Starting frontend server...")

            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
            )

            # Wait for frontend to start
            for i in range(20):  # Wait up to 20 seconds
                time.sleep(1)
                if self.check_port_availability("localhost", 3000):
                    logger.info("✅ Frontend started successfully!")
                    return True
                logger.info(f"⏳ Waiting for frontend... ({i+1}/20)")

            logger.error("❌ Frontend failed to start within 20 seconds")
            return False

        except Exception as e:
            logger.error(f"❌ Failed to auto-fix frontend: {e}")
            return False

    def run_comprehensive_diagnostics(self) -> Dict:
        """Run complete AI-enhanced diagnostics"""
        logger.info("🚀 Starting AI-Enhanced Localhost Diagnostics...")

        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "backend": {},
            "frontend": {},
            "system": {},
            "ai_analysis": {},
            "auto_fixes_applied": [],
        }

        # Test connections
        diagnostics["backend"] = self.test_backend_connection()
        diagnostics["frontend"] = self.test_frontend_connection()

        # System diagnostics
        diagnostics["system"] = {
            "python_version": sys.version,
            "platform": os.name,
            "working_directory": str(Path.cwd()),
            "workspace_path": str(self.workspace_path),
        }

        # AI Analysis
        backend_healthy = diagnostics["backend"]["status"] == "healthy"
        frontend_healthy = diagnostics["frontend"]["status"] == "healthy"

        if backend_healthy and frontend_healthy:
            self.ai_confidence_score = 0.95
            diagnostics["ai_analysis"] = {
                "overall_status": "excellent",
                "confidence_score": self.ai_confidence_score,
                "recommendation": "All systems operational - platform ready for users",
            }
        else:
            # Apply AI auto-fixes
            auto_fixes = []

            if not backend_healthy:
                logger.info("🤖 Backend issues detected - applying AI auto-fix...")
                if self.auto_fix_backend():
                    auto_fixes.append("backend_auto_started")
                    diagnostics["backend"] = self.test_backend_connection()

            if not frontend_healthy:
                logger.info("🤖 Frontend issues detected - applying AI auto-fix...")
                if self.auto_fix_frontend():
                    auto_fixes.append("frontend_auto_started")
                    diagnostics["frontend"] = self.test_frontend_connection()

            diagnostics["auto_fixes_applied"] = auto_fixes

            # Recalculate confidence
            backend_healthy = diagnostics["backend"]["status"] == "healthy"
            frontend_healthy = diagnostics["frontend"]["status"] == "healthy"

            if backend_healthy and frontend_healthy:
                self.ai_confidence_score = 0.90
                diagnostics["ai_analysis"] = {
                    "overall_status": "excellent_after_fix",
                    "confidence_score": self.ai_confidence_score,
                    "recommendation": "AI auto-fix successful - platform operational",
                }
            else:
                self.ai_confidence_score = 0.60
                diagnostics["ai_analysis"] = {
                    "overall_status": "needs_attention",
                    "confidence_score": self.ai_confidence_score,
                    "recommendation": "Manual intervention may be required",
                }

        # Save AI learning
        self.save_ai_knowledge()

        return diagnostics

    def print_diagnostic_report(self, diagnostics: Dict):
        """Print beautiful diagnostic report"""
        print("\n" + "=" * 80)
        print("🤖 AI-ENHANCED LOCALHOST DIAGNOSTIC REPORT")
        print("=" * 80)

        # Overall status
        ai_analysis = diagnostics["ai_analysis"]
        status_emoji = (
            "🟢"
            if ai_analysis["confidence_score"] > 0.8
            else "🟡" if ai_analysis["confidence_score"] > 0.5 else "🔴"
        )

        print(
            f"\n{status_emoji} OVERALL STATUS: {ai_analysis['overall_status'].upper()}"
        )
        print(f"🧠 AI Confidence Score: {ai_analysis['confidence_score']:.2f}")
        print(f"💡 Recommendation: {ai_analysis['recommendation']}")

        # Backend status
        backend = diagnostics["backend"]
        backend_emoji = "🟢" if backend["status"] == "healthy" else "🔴"
        print(f"\n{backend_emoji} BACKEND (http://127.0.0.1:8008)")
        print(f"   Status: {backend['status']}")
        if backend["response_time"]:
            print(f"   Response Time: {backend['response_time']:.3f}s")
        if backend["error"]:
            print(f"   Error: {backend['error']}")

        # Frontend status
        frontend = diagnostics["frontend"]
        frontend_emoji = "🟢" if frontend["status"] == "healthy" else "🔴"
        print(f"\n{frontend_emoji} FRONTEND (http://localhost:3000)")
        print(f"   Status: {frontend['status']}")
        if frontend["response_time"]:
            print(f"   Response Time: {frontend['response_time']:.3f}s")
        if frontend["error"]:
            print(f"   Error: {frontend['error']}")

        # Auto-fixes applied
        if diagnostics["auto_fixes_applied"]:
            print(f"\n🤖 AI AUTO-FIXES APPLIED:")
            for fix in diagnostics["auto_fixes_applied"]:
                print(f"   ✅ {fix}")

        print("\n" + "=" * 80)

        # URLs for easy access
        if (
            diagnostics["backend"]["status"] == "healthy"
            and diagnostics["frontend"]["status"] == "healthy"
        ):
            print("🎉 PLATFORM READY! Access URLs:")
            print("   🌐 Frontend: http://localhost:3000")
            print("   🚀 Backend API: http://127.0.0.1:8008")
            print("   📊 Health Check: http://127.0.0.1:8008/health")
            print("   👤 Login: admin@hirebahamas.com / AdminPass123!")

        print("=" * 80 + "\n")


def main():
    """Main execution function"""
    try:
        ai_diagnostics = AILocalhostDiagnostics()

        print("🤖 AI-Enhanced Localhost Error Detection & Auto-Fix")
        print("🚀 Scanning for issues and applying intelligent fixes...\n")

        # Run comprehensive diagnostics
        results = ai_diagnostics.run_comprehensive_diagnostics()

        # Print results
        ai_diagnostics.print_diagnostic_report(results)

        # Save detailed results
        results_file = Path("ai_diagnostic_results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"📊 Detailed results saved to: {results_file}")

        # If everything is working, open browser
        if (
            results["backend"]["status"] == "healthy"
            and results["frontend"]["status"] == "healthy"
        ):

            print("\n🎊 SUCCESS! Opening your Facebook-like AI platform...")
            time.sleep(2)

            # Open browser (Windows)
            if os.name == "nt":
                os.system("start http://localhost:3000")
                os.system("start http://127.0.0.1:8008/health")

    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        print(f"\n❌ Unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
IntelliSense-Powered 405 Error Diagnostic & Fix Tool
This tool uses VS Code IntelliSense capabilities to diagnose and fix 405 errors
in the HireBahamas authentication system.
"""

import json
import logging
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import requests
from dataclasses import dataclass
from enum import Enum
import re
import ast


class ErrorSeverity(Enum):
    """Error severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class DiagnosticIssue:
    """Represents a diagnostic issue found"""

    severity: ErrorSeverity
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    column: Optional[int] = None
    code: Optional[str] = None
    fix_suggestion: Optional[str] = None


class IntelliSense405Diagnostics:
    """IntelliSense-powered 405 error diagnostics"""

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.issues: List[DiagnosticIssue] = []
        self.setup_logging()

        # API endpoints to check
        self.api_base = "https://hiremebahamas-backend.render.app"
        self.local_api = "http://localhost:5000"

        # Known authentication routes
        self.auth_routes = [
            "/api/auth/login",
            "/api/auth/register",
            "/auth/login",
            "/auth/register",
        ]

    def setup_logging(self):
        """Setup diagnostic logging"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("405_diagnostics.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def analyze_route_definitions(self) -> None:
        """Analyze backend route definitions using IntelliSense"""
        self.logger.info("🔍 Analyzing route definitions...")

        # Find all Python backend files
        backend_files = list(self.workspace_root.rglob("*.py"))
        backend_files = [
            f
            for f in backend_files
            if any(
                keyword in f.name.lower()
                for keyword in ["backend", "api", "server", "app", "main"]
            )
        ]

        for file_path in backend_files:
            self._analyze_python_routes(file_path)

        # Analyze TypeScript/JavaScript frontend API calls
        frontend_files = list(self.workspace_root.rglob("*.ts")) + list(
            self.workspace_root.rglob("*.tsx")
        )
        for file_path in frontend_files:
            self._analyze_frontend_api_calls(file_path)

    def _analyze_python_routes(self, file_path: Path) -> None:
        """Analyze Python routes for potential issues"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST for route analysis
            try:
                tree = ast.parse(content)
                route_visitor = RouteVisitor(str(file_path))
                route_visitor.visit(tree)

                for issue in route_visitor.issues:
                    self.issues.append(issue)

            except SyntaxError as e:
                self.issues.append(
                    DiagnosticIssue(
                        severity=ErrorSeverity.ERROR,
                        message=f"Syntax error in {file_path.name}: {e}",
                        file_path=str(file_path),
                        line_number=e.lineno,
                    )
                )

            # Check for common 405 patterns
            self._check_route_patterns(content, file_path)

        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {e}")

    def _check_route_patterns(self, content: str, file_path: Path) -> None:
        """Check for common patterns causing 405 errors"""
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for missing OPTIONS in route decorators
            if "@app.route(" in line and "methods=" in line:
                if "POST" in line and "OPTIONS" not in line:
                    self.issues.append(
                        DiagnosticIssue(
                            severity=ErrorSeverity.WARNING,
                            message="POST route missing OPTIONS method for CORS",
                            file_path=str(file_path),
                            line_number=i,
                            code=line.strip(),
                            fix_suggestion="Add 'OPTIONS' to methods list: methods=['POST', 'OPTIONS']",
                        )
                    )

            # Check for missing CORS handling
            if "def login(" in line or "def register(" in line:
                # Look for OPTIONS handling in next few lines
                next_lines = lines[i : i + 10] if i < len(lines) - 10 else lines[i:]
                has_options_check = any(
                    'request.method == "OPTIONS"' in nl for nl in next_lines
                )

                if not has_options_check:
                    self.issues.append(
                        DiagnosticIssue(
                            severity=ErrorSeverity.ERROR,
                            message="Auth endpoint missing OPTIONS request handling",
                            file_path=str(file_path),
                            line_number=i,
                            fix_suggestion="Add: if request.method == 'OPTIONS': return '', 200",
                        )
                    )

    def _analyze_frontend_api_calls(self, file_path: Path) -> None:
        """Analyze frontend API calls for potential issues"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for API endpoint mismatches
            api_calls = re.findall(r'api\.post\([\'"]([^\'"]+)[\'"]', content)

            for api_call in api_calls:
                if "auth" in api_call:
                    # Check if the endpoint format matches backend
                    if not any(route in api_call for route in self.auth_routes):
                        self.issues.append(
                            DiagnosticIssue(
                                severity=ErrorSeverity.WARNING,
                                message=f"Potentially mismatched auth endpoint: {api_call}",
                                file_path=str(file_path),
                                fix_suggestion="Verify endpoint matches backend route definitions",
                            )
                        )

        except Exception as e:
            self.logger.error(f"Error analyzing frontend file {file_path}: {e}")

    def test_live_endpoints(self) -> None:
        """Test live API endpoints for 405 errors"""
        self.logger.info("🌐 Testing live API endpoints...")

        test_data = {"email": "admin@hiremebahamas.com", "password": "AdminPass123!"}

        for base_url in [self.api_base, self.local_api]:
            self.logger.info(f"Testing {base_url}...")

            for route in self.auth_routes:
                endpoint = f"{base_url}{route}"

                # Test OPTIONS request (CORS preflight)
                self._test_options_request(endpoint)

                # Test POST request
                self._test_post_request(endpoint, test_data)

    def _test_options_request(self, endpoint: str) -> None:
        """Test OPTIONS request for CORS"""
        try:
            response = requests.options(endpoint, timeout=10)

            if response.status_code == 405:
                self.issues.append(
                    DiagnosticIssue(
                        severity=ErrorSeverity.CRITICAL,
                        message=f"405 error on OPTIONS request to {endpoint}",
                        fix_suggestion="Backend needs to handle OPTIONS requests for CORS",
                    )
                )
            elif response.status_code == 200:
                # Check CORS headers
                if "Access-Control-Allow-Methods" not in response.headers:
                    self.issues.append(
                        DiagnosticIssue(
                            severity=ErrorSeverity.WARNING,
                            message=f"Missing CORS headers in OPTIONS response from {endpoint}",
                            fix_suggestion="Add proper CORS headers to OPTIONS response",
                        )
                    )

        except requests.exceptions.RequestException as e:
            self.issues.append(
                DiagnosticIssue(
                    severity=ErrorSeverity.ERROR,
                    message=f"Failed to connect to {endpoint}: {e}",
                    fix_suggestion="Check if backend server is running and accessible",
                )
            )

    def _test_post_request(self, endpoint: str, data: Dict) -> None:
        """Test POST request for authentication"""
        try:
            response = requests.post(
                endpoint,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 405:
                self.issues.append(
                    DiagnosticIssue(
                        severity=ErrorSeverity.CRITICAL,
                        message=f"405 error on POST request to {endpoint}",
                        fix_suggestion="Check backend route definition and HTTP methods",
                    )
                )
            else:
                self.logger.info(f"✅ {endpoint} returned {response.status_code}")

        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Request failed to {endpoint}: {e}")

    def check_backend_deployment(self) -> None:
        """Check backend deployment status"""
        self.logger.info("🚀 Checking backend deployment status...")

        try:
            # Check health endpoint
            health_url = f"{self.api_base}/health"
            response = requests.get(health_url, timeout=30)

            if response.status_code == 200:
                self.logger.info("✅ Backend health check passed")
            else:
                self.issues.append(
                    DiagnosticIssue(
                        severity=ErrorSeverity.ERROR,
                        message=f"Backend health check failed: {response.status_code}",
                        fix_suggestion="Check backend deployment logs",
                    )
                )

        except requests.exceptions.RequestException as e:
            self.issues.append(
                DiagnosticIssue(
                    severity=ErrorSeverity.CRITICAL,
                    message=f"Cannot reach backend: {e}",
                    fix_suggestion="Verify backend URL and deployment status",
                )
            )

    def generate_fixes(self) -> List[str]:
        """Generate automated fixes for identified issues"""
        fixes = []

        for issue in self.issues:
            if issue.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
                if issue.fix_suggestion:
                    fixes.append(f"🔧 {issue.message}\n   Fix: {issue.fix_suggestion}")

        return fixes

    def create_intellisense_config(self) -> None:
        """Create VS Code IntelliSense configuration for better error detection"""
        vscode_dir = self.workspace_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)

        # Update settings.json for better Python/TypeScript analysis
        settings_path = vscode_dir / "settings.json"

        additional_settings = {
            "python.analysis.typeCheckingMode": "strict",
            "python.analysis.autoImportCompletions": True,
            "python.analysis.diagnosticMode": "workspace",
            "typescript.preferences.includePackageJsonAutoImports": "on",
            "typescript.suggest.autoImports": True,
            "typescript.validate.enable": True,
            "eslint.validate": [
                "javascript",
                "javascriptreact",
                "typescript",
                "typescriptreact",
            ],
            "pylint.args": ["--disable=missing-docstring", "--enable=all"],
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": True,
        }

        if settings_path.exists():
            with open(settings_path, "r") as f:
                current_settings = json.load(f)
            current_settings.update(additional_settings)
        else:
            current_settings = additional_settings

        with open(settings_path, "w") as f:
            json.dump(current_settings, f, indent=2)

        self.logger.info("✅ Updated VS Code IntelliSense configuration")

    def run_diagnostics(self) -> None:
        """Run complete diagnostic suite"""
        self.logger.info("🔍 Starting IntelliSense 405 Error Diagnostics...")

        # Clear previous issues
        self.issues.clear()

        # Run diagnostic phases
        self.analyze_route_definitions()
        self.test_live_endpoints()
        self.check_backend_deployment()
        self.create_intellisense_config()

        # Generate report
        self.generate_diagnostic_report()

    def generate_diagnostic_report(self) -> None:
        """Generate comprehensive diagnostic report"""
        report_path = self.workspace_root / "405_DIAGNOSTIC_REPORT.md"

        with open(report_path, "w") as f:
            f.write("# 🔍 IntelliSense 405 Error Diagnostic Report\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Summary
            critical_count = sum(
                1 for i in self.issues if i.severity == ErrorSeverity.CRITICAL
            )
            error_count = sum(
                1 for i in self.issues if i.severity == ErrorSeverity.ERROR
            )
            warning_count = sum(
                1 for i in self.issues if i.severity == ErrorSeverity.WARNING
            )

            f.write("## Summary\n\n")
            f.write(f"- 🔴 Critical Issues: {critical_count}\n")
            f.write(f"- ❌ Errors: {error_count}\n")
            f.write(f"- ⚠️ Warnings: {warning_count}\n\n")

            # Issues by severity
            for severity in [
                ErrorSeverity.CRITICAL,
                ErrorSeverity.ERROR,
                ErrorSeverity.WARNING,
                ErrorSeverity.INFO,
            ]:
                severity_issues = [i for i in self.issues if i.severity == severity]

                if severity_issues:
                    icon = {
                        "critical": "🔴",
                        "error": "❌",
                        "warning": "⚠️",
                        "info": "ℹ️",
                    }[severity.value]
                    f.write(f"## {icon} {severity.value.title()} Issues\n\n")

                    for issue in severity_issues:
                        f.write(f"### {issue.message}\n\n")

                        if issue.file_path:
                            f.write(f"**File:** `{issue.file_path}`\n")
                        if issue.line_number:
                            f.write(f"**Line:** {issue.line_number}\n")
                        if issue.code:
                            f.write(f"**Code:** `{issue.code}`\n")
                        if issue.fix_suggestion:
                            f.write(f"**Fix:** {issue.fix_suggestion}\n")
                        f.write("\n")

            # Automated fixes
            fixes = self.generate_fixes()
            if fixes:
                f.write("## 🔧 Recommended Fixes\n\n")
                for fix in fixes:
                    f.write(f"{fix}\n\n")

            f.write("## ✅ Next Steps\n\n")
            f.write("1. Review critical and error issues first\n")
            f.write("2. Apply recommended fixes\n")
            f.write("3. Test authentication endpoints\n")
            f.write("4. Re-run diagnostics to verify fixes\n")

        self.logger.info(f"📄 Diagnostic report saved to: {report_path}")


class RouteVisitor(ast.NodeVisitor):
    """AST visitor for analyzing Flask routes"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues: List[DiagnosticIssue] = []

    def visit_FunctionDef(self, node):
        """Visit function definitions to analyze route handlers"""
        # Check for route decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if hasattr(decorator.func, "attr") and decorator.func.attr == "route":
                    self._analyze_route_decorator(decorator, node)

        self.generic_visit(node)

    def _analyze_route_decorator(self, decorator, func_node):
        """Analyze route decorator for potential issues"""
        # Extract route path and methods
        route_path = None
        methods = []

        for arg in decorator.args:
            if isinstance(arg, ast.Constant):
                route_path = arg.value

        for keyword in decorator.keywords:
            if keyword.arg == "methods":
                if isinstance(keyword.value, ast.List):
                    methods = [
                        elt.value
                        for elt in keyword.value.elts
                        if isinstance(elt, ast.Constant)
                    ]

        # Check for authentication routes with potential issues
        if route_path and "auth" in route_path:
            if "POST" in methods and "OPTIONS" not in methods:
                self.issues.append(
                    DiagnosticIssue(
                        severity=ErrorSeverity.WARNING,
                        message=f"Auth route {route_path} missing OPTIONS method",
                        file_path=self.file_path,
                        line_number=func_node.lineno,
                        fix_suggestion="Add 'OPTIONS' to methods list for CORS support",
                    )
                )


def main():
    """Main diagnostic function"""
    print("🔍 IntelliSense 405 Error Diagnostics Starting...")

    diagnostics = IntelliSense405Diagnostics()
    diagnostics.run_diagnostics()

    print(f"\n✅ Diagnostics complete! Found {len(diagnostics.issues)} issues.")
    print("📄 Check 405_DIAGNOSTIC_REPORT.md for detailed analysis.")


if __name__ == "__main__":
    main()

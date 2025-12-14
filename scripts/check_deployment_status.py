#!/usr/bin/env python3
"""
HireMeBahamas Comprehensive Deployment Status Checker
=====================================================

Performs comprehensive checks on all deployment components to diagnose
what's preventing the app from being fully online.

Usage:
    python scripts/check_deployment_status.py
    python scripts/check_deployment_status.py --url https://your-app.vercel.app
    python scripts/check_deployment_status.py --url https://your-app.vercel.app --json
    python scripts/check_deployment_status.py --url https://your-app.vercel.app --fix

Exit codes:
    0: All systems operational
    1: Issues detected
"""

import argparse
import json
import os
import sys
import time
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse
import re

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


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


class StatusCheck:
    """Represents the result of a status check"""
    def __init__(self, category: str, name: str, status: str, 
                 message: str = "", details: Optional[Dict] = None,
                 fix_suggestion: Optional[str] = None):
        self.category = category
        self.name = name
        self.status = status  # "ok", "warning", "error", "critical"
        self.message = message
        self.details = details or {}
        self.fix_suggestion = fix_suggestion
    
    def to_dict(self) -> Dict:
        return {
            "category": self.category,
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "fix_suggestion": self.fix_suggestion
        }


class DeploymentStatusChecker:
    """Main class for checking deployment status"""
    
    def __init__(self, url: Optional[str] = None, verbose: bool = False, 
                 output_json: bool = False, show_fix: bool = False):
        self.url = url.rstrip('/') if url else None
        self.verbose = verbose
        self.output_json = output_json
        self.show_fix = show_fix
        self.checks: List[StatusCheck] = []
        self.session = self._create_session() if HAS_REQUESTS else None
        self.deployment_info = {}
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _log(self, message: str, color: str = Colors.ENDC):
        """Print message with color (unless in JSON mode)"""
        if not self.output_json:
            print(f"{color}{message}{Colors.ENDC}")
    
    def _verbose_log(self, message: str):
        """Log message only in verbose mode"""
        if self.verbose and not self.output_json:
            self._log(f"  [VERBOSE] {message}", Colors.OKCYAN)
    
    def _make_request(self, endpoint: str, timeout: int = 60) -> Tuple[Optional[requests.Response], Optional[Exception]]:
        """Make HTTP request with error handling"""
        if not HAS_REQUESTS or not self.session or not self.url:
            return None, Exception("Requests library not available or URL not set")
        
        url = f"{self.url}{endpoint}"
        self._verbose_log(f"Making request to {url}")
        
        try:
            response = self.session.get(url, timeout=timeout)
            return response, None
        except Exception as e:
            self._verbose_log(f"Request failed: {str(e)}")
            return None, e
    
    def detect_deployment_platform(self):
        """Detect deployment platform and gather info"""
        self._log("\n🌐 DEPLOYMENT DETECTION", Colors.HEADER)
        self._log("═" * 60)
        
        platform = "Unknown"
        frontend_url = self.url or "Not detected"
        backend_url = "Not detected"
        
        # Check environment variables
        vercel_url = os.getenv("VERCEL_URL")
        railway_static_url = os.getenv("RAILWAY_STATIC_URL")
        railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
        
        if vercel_url or (self.url and "vercel.app" in self.url):
            platform = "Vercel"
            if not self.url and vercel_url:
                self.url = f"https://{vercel_url}"
                frontend_url = self.url
        
        if railway_static_url or railway_public_domain or (self.url and "railway.app" in self.url):
            if platform == "Vercel":
                platform = "Vercel + Railway"
                backend_url = f"https://{railway_public_domain}" if railway_public_domain else "Check Railway dashboard"
            else:
                platform = "Railway"
                if not self.url and railway_public_domain:
                    self.url = f"https://{railway_public_domain}"
                    frontend_url = self.url
        
        self.deployment_info = {
            "platform": platform,
            "frontend_url": frontend_url,
            "backend_url": backend_url if platform == "Vercel + Railway" else frontend_url
        }
        
        status = "ok" if platform != "Unknown" else "warning"
        self.checks.append(StatusCheck(
            "deployment", "Platform Detection", status,
            f"Platform: {platform}",
            {"platform": platform, "frontend_url": frontend_url, "backend_url": backend_url}
        ))
        
        self._log(f"   Platform: {platform}", Colors.OKGREEN if status == "ok" else Colors.WARNING)
        self._log(f"   Frontend: {frontend_url}", Colors.OKBLUE)
        if platform == "Vercel + Railway":
            self._log(f"   Backend: {backend_url}", Colors.OKBLUE)
        self._log(f"   Status: {'✅ Detected correctly' if status == 'ok' else '⚠️  Could not detect'}", 
                  Colors.OKGREEN if status == "ok" else Colors.WARNING)
    
    def check_frontend_health(self):
        """Check frontend deployment health"""
        self._log("\n📱 FRONTEND STATUS", Colors.HEADER)
        self._log("═" * 60)
        
        if not self.url:
            self.checks.append(StatusCheck(
                "frontend", "Frontend Check", "error",
                "No deployment URL provided",
                fix_suggestion="Provide --url parameter with deployment URL"
            ))
            self._log("   ❌ No URL provided - cannot check frontend", Colors.FAIL)
            return
        
        # Test 1: Frontend accessibility
        response, error = self._make_request("/", timeout=30)
        
        if error or not response or response.status_code != 200:
            error_msg = str(error) if error else f"Status {response.status_code if response else 'N/A'}"
            self.checks.append(StatusCheck(
                "frontend", "Frontend Accessible", "critical",
                f"Frontend not accessible: {error_msg}",
                fix_suggestion="Check Vercel deployment logs and ensure build completed successfully"
            ))
            self._log(f"   • Frontend accessible: ❌ {error_msg}", Colors.FAIL)
            return
        
        self.checks.append(StatusCheck(
            "frontend", "Frontend Accessible", "ok",
            f"Accessible at: {self.url}"
        ))
        self._log("   • Frontend accessible: ✅", Colors.OKGREEN)
        
        # Test 2: React app detection
        if response and response.text:
            has_root_div = 'id="root"' in response.text or 'id="app"' in response.text
            has_react_markers = 'react' in response.text.lower()
            
            if has_root_div or has_react_markers:
                self.checks.append(StatusCheck(
                    "frontend", "React App Loading", "ok",
                    "React app markup detected"
                ))
                self._log("   • React app loading: ✅", Colors.OKGREEN)
            else:
                self.checks.append(StatusCheck(
                    "frontend", "React App Loading", "warning",
                    "React app markup not found - may be a routing issue"
                ))
                self._log("   • React app loading: ⚠️  Not detected", Colors.WARNING)
        
        # Test 3: Assets serving
        assets_response, assets_error = self._make_request("/assets/index.js", timeout=10)
        # It's OK if this 404s - just checking if server responds
        if assets_response or (assets_error and "timeout" not in str(assets_error).lower()):
            self.checks.append(StatusCheck(
                "frontend", "Assets Serving", "ok",
                "Static assets endpoint responding"
            ))
            self._log("   • Assets serving: ✅", Colors.OKGREEN)
        
        # Test 4: Build configuration
        self.checks.append(StatusCheck(
            "frontend", "Build Config", "ok",
            "Frontend responding correctly"
        ))
        self._log("   • Build config: ✅", Colors.OKGREEN)
    
    def check_backend_health(self):
        """Check backend API health"""
        self._log("\n🔧 BACKEND STATUS", Colors.HEADER)
        self._log("═" * 60)
        
        if not self.url:
            self._log("   ❌ No URL provided - cannot check backend", Colors.FAIL)
            return
        
        backend_issues = 0
        
        # Test /api/health
        response, error = self._make_request("/api/health", timeout=60)
        
        if error or not response:
            error_msg = str(error) if error else "No response"
            self.checks.append(StatusCheck(
                "backend", "/api/health", "error",
                f"Failed: {error_msg}",
                fix_suggestion="Check Vercel function logs for errors. Verify api/index.py is deployed."
            ))
            self._log(f"   • /api/health: ❌ {error_msg}", Colors.FAIL)
            backend_issues += 1
        elif response.status_code == 200:
            try:
                data = response.json()
                self.checks.append(StatusCheck(
                    "backend", "/api/health", "ok",
                    "Status 200",
                    {"response": data}
                ))
                self._log("   • /api/health: ✅", Colors.OKGREEN)
            except:
                self.checks.append(StatusCheck(
                    "backend", "/api/health", "warning",
                    "Invalid JSON response"
                ))
                self._log("   • /api/health: ⚠️  Invalid JSON", Colors.WARNING)
        else:
            self.checks.append(StatusCheck(
                "backend", "/api/health", "error",
                f"Status {response.status_code}",
                fix_suggestion="Check Vercel function logs for server errors"
            ))
            self._log(f"   • /api/health: ❌ Status {response.status_code}", Colors.FAIL)
            backend_issues += 1
        
        # Test /api/status
        response, error = self._make_request("/api/status", timeout=60)
        
        if error or not response:
            error_msg = str(error) if error else "No response"
            self.checks.append(StatusCheck(
                "backend", "/api/status", "error",
                f"Failed: {error_msg}"
            ))
            self._log(f"   • /api/status: ❌ {error_msg}", Colors.FAIL)
            backend_issues += 1
        elif response.status_code == 200:
            self.checks.append(StatusCheck(
                "backend", "/api/status", "ok",
                "Status 200"
            ))
            self._log("   • /api/status: ✅", Colors.OKGREEN)
        else:
            self.checks.append(StatusCheck(
                "backend", "/api/status", "error",
                f"Status {response.status_code}"
            ))
            self._log(f"   • /api/status: ❌ Status {response.status_code}", Colors.FAIL)
            backend_issues += 1
        
        # Test /api/ready
        response, error = self._make_request("/api/ready", timeout=60)
        
        if error or not response:
            error_msg = str(error) if error else "No response"
            self.checks.append(StatusCheck(
                "backend", "/api/ready", "error",
                f"Failed: {error_msg}",
                fix_suggestion="Database may not be accessible. Check DATABASE_URL configuration."
            ))
            self._log(f"   • /api/ready: ❌ {error_msg}", Colors.FAIL)
            backend_issues += 1
        elif response.status_code == 200:
            self.checks.append(StatusCheck(
                "backend", "/api/ready", "ok",
                "Status 200"
            ))
            self._log("   • /api/ready: ✅", Colors.OKGREEN)
        else:
            self.checks.append(StatusCheck(
                "backend", "/api/ready", "error",
                f"Status {response.status_code}",
                fix_suggestion="Database may not be accessible. Check DATABASE_URL configuration."
            ))
            self._log(f"   • /api/ready: ❌ Status {response.status_code}", Colors.FAIL)
            backend_issues += 1
    
    def check_database_connectivity(self):
        """Check database connectivity and configuration"""
        self._log("\n💾 DATABASE STATUS", Colors.HEADER)
        self._log("═" * 60)
        
        # Check DATABASE_URL format
        database_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
        
        if not database_url:
            self.checks.append(StatusCheck(
                "database", "DATABASE_URL", "critical",
                "DATABASE_URL not set",
                fix_suggestion="Set DATABASE_URL in environment variables"
            ))
            self._log("   • DATABASE_URL: ❌ Not set", Colors.FAIL)
        else:
            # Validate DATABASE_URL format
            database_url = database_url.strip()
            
            # Check for common pattern errors
            parsed = urlparse(database_url)
            missing_fields = []
            
            if not parsed.username:
                missing_fields.append("username")
            if not parsed.password:
                missing_fields.append("password")
            if not parsed.hostname:
                missing_fields.append("hostname")
            if not parsed.path or len(parsed.path) <= 1:
                missing_fields.append("database name")
            
            if missing_fields:
                fix_msg = self._generate_database_url_fix(database_url, missing_fields)
                self.checks.append(StatusCheck(
                    "database", "DATABASE_URL", "critical",
                    f"INVALID FORMAT - Missing: {', '.join(missing_fields)}",
                    {"missing_fields": missing_fields, "error": "The string did not match the expected pattern"},
                    fix_suggestion=fix_msg
                ))
                self._log(f"   • DATABASE_URL: ❌ INVALID FORMAT", Colors.FAIL)
                self._log(f"     Error: \"The string did not match the expected pattern\"", Colors.FAIL)
                self._log(f"     Reason: Missing {', '.join(missing_fields)}", Colors.FAIL)
                self._log(f"     Current format: {self._mask_url(database_url)}", Colors.WARNING)
            else:
                # Check SSL mode
                has_sslmode = "sslmode=" in database_url
                if not has_sslmode:
                    self.checks.append(StatusCheck(
                        "database", "DATABASE_URL", "warning",
                        "Valid format but missing SSL mode",
                        fix_suggestion="Add ?sslmode=require to DATABASE_URL for secure connection"
                    ))
                    self._log("   • DATABASE_URL: ⚠️  Valid but missing SSL mode", Colors.WARNING)
                else:
                    self.checks.append(StatusCheck(
                        "database", "DATABASE_URL", "ok",
                        "Valid format with SSL mode"
                    ))
                    self._log("   • DATABASE_URL: ✅ Valid format", Colors.OKGREEN)
        
        # Try to check connection via /api/ready
        if self.url:
            response, error = self._make_request("/api/ready", timeout=60)
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    db_status = data.get("database", "unknown")
                    if db_status == "connected":
                        self.checks.append(StatusCheck(
                            "database", "Connection", "ok",
                            "Database connected"
                        ))
                        self._log("   • Connection: ✅ Connected", Colors.OKGREEN)
                    else:
                        self.checks.append(StatusCheck(
                            "database", "Connection", "error",
                            f"Database status: {db_status}"
                        ))
                        self._log(f"   • Connection: ❌ {db_status}", Colors.FAIL)
                except json.JSONDecodeError:
                    # Invalid JSON response, skip connection check
                    pass
                except Exception as e:
                    # Unexpected error, log it
                    self._verbose_log(f"Error parsing /api/ready response: {str(e)}")
            else:
                self.checks.append(StatusCheck(
                    "database", "Connection", "error",
                    "Cannot verify connection - backend not responding"
                ))
                self._log("   • Connection: ❌ Cannot verify (backend offline)", Colors.FAIL)
    
    def _generate_database_url_fix(self, current_url: str, missing_fields: List[str]) -> str:
        """Generate fix suggestion for DATABASE_URL"""
        if "database name" in missing_fields:
            return (
                "DATABASE_URL is missing the database name. "
                "Format should be: postgresql://username:password@hostname:5432/DATABASE_NAME?sslmode=require\n"
                "Fix:\n"
                "1. Go to your deployment platform (Vercel/Railway)\n"
                "2. Navigate to Environment Variables\n"
                "3. Update DATABASE_URL to include /database_name after the port\n"
                "4. Redeploy the application"
            )
        else:
            return (
                f"DATABASE_URL is incomplete. Missing: {', '.join(missing_fields)}.\n"
                "Required format: postgresql://username:password@hostname:5432/database_name?sslmode=require"
            )
    
    def _mask_url(self, url: str) -> str:
        """Mask password in URL for display"""
        if "@" not in url:
            return url
        try:
            auth_part, host_part = url.rsplit("@", 1)
            user_part = auth_part.rsplit(":", 1)[0]
            return f"{user_part}:****@{host_part}"
        except:
            return url
    
    def check_environment_variables(self):
        """Check required environment variables"""
        self._log("\n🔐 ENVIRONMENT VARIABLES", Colors.HEADER)
        self._log("═" * 60)
        
        required_vars = {
            "DATABASE_URL": os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL"),
            "SECRET_KEY": os.getenv("SECRET_KEY"),
            "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY"),
            "ENVIRONMENT": os.getenv("ENVIRONMENT")
        }
        
        for var_name, var_value in required_vars.items():
            if not var_value:
                self.checks.append(StatusCheck(
                    "environment", var_name, "warning",
                    "Not set",
                    fix_suggestion=f"Set {var_name} in deployment environment variables"
                ))
                self._log(f"   • {var_name}: ⚠️  Not set", Colors.WARNING)
            elif var_name in ["SECRET_KEY", "JWT_SECRET_KEY"]:
                # Check for default/weak values
                is_weak = len(var_value) < 32 or var_value in ["dev", "test", "secret"]
                if is_weak:
                    self.checks.append(StatusCheck(
                        "environment", var_name, "warning",
                        "Set but weak or default value",
                        fix_suggestion=f"Use a strong random secret for {var_name} in production"
                    ))
                    self._log(f"   • {var_name}: ⚠️  Set (weak value)", Colors.WARNING)
                else:
                    self.checks.append(StatusCheck(
                        "environment", var_name, "ok",
                        "Set (custom)"
                    ))
                    self._log(f"   • {var_name}: ✅ Set (custom)", Colors.OKGREEN)
            else:
                self.checks.append(StatusCheck(
                    "environment", var_name, "ok",
                    var_value if var_name == "ENVIRONMENT" else "Set"
                ))
                display_value = var_value if var_name == "ENVIRONMENT" else "✅"
                self._log(f"   • {var_name}: {display_value}", Colors.OKGREEN)
    
    def check_configuration_files(self):
        """Check configuration files"""
        self._log("\n⚙️  CONFIGURATION FILES", Colors.HEADER)
        self._log("═" * 60)
        
        # Check vercel.json
        vercel_json_path = "vercel.json"
        if os.path.exists(vercel_json_path):
            try:
                with open(vercel_json_path, 'r') as f:
                    config = json.load(f)
                
                # Check for API routing
                has_rewrites = "rewrites" in config
                has_api_rewrite = False
                if has_rewrites:
                    for rewrite in config.get("rewrites", []):
                        if "/api/" in rewrite.get("source", ""):
                            has_api_rewrite = True
                            break
                
                if has_api_rewrite:
                    self.checks.append(StatusCheck(
                        "config", "vercel.json", "ok",
                        "Valid routing configuration"
                    ))
                    self._log("   • vercel.json: ✅ Valid routing", Colors.OKGREEN)
                else:
                    self.checks.append(StatusCheck(
                        "config", "vercel.json", "warning",
                        "No API routing detected",
                        fix_suggestion="Add API rewrites to vercel.json"
                    ))
                    self._log("   • vercel.json: ⚠️  No API routing", Colors.WARNING)
                
                # Check API function config
                has_functions = "functions" in config
                if has_functions:
                    self.checks.append(StatusCheck(
                        "config", "API Functions", "ok",
                        "Configured correctly"
                    ))
                    self._log("   • API functions: ✅ Configured correctly", Colors.OKGREEN)
                
            except Exception as e:
                self.checks.append(StatusCheck(
                    "config", "vercel.json", "error",
                    f"Invalid JSON: {str(e)}"
                ))
                self._log(f"   • vercel.json: ❌ Invalid JSON", Colors.FAIL)
        else:
            self.checks.append(StatusCheck(
                "config", "vercel.json", "warning",
                "Not found"
            ))
            self._log("   • vercel.json: ⚠️  Not found", Colors.WARNING)
    
    def print_summary(self):
        """Print overall summary"""
        self._log("\n" + "╔" + "═" * 58 + "╗", Colors.BOLD)
        self._log("║" + " " * 10 + "HIREMEBAHAMAS APP STATUS CHECK" + " " * 18 + "║", Colors.BOLD)
        self._log("╚" + "═" * 58 + "╝", Colors.BOLD)
        
        # Count issues
        critical_issues = [c for c in self.checks if c.status == "critical"]
        error_issues = [c for c in self.checks if c.status == "error"]
        warning_issues = [c for c in self.checks if c.status == "warning"]
        
        total_issues = len(critical_issues) + len(error_issues)
        
        # Overall status
        if total_issues == 0:
            self._log(f"\n📊 OVERALL STATUS: ✅ ONLINE", Colors.OKGREEN)
        else:
            status_msg = f"❌ OFFLINE ({total_issues} critical issue{'s' if total_issues != 1 else ''})"
            self._log(f"\n📊 OVERALL STATUS: {status_msg}", Colors.FAIL)
        
        # Print summary by category
        self._print_category_summary()
        
        # Print critical issues
        if critical_issues or error_issues:
            self._print_critical_issues(critical_issues + error_issues)
        
        # Print action items if requested
        if self.show_fix and (critical_issues or error_issues):
            self._print_action_items(critical_issues + error_issues)
    
    def _print_category_summary(self):
        """Print summary grouped by category"""
        categories = {}
        for check in self.checks:
            if check.category not in categories:
                categories[check.category] = []
            categories[check.category].append(check)
        
        category_names = {
            "deployment": "🌐 DEPLOYMENT DETECTION",
            "frontend": "📱 FRONTEND STATUS",
            "backend": "🔧 BACKEND STATUS",
            "database": "💾 DATABASE STATUS",
            "environment": "🔐 ENVIRONMENT VARIABLES",
            "config": "⚙️  CONFIGURATION FILES"
        }
        
        for cat_key in ["deployment", "frontend", "backend", "database", "environment", "config"]:
            if cat_key not in categories:
                continue
            
            checks = categories[cat_key]
            cat_name = category_names.get(cat_key, cat_key.upper())
            
            # Determine category status
            has_critical = any(c.status == "critical" for c in checks)
            has_error = any(c.status == "error" for c in checks)
            has_warning = any(c.status == "warning" for c in checks)
            
            if has_critical or has_error:
                status_icon = "❌ OFFLINE" if cat_key in ["frontend", "backend", "database"] else "❌ ISSUES"
                issue_count = len([c for c in checks if c.status in ["critical", "error"]])
                status_text = f"{status_icon} ({issue_count} issue{'s' if issue_count != 1 else ''})"
                color = Colors.FAIL
            elif has_warning:
                status_icon = "⚠️  WARNINGS"
                status_text = status_icon
                color = Colors.WARNING
            else:
                status_icon = "✅ ONLINE" if cat_key in ["frontend", "backend", "database"] else "✅ OK"
                status_text = status_icon
                color = Colors.OKGREEN
            
            self._log(f"\n{cat_name}: {status_text}", color)
            
            # Print check details
            for check in checks:
                if check.status in ["critical", "error"]:
                    self._log(f"   • {check.name}: ❌ {check.message}", Colors.FAIL)
                elif check.status == "warning":
                    self._log(f"   • {check.name}: ⚠️  {check.message}", Colors.WARNING)
                else:
                    self._log(f"   • {check.name}: ✅", Colors.OKGREEN)
    
    def _print_critical_issues(self, issues: List[StatusCheck]):
        """Print critical issues section"""
        self._log("\n" + "🚨 CRITICAL ISSUES TO FIX:", Colors.FAIL)
        self._log("═" * 60, Colors.FAIL)
        
        for i, issue in enumerate(issues, 1):
            self._log(f"\n{i}. {issue.name}", Colors.BOLD)
            self._log(f"   ❌ Issue: {issue.message}", Colors.FAIL)
            
            if issue.details:
                if "error" in issue.details:
                    self._log(f"   Error: \"{issue.details['error']}\"", Colors.WARNING)
                if "missing_fields" in issue.details:
                    self._log(f"   Missing: {', '.join(issue.details['missing_fields'])}", Colors.WARNING)
            
            if issue.fix_suggestion:
                self._log(f"   \n   How to fix:", Colors.OKCYAN)
                for line in issue.fix_suggestion.split('\n'):
                    if line.strip():
                        self._log(f"   {line}", Colors.OKCYAN)
        
        # Add user impact section
        next_num = len(issues) + 1
        self._log(f"\n{next_num}. User Impact", Colors.BOLD)
        self._log(f"   Users see: \"Backend connection: The string did not match the expected pattern\"", Colors.WARNING)
        self._log(f"   This is displayed by frontend connection test on app load.", Colors.WARNING)
    
    def _print_action_items(self, issues: List[StatusCheck]):
        """Print action items section"""
        self._log("\n" + "📝 REQUIRED ACTIONS (Priority Order):", Colors.OKBLUE)
        self._log("═" * 60, Colors.OKBLUE)
        
        # Prioritize DATABASE_URL issues
        db_issues = [i for i in issues if "DATABASE_URL" in i.name or i.category == "database"]
        backend_issues = [i for i in issues if i.category == "backend"]
        other_issues = [i for i in issues if i not in db_issues and i not in backend_issues]
        
        priority_issues = db_issues + backend_issues + other_issues
        
        for i, issue in enumerate(priority_issues[:5], 1):  # Top 5 actions
            priority_label = ["[CRITICAL]", "[HIGH]", "[MEDIUM]", "[MEDIUM]", "[LOW]"][min(i-1, 4)]
            self._log(f"\n{i}. Fix {issue.name} {priority_label}", Colors.BOLD)
            
            if "DATABASE_URL" in issue.name:
                self._log("   - Platform: Vercel Dashboard → Settings → Environment Variables", Colors.OKBLUE)
                self._log("   - Variable: DATABASE_URL", Colors.OKBLUE)
                self._log("   - Update to: postgresql://username:password@hostname:5432/database_name?sslmode=require", Colors.OKBLUE)
                self._log("   - Redeploy after changing", Colors.OKBLUE)
            elif issue.category == "backend":
                self._log("   - Check backend logs for startup errors", Colors.OKBLUE)
                if self.url:
                    self._log(f"   - Test: curl {self.url}/api/health", Colors.OKBLUE)
                self._log("   - Expected: {\"status\": \"healthy\"}", Colors.OKBLUE)
            elif issue.fix_suggestion:
                for line in issue.fix_suggestion.split('\n')[:3]:
                    if line.strip():
                        self._log(f"   - {line.strip()}", Colors.OKBLUE)
    
    def output_json_result(self):
        """Output results as JSON"""
        result = {
            "status": "offline" if any(c.status in ["critical", "error"] for c in self.checks) else "online",
            "deployment_info": self.deployment_info,
            "checks": [c.to_dict() for c in self.checks],
            "summary": {
                "total_checks": len(self.checks),
                "critical": len([c for c in self.checks if c.status == "critical"]),
                "errors": len([c for c in self.checks if c.status == "error"]),
                "warnings": len([c for c in self.checks if c.status == "warning"]),
                "ok": len([c for c in self.checks if c.status == "ok"])
            }
        }
        print(json.dumps(result, indent=2))
    
    def run(self) -> int:
        """Run all checks and return exit code"""
        if not self.output_json:
            self._log("🔍 HireMeBahamas Comprehensive Deployment Status Check", Colors.BOLD + Colors.HEADER)
            self._log("═" * 60)
            if self.url:
                self._log(f"Testing deployment: {self.url}\n")
            else:
                self._log("Running local environment checks\n")
        
        try:
            # Run all checks
            self.detect_deployment_platform()
            self.check_frontend_health()
            self.check_backend_health()
            self.check_database_connectivity()
            self.check_environment_variables()
            self.check_configuration_files()
            
            # Output results
            if self.output_json:
                self.output_json_result()
            else:
                self.print_summary()
            
            # Determine exit code
            has_critical_or_error = any(c.status in ["critical", "error"] for c in self.checks)
            return 1 if has_critical_or_error else 0
            
        except KeyboardInterrupt:
            if not self.output_json:
                self._log("\n\n⚠️  Check interrupted by user", Colors.WARNING)
            return 130
        except Exception as e:
            if not self.output_json:
                self._log(f"\n\n❌ Check failed with error: {str(e)}", Colors.FAIL)
                if self.verbose:
                    import traceback
                    self._log(traceback.format_exc(), Colors.FAIL)
            return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="HireMeBahamas Comprehensive Deployment Status Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check local environment
  python scripts/check_deployment_status.py

  # Check deployed application
  python scripts/check_deployment_status.py --url https://your-app.vercel.app

  # Get JSON output for CI/CD
  python scripts/check_deployment_status.py --url https://your-app.vercel.app --json

  # Show detailed fix instructions
  python scripts/check_deployment_status.py --url https://your-app.vercel.app --fix

Exit Codes:
  0 - All systems operational
  1 - Issues detected
        """
    )
    
    parser.add_argument(
        '--url',
        help='Deployment URL to check (e.g., https://your-app.vercel.app)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging for detailed diagnostics'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON (for machine processing)'
    )
    
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Show detailed fix instructions for issues'
    )
    
    args = parser.parse_args()
    
    # Validate URL if provided
    if args.url:
        parsed = urlparse(args.url)
        if not parsed.scheme or not parsed.netloc:
            print(f"{Colors.FAIL}❌ Invalid URL: {args.url}{Colors.ENDC}")
            print(f"{Colors.WARNING}URL must include protocol (https://){Colors.ENDC}")
            return 1
    
    # Check for requests library
    if args.url and not HAS_REQUESTS:
        print(f"{Colors.FAIL}❌ requests library not installed{Colors.ENDC}")
        print(f"{Colors.WARNING}Install with: pip install requests{Colors.ENDC}")
        return 1
    
    # Run status check
    checker = DeploymentStatusChecker(
        url=args.url,
        verbose=args.verbose,
        output_json=args.json,
        show_fix=args.fix
    )
    return checker.run()


if __name__ == "__main__":
    sys.exit(main())

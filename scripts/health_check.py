#!/usr/bin/env python3
"""
Comprehensive Health Check Script for HireMeBahamas
====================================================

This script performs automated health checks across all critical systems:
- Database connectivity
- Environment configuration
- API endpoints
- Deployment status
- Security settings

Can be run manually, in CI/CD, or scheduled via GitHub Actions.

Usage:
    python scripts/health_check.py
    python scripts/health_check.py --format json
    python scripts/health_check.py --verbose
    python scripts/health_check.py --check database
    python scripts/health_check.py --url https://your-deployment.vercel.app
"""

import argparse
import json
import os
import sys
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse


# Check for optional dependencies
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Warning: 'requests' not installed. Remote health checks will be skipped.")

try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class HealthCheckResult:
    """Stores the result of a health check"""
    def __init__(self, name: str, status: str, message: str, 
                 details: Optional[Dict] = None, duration_ms: Optional[int] = None):
        self.name = name
        self.status = status  # "pass", "warn", "fail"
        self.message = message
        self.details = details or {}
        self.duration_ms = duration_ms
        self.timestamp = int(time.time())


class HealthChecker:
    """Main health checker class"""
    
    def __init__(self, verbose: bool = False, format: str = "text", url: Optional[str] = None):
        self.verbose = verbose
        self.format = format
        self.url = url
        self.results: List[HealthCheckResult] = []
        
    def log(self, message: str, color: str = Colors.ENDC):
        """Print message with color (text format only)"""
        if self.format == "text":
            print(f"{color}{message}{Colors.ENDC}")
    
    def verbose_log(self, message: str):
        """Print verbose message"""
        if self.verbose and self.format == "text":
            print(f"{Colors.OKCYAN}  [DEBUG] {message}{Colors.ENDC}")
    
    def add_result(self, result: HealthCheckResult):
        """Add a check result"""
        self.results.append(result)
        
        if self.format == "text":
            if result.status == "pass":
                self.log(f"✅ {result.name}: {result.message}", Colors.OKGREEN)
            elif result.status == "warn":
                self.log(f"⚠️  {result.name}: {result.message}", Colors.WARNING)
            else:
                self.log(f"❌ {result.name}: {result.message}", Colors.FAIL)
            
            if self.verbose and result.details:
                for key, value in result.details.items():
                    self.verbose_log(f"{key}: {value}")
    
    def check_environment_variables(self) -> List[HealthCheckResult]:
        """Check required environment variables"""
        self.log("\n🔐 ENVIRONMENT VARIABLES", Colors.HEADER)
        self.log("-" * 60)
        
        results = []
        
        # Critical variables
        critical_vars = {
            "DATABASE_URL": "Database connection string",
            "SECRET_KEY": "Flask secret key",
        }
        
        # Optional but recommended variables
        optional_vars = {
            "JWT_SECRET_KEY": "JWT authentication secret",
            "PORT": "Server port",
            "ENVIRONMENT": "Environment name (production/development)",
        }
        
        # Check critical variables
        for var, description in critical_vars.items():
            value = os.getenv(var)
            if value:
                # Don't expose actual values
                if "secret" in var.lower() or "key" in var.lower():
                    display = "***SET***"
                    # Check if using default/weak values
                    if value in ["your-secret-key-here", "changeme", "secret"]:
                        results.append(HealthCheckResult(
                            var,
                            "warn",
                            f"Set but using default/weak value - {description}",
                            {"secure": False}
                        ))
                    else:
                        results.append(HealthCheckResult(
                            var,
                            "pass",
                            f"Configured - {description}",
                            {"secure": True}
                        ))
                else:
                    # For DATABASE_URL, show host only
                    if "DATABASE_URL" in var:
                        try:
                            parsed = urlparse(value)
                            display = f"{parsed.hostname}"
                        except:
                            display = "***SET***"
                    else:
                        display = value[:20] + "..." if len(value) > 20 else value
                    
                    results.append(HealthCheckResult(
                        var,
                        "pass",
                        f"Configured: {display}",
                        {"value": display}
                    ))
            else:
                results.append(HealthCheckResult(
                    var,
                    "fail",
                    f"Not set - {description}",
                    {"required": True}
                ))
        
        # Check optional variables
        for var, description in optional_vars.items():
            value = os.getenv(var)
            if value:
                results.append(HealthCheckResult(
                    var,
                    "pass",
                    f"Configured - {description}",
                    {"optional": True}
                ))
            else:
                results.append(HealthCheckResult(
                    var,
                    "warn",
                    f"Not set (optional) - {description}",
                    {"optional": True, "recommended": True}
                ))
        
        return results
    
    def check_database_url_format(self) -> HealthCheckResult:
        """Validate DATABASE_URL format"""
        db_url = os.getenv("DATABASE_URL", "")
        
        if not db_url:
            return HealthCheckResult(
                "Database URL Format",
                "fail",
                "DATABASE_URL not set",
                {"required": True}
            )
        
        try:
            parsed = urlparse(db_url)
            
            # Check scheme
            valid_schemes = ["postgresql", "postgres", "postgresql+asyncpg"]
            if parsed.scheme not in valid_schemes:
                return HealthCheckResult(
                    "Database URL Format",
                    "warn",
                    f"Unexpected scheme: {parsed.scheme}",
                    {"scheme": parsed.scheme, "expected": valid_schemes}
                )
            
            # Check components
            if not parsed.hostname:
                return HealthCheckResult(
                    "Database URL Format",
                    "fail",
                    "No hostname in DATABASE_URL",
                    {"url_format": "invalid"}
                )
            
            details = {
                "scheme": parsed.scheme,
                "host": parsed.hostname,
                "port": parsed.port or "default",
                "database": parsed.path.lstrip("/") if parsed.path else "unknown"
            }
            
            return HealthCheckResult(
                "Database URL Format",
                "pass",
                f"Valid format: {parsed.scheme}://{parsed.hostname}",
                details
            )
            
        except Exception as e:
            return HealthCheckResult(
                "Database URL Format",
                "fail",
                f"Invalid URL format: {str(e)}",
                {"error": str(e)}
            )
    
    async def check_database_connectivity(self) -> HealthCheckResult:
        """Test database connection"""
        if not HAS_ASYNCPG:
            return HealthCheckResult(
                "Database Connectivity",
                "warn",
                "asyncpg not installed - skipping connectivity test",
                {"skipped": True, "reason": "missing dependency"}
            )
        
        db_url = os.getenv("DATABASE_URL", "")
        if not db_url:
            return HealthCheckResult(
                "Database Connectivity",
                "fail",
                "DATABASE_URL not set",
                {"required": True}
            )
        
        # Convert to asyncpg format
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        elif db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://')
        
        start_time = time.time()
        try:
            conn = await asyncpg.connect(db_url, timeout=10)
            
            # Test query
            result = await conn.fetchval('SELECT 1')
            await conn.close()
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            if result == 1:
                return HealthCheckResult(
                    "Database Connectivity",
                    "pass",
                    f"Connection successful ({duration_ms}ms)",
                    {"response_time_ms": duration_ms, "connected": True},
                    duration_ms
                )
            else:
                return HealthCheckResult(
                    "Database Connectivity",
                    "fail",
                    "Query returned unexpected result",
                    {"expected": 1, "got": result}
                )
                
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return HealthCheckResult(
                "Database Connectivity",
                "fail",
                f"Connection failed: {str(e)[:100]}",
                {"error": str(e), "duration_ms": duration_ms},
                duration_ms
            )
    
    def check_deployment_platform(self) -> HealthCheckResult:
        """Detect deployment platform"""
        platforms = []
        details = {}
        
        # Check Railway
        if os.getenv("RAILWAY_PROJECT_ID"):
            platforms.append("Railway")
            details["railway_project"] = os.getenv("RAILWAY_PROJECT_NAME", "unknown")
            details["railway_environment"] = os.getenv("RAILWAY_ENVIRONMENT", "unknown")
        
        # Check Vercel
        if os.getenv("VERCEL"):
            platforms.append("Vercel")
            details["vercel_env"] = os.getenv("VERCEL_ENV", "unknown")
            details["vercel_region"] = os.getenv("VERCEL_REGION", "unknown")
        
        # Check Render
        if os.getenv("RENDER"):
            platforms.append("Render")
            details["render_service"] = os.getenv("RENDER_SERVICE_NAME", "unknown")
        
        # Local/development
        if not platforms:
            platforms.append("Local/Development")
            details["environment"] = os.getenv("ENVIRONMENT", "development")
        
        return HealthCheckResult(
            "Deployment Platform",
            "pass",
            f"Running on: {', '.join(platforms)}",
            details
        )
    
    def check_remote_api(self) -> List[HealthCheckResult]:
        """Check remote API endpoints"""
        if not self.url:
            return [HealthCheckResult(
                "Remote API Check",
                "warn",
                "No URL provided - skipping remote checks",
                {"skipped": True, "reason": "no url provided"}
            )]
        
        if not HAS_REQUESTS:
            return [HealthCheckResult(
                "Remote API Check",
                "warn",
                "requests library not available - skipping remote checks",
                {"skipped": True, "reason": "missing dependency"}
            )]
        
        self.log("\n🌐 REMOTE API CHECKS", Colors.HEADER)
        self.log("-" * 60)
        
        results = []
        endpoints = [
            ("/api/health", "Health endpoint"),
            ("/api/status", "Status endpoint"),
            ("/api/ready", "Readiness endpoint"),
        ]
        
        for endpoint, description in endpoints:
            url = f"{self.url.rstrip('/')}{endpoint}"
            start_time = time.time()
            
            try:
                response = requests.get(url, timeout=30)
                duration_ms = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        results.append(HealthCheckResult(
                            f"{endpoint}",
                            "pass",
                            f"{description} responding ({duration_ms}ms)",
                            {"status_code": 200, "response_time_ms": duration_ms, "data": data},
                            duration_ms
                        ))
                    except:
                        results.append(HealthCheckResult(
                            f"{endpoint}",
                            "warn",
                            f"Responded but invalid JSON ({duration_ms}ms)",
                            {"status_code": 200, "response_time_ms": duration_ms},
                            duration_ms
                        ))
                else:
                    results.append(HealthCheckResult(
                        f"{endpoint}",
                        "fail",
                        f"HTTP {response.status_code}",
                        {"status_code": response.status_code, "response_time_ms": duration_ms},
                        duration_ms
                    ))
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                results.append(HealthCheckResult(
                    f"{endpoint}",
                    "fail",
                    f"Request failed: {str(e)[:50]}",
                    {"error": str(e), "duration_ms": duration_ms},
                    duration_ms
                ))
        
        return results
    
    def check_file_structure(self) -> List[HealthCheckResult]:
        """Check required files and directories exist"""
        self.log("\n📁 FILE STRUCTURE", Colors.HEADER)
        self.log("-" * 60)
        
        results = []
        
        required_files = [
            ("api/index.py", "Main API entry point"),
            ("api/requirements.txt", "API dependencies"),
            ("frontend/package.json", "Frontend dependencies"),
            ("vercel.json", "Vercel configuration"),
        ]
        
        for file_path, description in required_files:
            if os.path.exists(file_path):
                results.append(HealthCheckResult(
                    f"File: {file_path}",
                    "pass",
                    f"Found - {description}",
                    {"path": file_path, "exists": True}
                ))
            else:
                results.append(HealthCheckResult(
                    f"File: {file_path}",
                    "fail",
                    f"Missing - {description}",
                    {"path": file_path, "exists": False, "required": True}
                ))
        
        return results
    
    def print_summary(self):
        """Print summary of all checks"""
        self.log("\n" + "=" * 60, Colors.HEADER)
        self.log("📊 HEALTH CHECK SUMMARY", Colors.BOLD + Colors.HEADER)
        self.log("=" * 60, Colors.HEADER)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "pass")
        warned = sum(1 for r in self.results if r.status == "warn")
        failed = sum(1 for r in self.results if r.status == "fail")
        
        self.log(f"\nTotal Checks: {total}")
        self.log(f"✅ Passed: {passed}", Colors.OKGREEN)
        if warned > 0:
            self.log(f"⚠️  Warnings: {warned}", Colors.WARNING)
        if failed > 0:
            self.log(f"❌ Failed: {failed}", Colors.FAIL)
        
        # Show failed checks
        failed_checks = [r for r in self.results if r.status == "fail"]
        if failed_checks:
            self.log("\n❌ FAILED CHECKS:", Colors.FAIL)
            for check in failed_checks:
                self.log(f"  • {check.name}: {check.message}", Colors.FAIL)
        
        # Show warnings
        warned_checks = [r for r in self.results if r.status == "warn"]
        if warned_checks:
            self.log("\n⚠️  WARNINGS:", Colors.WARNING)
            for check in warned_checks:
                self.log(f"  • {check.name}: {check.message}", Colors.WARNING)
        
        # Overall status
        self.log("\n" + "=" * 60)
        if failed == 0 and warned == 0:
            self.log("✅ ALL SYSTEMS OPERATIONAL", Colors.OKGREEN)
            return 0
        elif failed == 0:
            self.log("⚠️  SYSTEM OPERATIONAL WITH WARNINGS", Colors.WARNING)
            return 0
        else:
            self.log("❌ CRITICAL ISSUES DETECTED", Colors.FAIL)
            return 1
    
    def output_json(self):
        """Output results as JSON"""
        output = {
            "timestamp": int(time.time()),
            "summary": {
                "total": len(self.results),
                "passed": sum(1 for r in self.results if r.status == "pass"),
                "warned": sum(1 for r in self.results if r.status == "warn"),
                "failed": sum(1 for r in self.results if r.status == "fail"),
            },
            "checks": [
                {
                    "name": r.name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                    "duration_ms": r.duration_ms,
                    "timestamp": r.timestamp,
                }
                for r in self.results
            ]
        }
        
        print(json.dumps(output, indent=2))
        
        # Return exit code based on failures
        return 0 if output["summary"]["failed"] == 0 else 1
    
    async def run_all_checks(self, check_filter: Optional[str] = None):
        """Run all health checks"""
        if self.format == "text":
            self.log("🏥 HireMeBahamas Health Check", Colors.BOLD + Colors.HEADER)
            self.log("=" * 60)
            self.log(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # File structure checks
        if not check_filter or check_filter == "files":
            for result in self.check_file_structure():
                self.add_result(result)
        
        # Environment checks
        if not check_filter or check_filter == "environment":
            self.log("\n🔐 ENVIRONMENT CONFIGURATION", Colors.HEADER)
            self.log("-" * 60)
            
            for result in self.check_environment_variables():
                self.add_result(result)
            
            result = self.check_database_url_format()
            self.add_result(result)
            
            result = self.check_deployment_platform()
            self.add_result(result)
        
        # Database checks
        if not check_filter or check_filter == "database":
            self.log("\n💾 DATABASE", Colors.HEADER)
            self.log("-" * 60)
            
            result = await self.check_database_connectivity()
            self.add_result(result)
        
        # Remote API checks
        if self.url and (not check_filter or check_filter == "api"):
            for result in self.check_remote_api():
                self.add_result(result)
        
        # Print summary and return exit code
        if self.format == "text":
            return self.print_summary()
        else:
            return self.output_json()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Comprehensive health check for HireMeBahamas deployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all checks
  python scripts/health_check.py
  
  # Run specific check category
  python scripts/health_check.py --check database
  python scripts/health_check.py --check environment
  
  # Check remote deployment
  python scripts/health_check.py --url https://your-app.vercel.app
  
  # Output as JSON (for CI/CD)
  python scripts/health_check.py --format json
  
  # Verbose output
  python scripts/health_check.py --verbose
        """
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--url',
        help='URL of deployed application to check'
    )
    
    parser.add_argument(
        '--check',
        choices=['files', 'environment', 'database', 'api'],
        help='Run only specific check category'
    )
    
    args = parser.parse_args()
    
    # Create health checker
    checker = HealthChecker(
        verbose=args.verbose,
        format=args.format,
        url=args.url
    )
    
    # Run checks
    try:
        exit_code = await checker.run_all_checks(args.check)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        if args.format == "text":
            print(f"\n{Colors.WARNING}Health check interrupted by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        if args.format == "text":
            print(f"{Colors.FAIL}Health check failed: {e}{Colors.ENDC}")
            if args.verbose:
                import traceback
                traceback.print_exc()
        else:
            print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

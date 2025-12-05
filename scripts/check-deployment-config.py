#!/usr/bin/env python3
"""
Check Deployment Configuration for HireMeBahamas

This script helps verify that all required secrets and environment variables
are properly configured for deploying to Vercel.

Usage:
    python3 scripts/check-deployment-config.py

Requirements:
    - Python 3.7+
    - No external dependencies (uses only standard library)
"""

import os
import sys
import urllib.request
import urllib.error
import json
from typing import Dict, List, Tuple, Optional

# Repository configuration
GITHUB_OWNER = os.getenv("GITHUB_REPOSITORY_OWNER", "cliffcho242")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY", "HireMeBahamas").split("/")[-1]
GITHUB_REPO_URL = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'


class ConfigChecker:
    """Check deployment configuration for HireMeBahamas"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []
    
    def check_env_var(self, var_name: str, required: bool = True, min_length: int = 0) -> bool:
        """Check if an environment variable is set"""
        value = os.getenv(var_name)
        
        if not value:
            if required:
                self.errors.append(f"{var_name} is not set")
                return False
            else:
                self.warnings.append(f"{var_name} is not set (optional)")
                return False
        
        if min_length > 0 and len(value) < min_length:
            self.errors.append(f"{var_name} is too short (minimum {min_length} characters)")
            return False
        
        self.passed.append(f"{var_name} is set ({len(value)} characters)")
        return True
    
    def check_database_url(self) -> bool:
        """Check if DATABASE_URL is properly formatted"""
        db_url = os.getenv("DATABASE_URL")
        
        if not db_url:
            self.errors.append("DATABASE_URL is not set")
            return False
        
        # Check if it's a PostgreSQL URL
        if not (db_url.startswith("postgresql://") or db_url.startswith("postgres://")):
            self.errors.append("DATABASE_URL must be a PostgreSQL connection string")
            return False
        
        # Check if SSL mode is specified (recommended for production)
        if "sslmode=" not in db_url:
            self.warnings.append("DATABASE_URL doesn't specify sslmode (recommended: ?sslmode=require)")
        
        # Mask sensitive parts for display
        try:
            # Extract just the host part for display
            if "@" in db_url:
                parts = db_url.split("@")
                if len(parts) >= 2:
                    host_part = parts[1].split("/")[0] if "/" in parts[1] else parts[1]
                    self.passed.append(f"DATABASE_URL is properly formatted (host: {host_part})")
                    return True
        except Exception:
            pass
        
        self.passed.append("DATABASE_URL is set")
        return True
    
    def check_secret_key(self, key_name: str) -> bool:
        """Check if a secret key is properly configured"""
        key = os.getenv(key_name)
        
        if not key:
            self.errors.append(f"{key_name} is not set")
            return False
        
        # Check if it's not the default/weak value
        weak_keys = [
            "dev-secret-key-change-in-production",
            "change-me",
            "secret",
            "password",
            "12345",
        ]
        
        if key.lower() in weak_keys:
            self.errors.append(f"{key_name} is set to a weak/default value")
            return False
        
        # Check minimum length (should be at least 32 characters)
        if len(key) < 32:
            self.warnings.append(f"{key_name} is shorter than recommended (32+ characters)")
        
        self.passed.append(f"{key_name} is properly configured")
        return True
    
    def test_backend_connection(self, url: str) -> Tuple[bool, Optional[str]]:
        """Test if backend API is accessible
        
        Args:
            url: Base URL of the backend to test (e.g., "http://localhost:8000")
        
        Returns:
            Tuple of (success: bool, message: Optional[str]):
                - success: True if backend is accessible and healthy
                - message: Status message from backend or error description
        
        Raises:
            No exceptions raised - errors are caught and returned in the tuple
        """
        try:
            req = urllib.request.Request(
                f"{url}/api/health",
                headers={'User-Agent': 'HireMeBahamas-Config-Checker/1.0'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    return True, data.get("status", "unknown")
                else:
                    return False, f"HTTP {response.status}"
        except urllib.error.URLError as e:
            return False, str(e.reason)
        except Exception as e:
            return False, str(e)
    
    def print_section(self, title: str):
        """Print a section header"""
        print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
        print(f"{BOLD}{BLUE}{title}{RESET}")
        print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")
    
    def print_results(self):
        """Print check results"""
        print(f"\n{BOLD}{'=' * 60}{RESET}")
        print(f"{BOLD}CONFIGURATION CHECK RESULTS{RESET}")
        print(f"{BOLD}{'=' * 60}{RESET}\n")
        
        # Passed checks
        if self.passed:
            print(f"{BOLD}{GREEN}✅ Passed ({len(self.passed)}):{RESET}")
            for item in self.passed:
                print(f"   {GREEN}✓{RESET} {item}")
            print()
        
        # Warnings
        if self.warnings:
            print(f"{BOLD}{YELLOW}⚠️  Warnings ({len(self.warnings)}):{RESET}")
            for item in self.warnings:
                print(f"   {YELLOW}!{RESET} {item}")
            print()
        
        # Errors
        if self.errors:
            print(f"{BOLD}{RED}❌ Errors ({len(self.errors)}):{RESET}")
            for item in self.errors:
                print(f"   {RED}✗{RESET} {item}")
            print()
        
        # Summary
        print(f"{BOLD}{'=' * 60}{RESET}")
        if not self.errors:
            print(f"{BOLD}{GREEN}🎉 Configuration looks good!{RESET}")
            if self.warnings:
                print(f"{YELLOW}Consider addressing the warnings above.{RESET}")
        else:
            print(f"{BOLD}{RED}❌ Configuration has {len(self.errors)} error(s).{RESET}")
            print(f"\n{BOLD}Next steps:{RESET}")
            print(f"1. Read: {BLUE}FIX_SIGN_IN_DEPLOYMENT_GUIDE.md{RESET}")
            print(f"2. Configure missing secrets in:")
            print(f"   - GitHub: {GITHUB_REPO_URL}/settings/secrets/actions")
            print(f"   - Vercel: https://vercel.com/dashboard (Settings → Environment Variables)")
        print(f"{BOLD}{'=' * 60}{RESET}\n")
    
    def run(self):
        """Run all configuration checks"""
        self.print_section("Checking Environment Variables")
        
        # Check database configuration
        print(f"{BOLD}Database Configuration:{RESET}")
        self.check_database_url()
        
        # Check secret keys
        print(f"\n{BOLD}Secret Keys:{RESET}")
        self.check_secret_key("SECRET_KEY")
        self.check_secret_key("JWT_SECRET_KEY")
        
        # Check optional variables
        print(f"\n{BOLD}Optional Configuration:{RESET}")
        self.check_env_var("ENVIRONMENT", required=False)
        self.check_env_var("VERCEL_ENV", required=False)
        
        # Test backend connectivity
        self.print_section("Testing Backend Connectivity")
        
        # Try local backend first
        print(f"{BOLD}Testing local backend...{RESET}")
        success, message = self.test_backend_connection("http://127.0.0.1:8000")
        if success:
            self.passed.append(f"Local backend is accessible (status: {message})")
            print(f"{GREEN}✓{RESET} Local backend is running")
        else:
            print(f"{YELLOW}!{RESET} Local backend is not accessible: {message}")
            print(f"  (This is normal if you're checking deployment configuration)")
        
        # Try Vercel deployment if URL is available
        vercel_url = os.getenv("VERCEL_URL")
        if vercel_url:
            print(f"\n{BOLD}Testing Vercel deployment...{RESET}")
            success, message = self.test_backend_connection(f"https://{vercel_url}")
            if success:
                self.passed.append(f"Vercel deployment is accessible (status: {message})")
                print(f"{GREEN}✓{RESET} Vercel deployment is running")
            else:
                self.warnings.append(f"Vercel deployment is not accessible: {message}")
                print(f"{RED}✗{RESET} Vercel deployment: {message}")
        
        # Print results
        self.print_results()
        
        # Exit with appropriate code
        return 0 if not self.errors else 1


def main():
    """Main entry point"""
    print(f"\n{BOLD}{BLUE}HireMeBahamas Deployment Configuration Checker{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")
    
    print(f"{BOLD}Purpose:{RESET}")
    print("  Verify that all required environment variables and secrets")
    print("  are properly configured for deploying to Vercel.")
    print()
    print(f"{BOLD}What this checks:{RESET}")
    print("  • DATABASE_URL configuration")
    print("  • SECRET_KEY and JWT_SECRET_KEY")
    print("  • Backend API connectivity")
    print()
    print(f"{BOLD}Note:{RESET}")
    print("  This script only checks local environment variables.")
    print("  You also need to configure the same variables in:")
    print("  • GitHub repository secrets")
    print("  • Vercel project environment variables")
    print()
    
    checker = ConfigChecker()
    exit_code = checker.run()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

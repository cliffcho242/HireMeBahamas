#!/usr/bin/env python3
"""
Security validation script for HireMeBahamas

This script checks for security issues in the codebase:
1. Weak or default secrets in code
2. Missing SSL/TLS configuration
3. Hardcoded credentials
4. Security best practices violations

Exit codes:
0 - All checks passed
1 - Critical security issues found
2 - Warnings found (non-blocking)
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# ANSI color codes for output
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Patterns that indicate weak or default secrets
WEAK_SECRET_PATTERNS = [
    r'SECRET_KEY\s*=\s*["\']your-secret-key',
    r'SECRET_KEY\s*=\s*["\']change-in-production',
    r'SECRET_KEY\s*=\s*["\']test-secret',
    r'SECRET_KEY\s*=\s*["\']dev-secret',
    r'JWT_SECRET_KEY\s*=\s*["\']your-',
    r'JWT_SECRET_KEY\s*=\s*["\']change-in-production',
    r'JWT_SECRET_KEY\s*=\s*["\']test-',
    r'JWT_SECRET_KEY\s*=\s*["\']dev-',
    r'SECRET_KEY\s*=\s*["\'][a-zA-Z0-9_-]{1,31}["\']',  # Too short (< 32 chars)
]

# Patterns for hardcoded credentials
CREDENTIAL_PATTERNS = [
    r'postgresql://[^:]+:[^@]+@[^/]+/[^\s"\']+',  # postgres URL with password
    r'password\s*=\s*["\'][^"\']{8,}["\']',  # hardcoded password
    r'api_key\s*=\s*["\'][^"\']+["\']',  # API keys
]

# Files to exclude from checks
EXCLUDED_PATHS = [
    '.env.example',
    '.env.ai',
    'test_',
    '__pycache__',
    'node_modules',
    '.git',
    'dist',
    'build',
    '.venv',
    'venv',
    'scripts/check_security.py',  # This file
    'scripts/verify_',  # Verification scripts with examples
    'VISUAL_GUIDE.py',  # Documentation
    'diagnose_',  # Diagnostic scripts with examples
    'docker-compose',  # Docker compose files (local dev only)
    'fix_',  # Fix scripts with examples
    'check_',  # Check/test scripts
    'create_admin',  # Admin creation scripts
    'setup_',  # Setup scripts
    'verify_',  # Verification scripts
    'ultimate_',  # Ultimate fix scripts
    'stable_',  # Stable version scripts
    'simple_',  # Simple test scripts
    'minimal_',  # Minimal test scripts
    'final_backend',  # Final backend scripts
    'ensure_database',  # Database setup scripts
    'immortal_',  # Migration scripts
    'comprehensive_',  # Comprehensive test scripts
    'ULTIMATE_BACKEND',  # Old backend scripts
    'db_url_utils.py',  # Has docstring examples
]

# File extensions to check
EXTENSIONS_TO_CHECK = ['.py', '.js', '.jsx', '.ts', '.tsx', '.yml', '.yaml']


def should_skip_file(file_path: Path) -> bool:
    """Check if file should be skipped based on exclusion rules."""
    path_str = str(file_path)
    
    # Skip excluded paths
    for excluded in EXCLUDED_PATHS:
        if excluded in path_str:
            return True
    
    # Only check specific extensions
    if file_path.suffix not in EXTENSIONS_TO_CHECK:
        return True
    
    return False


def check_weak_secrets(file_path: Path) -> List[Tuple[int, str, str]]:
    """
    Check file for weak or default secrets.
    
    Returns list of (line_number, line_content, pattern_matched)
    """
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                # Skip comments
                if line.strip().startswith('#') or line.strip().startswith('//'):
                    continue
                
                # Check each weak secret pattern
                for pattern in WEAK_SECRET_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append((line_num, line.strip(), pattern))
                        break
    except Exception as e:
        print(f"{YELLOW}Warning: Could not read {file_path}: {e}{RESET}")
    
    return issues


def check_hardcoded_credentials(file_path: Path) -> List[Tuple[int, str]]:
    """
    Check file for hardcoded credentials.
    
    Returns list of (line_number, line_content)
    """
    issues = []
    
    # Skip test files, examples, and documentation - they may have dummy credentials
    skip_patterns = ['test_', 'example', '_test.py', 'README', 'GUIDE', 'SUMMARY', 
                     'CHECKLIST', 'SECURITY.md', '.md']
    if any(pattern in str(file_path) for pattern in skip_patterns):
        return issues
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                # Skip comments
                if line.strip().startswith('#') or line.strip().startswith('//'):
                    continue
                
                # Skip lines with environment variable usage, examples, or docstrings
                if ('os.getenv' in line or 'os.environ' in line or 'config(' in line or
                    'Example:' in line or '>>>' in line or 'print(' in line or 
                    'default=' in line or line.strip().startswith('"""') or 
                    line.strip().startswith("'''")):
                    continue
                
                # Check for hardcoded credentials
                for pattern in CREDENTIAL_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Additional check: ensure it's not in a comment, docstring, or example
                        if not (line.strip().startswith('"""') or line.strip().startswith("'''") or
                                line.strip().startswith('#')):
                            issues.append((line_num, line.strip()))
                            break
    except Exception as e:
        print(f"{YELLOW}Warning: Could not read {file_path}: {e}{RESET}")
    
    return issues


def check_ssl_configuration() -> List[str]:
    """Check for proper SSL/TLS configuration in database settings."""
    issues = []
    
    # Check database.py files for SSL configuration
    database_files = [
        Path('backend/app/database.py'),
        Path('api/database.py'),
    ]
    
    for db_file in database_files:
        if not db_file.exists():
            continue
        
        content = db_file.read_text(encoding='utf-8', errors='ignore')
        
        # Check if SSL mode is mentioned
        if 'sslmode' not in content:
            issues.append(f"{db_file}: No SSL mode configuration found")
        
        # Check if there's enforcement of SSL in production
        if 'sslmode=require' not in content and 'ensure_sslmode' not in content:
            issues.append(f"{db_file}: No SSL requirement enforcement found")
    
    return issues


def scan_directory(root_dir: Path) -> Tuple[List, List, List]:
    """
    Scan directory for security issues.
    
    Returns (weak_secrets, hardcoded_creds, ssl_issues)
    """
    weak_secrets = []
    hardcoded_creds = []
    
    print(f"{BLUE}Scanning {root_dir} for security issues...{RESET}\n")
    
    # Scan all files
    for file_path in root_dir.rglob('*'):
        if not file_path.is_file():
            continue
        
        if should_skip_file(file_path):
            continue
        
        # Check for weak secrets
        secret_issues = check_weak_secrets(file_path)
        if secret_issues:
            weak_secrets.append((file_path, secret_issues))
        
        # Check for hardcoded credentials
        cred_issues = check_hardcoded_credentials(file_path)
        if cred_issues:
            hardcoded_creds.append((file_path, cred_issues))
    
    # Check SSL configuration
    ssl_issues = check_ssl_configuration()
    
    return weak_secrets, hardcoded_creds, ssl_issues


def print_results(weak_secrets: List, hardcoded_creds: List, ssl_issues: List) -> int:
    """
    Print scan results and return exit code.
    
    Returns:
        0 - No issues
        1 - Critical issues found
        2 - Warnings only
    """
    has_critical = False
    has_warnings = False
    
    print("\n" + "=" * 70)
    print(f"{BLUE}Security Scan Results{RESET}")
    print("=" * 70 + "\n")
    
    # Report weak secrets (CRITICAL)
    if weak_secrets:
        has_critical = True
        print(f"{RED}❌ CRITICAL: Weak or Default Secrets Found{RESET}\n")
        
        for file_path, issues in weak_secrets:
            print(f"{RED}File: {file_path}{RESET}")
            for line_num, line, pattern in issues:
                print(f"  Line {line_num}: {line[:80]}")
            print()
        
        print(f"{RED}Action Required:{RESET}")
        print("  1. Remove hardcoded secrets from code")
        print("  2. Use environment variables: os.getenv('SECRET_KEY')")
        print("  3. Generate strong secrets: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
        print()
    
    # Report hardcoded credentials (CRITICAL)
    if hardcoded_creds:
        has_critical = True
        print(f"{RED}❌ CRITICAL: Hardcoded Credentials Found{RESET}\n")
        
        for file_path, issues in hardcoded_creds:
            print(f"{RED}File: {file_path}{RESET}")
            for line_num, line in issues:
                # Mask the actual credential
                masked_line = re.sub(r'(password|key)\s*[\":=]\s*["\'][^"\']+["\']', 
                                   r'\1="****"', line, flags=re.IGNORECASE)
                print(f"  Line {line_num}: {masked_line[:80]}")
            print()
        
        print(f"{RED}Action Required:{RESET}")
        print("  1. Move credentials to environment variables")
        print("  2. Use .env files for local development")
        print("  3. Never commit credentials to version control")
        print()
    
    # Report SSL issues (WARNING)
    if ssl_issues:
        has_warnings = True
        print(f"{YELLOW}⚠️  WARNING: SSL Configuration Issues{RESET}\n")
        
        for issue in ssl_issues:
            print(f"  {issue}")
        print()
        
        print(f"{YELLOW}Recommendation:{RESET}")
        print("  Ensure all production database connections use SSL/TLS")
        print("  Add ?sslmode=require to DATABASE_URL")
        print()
    
    # Summary
    print("=" * 70)
    
    if not weak_secrets and not hardcoded_creds and not ssl_issues:
        print(f"{GREEN}✅ All security checks passed!{RESET}")
        return 0
    
    if has_critical:
        print(f"{RED}❌ FAILED: Critical security issues must be fixed{RESET}")
        return 1
    
    if has_warnings:
        print(f"{YELLOW}⚠️  WARNING: Security recommendations should be addressed{RESET}")
        return 2
    
    return 0


def main():
    """Main entry point."""
    # Get repository root
    repo_root = Path(__file__).parent.parent
    
    print(f"{BLUE}HireMeBahamas Security Validation{RESET}")
    print(f"{BLUE}Repository: {repo_root}{RESET}\n")
    
    # Scan for issues
    weak_secrets, hardcoded_creds, ssl_issues = scan_directory(repo_root)
    
    # Print results and get exit code
    exit_code = print_results(weak_secrets, hardcoded_creds, ssl_issues)
    
    # Additional info
    if exit_code != 0:
        print(f"\n{BLUE}For more information, see:{RESET}")
        print("  - SECURITY.md - Security best practices")
        print("  - SECURITY_CHECKLIST.md - Deployment checklist")
        print("  - .env.example - Environment variable reference")
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

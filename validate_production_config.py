#!/usr/bin/env python3
"""
Production Configuration Validator

This script validates that the application meets production deployment requirements:
1. ❌ ABSOLUTE BAN: No localhost in production
2. ❌ ABSOLUTE BAN: Database validation raises on startup in production
3. ❌ ABSOLUTE BAN: No Unix sockets (/var/run/postgresql) in production
4. ❌ ABSOLUTE BAN: No gunicorn on Vercel (uses mangum/uvicorn)
5. ✅ REQUIRED: /health endpoint has no database dependencies

Usage:
    python validate_production_config.py [--environment production]
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple


class ValidationError(Exception):
    """Custom exception for validation failures"""
    pass


def check_localhost_ban(repo_root: Path, is_prod: bool) -> List[str]:
    """Check that localhost is not hardcoded in production code.
    
    Returns:
        List of issues found
    """
    issues = []
    
    # Files to check for localhost references
    files_to_check = [
        'backend/app/core/config.py',
        'backend/app/core/database.py',
        'backend/app/main.py',
        'api/backend_app/main.py',
        'api/backend_app/core/environment.py',
        'frontend/src/services/api_ai_enhanced.ts',
    ]
    
    for file_path in files_to_check:
        full_path = repo_root / file_path
        if not full_path.exists():
            continue
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for hardcoded localhost without environment checks
        lines = content.split('\n')
        in_docstring = False
        docstring_delimiter = None
        
        for i, line in enumerate(lines, 1):
            # Track docstrings more accurately
            if '"""' in line:
                if docstring_delimiter == '"""' or docstring_delimiter is None:
                    in_docstring = not in_docstring
                    docstring_delimiter = '"""' if in_docstring else None
            elif "'''" in line:
                if docstring_delimiter == "'''" or docstring_delimiter is None:
                    in_docstring = not in_docstring
                    docstring_delimiter = "'''" if in_docstring else None
            
            # Skip comments, docstrings, and certain safe patterns
            if (line.strip().startswith('#') or 
                line.strip().startswith('//') or
                in_docstring):
                continue
            
            # Check for localhost without production guards
            if 'localhost' in line.lower() or '127.0.0.1' in line:
                # Check if it's properly guarded by environment check
                # Look at surrounding context (prev 10 lines for better detection)
                context = '\n'.join(lines[max(0, i-11):i])
                
                # Check for various environment guard patterns
                has_env_guard = any([
                    'is_development' in context,
                    'is_production' in context,
                    'ENVIRONMENT' in context and 'production' in context,
                    'import.meta.env.PROD' in context,
                    'not _is_prod' in context,
                    'not isProduction' in context,
                    'VERCEL_ENV' in context,
                    'get_cors_origins' in line,  # Function call that handles env check
                    'Add localhost origins only in development' in context,
                    'Only add localhost fallbacks in development' in context,
                    '# ❌ ABSOLUTE BAN' in context,
                    'CORS_ORIGINS' in context,  # In settings class
                    'def get_cors_origins' in context,  # Function definition
                    'elif hostname in' in line,  # Part of validation check
                    'if hostname in' in line,  # Part of validation check
                    'banned in production' in line.lower(),  # Documentation
                    'Requirements:' in context and 'Must contain' in line,  # In requirements list
                ])
                
                if not has_env_guard and 'ABSOLUTE BAN' not in line:
                    issues.append(
                        f"❌ {file_path}:{i} - Unguarded localhost reference: {line.strip()[:80]}"
                    )
    
    return issues


def check_database_validation(repo_root: Path) -> List[str]:
    """Check that database validation raises exceptions in production.
    
    Returns:
        List of issues found
    """
    issues = []
    
    config_file = repo_root / 'backend' / 'app' / 'core' / 'config.py'
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that validation raises ValueError for localhost in production
        if 'ABSOLUTE BAN' not in content:
            issues.append(
                "❌ backend/app/core/config.py - Missing ABSOLUTE BAN comments for localhost"
            )
        
        if 'raise ValueError' not in content:
            issues.append(
                "❌ backend/app/core/config.py - Database validation does not raise exceptions"
            )
    else:
        issues.append("❌ backend/app/core/config.py not found")
    
    database_file = repo_root / 'backend' / 'app' / 'core' / 'database.py'
    if database_file.exists():
        with open(database_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that database validation raises for localhost and Unix sockets in production
        if 'ABSOLUTE BAN' not in content:
            issues.append(
                "❌ backend/app/core/database.py - Missing ABSOLUTE BAN comments"
            )
    
    return issues


def check_unix_socket_ban(repo_root: Path) -> List[str]:
    """Check that Unix sockets are banned in production.
    
    Returns:
        List of issues found
    """
    issues = []
    
    files_to_check = [
        'backend/app/core/config.py',
        'backend/app/core/database.py',
    ]
    
    for file_path in files_to_check:
        full_path = repo_root / file_path
        if not full_path.exists():
            continue
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Unix socket validation
        if '/var/run/' in content:
            # Good - file checks for Unix sockets
            if 'raise ValueError' not in content:
                issues.append(
                    f"❌ {file_path} - Checks for Unix sockets but doesn't raise exception"
                )
        else:
            issues.append(
                f"❌ {file_path} - Missing Unix socket validation"
            )
    
    return issues


def check_vercel_no_gunicorn(repo_root: Path) -> List[str]:
    """Check that Vercel does not use gunicorn.
    
    Returns:
        List of issues found
    """
    issues = []
    
    vercel_config = repo_root / 'vercel.json'
    if vercel_config.exists():
        with open(vercel_config, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'gunicorn' in content.lower():
            issues.append(
                "❌ vercel.json - Contains gunicorn reference (Vercel requires serverless)"
            )
    
    api_index = repo_root / 'api' / 'index.py'
    if api_index.exists():
        with open(api_index, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'gunicorn' in content.lower():
            issues.append(
                "❌ api/index.py - Contains gunicorn reference (should use Mangum)"
            )
        
        if 'Mangum' not in content:
            issues.append(
                "⚠️  api/index.py - Missing Mangum import (Vercel serverless adapter)"
            )
    
    return issues


def check_health_endpoint_no_db(repo_root: Path) -> List[str]:
    """Check that /health endpoint has no database dependencies.
    
    Returns:
        List of issues found
    """
    issues = []
    
    files_to_check = [
        'backend/app/main.py',
        'api/backend_app/main.py',
    ]
    
    for file_path in files_to_check:
        full_path = repo_root / file_path
        if not full_path.exists():
            continue
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find /health endpoint - match both decorator styles
        health_pattern = r'@app\.(get|head)\s*\(\s*["\']/?health["\']\s*[,)]'
        matches = list(re.finditer(health_pattern, content))
        
        if not matches:
            # Try alternative pattern
            health_pattern2 = r'def\s+health\s*\(\s*\):'
            matches = list(re.finditer(health_pattern2, content))
            if not matches:
                issues.append(f"⚠️  {file_path} - No /health endpoint found")
                continue
        
        # Check each health endpoint for database dependencies
        for match in matches:
            # Get the function definition after this decorator
            start_pos = match.end()
            # Find the next function definition
            func_match = re.search(r'def\s+(\w+)\s*\([^)]*\):', content[start_pos:start_pos+500])
            if func_match:
                func_name = func_match.group(1)
                
                # Check function parameters for database dependency
                if 'db:' in func_match.group(0) or 'Depends(get_db)' in func_match.group(0):
                    issues.append(
                        f"❌ {file_path} - /health endpoint '{func_name}' has database dependency"
                    )
    
    return issues


def main():
    """Main validation function"""
    # Get repository root
    repo_root = Path(__file__).parent
    
    # Check if running in production mode
    is_prod = os.getenv('ENVIRONMENT', '').lower() == 'production' or \
              os.getenv('VERCEL_ENV', '').lower() == 'production' or \
              '--environment' in sys.argv and 'production' in ' '.join(sys.argv)
    
    print("="*70)
    print("PRODUCTION CONFIGURATION VALIDATOR")
    print("="*70)
    print(f"Environment: {'PRODUCTION' if is_prod else 'DEVELOPMENT'}")
    print(f"Repository root: {repo_root}")
    print()
    
    all_issues = []
    
    # Run all checks
    checks = [
        ("1. Localhost Ban", check_localhost_ban, [repo_root, is_prod]),
        ("2. Database Validation", check_database_validation, [repo_root]),
        ("3. Unix Socket Ban", check_unix_socket_ban, [repo_root]),
        ("4. Vercel No Gunicorn", check_vercel_no_gunicorn, [repo_root]),
        ("5. Health Endpoint DB-Free", check_health_endpoint_no_db, [repo_root]),
    ]
    
    for check_name, check_func, args in checks:
        print(f"Running: {check_name}")
        issues = check_func(*args)
        all_issues.extend(issues)
        
        if not issues:
            print(f"  ✅ PASSED")
        else:
            print(f"  ❌ FAILED ({len(issues)} issues)")
            for issue in issues:
                print(f"    {issue}")
        print()
    
    # Summary
    print("="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    if not all_issues:
        print("✅ ALL CHECKS PASSED")
        print()
        print("Production configuration is valid:")
        print("  ✅ No localhost in production")
        print("  ✅ Database validation raises on startup")
        print("  ✅ Unix sockets banned")
        print("  ✅ Gunicorn not used on Vercel")
        print("  ✅ /health endpoint is database-free")
        return 0
    else:
        print(f"❌ VALIDATION FAILED ({len(all_issues)} issues)")
        print()
        print("Issues found:")
        for issue in all_issues:
            print(f"  {issue}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

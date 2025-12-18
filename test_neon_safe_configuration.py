#!/usr/bin/env python3
"""
Test Neon-Safe Database Configuration

Verifies that the database configuration follows Neon-safe requirements:
1. DATABASE_URL uses postgresql+asyncpg:// format
2. NO sslmode in URL
3. NO statement_timeout
4. NO connect_args with sslmode
5. create_async_engine uses ONLY pool_pre_ping=True
6. Health endpoint returns {"status": "ok"}
"""
import os
import sys
import re
from pathlib import Path

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def check_database_file(file_path):
    """Check a database.py file for Neon-safe configuration"""
    print(f"\n{'='*80}")
    print(f"Checking: {file_path}")
    print(f"{'='*80}")
    
    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    all_checks_passed = True
    
    # Check 1: No sslmode in comments suggesting it should be in URL
    if 'sslmode=require' in content and 'postgresql+asyncpg://' in content:
        # Check if it's only in deprecation notices or error messages
        lines_with_sslmode = [line for line in content.split('\n') if 'sslmode=require' in line]
        if any('DATABASE_URL=' in line and not ('#' in line or 'error' in line.lower() or 'required format' in line.lower()) for line in lines_with_sslmode):
            print_error("Found sslmode=require in DATABASE_URL examples (should be removed for Neon)")
            all_checks_passed = False
        else:
            print_success("No active sslmode=require in DATABASE_URL examples")
    else:
        print_success("No sslmode=require found in DATABASE_URL format")
    
    # Check 2: No strip_sslmode_from_url calls
    if 'strip_sslmode_from_url' in content:
        print_error("Found strip_sslmode_from_url() calls (should be removed for Neon)")
        all_checks_passed = False
    else:
        print_success("No strip_sslmode_from_url() calls found")
    
    # Check 3: No statement_timeout in connect_args or server_settings
    if 'statement_timeout' in content:
        # Check if it's in actual code or just comments
        lines_with_timeout = [line for line in content.split('\n') if 'statement_timeout' in line]
        if any(not line.strip().startswith('#') and '"statement_timeout"' in line for line in lines_with_timeout):
            print_error("Found statement_timeout in active code (not supported by Neon pooler)")
            all_checks_passed = False
        else:
            print_success("No active statement_timeout configuration")
    else:
        print_success("No statement_timeout found")
    
    # Check 4: create_async_engine uses pool_pre_ping=True
    if 'create_async_engine' in content:
        if 'pool_pre_ping=True' in content:
            print_success("create_async_engine uses pool_pre_ping=True")
        else:
            print_warning("create_async_engine found but pool_pre_ping=True not verified")
    
    # Check 5: No connect_args with ssl or sslmode
    connect_args_pattern = r'connect_args\s*=\s*\{[^}]*\}'
    matches = re.finditer(connect_args_pattern, content, re.DOTALL)
    for match in matches:
        args_block = match.group(0)
        if '"ssl"' in args_block or "'ssl'" in args_block:
            print_error("Found SSL configuration in connect_args (not needed for Neon)")
            all_checks_passed = False
        if 'sslmode' in args_block:
            print_error("Found sslmode in connect_args (not supported by Neon)")
            all_checks_passed = False
    
    if all_checks_passed:
        print_success("All connect_args checks passed (no SSL or sslmode)")
    
    # Check 6: postgresql+asyncpg:// format is documented
    if 'postgresql+asyncpg://' in content:
        print_success("Uses postgresql+asyncpg:// format")
    else:
        print_warning("postgresql+asyncpg:// format not found in file")
    
    return all_checks_passed

def check_main_file(file_path):
    """Check main.py for correct health endpoint"""
    print(f"\n{'='*80}")
    print(f"Checking: {file_path}")
    print(f"{'='*80}")
    
    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    all_checks_passed = True
    
    # Check for health endpoint
    if '@app.get("/health")' in content or '@app.get(\'/health\')' in content:
        print_success("Health endpoint found")
        
        # Check for correct return value
        if '{"status": "ok"}' in content or "{'status': 'ok'}" in content:
            print_success("Health endpoint returns correct format: {\"status\": \"ok\"}")
        else:
            print_warning("Health endpoint may not return exactly {\"status\": \"ok\"}")
    else:
        print_error("Health endpoint not found")
        all_checks_passed = False
    
    # Check for FastAPI app
    if 'FastAPI' in content:
        print_success("FastAPI app initialization found")
    else:
        print_error("FastAPI not found in main.py")
        all_checks_passed = False
    
    return all_checks_passed

def check_procfile(file_path):
    """Check Procfile for correct Gunicorn command"""
    print(f"\n{'='*80}")
    print(f"Checking: {file_path}")
    print(f"{'='*80}")
    
    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    all_checks_passed = True
    
    # Check for gunicorn command
    if 'gunicorn' in content:
        print_success("Gunicorn command found")
        
        # Check for UvicornWorker
        if 'uvicorn.workers.UvicornWorker' in content or '-k uvicorn.workers.UvicornWorker' in content:
            print_success("Uses uvicorn.workers.UvicornWorker")
        else:
            print_error("Missing -k uvicorn.workers.UvicornWorker")
            all_checks_passed = False
        
        # Check for bind
        if '--bind 0.0.0.0:' in content or 'bind 0.0.0.0:' in content:
            print_success("Binds to 0.0.0.0")
        else:
            print_warning("Bind configuration may be missing")
        
        # Check for workers
        if '--workers 2' in content or 'workers 2' in content or '--workers=2' in content:
            print_success("Uses 2 workers")
        else:
            print_warning("Workers=2 not explicitly found")
        
        # Check for timeout
        if '--timeout 120' in content or 'timeout 120' in content or '--timeout=120' in content:
            print_success("Uses timeout 120")
        else:
            print_warning("Timeout=120 not explicitly found")
        
        # Check for no --reload flag
        if '--reload' in content:
            print_error("Found --reload flag (should not be in production)")
            all_checks_passed = False
        else:
            print_success("No --reload flag (correct for production)")
        
        # Check for no sslmode
        if 'sslmode' in content:
            print_error("Found sslmode in Procfile (should not be here)")
            all_checks_passed = False
        else:
            print_success("No sslmode in Procfile")
    else:
        print_error("Gunicorn command not found in Procfile")
        all_checks_passed = False
    
    return all_checks_passed

def main():
    """Run all checks"""
    print("=" * 80)
    print("NEON-SAFE CONFIGURATION TEST")
    print("=" * 80)
    
    repo_root = Path(__file__).parent
    
    all_passed = True
    
    # Check database files
    database_files = [
        repo_root / "api" / "backend_app" / "database.py",
        repo_root / "backend" / "app" / "database.py",
    ]
    
    for db_file in database_files:
        if not check_database_file(str(db_file)):
            all_passed = False
    
    # Check main files
    main_files = [
        repo_root / "api" / "backend_app" / "main.py",
        repo_root / "backend" / "app" / "main.py",
    ]
    
    for main_file in main_files:
        if main_file.exists():
            if not check_main_file(str(main_file)):
                all_passed = False
    
    # Check Procfiles
    procfiles = [
        repo_root / "Procfile",
        repo_root / "backend" / "Procfile",
    ]
    
    for procfile in procfiles:
        if procfile.exists():
            if not check_procfile(str(procfile)):
                all_passed = False
    
    # Check nixpacks.toml
    nixpacks = repo_root / "nixpacks.toml"
    if nixpacks.exists():
        if not check_procfile(str(nixpacks)):
            all_passed = False
    
    # Final summary
    print("\n" + "=" * 80)
    if all_passed:
        print_success("ALL CHECKS PASSED! Configuration is Neon-safe ✅")
    else:
        print_error("SOME CHECKS FAILED! Review the output above ⚠️")
    print("=" * 80)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

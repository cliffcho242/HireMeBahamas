#!/usr/bin/env python3
"""
Deployment Configuration Validator for HireMeBahamas
Checks for common deployment issues before you deploy
"""
import os
import sys
import re
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_success(text):
    print(f"✅ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def check_render_yaml():
    """Check render.yaml configuration"""
    print_header("Checking render.yaml")
    
    render_yaml_path = Path("render.yaml")
    if not render_yaml_path.exists():
        print_warning("render.yaml not found")
        return False
    
    content = render_yaml_path.read_text()
    
    # Check for multi-line commands with backslashes
    if "startCommand:" in content:
        # Extract the startCommand line and the next few lines
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'startCommand:' in line:
                command_line = line.split('startCommand:')[1].strip()
                
                # Check if the command has backslashes (multiline)
                if '\\' in command_line:
                    print_error("startCommand contains backslashes (\\)")
                    print_error("Multi-line commands don't work in YAML string values")
                    print_info("Fix: Use a single-line command")
                    return False
                
                # Check if the command uses the recommended entry point
                if 'app:app' in command_line and 'app.main:app' not in command_line:
                    print_warning("Using 'app:app' entry point (not recommended)")
                    print_info("Recommended: Use 'app.main:app' for clarity")
                elif 'app.main:app' in command_line:
                    print_success("Using recommended entry point: app.main:app")
                
                # Check for proper worker class if using gunicorn
                if 'gunicorn' in command_line:
                    if 'uvicorn.workers.UvicornWorker' in command_line:
                        print_success("Using Uvicorn workers with Gunicorn")
                    else:
                        print_warning("Gunicorn without Uvicorn workers detected")
                        print_info("For FastAPI, use: --worker-class uvicorn.workers.UvicornWorker")
                
                print_success("startCommand is properly formatted (single line)")
                print_info(f"Command: {command_line[:80]}...")
                return True
    else:
        print_warning("No startCommand found in render.yaml")
        return False

def check_render_toml():
    """Check render.toml configuration"""
    print_header("Checking render.toml")
    
    render_toml_path = Path("render.toml")
    if not render_toml_path.exists():
        print_warning("render.toml not found")
        return False
    
    content = render_toml_path.read_text()
    
    if "startCommand" in content:
        # Extract the startCommand
        match = re.search(r'startCommand\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            command = match.group(1)
            
            # Check for backslashes
            if '\\' in command:
                print_error("startCommand contains backslashes (\\)")
                print_error("Multi-line commands don't work in TOML string values")
                print_info("Fix: Use a single-line command")
                return False
            
            print_success("startCommand is properly formatted (single line)")
            print_info(f"Command: {command[:80]}...")
            return True
    
    if "cmd" in content:
        # Check [start] section
        match = re.search(r'\[start\].*?cmd\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
        if match:
            command = match.group(1)
            
            # Check for backslashes
            if '\\' in command:
                print_error("start.cmd contains backslashes (\\)")
                print_error("Multi-line commands don't work in TOML string values")
                print_info("Fix: Use a single-line command")
                return False
            
            print_success("start.cmd is properly formatted (single line)")
            print_info(f"Command: {command[:80]}...")
            return True
    
    print_warning("No startCommand or cmd found in render.toml")
    return False

def check_procfile():
    """Check Procfile configuration"""
    print_header("Checking Procfile")
    
    procfile_path = Path("Procfile")
    if not procfile_path.exists():
        print_warning("Procfile not found in root directory")
        # Check backend/Procfile
        procfile_path = Path("backend/Procfile")
        if procfile_path.exists():
            print_info("Found Procfile in backend/ directory")
        else:
            print_warning("No Procfile found")
            return False
    
    content = procfile_path.read_text()
    
    # Check for multi-line commands with backslashes
    if '\\' in content:
        print_error("Procfile contains backslashes (\\)")
        print_error("Multi-line commands don't work in Procfile")
        print_info("Fix: Each process type should be on a single line")
        return False
    
    # Check for web process
    if 'web:' in content:
        print_success("web process defined")
        # Extract the command
        for line in content.split('\n'):
            if line.startswith('web:'):
                command = line.split('web:')[1].strip()
                print_info(f"Command: {command[:80]}...")
                
                # Check if using recommended entry point
                if 'app:app' in command and 'app.main:app' not in command:
                    print_warning("Using 'app:app' entry point (not recommended)")
                    print_info("Recommended: Use 'app.main:app' for clarity")
                
                return True
    else:
        print_warning("No web process defined in Procfile")
        return False

def check_gunicorn_config():
    """Check gunicorn.conf.py for common issues"""
    print_header("Checking gunicorn.conf.py")
    
    config_path = Path("gunicorn.conf.py")
    if not config_path.exists():
        print_info("gunicorn.conf.py not found (optional)")
        return True
    
    content = config_path.read_text()
    
    # Check preload_app setting
    if 'preload_app' in content:
        if re.search(r'preload_app\s*=\s*True', content):
            print_warning("preload_app = True detected")
            print_warning("This can cause database connection issues")
            print_info("Consider: preload_app = False for database safety")
        elif re.search(r'preload_app\s*=\s*False', content):
            print_success("preload_app = False (database-safe configuration)")
    
    # Check worker configuration
    if 'workers' in content:
        print_info("Worker configuration found in gunicorn.conf.py")
    
    print_success("gunicorn.conf.py exists and looks reasonable")
    return True

def check_entry_points():
    """Check if the application entry points exist"""
    print_header("Checking Application Entry Points")
    
    # Check for FastAPI entry point
    fastapi_paths = [
        Path("backend/app/main.py"),
        Path("app/main.py"),
    ]
    
    fastapi_found = False
    for path in fastapi_paths:
        if path.exists():
            print_success(f"FastAPI entry point found: {path}")
            fastapi_found = True
            break
    
    if not fastapi_found:
        print_warning("FastAPI entry point (app/main.py) not found")
    
    # Check for Flask entry point
    flask_path = Path("final_backend_postgresql.py")
    if flask_path.exists():
        print_success(f"Flask entry point found: {flask_path}")
    else:
        print_info("Flask entry point (final_backend_postgresql.py) not found")
    
    if not fastapi_found and not flask_path.exists():
        print_error("No valid entry points found!")
        print_info("Expected: backend/app/main.py or final_backend_postgresql.py")
        return False
    
    return True

def check_requirements():
    """Check requirements.txt for essential packages"""
    print_header("Checking requirements.txt")
    
    req_paths = [
        Path("requirements.txt"),
        Path("backend/requirements.txt"),
    ]
    
    found = False
    for req_path in req_paths:
        if req_path.exists():
            found = True
            content = req_path.read_text().lower()
            
            print_success(f"Found: {req_path}")
            
            # Check for essential packages
            if 'gunicorn' in content or 'uvicorn' in content:
                print_success("ASGI/WSGI server found (gunicorn or uvicorn)")
            else:
                print_error("No ASGI/WSGI server found")
                print_info("Add: gunicorn or uvicorn to requirements.txt")
            
            if 'fastapi' in content or 'flask' in content:
                print_success("Web framework found (FastAPI or Flask)")
            else:
                print_warning("No web framework found in requirements")
            
            if 'sqlalchemy' in content or 'psycopg2' in content or 'asyncpg' in content:
                print_success("Database driver found")
            else:
                print_warning("No database driver found")
            
            break
    
    if not found:
        print_error("No requirements.txt found")
        return False
    
    return True

def check_environment_example():
    """Check if .env.example exists and has required variables"""
    print_header("Checking Environment Configuration")
    
    env_example_path = Path(".env.example")
    if env_example_path.exists():
        print_success(".env.example found")
        content = env_example_path.read_text()
        
        required_vars = ['DATABASE_URL', 'SECRET_KEY', 'JWT_SECRET_KEY']
        for var in required_vars:
            # Use regex to match actual variable definitions, not just mentions in comments
            import re
            pattern = rf'^{re.escape(var)}\s*='
            if re.search(pattern, content, re.MULTILINE):
                print_success(f"{var} documented in .env.example")
            else:
                print_warning(f"{var} not found in .env.example")
    else:
        print_info(".env.example not found (optional)")
    
    return True

def main():
    """Run all validation checks"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "HireMeBahamas Deployment Validator" + " " * 19 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Change to repository root if script is run from subdirectory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    results = []
    
    results.append(("render.yaml", check_render_yaml()))
    results.append(("render.toml", check_render_toml()))
    results.append(("Procfile", check_procfile()))
    results.append(("gunicorn.conf.py", check_gunicorn_config()))
    results.append(("Entry Points", check_entry_points()))
    results.append(("requirements.txt", check_requirements()))
    results.append(("Environment", check_environment_example()))
    
    # Summary
    print_header("Validation Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "⚠️  WARN"
        print(f"{status}: {name}")
    
    print("\n" + "=" * 70)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print_success("All checks passed! Your configuration looks good.")
        print_info("You can proceed with deployment.")
    else:
        print_warning("Some checks failed or have warnings.")
        print_info("Review the warnings above before deploying.")
        print_info("\nFor help with common issues:")
        print_info("  • FIX_RENDER_GUNICORN_ERROR.md - Fix gunicorn errors")
        print_info("  • DEPLOYMENT_COMMANDS_QUICK_REF.md - All deployment commands")
        print_info("  • GUNICORN_ENTRY_POINTS.md - Entry point documentation")
    
    print("=" * 70 + "\n")
    
    # Return exit code based on critical failures
    # Only fail if entry points or requirements are missing
    critical_checks = ["Entry Points", "requirements.txt"]
    critical_failed = any(
        not result for name, result in results if name in critical_checks
    )
    
    return 0 if not critical_failed else 1

if __name__ == "__main__":
    sys.exit(main())

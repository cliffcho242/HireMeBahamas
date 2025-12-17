#!/usr/bin/env python3
"""
Validation Script: Gunicorn Master Fix
Verifies all Gunicorn commands are correct and production-safe.
"""
import re
import sys
from pathlib import Path


def validate_command(command: str, source: str) -> list[str]:
    """
    Validate a Gunicorn command against the master requirements.
    
    Returns list of issues found (empty list = valid).
    """
    issues = []
    
    # Check 1: Single line (no newlines except at end)
    if '\n' in command.strip():
        issues.append(f"{source}: Command spans multiple lines")
    
    # Check 2: No backslashes used for line continuation
    # Look for backslash followed by whitespace (line continuation pattern)
    if re.search(r'\\\s', command):
        issues.append(f"{source}: Contains backslash line continuations")
    
    # Check 3: Must specify worker-class
    if '--worker-class' not in command and 'worker-class' not in command:
        issues.append(f"{source}: Missing --worker-class argument")
    
    # Check 4: Worker class must be uvicorn.workers.UvicornWorker
    if 'uvicorn.workers.UvicornWorker' not in command:
        issues.append(f"{source}: Wrong or missing worker class (must be uvicorn.workers.UvicornWorker)")
    
    # Check 5: Must specify bind or use $PORT
    if '--bind' not in command and 'bind' not in command:
        issues.append(f"{source}: Missing --bind argument")
    
    # Check 6: Bind should be 0.0.0.0:$PORT
    if '$PORT' not in command and '${PORT}' not in command:
        issues.append(f"{source}: Not using $PORT variable for dynamic port")
    
    # Check 7: Workers should be 1
    # Match both --workers 1 and --workers=1 formats
    workers_match = re.search(r'--workers(?:\s+|=)(\d+)', command)
    if workers_match:
        workers = int(workers_match.group(1))
        if workers != 1:
            issues.append(f"{source}: Workers set to {workers}, should be 1")
    else:
        issues.append(f"{source}: --workers argument not found")
    
    # Check 8: Must use app.main:app entry point
    if 'app.main:app' not in command:
        issues.append(f"{source}: Incorrect entry point (should be app.main:app)")
    
    # Check 9: Should NOT have --preload on command line
    if '--preload' in command or ' preload ' in command:
        issues.append(f"{source}: Contains --preload flag (dangerous with databases)")
    
    # Check 10: Should have timeout
    if '--timeout' not in command and 'timeout' not in command:
        issues.append(f"{source}: Missing --timeout argument")
    
    # Check 11: No smart quotes or other problematic characters
    forbidden_quotes = ['"', '"', ''', ''']
    if any(quote in command for quote in forbidden_quotes):
        issues.append(f"{source}: Contains smart quotes (use straight quotes)")
    
    return issues


def validate_file(filepath: Path, pattern: str) -> list[str]:
    """Validate Gunicorn commands in a file."""
    issues = []
    
    if not filepath.exists():
        return [f"{filepath}: File not found"]
    
    try:
        content = filepath.read_text()
        
        # Find lines matching the pattern
        for line_num, line in enumerate(content.splitlines(), 1):
            if pattern in line and 'gunicorn' in line:
                # Extract the command part
                if ':' in line:
                    command = line.split(':', 1)[1].strip()
                else:
                    command = line.strip()
                
                issues.extend(validate_command(command, f"{filepath.name}:{line_num}"))
    
    except Exception as e:
        issues.append(f"{filepath}: Error reading file: {e}")
    
    return issues


def main():
    """Run validation on all configuration files."""
    print("=" * 80)
    print("🔍 Gunicorn Master Fix - Command Validation")
    print("=" * 80)
    print()
    
    repo_root = Path(__file__).parent
    all_issues = []
    
    # Validate render.yaml
    print("📄 Checking render.yaml...")
    render_yaml = repo_root / "render.yaml"
    issues = validate_file(render_yaml, "startCommand")
    if issues:
        all_issues.extend(issues)
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print("  ✅ render.yaml is correct")
    print()
    
    # Validate root Procfile
    print("📄 Checking Procfile (root)...")
    procfile = repo_root / "Procfile"
    issues = validate_file(procfile, "web:")
    if issues:
        all_issues.extend(issues)
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print("  ✅ Procfile (root) is correct")
    print()
    
    # Validate backend/Procfile
    print("📄 Checking backend/Procfile...")
    backend_procfile = repo_root / "backend" / "Procfile"
    issues = validate_file(backend_procfile, "web:")
    if issues:
        all_issues.extend(issues)
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print("  ✅ backend/Procfile is correct")
    print()
    
    # Validate gunicorn.conf.py
    print("📄 Checking backend/gunicorn.conf.py...")
    gunicorn_conf = repo_root / "backend" / "gunicorn.conf.py"
    if not gunicorn_conf.exists():
        print("  ❌ backend/gunicorn.conf.py not found")
        all_issues.append("backend/gunicorn.conf.py not found")
    else:
        content = gunicorn_conf.read_text()
        config_issues = []
        
        # Check worker_class
        if 'worker_class = "uvicorn.workers.UvicornWorker"' not in content:
            config_issues.append("worker_class not set to uvicorn.workers.UvicornWorker")
        
        # Check bind
        if 'bind = ' not in content:
            config_issues.append("bind not configured")
        
        # Check workers default
        if 'workers = ' not in content and 'WEB_CONCURRENCY' not in content:
            config_issues.append("workers not configured")
        
        # Check preload_app
        if 'preload_app = True' in content:
            config_issues.append("preload_app = True (should be False for databases)")
        
        if config_issues:
            all_issues.extend([f"gunicorn.conf.py: {issue}" for issue in config_issues])
            for issue in config_issues:
                print(f"  ❌ {issue}")
        else:
            print("  ✅ backend/gunicorn.conf.py is correct")
    print()
    
    # Summary
    print("=" * 80)
    if all_issues:
        print(f"❌ VALIDATION FAILED - {len(all_issues)} issue(s) found")
        print("=" * 80)
        print()
        print("Issues found:")
        for issue in all_issues:
            print(f"  • {issue}")
        print()
        print("📚 Fix these issues using the guide in GUNICORN_MASTER_FIX_FOREVER.md")
        sys.exit(1)
    else:
        print("✅ ALL VALIDATIONS PASSED")
        print("=" * 80)
        print()
        print("🎉 All Gunicorn commands are correct and production-safe!")
        print()
        print("Next steps:")
        print("  1. Commit these changes")
        print("  2. Deploy to your platform (Render/Railway/Heroku)")
        print("  3. Verify deployment logs show successful startup")
        print("  4. Test health endpoint: curl https://your-app/health")
        print()
        print("📚 For troubleshooting, see GUNICORN_MASTER_FIX_FOREVER.md")
        sys.exit(0)


if __name__ == "__main__":
    main()

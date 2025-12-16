#!/usr/bin/env python3
"""
Test script to validate gunicorn command syntax
Ensures no invalid arguments are present in deployment configurations
"""
import re
import subprocess
import sys
from pathlib import Path


def parse_procfile(file_path):
    """Extract gunicorn commands from Procfile"""
    commands = []
    try:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line.startswith('web:') and 'gunicorn' in line:
                    # Extract command after 'web:'
                    cmd = line.split('web:', 1)[1].strip()
                    commands.append((file_path, line_num, cmd))
    except FileNotFoundError:
        pass
    return commands


def parse_yaml_startcommand(file_path):
    """Extract gunicorn startCommand from YAML files"""
    commands = []
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Look for startCommand lines with gunicorn
            for match in re.finditer(r'startCommand:\s*(.+)', content):
                cmd = match.group(1).strip()
                if 'gunicorn' in cmd:
                    line_num = content[:match.start()].count('\n') + 1
                    commands.append((file_path, line_num, cmd))
    except FileNotFoundError:
        pass
    return commands


def check_gunicorn_args(cmd_str):
    """
    Check if gunicorn command has valid syntax
    Returns (is_valid, issues)
    """
    issues = []
    
    # Check for common problematic patterns
    if '--preload' in cmd_str:
        issues.append("WARNING: --preload flag conflicts with gunicorn.conf.py (preload_app=False)")
    
    # Check for unrecognized text patterns (non-flag words after flags)
    # This is a heuristic check for accidentally added text
    parts = cmd_str.split()
    i = 0
    # Track if we're in a cd command
    skip_next = False
    while i < len(parts):
        part = parts[i]
        if skip_next:
            skip_next = False
            i += 1
            continue
        # Skip shell constructs and their arguments
        if part in ['cd', '&&', '||', '|', '>', '<', '2>&1']:
            if part == 'cd':
                skip_next = True  # Skip the directory argument
            i += 1
            continue
        # Skip environment variable references
        if part.startswith('$') or '${' in part:
            i += 1
            continue
        # Check if it looks like gunicorn or a path
        if 'gunicorn' in part or part.startswith('./') or part.startswith('/'):
            i += 1
            continue
        # Check if it looks like an app module
        if ':' in part and not part.startswith('--'):
            i += 1
            continue
        # Check if it's a valid flag
        if part.startswith('--') or part.startswith('-'):
            i += 1
            # Some flags take arguments, skip the next part
            if part in ['--workers', '--worker-class', '--bind', '--timeout', '--log-level', 
                       '--config', '-w', '-k', '-b', '-t', '--chdir', '-c']:
                i += 1  # Skip the argument
            continue
        # If we get here and it's not a number (worker count, etc), it might be problematic
        if not part.isdigit() and part not in ['info', 'debug', 'warning', 'error', 'critical']:
            # This might be accidentally added text
            issues.append(f"POTENTIAL ISSUE: Unexpected text '{part}' in command")
        i += 1
    
    return len(issues) == 0 or (len(issues) == 1 and 'WARNING' in issues[0]), issues


def main():
    """Main test function"""
    print("=" * 80)
    print("Testing Gunicorn Command Syntax")
    print("=" * 80)
    print()
    
    # Collect all gunicorn commands from various config files
    all_commands = []
    
    repo_root = Path(__file__).parent
    
    # Check Procfiles
    for procfile in [repo_root / 'Procfile', repo_root / 'backend' / 'Procfile']:
        all_commands.extend(parse_procfile(procfile))
    
    # Check YAML files
    for yaml_file in [repo_root / 'render.yaml', repo_root / 'api' / 'render.yaml']:
        all_commands.extend(parse_yaml_startcommand(yaml_file))
    
    if not all_commands:
        print("❌ No gunicorn commands found in configuration files!")
        return 1
    
    print(f"Found {len(all_commands)} gunicorn command(s) to validate:\n")
    
    all_valid = True
    for file_path, line_num, cmd in all_commands:
        print(f"File: {file_path}")
        print(f"Line: {line_num}")
        print(f"Command: {cmd}")
        
        is_valid, issues = check_gunicorn_args(cmd)
        
        if issues:
            for issue in issues:
                if 'WARNING' in issue:
                    print(f"  ⚠️  {issue}")
                else:
                    print(f"  ❌ {issue}")
                    all_valid = False
        else:
            print(f"  ✅ Command syntax looks valid")
        print()
    
    print("=" * 80)
    if all_valid:
        print("✅ All gunicorn commands passed validation!")
        print()
        print("Note: If you're still seeing 'unrecognized arguments' errors:")
        print("1. Check your deployment platform dashboard (Railway/Render)")
        print("2. Look for environment variables with extra text")
        print("3. Verify no custom start commands in the platform settings")
        return 0
    else:
        print("❌ Some gunicorn commands have issues that need to be fixed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())

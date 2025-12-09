#!/usr/bin/env python3
"""
Railway PostgreSQL Configuration Validator

This script validates that your Railway configuration is set up correctly
to avoid the "root execution of PostgreSQL server is not permitted" error.

Usage:
    python validate_railway_postgres_config.py
"""

import json
import os
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")


def print_success(text):
    """Print a success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text):
    """Print an error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text):
    """Print an info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def validate_railway_json():
    """Validate railway.json configuration"""
    print_header("Validating railway.json")
    
    railway_json_path = Path("railway.json")
    
    if not railway_json_path.exists():
        print_error("railway.json not found in root directory")
        print_info("Railway will use default configuration")
        return False
    
    try:
        with open(railway_json_path, 'r') as f:
            config = json.load(f)
        
        print_success("railway.json found and valid JSON")
        
        # Check build configuration
        build = config.get('build', {})
        
        if build.get('builder') == 'NIXPACKS':
            print_success("Builder is set to NIXPACKS ✓")
        else:
            print_error(f"Builder is set to '{build.get('builder')}' instead of 'NIXPACKS'")
            return False
        
        if build.get('dockerCompose') == False:
            print_success("Docker Compose is explicitly disabled ✓")
        else:
            print_warning("dockerCompose should be set to false")
            return False
        
        if build.get('dockerfilePath') is None:
            print_success("dockerfilePath is null (Dockerfile disabled) ✓")
        elif 'dockerfilePath' not in build:
            print_info("dockerfilePath not specified (will use default)")
        else:
            print_warning(f"dockerfilePath is set to '{build.get('dockerfilePath')}'")
            print_warning("This may cause Railway to use Dockerfile instead of Nixpacks")
        
        return True
        
    except json.JSONDecodeError as e:
        print_error(f"railway.json is not valid JSON: {e}")
        return False
    except Exception as e:
        print_error(f"Error reading railway.json: {e}")
        return False


def validate_railwayignore():
    """Validate .railwayignore file"""
    print_header("Validating .railwayignore")
    
    railwayignore_path = Path(".railwayignore")
    
    if not railwayignore_path.exists():
        print_warning(".railwayignore not found")
        print_info("Consider creating one to exclude docker-compose files")
        return False
    
    try:
        with open(railwayignore_path, 'r') as f:
            content = f.read()
        
        print_success(".railwayignore found")
        
        # Check for docker-compose exclusions
        docker_compose_patterns = [
            'docker-compose',
            '*.yml',
            '*.yaml'
        ]
        
        has_docker_compose_ignore = any(pattern in content for pattern in docker_compose_patterns)
        
        if has_docker_compose_ignore:
            print_success("Docker Compose files are excluded ✓")
            return True
        else:
            print_warning("docker-compose files are not explicitly excluded")
            print_info("Add 'docker-compose*.yml' to .railwayignore")
            return False
            
    except Exception as e:
        print_error(f"Error reading .railwayignore: {e}")
        return False


def validate_nixpacks_toml():
    """Validate nixpacks.toml configuration"""
    print_header("Validating nixpacks.toml")
    
    nixpacks_path = Path("nixpacks.toml")
    
    if not nixpacks_path.exists():
        print_warning("nixpacks.toml not found")
        print_info("Railway will use default Nixpacks configuration")
        return False
    
    try:
        with open(nixpacks_path, 'r') as f:
            lines = f.readlines()
        
        print_success("nixpacks.toml found")
        
        # Parse only non-comment lines for package detection
        package_lines = []
        in_aptpkgs_section = False
        
        for line in lines:
            stripped = line.strip()
            # Check if we're in the aptPkgs section
            if 'aptpkgs' in stripped.lower() and '=' in stripped:
                in_aptpkgs_section = True
                continue
            # Exit aptPkgs section when we hit a new section or closing bracket
            if in_aptpkgs_section and (stripped.startswith('[') or stripped == ']'):
                in_aptpkgs_section = False
            # Collect package lines (ignore comments)
            if in_aptpkgs_section and not stripped.startswith('#') and stripped:
                package_lines.append(stripped.lower())
        
        packages_content = ' '.join(package_lines)
        
        # Check for PostgreSQL server packages (should NOT be present)
        bad_packages = [
            ('postgresql-16', 'postgresql-16'),
            ('postgresql-15', 'postgresql-15'),
            ('postgresql-14', 'postgresql-14'),
            ('postgresql-13', 'postgresql-13'),
            ('postgresql-12', 'postgresql-12'),
            ('"postgresql"', 'postgresql (server)'),
            ('postgresql-server', 'postgresql-server'),
            ('postgres-server', 'postgres-server')
        ]
        
        found_bad_packages = []
        for pkg_pattern, pkg_name in bad_packages:
            # Look for the package as a quoted string in the list
            if f'"{pkg_pattern.strip("\"")}"' in packages_content or \
               f"'{pkg_pattern.strip('\"')}'" in packages_content:
                found_bad_packages.append(pkg_name)
        
        if found_bad_packages:
            print_error("Found PostgreSQL SERVER packages (should only have client):")
            for pkg in found_bad_packages:
                print_error(f"  - {pkg}")
            print_info("Remove server packages, keep only postgresql-client and libpq-dev")
            return False
        
        # Check for PostgreSQL client packages (should be present)
        good_packages = [
            ('postgresql-client', 'postgresql-client'),
            ('libpq', 'libpq-dev or libpq5')
        ]
        found_good_packages = []
        
        for pkg_pattern, pkg_name in good_packages:
            if pkg_pattern in packages_content:
                found_good_packages.append(pkg_name)
        
        if found_good_packages:
            print_success("PostgreSQL client libraries found ✓")
            for pkg in found_good_packages:
                print_success(f"  - {pkg}")
        else:
            print_warning("No PostgreSQL client libraries found")
            print_info("Consider adding postgresql-client and libpq-dev")
        
        if not found_bad_packages:
            print_success("No PostgreSQL server packages found ✓")
        
        return True
        
    except Exception as e:
        print_error(f"Error reading nixpacks.toml: {e}")
        return False


def check_docker_compose_files():
    """Check for docker-compose files that shouldn't be deployed"""
    print_header("Checking for Docker Compose Files")
    
    docker_compose_files = list(Path(".").glob("docker-compose*.yml")) + \
                          list(Path(".").glob("docker-compose*.yaml"))
    
    if not docker_compose_files:
        print_success("No docker-compose files found in root directory ✓")
        return True
    
    print_warning(f"Found {len(docker_compose_files)} docker-compose file(s):")
    for file in docker_compose_files:
        print_info(f"  - {file}")
    
    print_info("\nThese files should:")
    print_info("  1. Be excluded in .railwayignore")
    print_info("  2. Have '.local' in filename (e.g., docker-compose.local.yml)")
    print_info("  3. Include warnings that they are for LOCAL DEV ONLY")
    
    # Check if they're properly named as local
    local_files = [f for f in docker_compose_files if '.local' in str(f)]
    if local_files:
        print_success(f"{len(local_files)} file(s) properly named with '.local'")
    
    return len(local_files) == len(docker_compose_files)


def validate_environment_variables():
    """Check environment variables for Railway"""
    print_header("Checking Environment Variables")
    
    database_url = os.environ.get('DATABASE_URL')
    database_private_url = os.environ.get('DATABASE_PRIVATE_URL')
    
    if database_url:
        print_success("DATABASE_URL is set")
        if database_url.startswith('postgresql://'):
            print_success("DATABASE_URL uses PostgreSQL protocol ✓")
        else:
            print_warning(f"DATABASE_URL has unexpected protocol: {database_url.split('://')[0]}")
    else:
        print_info("DATABASE_URL not set (Railway will inject it at runtime)")
    
    if database_private_url:
        print_success("DATABASE_PRIVATE_URL is set (internal network) ✓")
        print_info("Using private URL saves on egress costs")
    else:
        print_info("DATABASE_PRIVATE_URL not set (will be available on Railway)")
    
    return True


def print_summary(results):
    """Print validation summary"""
    print_header("Validation Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nPassed: {passed}/{total} checks\n")
    
    for check, result in results.items():
        if result:
            print_success(check)
        else:
            print_error(check)
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All checks passed! Your configuration is correct.{Colors.END}\n")
        print_info("Deploy to Railway with confidence!")
        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  Some checks failed. Review the issues above.{Colors.END}\n")
        print_info("See RAILWAY_POSTGRES_ROOT_ERROR_FIX.md for detailed fixes")
        return False


def main():
    """Main validation function"""
    print(f"{Colors.BOLD}Railway PostgreSQL Configuration Validator{Colors.END}")
    print("Checking for common misconfigurations that cause 'root execution' errors...\n")
    
    results = {
        'railway.json configuration': validate_railway_json(),
        '.railwayignore file': validate_railwayignore(),
        'nixpacks.toml configuration': validate_nixpacks_toml(),
        'Docker Compose files': check_docker_compose_files(),
        'Environment variables': validate_environment_variables()
    }
    
    success = print_summary(results)
    
    if not success:
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}📖 Next Steps:{Colors.END}\n")
        print("1. Fix the issues identified above")
        print("2. Run this script again to verify")
        print("3. Read RAILWAY_POSTGRES_ROOT_ERROR_FIX.md for detailed guidance")
        print("4. Ensure Railway is using MANAGED PostgreSQL database, not containers")
        print("=" * 70 + "\n")
        sys.exit(1)
    else:
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}✅ Configuration Validated!{Colors.END}\n")
        print("Your Railway configuration is correct. If you're still seeing errors:")
        print("\n1. Check Railway Dashboard for managed PostgreSQL database")
        print("2. Verify DATABASE_URL is injected into your backend service")
        print("3. Ensure you're NOT deploying PostgreSQL as a container")
        print("4. Read RAILWAY_POSTGRES_ROOT_ERROR_FIX.md for Railway-specific setup")
        print("=" * 70 + "\n")
        sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Validation cancelled by user{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        sys.exit(1)

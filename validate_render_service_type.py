#!/usr/bin/env python3
"""
Render Service Type Validator
=============================

This script validates that the render.yaml configuration file has the correct
service type and runtime settings for the HireMeBahamas backend.

Usage:
    python validate_render_service_type.py
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple


def validate_render_config(config_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate the render.yaml configuration.
    
    Args:
        config_path: Path to the render.yaml file
        
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    # Check if file exists
    if not config_path.exists():
        errors.append(f"❌ Configuration file not found: {config_path}")
        return False, errors
    
    # Parse YAML
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"❌ Invalid YAML syntax: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"❌ Error reading file: {e}")
        return False, errors
    
    # Check services key exists
    if 'services' not in config:
        errors.append("❌ Missing 'services' key in render.yaml")
        return False, errors
    
    services = config['services']
    if not isinstance(services, list) or len(services) == 0:
        errors.append("❌ 'services' must be a non-empty list")
        return False, errors
    
    # Validate each service
    for idx, service in enumerate(services):
        service_name = service.get('name', f'service-{idx}')
        
        # Check type
        service_type = service.get('type')
        if service_type != 'web':
            errors.append(
                f"❌ Service '{service_name}': type must be 'web', got '{service_type}'\n"
                f"   → In Render Dashboard, this service MUST be created as 'Web Service'"
            )
        
        # Check runtime
        runtime = service.get('runtime')
        if runtime != 'python':
            errors.append(
                f"❌ Service '{service_name}': runtime must be 'python', got '{runtime}'\n"
                f"   → In Render Dashboard, runtime MUST be 'Python'"
            )
        
        # Check other important settings
        if 'name' not in service:
            errors.append(f"⚠️  Service {idx}: Missing 'name' field (recommended)")
        
        if 'region' not in service:
            errors.append(f"⚠️  Service '{service_name}': Missing 'region' field (recommended)")
        
        # Check start command for web services
        if service_type == 'web' and 'startCommand' not in service:
            errors.append(f"⚠️  Service '{service_name}': Missing 'startCommand' (recommended)")
    
    return len(errors) == 0, errors


def print_success_message():
    """Print success message with instructions."""
    print("\n" + "="*80)
    print("✅ RENDER CONFIGURATION VALID")
    print("="*80)
    print("\nYour render.yaml is correctly configured with:")
    print("  ✅ type: web")
    print("  ✅ runtime: python")
    print("\n📋 NEXT STEPS:")
    print("\n1. Verify in Render Dashboard:")
    print("   - Go to: https://dashboard.render.com")
    print("   - Find your backend service")
    print("   - Confirm it shows: 'Type: Web Service' and 'Runtime: Python'")
    print("\n2. If service type is wrong in Dashboard:")
    print("   - You CANNOT change the type after creation")
    print("   - You must DELETE the service and create a NEW 'Web Service'")
    print("   - See: RENDER_SERVICE_TYPE_VERIFICATION.md for instructions")
    print("\n3. Environment Variables:")
    print("   - Set DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY in Render Dashboard")
    print("   - See render.yaml for full list of required variables")
    print("\n4. Deploy:")
    print("   - Push to GitHub main branch")
    print("   - Render will auto-deploy")
    print("   - Check logs for: 'Application startup complete'")
    print("="*80 + "\n")


def print_error_summary(errors: List[str]):
    """Print error summary."""
    print("\n" + "="*80)
    print("❌ RENDER CONFIGURATION ERRORS FOUND")
    print("="*80)
    print("\nThe following issues were found in your render.yaml:\n")
    for error in errors:
        print(error)
    print("\n📖 For help fixing these issues, see:")
    print("   - RENDER_SERVICE_TYPE_VERIFICATION.md")
    print("   - CORRECT_STACK.md")
    print("="*80 + "\n")


def main():
    """Main entry point."""
    print("\n🔍 Validating Render Service Type Configuration...\n")
    
    # Get the repository root
    repo_root = Path(__file__).parent
    
    # Check root render.yaml
    root_config = repo_root / "render.yaml"
    print(f"Checking: {root_config}")
    
    is_valid, errors = validate_render_config(root_config)
    
    # Also check api/render.yaml if it exists
    api_config = repo_root / "api" / "render.yaml"
    if api_config.exists():
        print(f"Checking: {api_config}")
        api_valid, api_errors = validate_render_config(api_config)
        if not api_valid:
            print("\n⚠️  Note: api/render.yaml is marked as deprecated.")
            print("   You should use the root render.yaml instead.")
            # Don't fail on api/render.yaml errors since it's deprecated
    
    # Print results
    if is_valid:
        print_success_message()
        return 0
    else:
        print_error_summary(errors)
        return 1


if __name__ == "__main__":
    sys.exit(main())

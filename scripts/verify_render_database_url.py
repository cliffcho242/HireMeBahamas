#!/usr/bin/env python3
"""
Verify Render DATABASE_URL Environment Variable

This script validates that a DATABASE_URL meets all requirements:
1. No quotes
2. No spaces
3. Real domain (not placeholder "host")
4. Includes sslmode=require

Usage:
    python scripts/verify_render_database_url.py
    
    Or test a specific URL:
    python scripts/verify_render_database_url.py "postgresql://user:pass@host:5432/db?sslmode=require"
"""

import sys
import os
from urllib.parse import urlparse


def validate_database_url(url: str) -> tuple[bool, list[str]]:
    """
    Validate DATABASE_URL against all requirements.
    
    Args:
        url: The DATABASE_URL to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check 1: No quotes
    if '"' in url or "'" in url:
        errors.append("❌ FAILED: DATABASE_URL contains quotes (remove all \" and ' characters)")
    
    # Check 2: No spaces
    if ' ' in url:
        errors.append("❌ FAILED: DATABASE_URL contains spaces (spaces are not allowed)")
    
    # Check 3: Must start with postgresql://
    if not url.startswith('postgresql://'):
        if url.startswith('postgres://'):
            errors.append("❌ FAILED: Use 'postgresql://' not 'postgres://' (add 'ql' to postgres)")
        else:
            errors.append("❌ FAILED: DATABASE_URL must start with 'postgresql://'")
    
    # Check 4: Parse URL to validate format
    try:
        parsed = urlparse(url)
        
        # Check hostname is not a placeholder
        hostname = parsed.hostname
        if hostname:
            # Common placeholder values
            placeholders = ['host', 'localhost', 'example.com', 'your-host', 'YOUR-HOST', 
                          'your_host', 'hostname', 'HOSTNAME']
            if hostname.lower() in [p.lower() for p in placeholders]:
                errors.append(f"❌ FAILED: Hostname '{hostname}' is a placeholder (use your actual database hostname)")
        else:
            errors.append("❌ FAILED: DATABASE_URL has no hostname")
        
        # Check port is valid
        if parsed.port:
            if not (1 <= parsed.port <= 65535):
                errors.append(f"❌ FAILED: Invalid port number {parsed.port}")
        
        # Check has database name
        if not parsed.path or parsed.path == '/':
            errors.append("❌ FAILED: DATABASE_URL missing database name")
            
    except Exception as e:
        errors.append(f"❌ FAILED: Invalid URL format - {str(e)}")
    
    # Check 5: Must include sslmode=require
    if 'sslmode=require' not in url:
        errors.append("❌ FAILED: DATABASE_URL must include '?sslmode=require' at the end")
    
    # Check 6: Validate it looks like a real database domain
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if hostname:
            # Should have at least one dot (domain.tld)
            if '.' not in hostname:
                errors.append(f"❌ FAILED: Hostname '{hostname}' doesn't look like a valid domain (missing TLD)")
            
            # Common database provider patterns
            known_providers = [
                'neon.tech',
                'railway.app', 
                'railway.internal',
                'render.com',
                'supabase.co',
                'aws.amazon.com',
                'postgres.database.azure.com'
            ]
            
            is_known_provider = any(provider in hostname for provider in known_providers)
            
            # If not a known provider, just warn (not an error)
            if not is_known_provider and hostname not in ['localhost', '127.0.0.1']:
                print(f"⚠️  WARNING: Hostname '{hostname}' is not a recognized database provider")
                print(f"   This may be fine if you're using a custom database host")
    except:
        pass  # Already caught parsing errors above
    
    return len(errors) == 0, errors


def print_success():
    """Print success message."""
    print("\n" + "="*70)
    print("🎉 SUCCESS! Your DATABASE_URL is valid!")
    print("="*70)
    print("\n✅ All checks passed:")
    print("   • No quotes found")
    print("   • No spaces found")
    print("   • Real domain detected")
    print("   • sslmode=require present")
    print("   • Valid URL format")
    print("\n✅ You can use this DATABASE_URL in Render Environment variables")
    print("\nNext steps:")
    print("1. Go to Render Dashboard → Your Web Service → Environment")
    print("2. Set DATABASE_URL to this value (without quotes)")
    print("3. Save and wait for automatic redeploy")
    print("4. Check logs for successful database connection")
    print()


def print_failure(errors: list[str]):
    """Print failure message with errors."""
    print("\n" + "="*70)
    print("❌ VALIDATION FAILED - Please fix the following issues:")
    print("="*70)
    print()
    for error in errors:
        print(error)
    print("\n" + "="*70)
    print("📖 See RENDER_DATABASE_URL_VERIFICATION.md for detailed help")
    print("="*70)
    print()


def get_example_url(original_url: str = None) -> str:
    """Generate an example corrected URL."""
    if original_url:
        # Try to fix common issues
        url = original_url.strip()
        url = url.strip('"').strip("'")  # Remove quotes
        url = url.replace(' ', '')  # Remove spaces
        
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        
        if 'sslmode=require' not in url:
            if '?' in url:
                url += '&sslmode=require'
            else:
                url += '?sslmode=require'
        
        return url
    
    return "postgresql://user:password@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"


def main():
    """Main function."""
    print("\n" + "="*70)
    print("🔍 Render DATABASE_URL Verification Tool")
    print("="*70)
    print()
    
    # Get DATABASE_URL from command line or environment
    database_url = None
    
    if len(sys.argv) > 1:
        database_url = sys.argv[1]
        print(f"Testing provided DATABASE_URL...")
    else:
        # Try to get from environment
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            print(f"Testing DATABASE_URL from environment...")
        else:
            print("❌ No DATABASE_URL provided!")
            print("\nUsage:")
            print('  python scripts/verify_render_database_url.py "postgresql://..."')
            print("\nOr set DATABASE_URL environment variable:")
            print('  export DATABASE_URL="postgresql://..."')
            print('  python scripts/verify_render_database_url.py')
            print("\nExample valid DATABASE_URL:")
            print('  postgresql://user:pass@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require')
            sys.exit(1)
    
    print()
    
    # Validate
    is_valid, errors = validate_database_url(database_url)
    
    if is_valid:
        print_success()
        sys.exit(0)
    else:
        print_failure(errors)
        
        # Try to provide a corrected example
        print("\n💡 Suggested fix:")
        corrected = get_example_url(database_url)
        print(f"   {corrected}")
        print("\n⚠️  Note: Replace with your actual database credentials!")
        print()
        
        sys.exit(1)


if __name__ == '__main__':
    main()

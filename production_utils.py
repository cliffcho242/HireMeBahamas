#!/usr/bin/env python3
"""
Production utility functions for HireMeBahamas.

Provides helper functions to detect production environment and
prevent accidental insertion of test/sample data in production.
"""

import os
import sys


def is_production():
    """
    Check if the application is running in production environment.

    Returns:
        bool: True if in production, False otherwise

    Checks the following environment variables:
    - PRODUCTION (set to 'true', '1', 'yes' for production)
    - FLASK_ENV (checks if set to 'production')
    - ENVIRONMENT (checks if set to 'production')
    - DATABASE_URL (checks if contains 'postgresql' and not 'localhost')
    """
    # Check explicit production flag
    production = os.environ.get("PRODUCTION", "").lower()
    if production in ("true", "1", "yes"):
        return True

    # Check Flask environment
    flask_env = os.environ.get("FLASK_ENV", "").lower()
    if flask_env == "production":
        return True

    # Check general environment variable
    environment = os.environ.get("ENVIRONMENT", "").lower()
    if environment == "production":
        return True

    # Check if using remote PostgreSQL (likely production)
    db_url = os.environ.get("DATABASE_URL", "")
    if "postgresql" in db_url and "localhost" not in db_url:
        return True

    return False


def is_development():
    """
    Check if the application is running in development environment.

    Returns:
        bool: True if in development, False otherwise
    """
    return not is_production()


def confirm_sample_data_insertion():
    """
    Prompt user to confirm insertion of sample/test data.
    Should be called before inserting any sample data.

    Returns:
        bool: True if user confirms, False otherwise
    """
    if is_production():
        print("⚠️  WARNING: You are running in PRODUCTION mode!")
        print("⚠️  Inserting sample/test data in production is NOT recommended.")
        print()
        response = input("Are you ABSOLUTELY SURE you want to continue? (yes/no): ")
        return response.lower() == "yes"

    print("ℹ️  Running in DEVELOPMENT mode")
    print("   Sample/test data will be inserted...")
    return True


def check_dev_flag(args=None):
    """
    Check if --dev or --development flag is present in command line arguments.

    Args:
        args: Optional list of arguments. If None, uses sys.argv

    Returns:
        bool: True if --dev or --development flag is present
    """
    if args is None:
        args = sys.argv

    return "--dev" in args or "--development" in args


def print_environment_info():
    """Print information about the current environment"""
    print("=" * 60)
    print("ENVIRONMENT INFORMATION")
    print("=" * 60)
    print(f"Production mode:  {is_production()}")
    print(f"Development mode: {is_development()}")
    print(f"PRODUCTION env:   {os.environ.get('PRODUCTION', 'not set')}")
    print(f"FLASK_ENV:        {os.environ.get('FLASK_ENV', 'not set')}")
    print(f"ENVIRONMENT:      {os.environ.get('ENVIRONMENT', 'not set')}")
    print(f"DATABASE_URL:     {os.environ.get('DATABASE_URL', 'not set')[:50]}...")
    print("=" * 60)
    print()

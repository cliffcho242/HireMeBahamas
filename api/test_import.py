"""
Simple test function to verify Vercel can install and import fastapi.
This helps diagnose if the issue is with dependency installation or with the main handler.
"""

def handler(event, context):
    """
    Minimal Vercel serverless function to test fastapi import.
    
    Access this endpoint at: /api/test_import
    
    Returns:
        dict: Status of fastapi import and available modules
    """
    import sys
    import os
    
    result = {
        "status": "ok",
        "python_version": sys.version,
        "python_path": sys.path[:5],  # First 5 entries
        "working_directory": os.getcwd(),
        "environment": os.getenv("VERCEL_ENV", "unknown"),
    }
    
    # Test fastapi import
    try:
        import fastapi
        result["fastapi"] = {
            "status": "✓ INSTALLED",
            "version": fastapi.__version__,
            "location": fastapi.__file__,
        }
    except ImportError as e:
        result["fastapi"] = {
            "status": "✗ NOT FOUND",
            "error": str(e),
        }
    
    # Test mangum import
    try:
        import mangum
        result["mangum"] = {
            "status": "✓ INSTALLED",
            "version": mangum.__version__ if hasattr(mangum, "__version__") else "unknown",
        }
    except ImportError as e:
        result["mangum"] = {
            "status": "✗ NOT FOUND",
            "error": str(e),
        }
    
    # Test pydantic import
    try:
        import pydantic
        result["pydantic"] = {
            "status": "✓ INSTALLED",
            "version": pydantic.__version__,
        }
    except ImportError as e:
        result["pydantic"] = {
            "status": "✗ NOT FOUND",
            "error": str(e),
        }
    
    # List installed packages
    try:
        import pkg_resources
        installed = [f"{pkg.key}=={pkg.version}" for pkg in pkg_resources.working_set]
        result["installed_packages_count"] = len(installed)
        result["sample_packages"] = installed[:10]  # First 10 packages
    except Exception as e:
        result["installed_packages_error"] = str(e)
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": str(result),
    }

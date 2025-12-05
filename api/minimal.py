"""
Minimal Python function to verify Vercel can execute Python serverless functions.
No external dependencies - uses only Python standard library.
"""
import json
import sys
import os


def handler(event, context):
    """
    Minimal Vercel serverless function with zero external dependencies.
    
    This function uses only Python standard library to verify:
    1. Vercel can execute Python functions
    2. Python version is correct
    3. Basic runtime environment is working
    
    Access at: /api/minimal
    """
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps({
            "message": "✓ Vercel Python runtime is working!",
            "python_version": sys.version,
            "python_version_info": {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro,
            },
            "platform": sys.platform,
            "executable": sys.executable,
            "working_directory": os.getcwd(),
            "environment_vars": {
                "VERCEL": os.getenv("VERCEL", "not set"),
                "VERCEL_ENV": os.getenv("VERCEL_ENV", "not set"),
                "VERCEL_REGION": os.getenv("VERCEL_REGION", "not set"),
            },
            "sys_path_count": len(sys.path),
            "note": "If you can see this, Vercel Python runtime is working. Now check /api/test_import to verify dependencies.",
        }),
    }

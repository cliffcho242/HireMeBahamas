#!/usr/bin/env python3
"""
Validation script to ensure requirements.txt contains all critical dependencies.

This script verifies that the root requirements.txt file contains:
1. Basic FastAPI dependencies: fastapi, uvicorn, python-multipart
2. JWT/Auth dependencies: python-jose, passlib[bcrypt]
3. Database dependencies: sqlalchemy, psycopg2-binary

Exit code 0 on success, 1 on failure.
"""
import sys
import re
from pathlib import Path


def validate_requirements():
    """Validate that requirements.txt contains all critical dependencies."""
    
    # Define required dependencies
    required_deps = {
        'Basic': ['fastapi', 'uvicorn', 'python-multipart'],
        'Auth': ['python-jose', 'passlib'],
        'Database': ['sqlalchemy', 'psycopg2-binary']
    }
    
    # Read requirements.txt
    req_file = Path(__file__).parent / 'requirements.txt'
    if not req_file.exists():
        print(f"❌ ERROR: requirements.txt not found at {req_file}")
        return False
    
    content = req_file.read_text()
    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
    
    print("=" * 70)
    print("REQUIREMENTS.TXT VALIDATION")
    print("=" * 70)
    
    all_valid = True
    
    for category, deps in required_deps.items():
        print(f"\n{category} Dependencies:")
        print("-" * 70)
        
        for dep in deps:
            # Create regex pattern to match dependency (handles extras like [bcrypt])
            pattern = re.compile(f'^{re.escape(dep)}[\\[\\w,\\]]*==', re.IGNORECASE)
            found = False
            matched_line = None
            
            for line in lines:
                if pattern.match(line):
                    found = True
                    matched_line = line
                    break
            
            if found:
                print(f"  ✅ {matched_line}")
            else:
                print(f"  ❌ MISSING: {dep}")
                all_valid = False
    
    print("\n" + "=" * 70)
    
    # Special check for FastAPI being explicitly listed (not commented)
    fastapi_pattern = re.compile(r'^fastapi==[\d.]+$', re.IGNORECASE)
    fastapi_found = any(fastapi_pattern.match(line) for line in lines)
    
    if fastapi_found:
        print("✅ FastAPI is EXPLICITLY listed (not commented)")
    else:
        print("❌ ERROR: FastAPI is NOT explicitly listed or is commented out")
        all_valid = False
    
    print("=" * 70)
    
    if all_valid:
        print("\n✅ SUCCESS: All required dependencies are present!")
        return True
    else:
        print("\n❌ FAILURE: Some required dependencies are missing!")
        return False


if __name__ == '__main__':
    success = validate_requirements()
    sys.exit(0 if success else 1)

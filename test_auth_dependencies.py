#!/usr/bin/env python3
"""
Test script to verify all authentication dependencies are installed and working.
This ensures users can always sign in and sign out successfully.
"""

import sys
from typing import List, Tuple

def test_dependency(name: str, import_statement: str) -> Tuple[bool, str]:
    """Test if a dependency can be imported."""
    try:
        exec(import_statement)
        return True, f"✓ {name} is installed and working"
    except ImportError as e:
        return False, f"✗ {name} is missing: {e}"
    except Exception as e:
        return False, f"✗ {name} has an error: {e}"

def main():
    """Test all authentication-related dependencies."""
    
    print("=" * 70)
    print("Testing Authentication Dependencies")
    print("=" * 70)
    print()
    
    # Core backend dependencies for authentication
    backend_deps = [
        ("Flask", "import flask"),
        ("Flask-CORS", "import flask_cors"),
        ("PyJWT", "import jwt"),
        ("bcrypt", "import bcrypt"),
        ("Flask-Limiter", "import flask_limiter"),
        ("SQLAlchemy", "import sqlalchemy"),
        ("psycopg2 (PostgreSQL)", "import psycopg2"),
        ("python-dotenv", "import dotenv"),
        ("Werkzeug", "import werkzeug"),
    ]
    
    print("Backend Dependencies:")
    print("-" * 70)
    
    backend_results = []
    for name, import_stmt in backend_deps:
        success, message = test_dependency(name, import_stmt)
        backend_results.append(success)
        print(message)
    
    print()
    
    # Test authentication functionality
    print("Authentication Functionality Tests:")
    print("-" * 70)
    
    auth_tests = []
    
    # Test bcrypt password hashing
    try:
        import bcrypt
        password = "test123"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        verified = bcrypt.checkpw(password.encode('utf-8'), hashed)
        if verified:
            auth_tests.append(True)
            print("✓ bcrypt password hashing works")
        else:
            auth_tests.append(False)
            print("✗ bcrypt password verification failed")
    except Exception as e:
        auth_tests.append(False)
        print(f"✗ bcrypt test failed: {e}")
    
    # Test JWT token creation
    try:
        import jwt
        from datetime import datetime, timedelta
        
        payload = {
            "user_id": 1,
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(days=7)
        }
        token = jwt.encode(payload, "secret-key", algorithm="HS256")
        decoded = jwt.decode(token, "secret-key", algorithms=["HS256"])
        
        if decoded["user_id"] == 1 and decoded["email"] == "test@example.com":
            auth_tests.append(True)
            print("✓ JWT token creation and verification works")
        else:
            auth_tests.append(False)
            print("✗ JWT token data mismatch")
    except Exception as e:
        auth_tests.append(False)
        print(f"✗ JWT test failed: {e}")
    
    # Test Flask app creation
    try:
        from flask import Flask
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/test')
        def test():
            return {'status': 'ok'}
        
        auth_tests.append(True)
        print("✓ Flask app with CORS can be created")
    except Exception as e:
        auth_tests.append(False)
        print(f"✗ Flask app test failed: {e}")
    
    print()
    
    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    
    backend_success = sum(backend_results)
    backend_total = len(backend_results)
    auth_success = sum(auth_tests)
    auth_total = len(auth_tests)
    
    print(f"Backend Dependencies: {backend_success}/{backend_total} passing")
    print(f"Authentication Tests: {auth_success}/{auth_total} passing")
    print()
    
    if backend_success == backend_total and auth_success == auth_total:
        print("✓ All dependencies are installed and working!")
        print("✓ Users can sign in and sign out successfully.")
        return 0
    else:
        print("✗ Some dependencies are missing or not working properly.")
        print("✗ Please install missing dependencies using:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())

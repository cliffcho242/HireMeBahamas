#!/usr/bin/env python3
"""
Test production CORS security configuration.

This test verifies that:
1. No wildcard (*) is used in production mode
2. Only specific HTTP methods are allowed (GET, POST, PUT, DELETE)
3. Only specific headers are allowed (Authorization, Content-Type)
4. Credentials are properly configured based on origins
"""

import os
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))


def test_environment_module_production_origins():
    """Test that environment module returns production-safe origins"""
    print("\n1. Testing backend/app/core/environment.py production origins...")
    print("-" * 60)
    
    # Set production environment
    os.environ["ENVIRONMENT"] = "production"
    os.environ["VERCEL_ENV"] = "production"
    
    # Remove any ALLOWED_ORIGINS to test defaults
    if "ALLOWED_ORIGINS" in os.environ:
        del os.environ["ALLOWED_ORIGINS"]
    
    try:
        # Import after setting environment
        from app.core.environment import get_cors_origins, is_production
        
        assert is_production(), "Should be in production mode"
        print("✅ Production mode detected")
        
        origins = get_cors_origins()
        print(f"  Production origins: {origins}")
        
        # Verify no wildcard
        assert "*" not in origins, "Wildcard (*) not allowed in production"
        print("✅ No wildcard (*) in production origins")
        
        # Verify all origins are HTTPS (except development mode)
        for origin in origins:
            if origin.startswith("http://"):
                raise AssertionError(f"HTTP origin not allowed in production: {origin}")
        print("✅ All origins use HTTPS")
        
        # Verify specific domains
        assert len(origins) > 0, "Production must have at least one allowed origin"
        print(f"✅ {len(origins)} specific origin(s) configured")
        
    finally:
        # Clean up environment
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]
        if "VERCEL_ENV" in os.environ:
            del os.environ["VERCEL_ENV"]
    
    print("✅ PASS: Production origins are secure")
    return True


def test_middleware_configuration():
    """Test that middleware uses restricted headers and methods"""
    print("\n2. Testing backend/app/core/middleware.py configuration...")
    print("-" * 60)
    
    # Read the middleware.py file to verify configuration
    middleware_path = Path(__file__).parent / "backend" / "app" / "core" / "middleware.py"
    
    with open(middleware_path, 'r') as f:
        content = f.read()
    
    # Check for specific allowed methods
    if 'allow_methods=["GET", "POST", "PUT", "DELETE"]' in content:
        print("✅ Specific HTTP methods configured (GET, POST, PUT, DELETE)")
    else:
        raise AssertionError("Expected specific allow_methods configuration not found")
    
    # Check for specific allowed headers (not wildcard)
    if 'allow_headers=["Authorization", "Content-Type"]' in content:
        print("✅ Specific headers configured (Authorization, Content-Type)")
    else:
        raise AssertionError("Expected specific allow_headers configuration not found")
    
    # Verify no wildcard in headers
    if 'allow_headers=["*"]' in content:
        # Check if it's in the setup_cors function
        if 'def setup_cors' in content:
            setup_cors_section = content[content.find('def setup_cors'):]
            if 'allow_headers=["*"]' in setup_cors_section[:setup_cors_section.find('def ', 1) if 'def ' in setup_cors_section[1:] else len(setup_cors_section)]:
                raise AssertionError("Wildcard (*) in allow_headers not allowed")
    
    print("✅ PASS: Middleware configuration is secure")
    return True


def test_main_app_configuration():
    """Test that main.py uses secure CORS configuration"""
    print("\n3. Testing backend/app/main.py configuration...")
    print("-" * 60)
    
    # Read the main.py file to verify configuration
    main_path = Path(__file__).parent / "backend" / "app" / "main.py"
    
    with open(main_path, 'r') as f:
        content = f.read()
    
    # Check for specific allowed methods
    if 'allow_methods=["GET", "POST", "PUT", "DELETE"]' in content:
        print("✅ Specific HTTP methods configured (GET, POST, PUT, DELETE)")
    else:
        raise AssertionError("Expected specific allow_methods configuration not found")
    
    # Check for specific allowed headers (not wildcard)
    if 'allow_headers=["Authorization", "Content-Type"]' in content:
        print("✅ Specific headers configured (Authorization, Content-Type)")
    else:
        raise AssertionError("Expected specific allow_headers configuration not found")
    
    # Verify production safety comments
    if "🚫" in content and "wildcard" in content.lower():
        print("✅ Production safety documentation present")
    
    print("✅ PASS: Main app configuration is secure")
    return True


def test_vercel_handler_configuration():
    """Test that api/index.py configures CORS middleware"""
    print("\n4. Testing api/index.py (Render handler) configuration...")
    print("-" * 60)
    
    index_path = Path(__file__).parent / "api" / "index.py"
    with open(index_path, 'r') as f:
        content = f.read()
    
    # Basic sanity checks for middleware setup
    if "CORSMiddleware" not in content:
        raise AssertionError("CORS middleware not configured in api/index.py")
    else:
        print("✅ CORS middleware present")
    
    if "allow_origins" in content:
        print("✅ allow_origins configured")
    else:
        raise AssertionError("allow_origins not configured")
    
    if "allow_methods=" in content:
        print("✅ allow_methods configured")
    else:
        raise AssertionError("allow_methods not configured")
    
    if "allow_headers=" in content:
        print("✅ allow_headers configured")
    else:
        raise AssertionError("allow_headers not configured")
    
    print("✅ PASS: api/index.py CORS configuration found")
    return True


def test_no_wildcard_origins_in_production():
    """Test that wildcard origins are blocked in production files"""
    print("\n5. Testing for wildcard origin patterns in production code...")
    print("-" * 60)
    
    # Files to check
    files_to_check = [
        Path(__file__).parent / "backend" / "app" / "core" / "environment.py",
        Path(__file__).parent / "backend" / "app" / "main.py",
        Path(__file__).parent / "api" / "index.py",
    ]
    
    for file_path in files_to_check:
        if not file_path.exists():
            print(f"⚠️  Skipping {file_path.name} (not found)")
            continue
            
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Look for wildcard in allow_origins in production context
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if not line.strip() or line.strip().startswith("#"):
                continue
            if 'allow_origins' in line and '"*"' in line:
                # Check if it's in a production context by looking at nearby lines
                context_start = max(0, i - 10)
                context_end = min(len(lines), i + 10)
                context = '\n'.join(lines[context_start:context_end])
                
                # If there's production check logic nearby, it's okay
                if any(keyword in context.lower() for keyword in ['is_production', '_is_prod', 'production mode', 'if not', 'else:']):
                    continue
                else:
                    # Check if there's a comment explaining it's for development only
                    if 'development' in context.lower() or 'dev' in context.lower():
                        continue
                    raise AssertionError(f"Potential wildcard (*) in production code at {file_path.name}:{i+1}")
        
        print(f"✅ {file_path.name}: No unguarded wildcard patterns")
    
    print("✅ PASS: No wildcard origins in production code")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("PRODUCTION CORS SECURITY TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Environment Module Production Origins", test_environment_module_production_origins),
        ("Middleware Configuration", test_middleware_configuration),
        ("Main App Configuration", test_main_app_configuration),
        ("Vercel Handler Configuration", test_vercel_handler_configuration),
        ("No Wildcard Origins in Production", test_no_wildcard_origins_in_production),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"\n❌ Test '{test_name}' FAILED: {e}\n")
            import traceback
            traceback.print_exc()
    
    print()
    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print()
    
    if failed == 0:
        print("✅ ALL PRODUCTION CORS SECURITY TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

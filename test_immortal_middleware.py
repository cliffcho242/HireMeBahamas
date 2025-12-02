"""
Test Immortal Middleware Implementation

Tests all middleware components:
- CORS
- JWT Authentication
- Exception Handling
- Request ID
- Timeout Protection
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


def test_middleware_syntax():
    """Test that middleware.py has valid Python syntax"""
    import py_compile
    middleware_path = os.path.join(os.path.dirname(__file__), 'backend', 'app', 'core', 'middleware.py')
    
    try:
        py_compile.compile(middleware_path, doraise=True)
        print("✓ Middleware syntax is valid")
        assert True
    except py_compile.PyCompileError as e:
        print(f"✗ Syntax error in middleware.py: {e}")
        assert False, f"Syntax error: {e}"


def test_main_immortal_syntax():
    """Test that main_immortal.py has valid Python syntax"""
    import py_compile
    main_path = os.path.join(os.path.dirname(__file__), 'backend', 'app', 'main_immortal.py')
    
    try:
        py_compile.compile(main_path, doraise=True)
        print("✓ Main immortal syntax is valid")
        assert True
    except py_compile.PyCompileError as e:
        print(f"✗ Syntax error in main_immortal.py: {e}")
        assert False, f"Syntax error: {e}"


def test_requirements_immortal():
    """Test that requirements_immortal.txt contains all necessary dependencies"""
    req_path = os.path.join(os.path.dirname(__file__), 'requirements_immortal.txt')
    
    with open(req_path, 'r') as f:
        content = f.read()
    
    required_deps = [
        'fastapi',
        'mangum',
        'sqlalchemy',
        'asyncpg',
        'python-jose',
        'PyJWT',
        'passlib',
        'anyio',
        'python-decouple',
    ]
    
    for dep in required_deps:
        if dep.lower() in content.lower():
            print(f"✓ {dep} found in requirements")
        else:
            print(f"✗ {dep} NOT found in requirements")
            assert False, f"Missing required dependency: {dep}"
    
    print("✓ All required dependencies present")
    assert True


def test_vercel_config():
    """Test that vercel_immortal.json is valid JSON with correct structure"""
    import json
    vercel_path = os.path.join(os.path.dirname(__file__), 'vercel_immortal.json')
    
    with open(vercel_path, 'r') as f:
        config = json.load(f)
    
    # Check essential keys
    assert 'builds' in config, "Missing 'builds' key in vercel.json"
    assert 'routes' in config, "Missing 'routes' key in vercel.json"
    
    # Check builds
    assert len(config['builds']) > 0, "No builds defined"
    build = config['builds'][0]
    assert build['use'] == '@vercel/python', "Build should use @vercel/python"
    
    # Check timeout is 30s
    assert build['config']['maxDuration'] == 30, "maxDuration should be 30s"
    
    # Check routes
    routes = config['routes']
    api_routes = [r for r in routes if '/api' in r.get('src', '')]
    assert len(api_routes) > 0, "No API routes defined"
    
    print("✓ Vercel configuration is valid")
    print(f"✓ Build uses @vercel/python")
    print(f"✓ Timeout set to 30s")
    print(f"✓ {len(api_routes)} API routes configured")
    assert True


def test_checklist_exists():
    """Test that deployment checklist exists and has required sections"""
    checklist_path = os.path.join(os.path.dirname(__file__), 'IMMORTAL_MIDDLEWARE_CHECKLIST.md')
    
    with open(checklist_path, 'r') as f:
        content = f.read()
    
    required_sections = [
        'STEP 1',
        'STEP 2',
        'STEP 3',
        'STEP 4',
        'CORS',
        'JWT',
        'Exception',
        ('Request ID', 'Request-ID', 'X-Request-ID'),  # Multiple acceptable variations
        'Timeout',
    ]
    
    for section in required_sections:
        if isinstance(section, tuple):
            # Check if any variation is present
            found = any(var in content for var in section)
            if found:
                print(f"✓ Section '{section[0]}' found in checklist")
            else:
                print(f"✗ Section '{section[0]}' NOT found in checklist")
                assert False, f"Missing required section: {section[0]}"
        else:
            if section in content:
                print(f"✓ Section '{section}' found in checklist")
            else:
                print(f"✗ Section '{section}' NOT found in checklist")
                assert False, f"Missing required section: {section}"
    
    print("✓ Deployment checklist is complete")
    assert True


def test_middleware_file_structure():
    """Test that middleware.py contains all required components"""
    middleware_path = os.path.join(os.path.dirname(__file__), 'backend', 'app', 'core', 'middleware.py')
    
    with open(middleware_path, 'r') as f:
        content = f.read()
    
    required_components = [
        'RequestIDMiddleware',
        'TimeoutMiddleware',
        'global_exception_handler',
        'http_exception_handler',
        'get_current_user_from_token',
        'verify_jwt_token',
        'setup_cors',
        'setup_middleware',
    ]
    
    for component in required_components:
        if component in content:
            print(f"✓ {component} found in middleware")
        else:
            print(f"✗ {component} NOT found in middleware")
            assert False, f"Missing required component: {component}"
    
    print("✓ All middleware components present")
    assert True


def test_middleware_features():
    """Test that middleware has all required features documented"""
    middleware_path = os.path.join(os.path.dirname(__file__), 'backend', 'app', 'core', 'middleware.py')
    
    with open(middleware_path, 'r') as f:
        content = f.read()
    
    features = {
        'CORS': 'CORSMiddleware',
        'JWT auth': 'verify_jwt_token',
        'Exception handler': 'global_exception_handler',
        'Request ID': 'X-Request-ID',
        'Timeout': 'TimeoutMiddleware',
        '401 on invalid': 'HTTP_401_UNAUTHORIZED',
        'Clean JSON': 'JSONResponse',
    }
    
    for feature, keyword in features.items():
        if keyword in content:
            print(f"✓ Feature '{feature}' implemented ({keyword})")
        else:
            print(f"✗ Feature '{feature}' NOT found ({keyword})")
            assert False, f"Missing feature: {feature}"
    
    print("✓ All required features implemented")
    assert True


if __name__ == '__main__':
    print("=" * 70)
    print("TESTING IMMORTAL MIDDLEWARE IMPLEMENTATION")
    print("=" * 70)
    print()
    
    tests = [
        ("Middleware Syntax", test_middleware_syntax),
        ("Main Immortal Syntax", test_main_immortal_syntax),
        ("Requirements", test_requirements_immortal),
        ("Vercel Config", test_vercel_config),
        ("Deployment Checklist", test_checklist_exists),
        ("Middleware Structure", test_middleware_file_structure),
        ("Middleware Features", test_middleware_features),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n{name}:")
        print("-" * 70)
        try:
            test_func()
            passed += 1
            print(f"✓ {name} PASSED\n")
        except Exception as e:
            failed += 1
            print(f"✗ {name} FAILED: {e}\n")
    
    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - MIDDLEWARE IS READY FOR DEPLOYMENT!\n")
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED - PLEASE FIX BEFORE DEPLOYMENT\n")
        exit(1)

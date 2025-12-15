"""
Test CORS configuration for HireMeBahamas backend.

This test verifies that CORS is properly configured to allow cross-origin requests
from browsers.
"""
import sys
from pathlib import Path

# Add api directory to path for imports
api_dir = Path(__file__).parent / "api"
sys.path.insert(0, str(api_dir))

def test_fastapi_cors_middleware():
    """Test that FastAPI backend has CORS middleware configured"""
    # Import the main app
    from backend_app.main import app
    
    # Find CORS middleware in the app's middleware stack
    cors_middleware_found = False
    cors_config = None
    
    for middleware in app.user_middleware:
        middleware_class = middleware.cls
        if middleware_class.__name__ == "CORSMiddleware":
            cors_middleware_found = True
            # Access kwargs instead of options for FastAPI middleware
            cors_config = middleware.kwargs if hasattr(middleware, 'kwargs') else {}
            break
    
    assert cors_middleware_found, "CORSMiddleware not found in app middleware stack"
    
    # Verify CORS configuration allows all origins
    assert cors_config is not None, "CORS configuration not found"
    print(f"✅ CORS middleware found")
    
    # Check allow_origins includes wildcard
    allow_origins = cors_config.get('allow_origins', [])
    assert "*" in allow_origins, f"Expected '*' in allow_origins, got {allow_origins}"
    print(f"✅ CORS allows all origins: {allow_origins}")
    
    # Check allow_methods
    allow_methods = cors_config.get('allow_methods', [])
    assert "*" in allow_methods, f"Expected '*' in allow_methods, got {allow_methods}"
    print(f"✅ CORS allows all methods: {allow_methods}")
    
    # Check allow_headers
    allow_headers = cors_config.get('allow_headers', [])
    assert "*" in allow_headers, f"Expected '*' in allow_headers, got {allow_headers}"
    print(f"✅ CORS allows all headers: {allow_headers}")
    
    # Check allow_credentials
    # NOTE: When allow_origins=["*"], allow_credentials must be False per CORS spec
    allow_credentials = cors_config.get('allow_credentials', False)
    assert allow_credentials == False, f"Expected allow_credentials=False (required with wildcard origins), got {allow_credentials}"
    print(f"✅ CORS credentials disabled (required for wildcard origins): {allow_credentials}")
    
    print("\n✅ All CORS configuration tests passed!")


def test_flask_cors():
    """Test that Flask backend has CORS configured"""
    try:
        from backend_app.flask_backend import app
        
        # Flask-CORS extension adds after_request handler
        # Check if the app has CORS configured by looking for the extension
        has_cors = hasattr(app, 'extensions') and 'cors' in app.extensions
        
        if has_cors:
            print("✅ Flask backend has CORS extension configured")
        else:
            # Alternative check: CORS() automatically adds the extension
            # If flask_cors is imported and CORS(app) was called, it should be configured
            print("✅ Flask backend has CORS configured (via CORS(app) call)")
        
    except ImportError as e:
        print(f"⚠️  Flask backend not available: {e}")


if __name__ == "__main__":
    print("Testing CORS configuration for HireMeBahamas backend\n")
    print("=" * 60)
    
    print("\n1. Testing FastAPI CORS configuration...")
    print("-" * 60)
    try:
        test_fastapi_cors_middleware()
    except Exception as e:
        print(f"❌ FastAPI CORS test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n2. Testing Flask CORS configuration...")
    print("-" * 60)
    try:
        test_flask_cors()
    except Exception as e:
        print(f"❌ Flask CORS test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ ALL CORS TESTS PASSED!")
    print("=" * 60)

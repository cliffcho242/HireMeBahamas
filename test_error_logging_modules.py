"""
Test script to demonstrate and validate the central error handling and logging modules.

This script creates a minimal FastAPI application using the new error handling
and logging modules to ensure they work correctly.
"""
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from app.errors import register_error_handlers
from app.logging import setup_logging


def test_logging_setup():
    """Test that logging configuration works correctly."""
    print("Testing logging setup...")
    
    # Setup logging
    setup_logging()
    
    # Create a test logger and verify it works
    import logging
    test_logger = logging.getLogger("test")
    
    # Capture log output
    import io
    from contextlib import redirect_stderr
    
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.INFO)
    
    # Test logging
    test_logger.info("Test log message")
    
    # Verify log output
    log_output = log_capture.getvalue()
    assert "INFO" in log_output, "Log level not found in output"
    assert "test" in log_output, "Logger name not found in output"
    assert "Test log message" in log_output, "Log message not found in output"
    
    print("✅ Logging setup works correctly")
    print(f"   Sample output: {log_output.strip()}")


def test_error_handlers():
    """Test that error handlers work correctly."""
    print("\nTesting error handlers...")
    
    # Setup logging first
    setup_logging()
    
    # Create a minimal FastAPI app
    app = FastAPI()
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add a test endpoint that raises an exception
    @app.get("/test-error")
    async def test_error():
        raise ValueError("This is a test error")
    
    # Add a normal endpoint
    @app.get("/test-normal")
    async def test_normal():
        return {"status": "ok"}
    
    # Test the app (raise_server_exceptions=False allows testing error responses)
    client = TestClient(app, raise_server_exceptions=False)
    
    # Test normal endpoint
    response = client.get("/test-normal")
    assert response.status_code == 200, "Normal endpoint should return 200"
    assert response.json() == {"status": "ok"}, "Normal endpoint should return correct data"
    print("✅ Normal endpoint works correctly")
    
    # Test error endpoint
    response = client.get("/test-error")
    assert response.status_code == 500, "Error endpoint should return 500"
    response_data = response.json()
    assert "detail" in response_data, "Error response should contain 'detail'"
    assert response_data["detail"] == "Internal server error", "Error message should be generic"
    print("✅ Error handler works correctly")
    print(f"   Error response: {response_data}")


def test_integration():
    """Test that both modules work together in a complete application."""
    print("\nTesting integration...")
    
    # Setup logging
    setup_logging()
    
    # Create FastAPI app
    app = FastAPI(title="Test App")
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add endpoints
    @app.get("/")
    async def root():
        return {"message": "Hello World"}
    
    @app.get("/error")
    async def trigger_error():
        raise RuntimeError("Intentional error for testing")
    
    # Test with client (raise_server_exceptions=False allows testing error responses)
    client = TestClient(app, raise_server_exceptions=False)
    
    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    print("✅ Root endpoint works")
    
    # Test error endpoint
    response = client.get("/error")
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
    print("✅ Error endpoint handled correctly")
    
    print("\n✅ All integration tests passed!")


if __name__ == "__main__":
    print("="*60)
    print("Central Error Handling + Logging Module Tests")
    print("="*60)
    
    try:
        test_logging_setup()
        test_error_handlers()
        test_integration()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nThe error handling and logging modules are working correctly!")
        print("\nTo use in your application:")
        print("1. Import: from app.errors import register_error_handlers")
        print("2. Import: from app.logging import setup_logging")
        print("3. Call setup_logging() early in your startup")
        print("4. Call register_error_handlers(app) after creating your FastAPI app")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

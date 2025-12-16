"""
Test the health router endpoint to verify it works correctly.
"""
import sys
import os

# Add backend_app to path
backend_path = os.path.join(os.path.dirname(__file__), 'api', 'backend_app')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

def test_health_ping():
    """Test /health/ping endpoint from health router"""
    print("Testing /health/ping endpoint from health router...")
    
    # Import the health router
    from api.health import router, ping
    
    # Verify router exists
    assert router is not None, "Health router should exist"
    
    # Test the ping function directly
    result = ping()
    print(f"Direct function call result: {result}")
    assert result == {"status": "ok"}, f"Expected {{'status': 'ok'}}, got {result}"
    
    print("✅ Health router test passed!")

if __name__ == "__main__":
    test_health_ping()
    print("\n✅ All tests passed!")

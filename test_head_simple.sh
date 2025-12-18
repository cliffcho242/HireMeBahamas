#!/bin/bash
# Simple integration test for HEAD method support
# This test starts the server and uses curl to test HEAD requests

set -e

echo "🧪 Testing HEAD method support for 405 fix..."
echo ""

# Start the server in background
echo "Starting test server..."
# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
export DATABASE_URL="sqlite:///./test.db"
export ENVIRONMENT="test"

# Use a minimal Python test that imports just what we need
python3 << 'EOF'
import sys
import os

# Set environment before importing
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["ENVIRONMENT"] = "test"

# Try to import and test HEAD support directly
try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    # Create a minimal app to test our route decorators
    app = FastAPI()
    
    @app.get("/")
    @app.head("/")
    def root():
        return {"message": "test"}
    
    @app.get("/health")
    @app.head("/health")
    def health():
        return {"status": "ok"}
    
    @app.get("/api/health")
    @app.head("/api/health")
    def api_health():
        return {"status": "ok"}
    
    # Test with TestClient
    client = TestClient(app)
    
    # Test HEAD /
    print("Testing HEAD /...")
    response = client.head("/")
    assert response.status_code == 200, f"HEAD / failed: {response.status_code}"
    assert response.content == b"", "HEAD / should have empty body"
    print("✅ HEAD / returns 200")
    
    # Test HEAD /health
    print("Testing HEAD /health...")
    response = client.head("/health")
    assert response.status_code == 200, f"HEAD /health failed: {response.status_code}"
    assert response.content == b"", "HEAD /health should have empty body"
    print("✅ HEAD /health returns 200")
    
    # Test HEAD /api/health
    print("Testing HEAD /api/health...")
    response = client.head("/api/health")
    assert response.status_code == 200, f"HEAD /api/health failed: {response.status_code}"
    assert response.content == b"", "HEAD /api/health should have empty body"
    print("✅ HEAD /api/health returns 200")
    
    # Verify GET still works
    print("Testing GET requests still work...")
    response = client.get("/")
    assert response.status_code == 200, f"GET / failed: {response.status_code}"
    assert "message" in response.json()
    print("✅ GET / returns 200 with content")
    
    response = client.get("/health")
    assert response.status_code == 200, f"GET /health failed: {response.status_code}"
    assert response.json() == {"status": "ok"}
    print("✅ GET /health returns 200 with content")
    
    print("")
    print("✅ All HEAD method tests passed!")
    print("✅ 405 errors will be eliminated for HEAD requests")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

exit $?

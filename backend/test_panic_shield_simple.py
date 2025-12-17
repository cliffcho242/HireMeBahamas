"""
Simple manual test for the panic shield exception handler.

This test verifies the exception handler works by making HTTP requests.
"""

import sys
import os
import asyncio
import httpx

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_exception_handler():
    """Test that the exception handler catches exceptions"""
    # Import the app
    from backend.app.main import app
    from fastapi import Request
    
    # Add a test endpoint that raises an exception
    @app.get("/test-exception")
    async def test_exception(request: Request):
        # Set a request ID in state
        request.state.id = "test-123"
        raise ValueError("Test exception for panic shield")
    
    # Start uvicorn in the background
    import uvicorn
    from threading import Thread
    
    def run_server():
        uvicorn.run(app, host="127.0.0.1", port=8999, log_level="error")
    
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give the server time to start
    await asyncio.sleep(2)
    
    # Make a request to the test endpoint
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://127.0.0.1:8999/test-exception")
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.json()}")
            
            # Check the response
            assert response.status_code == 500, f"Expected 500, got {response.status_code}"
            data = response.json()
            assert "error" in data, f"Expected 'error' key in response, got {data}"
            assert data["error"] == "Temporary issue. Try again.", f"Expected specific error message, got {data['error']}"
            
            print("✅ Test passed: Exception handler works correctly!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
    
    return True


if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_exception_handler())

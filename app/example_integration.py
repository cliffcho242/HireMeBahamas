"""
Example Integration: Central Error Handling + Logging

This example demonstrates how to integrate the central error handling
and logging modules into a FastAPI application.

Usage:
    python -m app.example_integration
    
    Then test the endpoints:
    - GET http://localhost:8000/ - Normal endpoint
    - GET http://localhost:8000/health - Health check
    - GET http://localhost:8000/error - Trigger error to test error handler
"""
from fastapi import FastAPI
from app.errors import register_error_handlers
from app.logging import setup_logging

# Step 1: Set up logging FIRST (before creating the app)
# This ensures all logs use the consistent format
setup_logging()

# Step 2: Create your FastAPI application
app = FastAPI(
    title="HireMeBahamas Example",
    description="Example application with central error handling and logging",
    version="1.0.0"
)

# Step 3: Register error handlers
# This should be done after creating the app but before adding routes
register_error_handlers(app)

# Step 4: Add your application routes
@app.get("/")
async def root():
    """Root endpoint - returns a welcome message"""
    return {"message": "Welcome to HireMeBahamas", "status": "operational"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "hiremebahamas"}


@app.get("/error")
async def trigger_error():
    """Endpoint that triggers an error to demonstrate error handling"""
    # This will be caught by the global exception handler
    # and logged with full traceback
    raise ValueError("This is a test error to demonstrate error handling")


if __name__ == "__main__":
    import uvicorn
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info("Starting example application with central error handling and logging...")
    logger.info("Access the application at http://localhost:8000")
    logger.info("Try these endpoints:")
    logger.info("  - GET / (normal endpoint)")
    logger.info("  - GET /health (health check)")
    logger.info("  - GET /error (trigger error)")
    logger.info("  - GET /docs (API documentation)")
    
    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

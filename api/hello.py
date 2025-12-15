"""
Example Vercel Serverless Function - Hello World
=================================================

This is a simple example serverless function that demonstrates how to add
new serverless functions to the HireMeBahamas project.

Endpoint: /api/hello
Method: GET
Response: JSON greeting message

You can add more serverless functions by creating new .py files in the api/ directory.
Each file automatically becomes a serverless endpoint at /api/<filename>
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    """Vercel Serverless Function handler for hello endpoint."""
    
    def _set_headers(self, status=200):
        """Set response headers with CORS support."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        
        # SECURITY: Configure CORS based on environment
        # For production, use specific domain from environment variable
        # For development/demo, allow all origins (use with caution)
        allowed_origin = os.getenv("FRONTEND_URL", "*")
        self.send_header("Access-Control-Allow-Origin", allowed_origin)
        
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests."""
        self._set_headers(200)
    
    def do_GET(self):
        """
        Handle GET request for hello endpoint.
        
        Returns:
            JSON response with greeting message and metadata
        """
        try:
            response_data = {
                "message": "Hello from HireMeBahamas Serverless Function! 🇧🇸",
                "endpoint": "/api/hello",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "platform": "vercel-serverless",
                "region": os.getenv("VERCEL_REGION", "unknown"),
                "environment": os.getenv("ENVIRONMENT", "production"),
                "status": "success",
                "documentation": {
                    "guide": "VERCEL_SERVERLESS_SETUP.md",
                    "description": "This is an example serverless function",
                    "how_to_add_more": "Create new .py files in api/ directory",
                    "example_endpoints": [
                        "/api/hello (this endpoint)",
                        "/api/health (health check)",
                        "/api/main (full backend API)"
                    ]
                }
            }
            
            self._set_headers(200)
            self.wfile.write(json.dumps(response_data, indent=2).encode())
            
        except Exception as e:
            error_response = {
                "status": "error",
                "message": "Internal server error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            self._set_headers(500)
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_POST(self):
        """
        Handle POST request for hello endpoint with personalized greeting.
        
        Request Body:
            {
                "name": "John Doe"
            }
        
        Returns:
            JSON response with personalized greeting
        """
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                name = data.get('name', 'Guest')
            else:
                name = 'Guest'
            
            response_data = {
                "message": f"Hello, {name}! Welcome to HireMeBahamas! 🇧🇸",
                "endpoint": "/api/hello",
                "method": "POST",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "platform": "vercel-serverless",
                "status": "success"
            }
            
            self._set_headers(200)
            self.wfile.write(json.dumps(response_data, indent=2).encode())
            
        except Exception as e:
            error_response = {
                "status": "error",
                "message": "Internal server error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            self._set_headers(500)
            self.wfile.write(json.dumps(error_response).encode())

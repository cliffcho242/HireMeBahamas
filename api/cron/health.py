"""
Vercel Cron Job Handler - Health Check & Keep-Alive
====================================================

Replaces Render's keep-alive background worker with Vercel Cron Jobs.

Schedule: Every 5 minutes (*/5 * * * *)
Purpose: Keeps serverless functions warm and monitors health
Cost: Free on Vercel Hobby tier (up to 2 cron jobs)

This endpoint:
1. Confirms the API is responsive
2. Reports execution time for monitoring

IMPORTANT: This endpoint MUST NOT ping the database or any external services.
Background database pings break serverless environments and cause connection pool exhaustion.
Health checks in cron jobs should only verify the function is responsive, not check dependencies.
"""
import json
import os
import time
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    """Vercel Serverless Function handler for cron health checks."""
    
    def _set_headers(self, status=200):
        """Set response headers with CORS support."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
    
    def do_GET(self):
        """
        Handle GET request for cron health check.
        
        Returns JSON with:
        - status: "healthy" or "unhealthy"
        - timestamp: Unix timestamp
        - environment: Current environment
        - execution_time_ms: Time taken to process request
        """
        start_time = time.time()
        current_timestamp = int(start_time)
        
        # Check for CRON_SECRET authorization
        cron_secret = os.getenv("CRON_SECRET")
        if cron_secret:
            auth_header = self.headers.get("Authorization", "")
            expected_auth = f"Bearer {cron_secret}"
            if auth_header != expected_auth:
                self._set_headers(401)
                error_response = {
                    "error": "Unauthorized",
                    "message": "Invalid or missing Authorization header"
                }
                self.wfile.write(json.dumps(error_response).encode())
                return
        
        try:
            response_data = {
                "status": "healthy",
                "timestamp": current_timestamp,
                "environment": os.getenv("ENVIRONMENT", "production"),
                "vercel_region": os.getenv("VERCEL_REGION", "unknown"),
                "message": "Vercel cron health check OK",
                "cron_schedule": "*/5 * * * *",
                "execution_time_ms": round((time.time() - start_time) * 1000, 2)
            }
            
            self._set_headers(200)
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            error_response = {
                "status": "unhealthy",
                "timestamp": current_timestamp,
                "error": str(e),
                "execution_time_ms": round((time.time() - start_time) * 1000, 2)
            }
            self._set_headers(500)
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_POST(self):
        """Handle POST request (for manual trigger or extended health checks)."""
        # Vercel cron jobs send GET requests, but support POST for manual triggers
        self.do_GET()

#!/usr/bin/env python3
"""
SIMPLE WORKING BACKEND - Direct server execution
"""

import http.server
import json
import socketserver
import time


class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "status": "healthy",
                "message": "SIMPLE WORKING BACKEND",
                "timestamp": time.time(),
                "server": "Python HTTP Server",
            }
            self.wfile.write(json.dumps(response).encode())
            print(f"✅ Health check served at {time.strftime('%H:%M:%S')}")
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {"error": "Not found", "endpoint": "/health"}
            self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        # Reduce noise - only log important requests
        if "health" in format or "GET" in format:
            print(f"📡 {self.address_string()} - {format % args}")
        # Suppress other logs


if __name__ == "__main__":
    port = 8008
    print("=" * 50)
    print("🚀 SIMPLE WORKING BACKEND")
    print("=" * 50)
    print(f"Starting server on http://127.0.0.1:{port}")
    print(f"Health endpoint: http://127.0.0.1:{port}/health")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    try:
        with socketserver.TCPServer(("127.0.0.1", port), SimpleHandler) as httpd:
            print("✅ Server is running and listening!")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

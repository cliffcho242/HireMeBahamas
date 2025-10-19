#!/usr/bin/env python3
"""
PERMANENT BACKEND - Stays running until manually stopped
"""

import http.server
import socketserver
import json
import time

class PermanentHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            response = {
                "status": "healthy",
                "message": "PERMANENT BACKEND RUNNING",
                "timestamp": time.time(),
                "server": "Python HTTP Server",
                "endpoints": ["/health"]
            }
            self.wfile.write(json.dumps(response).encode())
            print(f"✅ Health check: {time.strftime('%H:%M:%S')}")
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "error": "Not found",
                "available_endpoints": ["/health"],
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def log_message(self, format, *args):
        # Reduce log noise
        if "health" in format.lower() or "GET /health" in format:
            print(f"📡 Health request from {self.address_string()}")

if __name__ == "__main__":
    port = 8008
    print("=" * 60)
    print("🔥 PERMANENT BACKEND SERVER")
    print("=" * 60)
    print(f"🚀 Starting on http://127.0.0.1:{port}")
    print(f"📍 Health endpoint: http://127.0.0.1:{port}/health")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)

    try:
        with socketserver.TCPServer(("127.0.0.1", port), PermanentHandler) as httpd:
            print("✅ Server is running and accepting connections!")
            print("💡 Leave this terminal open and test from another terminal")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
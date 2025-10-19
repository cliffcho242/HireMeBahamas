#!/usr/bin/env python3
"""Direct Test without Flask"""

import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

class LoginHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "OK"}).encode())
        
    def do_POST(self):
        if self.path == '/api/auth/login':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "token": "test-token-123",
                "user": {
                    "email": "admin@hirebahamas.com",
                    "id": 1,
                    "first_name": "Admin",
                    "last_name": "User"
                }
            }
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    PORT = 8009
    
    print(f"Starting simple HTTP server on port {PORT}")
    print(f"Health check: http://127.0.0.1:{PORT}/health")
    print(f"Login: http://127.0.0.1:{PORT}/api/auth/login")
    
    with socketserver.TCPServer(("127.0.0.1", PORT), LoginHandler) as httpd:
        print(f"Server running at http://127.0.0.1:{PORT}")
        httpd.serve_forever()
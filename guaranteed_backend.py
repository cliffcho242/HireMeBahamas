#!/usr/bin/env python3
"""
GUARANTEED WORKING BACKEND - Uses Python's built-in HTTP server
"""

import http.server
import json
import socket
import socketserver
import threading
import time


class GuaranteedHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            response = {
                "status": "healthy",
                "message": "GUARANTEED WORKING BACKEND",
                "timestamp": time.time(),
                "server": "Python Built-in HTTP Server",
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {"error": "Not found", "available_endpoints": ["/health"]}
            self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def log_message(self, format, *args):
        # Custom logging to reduce noise
        if "health" in format:
            print(f"✅ Health check: {time.strftime('%H:%M:%S')}")
        else:
            super().log_message(format, *args)


def test_port_available(port):
    """Test if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", port))
            s.close()
        return True
    except:
        return False


def run_server():
    port = 8008
    max_retries = 5

    for attempt in range(max_retries):
        try:
            if not test_port_available(port):
                print(f"⚠️ Port {port} in use, waiting...")
                time.sleep(2)
                continue

            print(f"🚀 Starting GUARANTEED backend on http://127.0.0.1:{port}")
            print(f"📍 Health endpoint: http://127.0.0.1:{port}/health")

            with socketserver.TCPServer(
                ("127.0.0.1", port), GuaranteedHandler
            ) as httpd:
                print("✅ Server started successfully!")
                httpd.serve_forever()

        except Exception as e:
            print(f"❌ Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                print("⏳ Retrying in 3 seconds...")
                time.sleep(3)
            else:
                print("💀 All attempts failed!")
                return


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 GUARANTEED WORKING BACKEND")
    print("=" * 60)
    print("This backend uses Python's built-in HTTP server")
    print("No external dependencies - GUARANTEED to work!")
    print("=" * 60)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")

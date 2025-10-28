#!/usr/bin/env python3
"""
LONG RUNNING TEST BACKEND
"""

import http.server
import json
import socketserver
import threading
import time


class LongRunningHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        response = {
            "status": "healthy",
            "message": "LONG RUNNING BACKEND",
            "timestamp": time.time(),
            "server": "Python HTTP Server",
            "port": self.server.server_address[1],
        }
        self.wfile.write(json.dumps(response).encode())
        print(f"✅ Request served at {time.strftime('%H:%M:%S')}")

    def log_message(self, format, *args):
        # Only log health requests
        if "GET" in format:
            print(f"📡 {format % args}")


def run_server(port):
    print(f"🚀 Starting server on port {port}")
    print(f"📍 URL: http://127.0.0.1:{port}")
    print("Server will run for 30 seconds...")

    try:
        with socketserver.TCPServer(("127.0.0.1", port), LongRunningHandler) as httpd:
            print("✅ Server is listening!")

            # Run for 30 seconds
            start_time = time.time()
            while time.time() - start_time < 30:
                httpd.timeout = 1.0  # Check for timeout every second
                httpd.handle_request()  # Handle one request at a time

            print("⏰ 30 seconds elapsed, stopping server...")

    except Exception as e:
        print(f"❌ Server error: {e}")


if __name__ == "__main__":
    port = 8008
    print("=" * 50)
    print("⏳ LONG RUNNING TEST BACKEND")
    print("=" * 50)

    server_thread = threading.Thread(target=run_server, args=(port,))
    server_thread.start()

    # Wait a bit then test
    time.sleep(2)
    print("\n🧪 Testing connection...")

    try:
        import urllib.request

        response = urllib.request.urlopen(f"http://127.0.0.1:{port}", timeout=5)
        data = json.loads(response.read().decode())
        print(f"✅ SUCCESS! Response: {data['message']}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

    # Wait for server to finish
    server_thread.join()
    print("🏁 Test complete")

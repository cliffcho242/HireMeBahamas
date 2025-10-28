#!/usr/bin/env python3
"""
TEST BACKEND - Testing different ports
"""

import http.server
import json
import socketserver
import sys
import time


class TestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        response = {
            "status": "working",
            "message": "TEST BACKEND SUCCESS",
            "timestamp": time.time(),
            "port": self.server.server_address[1],
        }
        self.wfile.write(json.dumps(response).encode())
        print(f"✅ Request served on port {self.server.server_address[1]}")


def test_ports():
    ports_to_test = [8008, 8080, 3000, 5000, 9000]

    for port in ports_to_test:
        print(f"\n🧪 Testing port {port}...")
        try:
            with socketserver.TCPServer(("127.0.0.1", port), TestHandler) as httpd:
                print(f"✅ Port {port} is available and server started!")
                print(f"📍 Test URL: http://127.0.0.1:{port}")

                # Test the server immediately
                import urllib.request

                try:
                    response = urllib.request.urlopen(
                        f"http://127.0.0.1:{port}", timeout=2
                    )
                    data = json.loads(response.read().decode())
                    print(f"✅ Self-test successful: {data['message']}")
                    return port  # Return the working port
                except Exception as e:
                    print(f"❌ Self-test failed: {e}")

        except Exception as e:
            print(f"❌ Port {port} failed: {e}")

    return None


if __name__ == "__main__":
    print("🔍 TESTING PORT AVAILABILITY")
    print("=" * 40)

    working_port = test_ports()

    if working_port:
        print(f"\n🎉 SUCCESS! Port {working_port} is working!")
        print(f"💡 Use this port for your backend instead of 8008")
    else:
        print("\n💀 No ports are working. Check firewall/antivirus.")

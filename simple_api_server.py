#!/usr/bin/env python3
"""
Simple HTTP server for HireMeBahamas API
"""

import http.server
import json
import os
import socketserver
import sqlite3
import urllib.parse
from datetime import datetime, timedelta

import bcrypt
import jwt

PORT = 5000
SECRET_KEY = "your-secret-key-here-change-in-production"


class HireMeBahamasAPI(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "status": "healthy",
                "message": "HireMeBahamas API is running",
                "timestamp": datetime.now().isoformat(),
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        if self.path == "/auth/login":
            self.handle_login()
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def handle_login(self):
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            email = data.get("email", "").strip()
            password = data.get("password", "").strip()

            if not email or not password:
                self.send_error_response(400, "Email and password are required")
                return

            # Connect to database
            db_path = os.path.join(os.path.dirname(__file__), "hiremebahamas.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Query user
            cursor.execute(
                """
                SELECT id, email, password_hash, first_name, last_name,
                       user_type, is_active
                FROM users WHERE email = ?
            """,
                (email,),
            )

            user = cursor.fetchone()
            conn.close()

            if not user:
                self.send_error_response(401, "Invalid email or password")
                return

            (
                user_id,
                user_email,
                password_hash,
                first_name,
                last_name,
                user_type,
                is_active,
            ) = user

            # Verify password
            if bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
                # Create JWT token
                payload = {
                    "user_id": user_id,
                    "email": user_email,
                    "is_admin": user_type == "admin",
                    "exp": datetime.utcnow() + timedelta(hours=24),
                }

                token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

                response = {
                    "success": True,
                    "message": "Login successful",
                    "token": token,
                    "user": {
                        "id": user_id,
                        "email": user_email,
                        "username": user_email.split("@")[0],
                        "full_name": f"{first_name or ''} {last_name or ''}".strip(),
                        "is_active": bool(is_active),
                    },
                }

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_error_response(401, "Invalid email or password")

        except Exception as e:
            print(f"Login error: {e}")
            self.send_error_response(500, f"Login error: {str(e)}")

    def send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        response = {"success": False, "message": message}
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        # Override to reduce noise
        pass


if __name__ == "__main__":
    print(f"Starting HireMeBahamas API server on port {PORT}")
    print(f"Server will be available at http://127.0.0.1:{PORT}")

    try:
        with socketserver.TCPServer(("", PORT), HireMeBahamasAPI) as httpd:
            print("Server started successfully!")
            print("Press Ctrl+C to stop")
            httpd.serve_forever()
    except Exception as e:
        print(f"Server error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("Server stopped")

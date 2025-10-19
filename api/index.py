from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs

# In-memory data
users = {
    "admin@hiremebahamas.com": {
        "email": "admin@hiremebahamas.com",
        "password": "AdminPass123!",
        "user_type": "admin",
        "first_name": "Admin",
        "last_name": "User"
    }
}
jobs = []
posts = []

class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
        return
    
    def do_GET(self):
        path = self.path
        
        if path == '/health':
            self._set_headers()
            response = {"status": "healthy", "message": "Backend is running"}
            self.wfile.write(json.dumps(response).encode())
        
        elif path == '/api/jobs':
            self._set_headers()
            self.wfile.write(json.dumps(jobs).encode())
        
        elif path == '/api/posts':
            self._set_headers()
            self.wfile.write(json.dumps(posts).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body)
        except:
            data = {}
        
        path = self.path
        
        if path == '/api/auth/login':
            email = data.get('email')
            password = data.get('password')
            
            if email in users and users[email]['password'] == password:
                self._set_headers()
                response = {
                    "access_token": "demo_token_12345",
                    "user": {
                        "email": email,
                        "user_type": users[email]['user_type'],
                        "first_name": users[email]['first_name'],
                        "last_name": users[email]['last_name']
                    }
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Invalid credentials"}).encode())
        
        elif path == '/api/auth/register':
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')
            user_type = data.get('user_type', 'job_seeker')
            
            if email in users:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "User already exists"}).encode())
            else:
                users[email] = {
                    "email": email,
                    "password": password,
                    "user_type": user_type,
                    "first_name": first_name,
                    "last_name": last_name
                }
                self._set_headers(201)
                response = {
                    "message": "User registered successfully",
                    "user": {"email": email, "user_type": user_type, "first_name": first_name, "last_name": last_name}
                }
                self.wfile.write(json.dumps(response).encode())
        
        elif path == '/api/jobs':
            job = {
                "id": len(jobs) + 1,
                "title": data.get('title'),
                "company": data.get('company'),
                "location": data.get('location'),
                "description": data.get('description'),
                "salary": data.get('salary', 'Negotiable')
            }
            jobs.append(job)
            self._set_headers(201)
            self.wfile.write(json.dumps(job).encode())
        
        elif path == '/api/posts':
            post = {
                "id": len(posts) + 1,
                "content": data.get('content'),
                "image_url": data.get('image_url'),
                "user": {"id": 1, "first_name": "Admin", "last_name": "User", "email": "admin@hiremebahamas.com"},
                "likes_count": 0
            }
            posts.append(post)
            self._set_headers(201)
            self.wfile.write(json.dumps(post).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

#!/usr/bin/env python3
"""Minimal Backend Test"""

from flask import Flask, jsonify
import threading
import time

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "OK"})

@app.route('/api/auth/login', methods=['POST'])
def login():
    return jsonify({
        "token": "test-token",
        "user": {"email": "admin@hirebahamas.com", "id": 1}
    })

def run_server():
    app.run(host='127.0.0.1', port=8008, debug=False, use_reloader=False)

if __name__ == '__main__':
    print("Starting minimal test server on http://127.0.0.1:8008")
    
    # Start server in a thread to avoid blocking
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    print("Server started. Keeping alive...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
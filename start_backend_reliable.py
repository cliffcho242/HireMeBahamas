#!/usr/bin/env python3
"""
Simple Reliable Backend Launcher
Starts the Flask backend server using Waitress and keeps it running
"""

import sys
import os

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("HireMeBahamas Backend Server")
print("="*60)
print()

try:
    print("[1/3] Importing Flask application...")
    from final_backend import app
    print("[OK] Flask app loaded successfully")
    print()
    
    print("[2/3] Importing Waitress WSGI server...")
    from waitress import serve
    print("[OK] Waitress ready")
    print()
    
    print("[3/3] Starting server...")
    print("="*60)
    print("Backend URL: http://127.0.0.1:9999")
    print("API Endpoints:")
    print("  - POST /api/auth/login")
    print("  - POST /api/auth/register")
    print("  - GET  /api/auth/profile")
    print("  - GET  /health")
    print("="*60)
    print()
    print("Server is RUNNING - Press Ctrl+C to stop")
    print()
    
    # Start Waitress server
    serve(
        app,
        host='127.0.0.1',
        port=9999,
        threads=6,
        connection_limit=1000,
        channel_timeout=60,
        cleanup_interval=10
    )
    
except KeyboardInterrupt:
    print()
    print("Server stopped by user")
    sys.exit(0)
    
except Exception as e:
    print(f"[ERROR] Failed to start server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

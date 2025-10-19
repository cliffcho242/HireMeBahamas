#!/usr/bin/env python3
"""
Permanent Backend Server - Ensures stable connection
"""
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("Starting HireMeBahamas Backend Server")
print("="*60)
print()

try:
    from final_backend import app
    print("[OK] Flask app loaded")
    print()
    print("Starting server on http://0.0.0.0:9999")
    print("Press Ctrl+C to stop")
    print("="*60)
    print()
    
    # Start server - this blocks until stopped
    app.run(
        host='0.0.0.0',
        port=9999,
        debug=True,
        use_reloader=False,
        threaded=True
    )
    
except KeyboardInterrupt:
    print("\nServer stopped")
    sys.exit(0)
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

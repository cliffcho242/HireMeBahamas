"""
SOLUTION: Frontend Directory Fix
Run this script to properly start both servers
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    print("=" * 50)
    print("HireBahamas Platform - Directory Fix Solution")
    print("=" * 50)

    workspace = Path("C:/Users/Dell/OneDrive/Desktop/HireBahamas")

    print("\nThe issue was: npm run dev was run from root directory")
    print("Solution: Frontend must be started from frontend/ directory")
    print("\nCorrect commands:")
    print("1. cd frontend")
    print("2. npm run dev")

    print("\nStarting servers now...")

    # Backend
    print("\n[1/2] Starting Backend...")
    backend_cmd = [
        str(workspace / ".venv" / "Scripts" / "python.exe"),
        str(workspace / "facebook_like_backend.py"),
    ]

    try:
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=str(workspace),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
        )
        print(f"Backend started with PID: {backend_process.pid}")
    except Exception as e:
        print(f"Backend error: {e}")

    # Frontend
    print("\n[2/2] Starting Frontend...")
    frontend_dir = workspace / "frontend"

    try:
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(frontend_dir),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
        )
        print(f"Frontend started with PID: {frontend_process.pid}")
    except Exception as e:
        print(f"Frontend error: {e}")

    print("\n" + "=" * 50)
    print("SERVERS STARTING...")
    print("Frontend: http://localhost:3000")
    print("Backend: http://127.0.0.1:8008")
    print("Login: admin@hirebahamas.com / AdminPass123!")
    print("=" * 50)

    # Open browser
    import time

    time.sleep(5)
    if os.name == "nt":
        os.system("start http://localhost:3000")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Automated startup script for HireBahamas application
This script starts both backend and frontend servers reliably
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def find_free_port(start_port=8005):
    """Find a free port starting from start_port"""
    import socket

    for port in range(start_port, start_port + 10):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return None


def kill_processes_on_ports(ports):
    """Kill any processes running on specified ports"""
    for port in ports:
        try:
            # Windows command to find and kill processes on port
            result = subprocess.run(
                f"netstat -ano | findstr :{port}",
                shell=True,
                capture_output=True,
                text=True,
            )
            if result.stdout:
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if "LISTENING" in line:
                        parts = line.split()
                        if parts:
                            pid = parts[-1]
                            try:
                                subprocess.run(
                                    f"taskkill /F /PID {pid}", shell=True, check=True
                                )
                                print(f"Killed process {pid} on port {port}")
                            except:
                                pass
        except:
            pass


def start_backend(port=8005):
    """Start the FastAPI backend server"""
    print(f"Starting backend server on port {port}...")

    # Change to project directory
    project_dir = Path(__file__).parent
    backend_dir = project_dir / "backend"

    # Activate virtual environment and start server
    if os.name == "nt":  # Windows
        venv_python = project_dir / ".venv" / "Scripts" / "python.exe"
        activate_script = project_dir / ".venv" / "Scripts" / "Activate.ps1"
    else:  # Unix/Linux
        venv_python = project_dir / ".venv" / "bin" / "python"
        activate_script = project_dir / ".venv" / "bin" / "activate"

    # Create the backend startup command
    cmd = [
        str(venv_python),
        "-c",
        f"""
import uvicorn
import sys
sys.path.insert(0, '{backend_dir}')
from app.main import app
uvicorn.run(app, host='127.0.0.1', port={port}, log_level='info')
""",
    ]

    # Start backend process
    backend_process = subprocess.Popen(
        cmd,
        cwd=str(project_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    )

    return backend_process


def start_frontend():
    """Start the React frontend server"""
    print("Starting frontend server...")

    project_dir = Path(__file__).parent
    frontend_dir = project_dir / "frontend"

    # Start frontend development server
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    )

    return frontend_process


def wait_for_server(port, timeout=30):
    """Wait for server to be ready"""
    import socket
    import time

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(("127.0.0.1", port))
                if result == 0:
                    return True
        except:
            pass
        time.sleep(1)
    return False


def main():
    """Main startup function"""
    print("🚀 Starting HireBahamas Application...")

    # Kill any existing processes on our ports
    print("Cleaning up existing processes...")
    kill_processes_on_ports([8001, 8002, 8003, 8004, 8005, 3000])
    time.sleep(2)

    # Find free port for backend
    backend_port = find_free_port(8005)
    if not backend_port:
        print("❌ Could not find a free port for backend")
        sys.exit(1)

    try:
        # Start backend
        backend_process = start_backend(backend_port)

        # Wait for backend to start
        print(f"⏳ Waiting for backend server on port {backend_port}...")
        if wait_for_server(backend_port, 30):
            print(
                f"✅ Backend server started successfully on http://127.0.0.1:{backend_port}"
            )
        else:
            print("❌ Backend server failed to start")
            backend_process.terminate()
            sys.exit(1)

        # Start frontend
        frontend_process = start_frontend()

        # Wait for frontend to start
        print("⏳ Waiting for frontend server...")
        if wait_for_server(3000, 30):
            print("✅ Frontend server started successfully on http://localhost:3000")
        else:
            print("❌ Frontend server failed to start")
            frontend_process.terminate()
            backend_process.terminate()
            sys.exit(1)

        print("\n🎉 HireBahamas Application is ready!")
        print(f"📊 Backend API: http://127.0.0.1:{backend_port}")
        print(f"📊 API Docs: http://127.0.0.1:{backend_port}/docs")
        print("🌐 Frontend: http://localhost:3000")
        print("\nPress Ctrl+C to stop all servers...")

        # Wait for interrupt
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down servers...")
            frontend_process.terminate()
            backend_process.terminate()

            # Wait for processes to terminate
            frontend_process.wait(timeout=5)
            backend_process.wait(timeout=5)

            print("✅ All servers stopped successfully")

    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

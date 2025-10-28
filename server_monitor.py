#!/usr/bin/env python3
"""
HireMeBahamas Backend Server Monitor
Keeps the Flask server running and monitors its health
"""

import os
import subprocess
import sys
import time
from datetime import datetime

import requests


def log_message(message):
    """Log a message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def check_server_health():
    """Check if the server is responding to health requests"""
    try:
        response = requests.get("http://127.0.0.1:8008/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def start_server():
    """Start the Flask server process"""
    try:
        # Get the path to the virtual environment Python
        venv_python = os.path.join(
            os.path.dirname(__file__), ".venv", "Scripts", "python.exe"
        )
        backend_script = os.path.join(os.path.dirname(__file__), "final_backend.py")

        log_message(f"Starting server with: {venv_python} {backend_script}")

        # Start the server process
        process = subprocess.Popen(
            [venv_python, backend_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=os.path.dirname(__file__),
        )

        return process
    except Exception as e:
        log_message(f"Error starting server: {e}")
        return None


def main():
    log_message("Starting HireMeBahamas Backend Server Monitor")
    log_message("Server will be available at: http://127.0.0.1:8008")

    max_retries = 10
    retry_count = 0

    while retry_count < max_retries:
        log_message(f"Starting server (Attempt {retry_count + 1}/{max_retries})")

        # Start the server
        server_process = start_server()

        if not server_process:
            retry_count += 1
            if retry_count < max_retries:
                log_message("Failed to start server, retrying in 5 seconds...")
                time.sleep(5)
            continue

        # Wait for server to start
        log_message("Waiting for server to initialize...")
        time.sleep(5)

        # Check server health
        health_checks = 0
        server_healthy = False

        while health_checks < 10:  # Try 10 times
            if check_server_health():
                log_message("Server is healthy and responding!")
                server_healthy = True
                break
            else:
                log_message(f"Health check {health_checks + 1} failed, retrying...")
                time.sleep(2)
                health_checks += 1

        if server_healthy:
            log_message("Server started successfully. Monitoring...")

            # Monitor the server
            while True:
                time.sleep(30)  # Check every 30 seconds

                if not check_server_health():
                    log_message("Server health check failed! Restarting...")
                    break

                # Check if process is still running
                if server_process.poll() is not None:
                    log_message("Server process terminated unexpectedly!")
                    break

        # Stop the server process if it's still running
        if server_process and server_process.poll() is None:
            log_message("Stopping server process...")
            server_process.terminate()
            try:
                server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server_process.kill()

        retry_count += 1
        if retry_count < max_retries:
            log_message("Server stopped, restarting in 5 seconds...")
            time.sleep(5)

    log_message("Maximum retries exceeded. Giving up.")
    sys.exit(1)


if __name__ == "__main__":
    main()

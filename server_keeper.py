#!/usr/bin/env python3
"""
Server keeper for HireMeBahamas API
"""

import os
import subprocess
import sys
import time
from datetime import datetime


def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def run_server():
    log_message("Starting HireMeBahamas Flask API Server Keeper")
    log_message("Server will be available at: http://127.0.0.1:8080")

    while True:
        try:
            log_message("Starting Flask server...")

            # Run the Flask server
            process = subprocess.Popen(
                [sys.executable, "minimal_flask_server.py"],
                cwd=os.path.dirname(__file__),
            )

            # Wait for the process to finish
            process.wait()

            log_message(f"Server exited with code: {process.returncode}")

        except Exception as e:
            log_message(f"Error running server: {e}")

        log_message("Restarting server in 3 seconds...")
        time.sleep(3)


if __name__ == "__main__":
    run_server()

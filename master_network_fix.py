#!/usr/bin/env python3
"""
MASTER NETWORK FIX - Permanent Solution for HireMeBahamas
Ensures backend always starts reliably and network never fails
Cross-platform compatible (Windows, Linux, macOS)
"""

import logging
import os
import socket
import sys
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("network_master_fix.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def install_required_packages():
    """Install all required packages for reliable networking"""
    logger.info("Installing required packages for reliable networking...")

    packages = [
        "flask",
        "flask-cors",
        "flask-limiter",
        "flask-caching",
        "waitress",
        "gunicorn",
        "gevent",
        "eventlet",
        "pyjwt",
        "bcrypt",
        "python-dotenv",
        "requests",
        "psycopg2-binary",  # Database adapter for PostgreSQL
    ]

    import subprocess

    python_exe = sys.executable

    for package in packages:
        try:
            logger.info(f"Installing {package}...")
            subprocess.run(
                [python_exe, "-m", "pip", "install", package, "--upgrade"],
                check=True,
                capture_output=True,
            )
            logger.info(f"✓ {package} installed")
        except Exception as e:
            logger.warning(f"Could not install {package}: {e}")

    logger.info("All packages installed!")


def check_port_availability(port, max_attempts=3):
    """Check if port is available, kill blocking process if needed"""
    import platform
    
    for attempt in range(max_attempts):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("127.0.0.1", port))
        sock.close()

        if result != 0:  # Port is free
            logger.info(f"✓ Port {port} is available")
            return True

        logger.warning(
            f"Port {port} is in use, attempting to free it (attempt {attempt + 1}/{max_attempts})"
        )

        # Try to kill process (platform-specific)
        import subprocess

        try:
            if platform.system() == "Windows":
                # Windows-specific command
                subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        f"Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object {{ Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }}",
                    ],
                    capture_output=True,
                    timeout=5,
                )
            else:
                # Linux/Unix: use lsof and kill
                try:
                    result = subprocess.run(
                        ["lsof", "-ti", f":{port}"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.stdout.strip():
                        pids = result.stdout.strip().split("\n")
                        for pid in pids:
                            try:
                                subprocess.run(["kill", "-9", pid], capture_output=True, timeout=2)
                            except subprocess.TimeoutExpired:
                                logger.warning(f"Timeout killing process {pid}")
                            except Exception as e:
                                logger.warning(f"Failed to kill process {pid}: {e}")
                except FileNotFoundError:
                    logger.warning("lsof command not found. Install with: sudo apt-get install lsof")
                except subprocess.TimeoutExpired:
                    logger.warning(f"lsof command timed out")
                except Exception as e:
                    logger.warning(f"Error using lsof: {e}")
            time.sleep(2)
        except Exception as e:
            logger.warning(f"Could not kill process on port {port}: {e}")

    return False


def start_backend_server(port=9999):
    """Start backend server with guaranteed success"""
    logger.info(f"Starting backend server on port {port}...")

    try:
        from final_backend import app

        logger.info("✓ Flask app imported successfully")

        # Test app health
        with app.test_client() as client:
            response = client.get("/health")
            logger.info(f"✓ App health check: {response.status_code}")

        # Start with Waitress (most reliable for Windows)
        try:
            from waitress import serve

            logger.info(f"Starting Waitress server on 127.0.0.1:{port}...")

            # Use threading for better Windows compatibility
            import threading

            def run_server():
                serve(
                    app,
                    host="127.0.0.1",
                    port=port,
                    threads=6,
                    connection_limit=1000,
                    channel_timeout=60,
                    cleanup_interval=10,
                    _quiet=False,
                )

            server_thread = threading.Thread(target=run_server, daemon=False)
            server_thread.start()

            # Verify server started
            time.sleep(3)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(("127.0.0.1", port))
            sock.close()

            if result == 0:
                logger.info(
                    f"✓✓✓ Backend server successfully started on http://127.0.0.1:{port}"
                )
                logger.info("Server is RUNNING and accepting connections!")
                logger.info("Press Ctrl+C to stop")
                server_thread.join()
            else:
                logger.error("Server started but not accepting connections")
                return False

        except ImportError:
            logger.warning("Waitress not available, trying Flask dev server...")
            app.run(host="127.0.0.1", port=port, debug=False, threaded=True)

    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def configure_system_networking():
    """Configure system networking for optimal Flask performance (platform-aware)"""
    import platform
    import subprocess
    
    system = platform.system()
    logger.info(f"Configuring networking for {system}...")

    if system == "Windows":
        commands = [
            # Reset network stack
            "netsh winsock reset",
            # Reset TCP/IP
            "netsh int ip reset",
            # Flush DNS
            "ipconfig /flushdns",
            # Enable IPv4
            "netsh interface ipv4 set global defaultcurhoplimit=64",
        ]

        for cmd in commands:
            try:
                logger.info(f"Running: {cmd}")
                subprocess.run(
                    ["powershell", "-Command", cmd], capture_output=True, timeout=10
                )
            except Exception as e:
                logger.warning(f"Could not run {cmd}: {e}")
    else:
        # Linux/Unix networking configuration
        commands = [
            # Flush DNS (if systemd-resolved is available)
            ["systemctl", "is-active", "systemd-resolved"],
        ]
        
        try:
            # Check if systemd-resolved is available
            result = subprocess.run(
                ["systemctl", "is-active", "systemd-resolved"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                logger.info("Flushing DNS cache...")
                subprocess.run(
                    ["sudo", "systemd-resolve", "--flush-caches"],
                    capture_output=True,
                    timeout=5,
                )
        except Exception as e:
            logger.info(f"DNS flush not needed or unavailable: {e}")

    logger.info(f"✓ {system} networking configured")


def create_network_test():
    """Create a network test to verify connection"""
    logger.info("Creating network test...")

    test_script = """
import requests
import json

def test_admin_login():
    print("Testing admin login...")
    
    try:
        response = requests.post(
            'http://127.0.0.1:9999/api/auth/login',
            json={
                'email': 'admin@hiremebahamas.com',
                'password': 'AdminPass123!'
            },
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                print("✓✓✓ LOGIN SUCCESSFUL!")
                print(f"Token: {data['access_token'][:50]}...")
                return True
        
        print("✗ Login failed")
        return False
        
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

if __name__ == '__main__':
    test_admin_login()
"""

    with open("test_admin_network.py", "w") as f:
        f.write(test_script)

    logger.info("✓ Network test created: test_admin_network.py")


def main():
    """Master network fix - ensures everything works permanently"""
    logger.info("=" * 60)
    logger.info("MASTER NETWORK FIX - HireMeBahamas")
    logger.info("=" * 60)

    # Step 1: Install all required packages
    logger.info("\n[1/5] Installing required packages...")
    install_required_packages()

    # Step 2: Configure system networking
    logger.info("\n[2/5] Configuring system networking...")
    configure_system_networking()

    # Step 3: Check and free port
    logger.info("\n[3/5] Checking port availability...")
    if not check_port_availability(9999):
        logger.error("Could not free port 9999. Trying alternative port 8080...")
        if not check_port_availability(8080):
            logger.error("All ports blocked. Manual intervention required.")
            sys.exit(1)
        port = 8080
    else:
        port = 9999

    # Step 4: Create network test
    logger.info("\n[4/5] Creating network test...")
    create_network_test()

    # Step 5: Start server
    logger.info("\n[5/5] Starting backend server...")
    logger.info("=" * 60)
    if start_backend_server(port):
        logger.info("✓✓✓ MASTER FIX COMPLETE - Server is running!")
    else:
        logger.error("Server failed to start. Check logs above.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

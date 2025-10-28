#!/usr/bin/env python3
"""
Automated Server Launcher for HireMeBahamas
Forces server binding and handles Windows-specific issues
"""

import logging
import os
import socket
import sys
import threading
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("server_automation.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def check_port_binding(host, port, timeout=5):
    """Check if a port is actually bound and listening"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0  # 0 means connection successful
    except Exception as e:
        logger.error(f"Port check failed: {e}")
        return False


def force_server_binding(app, host="127.0.0.1", port=9999):
    """Force server binding using multiple methods"""

    logger.info(f"Attempting to bind server to {host}:{port}")

    # Method 1: Try waitress with different configurations
    try:
        logger.info("Trying Waitress WSGI server...")
        from waitress import serve

        # Try different configurations
        configs = [
            {"threads": 4, "connection_limit": 100},
            {"threads": 1, "connection_limit": 10},  # Minimal config
            {"threads": 8, "connection_limit": 1000},  # High concurrency
        ]

        for i, config in enumerate(configs):
            logger.info(f"Waitress config {i+1}: {config}")
            try:
                serve(app, host=host, port=port, **config)
                # If we get here, server started
                time.sleep(2)  # Give it time to bind
                if check_port_binding(host, port):
                    logger.info(f"SUCCESS: Server successfully bound to {host}:{port}")
                    return True
                else:
                    logger.warning(f"Server reported start but port not bound")
            except Exception as e:
                logger.error(f"Waitress config {i+1} failed: {e}")
                continue

    except ImportError:
        logger.error("Waitress not available")

    # Method 2: Try Flask development server with forced binding
    try:
        logger.info("Trying Flask development server with forced binding...")

        # Create a custom WSGI server that forces binding
        from werkzeug.serving import make_server

        server = make_server(host, port, app, threaded=True)
        logger.info(f"Starting Werkzeug server on {host}:{port}")

        # Start server in background thread
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        # Wait for binding
        time.sleep(3)
        if check_port_binding(host, port):
            logger.info(f"SUCCESS: Flask server successfully bound to {host}:{port}")
            # Keep the main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Shutting down server...")
                server.shutdown()
                return True
        else:
            logger.error("Flask server failed to bind")
            server.shutdown()

    except Exception as e:
        logger.error(f"Flask development server failed: {e}")

    # Method 3: Try different host bindings
    hosts_to_try = ["0.0.0.0", "localhost", "127.0.0.1"]
    for alt_host in hosts_to_try:
        if alt_host == host:
            continue
        logger.info(f"Trying alternative host: {alt_host}")
        try:
            from waitress import serve

            serve(app, host=alt_host, port=port, threads=4)
            time.sleep(2)
            if check_port_binding(alt_host, port):
                logger.info(f"SUCCESS: Server bound to {alt_host}:{port}")
                return True
        except Exception as e:
            logger.error(f"Alternative host {alt_host} failed: {e}")

    # Method 4: Force binding with socket manipulation
    try:
        logger.info("Attempting forced socket binding...")
        import socket as sock

        # Create and bind socket manually
        server_sock = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        server_sock.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)

        try:
            server_sock.bind((host, port))
            server_sock.listen(5)
            logger.info(f"SUCCESS: Manual socket binding successful on {host}:{port}")

            # Now try to serve with the bound socket
            from waitress import serve

            serve(app, host=host, port=port, threads=4, socket=server_sock)
            return True

        except Exception as e:
            logger.error(f"Manual socket binding failed: {e}")
            server_sock.close()

    except Exception as e:
        logger.error(f"Socket manipulation failed: {e}")

    return False


def main():
    """Main automation function"""
    logger.info("Starting HireMeBahamas Server Automation")

    # Import the app
    try:
        from final_backend import app

        logger.info("App imported successfully")
    except Exception as e:
        logger.error(f"Failed to import app: {e}")
        sys.exit(1)

    # Test app functionality
    try:
        with app.test_client() as client:
            response = client.get("/health")
            logger.info(f"App health check: {response.status_code}")
    except Exception as e:
        logger.error(f"App health check failed: {e}")
        sys.exit(1)

    # Try different ports
    ports_to_try = [9999, 8080, 8000, 5000, 3000]

    for port in ports_to_try:
        logger.info(f"Testing port {port}...")
        if not check_port_binding("127.0.0.1", port):
            logger.info(f"Port {port} is available")
            if force_server_binding(app, "127.0.0.1", port):
                logger.info(f"Server successfully started on port {port}")
                return
        else:
            logger.warning(f"Port {port} is already in use")

    logger.error("All server binding attempts failed")
    logger.info("Troubleshooting suggestions:")
    logger.info("   - Check Windows Firewall settings")
    logger.info("   - Try running as Administrator")
    logger.info("   - Check for antivirus interference")
    logger.info("   - Try different ports")
    sys.exit(1)


if __name__ == "__main__":
    main()

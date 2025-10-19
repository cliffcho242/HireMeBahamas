#!/usr/bin/env python3
"""
Production WSGI Server Launcher for HireMeBahamas
Optimized for high concurrency and production deployment
"""

from waitress import serve
from final_backend import app
import os
import sys
import logging
from datetime import datetime, timezone

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main server launcher with production optimizations"""

    # Production configuration
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', '9999'))
    workers = int(os.getenv('WORKERS', '4'))  # Multiple workers for concurrency
    threads = int(os.getenv('THREADS', '100'))  # High thread count for concurrent users
    connection_limit = int(os.getenv('CONNECTION_LIMIT', '1000'))  # Max concurrent connections
    cleanup_interval = int(os.getenv('CLEANUP_INTERVAL', '10'))  # Cleanup interval in seconds

    logger.info("🚀 Starting HireMeBahamas Production Server")
    logger.info(f"📍 Host: {host}")
    logger.info(f"🔌 Port: {port}")
    logger.info(f"👥 Workers: {workers}")
    logger.info(f"🧵 Threads per worker: {threads}")
    logger.info(f"🔗 Max connections: {connection_limit}")
    logger.info(f"🧹 Cleanup interval: {cleanup_interval}s")
    logger.info(f"⏰ Started at: {datetime.now(timezone.utc).isoformat()}")

    try:
        # Production server configuration
        serve(
            app,
            host=host,
            port=port,
            threads=threads,
            connection_limit=connection_limit,
            cleanup_interval=cleanup_interval,
            # Additional production settings
            channel_timeout=300,  # 5 minutes
            max_request_body_size=104857600,  # 100MB
            max_request_header_size=8192,  # 8KB
            asyncore_use_poll=True,  # Better performance on Windows
            ident='HireMeBahamas/1.0.0'
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested by user")
    except Exception as e:
        logger.error(f"💥 Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

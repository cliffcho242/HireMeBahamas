"""
Logging configuration for HireMeBahamas API
"""
import logging
import sys


def setup_logging():
    """Configure logging for the application"""
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set log levels for specific modules
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")

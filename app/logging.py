"""
Central Logging Configuration for HireMeBahamas API

This module provides centralized logging configuration for the FastAPI application.
It sets up consistent logging format and level across the application.
"""
import logging


def setup_logging():
    """Configure logging for the application.
    
    Sets up the root logger with:
    - INFO level logging for production use
    - Consistent format with timestamp, level, logger name, and message
    - Output to console (stdout/stderr)
    
    This should be called early in the application startup process,
    before any other modules that might use logging.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

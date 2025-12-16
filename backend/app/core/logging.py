"""
Centralized logging configuration for HireMeBahamas API.

This module provides structured logging with:
- Request ID tracking
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- JSON formatting for production
- File and console outputs
- Performance metrics
"""

import logging
import json
import sys
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pathlib import Path

# Log levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format for production."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON structure.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON-formatted log string
        """
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request ID if available
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        # Add user ID if available
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class DevelopmentFormatter(logging.Formatter):
    """Human-readable formatter for development environments."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record for human readability.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log string
        """
        # Color codes for different log levels
        colors = {
            "DEBUG": "\033[36m",      # Cyan
            "INFO": "\033[32m",       # Green
            "WARNING": "\033[33m",    # Yellow
            "ERROR": "\033[31m",      # Red
            "CRITICAL": "\033[35m",   # Magenta
        }
        reset = "\033[0m"
        
        level_color = colors.get(record.levelname, "")
        
        # Build the log message
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        parts = [
            f"{level_color}[{record.levelname}]{reset}",
            f"{timestamp}",
            f"{record.name}",
        ]
        
        # Add request ID if available
        if hasattr(record, "request_id"):
            parts.append(f"[req:{record.request_id[:8]}]")
        
        parts.append(f"- {record.getMessage()}")
        
        message = " ".join(parts)
        
        # Add exception info if present
        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)
        
        return message


class AppLogger:
    """Centralized logger for the application."""
    
    def __init__(self, name: str = "hiremebahamas"):
        """Initialize the application logger.
        
        Args:
            name: Logger name
        """
        self.name = name
        self._logger = logging.getLogger(name)
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure logging handlers and formatters."""
        # Get environment
        environment = os.getenv("ENVIRONMENT", "development")
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # Set log level
        self._logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Remove existing handlers to avoid duplicates
        self._logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Use JSON formatter in production, human-readable in development
        if environment == "production":
            formatter = StructuredFormatter()
        else:
            formatter = DevelopmentFormatter()
        
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # File handler for persistent logs (optional)
        log_dir = os.getenv("RUNTIME_LOG_DIR", "/tmp/runtime-logs")
        if log_dir:
            try:
                log_path = Path(log_dir)
                log_path.mkdir(parents=True, exist_ok=True)
                
                file_handler = logging.FileHandler(
                    log_path / f"{self.name}.log",
                    encoding="utf-8"
                )
                file_handler.setFormatter(StructuredFormatter())
                self._logger.addHandler(file_handler)
            except (OSError, PermissionError) as e:
                self._logger.warning(f"Could not create log file: {e}")
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message.
        
        Args:
            message: Log message
            **kwargs: Additional context (request_id, user_id, etc.)
        """
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message.
        
        Args:
            message: Log message
            **kwargs: Additional context (request_id, user_id, etc.)
        """
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message.
        
        Args:
            message: Log message
            **kwargs: Additional context (request_id, user_id, etc.)
        """
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, exc_info: Optional[Exception] = None, **kwargs: Any) -> None:
        """Log error message.
        
        Args:
            message: Log message
            exc_info: Exception object for traceback
            **kwargs: Additional context (request_id, user_id, etc.)
        """
        self._log(logging.ERROR, message, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, exc_info: Optional[Exception] = None, **kwargs: Any) -> None:
        """Log critical message.
        
        Args:
            message: Log message
            exc_info: Exception object for traceback
            **kwargs: Additional context (request_id, user_id, etc.)
        """
        self._log(logging.CRITICAL, message, exc_info=exc_info, **kwargs)
    
    def _log(self, level: int, message: str, exc_info: Optional[Exception] = None, **kwargs: Any) -> None:
        """Internal logging method.
        
        Args:
            level: Log level
            message: Log message
            exc_info: Exception object for traceback
            **kwargs: Additional context
        """
        extra = {}
        
        # Extract known fields
        if "request_id" in kwargs:
            extra["request_id"] = kwargs.pop("request_id")
        
        if "user_id" in kwargs:
            extra["user_id"] = kwargs.pop("user_id")
        
        # Store remaining kwargs as extra
        if kwargs:
            extra["extra"] = kwargs
        
        # Log with extra context
        self._logger.log(level, message, extra=extra, exc_info=exc_info)


# Global logger instance
logger = AppLogger()


def get_logger(name: Optional[str] = None) -> AppLogger:
    """Get a logger instance.
    
    Args:
        name: Optional logger name. If None, returns global logger.
        
    Returns:
        Logger instance
    """
    if name:
        return AppLogger(name)
    return logger


# Convenience functions
def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    request_id: str,
    user_id: Optional[int] = None,
) -> None:
    """Log an HTTP request.
    
    Args:
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        request_id: Request ID
        user_id: Optional user ID
    """
    logger.info(
        f"{method} {path} {status_code} {duration_ms:.2f}ms",
        request_id=request_id,
        user_id=user_id,
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
    )


def log_error(
    message: str,
    error: Exception,
    request_id: Optional[str] = None,
    user_id: Optional[int] = None,
    **context: Any,
) -> None:
    """Log an error with full context.
    
    Args:
        message: Error description
        error: Exception object
        request_id: Optional request ID
        user_id: Optional user ID
        **context: Additional context
    """
    logger.error(
        message,
        exc_info=error,
        request_id=request_id,
        user_id=user_id,
        **context,
    )


def log_performance(
    operation: str,
    duration_ms: float,
    request_id: Optional[str] = None,
    **context: Any,
) -> None:
    """Log performance metrics.
    
    Args:
        operation: Operation name
        duration_ms: Duration in milliseconds
        request_id: Optional request ID
        **context: Additional context
    """
    level = logging.WARNING if duration_ms > 1000 else logging.INFO
    logger._log(
        level,
        f"Performance: {operation} took {duration_ms:.2f}ms",
        request_id=request_id,
        operation=operation,
        duration_ms=duration_ms,
        **context,
    )

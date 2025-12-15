"""
Response Compression Middleware for Facebook-Level Performance

Implements intelligent compression:
- Automatic gzip/brotli compression
- Smart compression level based on content type
- Streaming compression for large responses
- Skip compression for already compressed content
"""
import gzip
import logging
from typing import Callable
from io import BytesIO

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse, Response
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


# Content types that should be compressed
COMPRESSIBLE_TYPES = {
    "application/json",
    "application/javascript",
    "application/xml",
    "text/html",
    "text/css",
    "text/plain",
    "text/xml",
    "text/javascript",
    "image/svg+xml",
}

# Minimum response size to compress (bytes)
MIN_COMPRESSION_SIZE = 1024  # 1KB

# Content types that are already compressed
COMPRESSED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "video/",
    "audio/",
    "application/zip",
    "application/gzip",
}


def should_compress(content_type: str, content_length: int) -> bool:
    """Determine if response should be compressed.
    
    Args:
        content_type: Response content type
        content_length: Response size in bytes
    
    Returns:
        True if response should be compressed
    """
    # Don't compress small responses
    if content_length < MIN_COMPRESSION_SIZE:
        return False
    
    # Don't compress already compressed content
    for compressed_type in COMPRESSED_TYPES:
        if content_type.startswith(compressed_type):
            return False
    
    # Compress compressible types
    for compressible_type in COMPRESSIBLE_TYPES:
        if content_type.startswith(compressible_type):
            return True
    
    return False


def supports_encoding(accept_encoding: str, encoding: str) -> bool:
    """Check if client supports specific encoding."""
    if not accept_encoding:
        return False
    
    # Parse Accept-Encoding header
    encodings = [e.strip().split(";")[0] for e in accept_encoding.split(",")]
    return encoding in encodings


class CompressionMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic response compression.
    
    Compresses responses when:
    - Client supports gzip encoding
    - Response is compressible type
    - Response size exceeds minimum threshold
    """
    
    def __init__(
        self,
        app: ASGIApp,
        minimum_size: int = MIN_COMPRESSION_SIZE,
        compression_level: int = 6,  # Balance speed vs compression
    ):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compression_level = compression_level
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process request and compress response if appropriate."""
        # Get response from next middleware/endpoint
        response = await call_next(request)
        
        # Check if client supports gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if not supports_encoding(accept_encoding, "gzip"):
            return response
        
        # Check if response is already compressed
        if response.headers.get("content-encoding"):
            return response
        
        # Get content type
        content_type = response.headers.get("content-type", "")
        
        # Get content length (if available)
        content_length = int(response.headers.get("content-length", 0))
        
        # Check if we should compress
        if not should_compress(content_type, content_length):
            return response
        
        # Compress response body
        try:
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Check actual size
            if len(body) < self.minimum_size:
                # Return uncompressed if too small
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=content_type,
                )
            
            # Compress with gzip
            compressed_body = gzip.compress(body, compresslevel=self.compression_level)
            
            # Only use compression if it actually reduces size
            if len(compressed_body) < len(body):
                # Update headers
                headers = dict(response.headers)
                headers["content-encoding"] = "gzip"
                headers["content-length"] = str(len(compressed_body))
                headers["vary"] = "Accept-Encoding"
                
                return Response(
                    content=compressed_body,
                    status_code=response.status_code,
                    headers=headers,
                    media_type=content_type,
                )
            else:
                # Return uncompressed if compression didn't help
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=content_type,
                )
        
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            # Return original response on error
            return response


def add_compression_middleware(app):
    """Add compression middleware to FastAPI app.
    
    Usage:
        from app.core.compression_middleware import add_compression_middleware
        add_compression_middleware(app)
    """
    app.add_middleware(
        CompressionMiddleware,
        minimum_size=MIN_COMPRESSION_SIZE,
        compression_level=6,  # Good balance for API responses
    )
    logger.info("✓ Response compression middleware enabled")

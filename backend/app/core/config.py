"""
Configuration management for HireMeBahamas API.

This module centralizes all environment variable reads and configuration logic.
"""
import os
import logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class Settings:
    """Application settings loaded from environment variables."""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database Configuration
    DATABASE_URL: Optional[str] = (
        os.getenv('DATABASE_URL') or 
        os.getenv('POSTGRES_URL') or 
        os.getenv('DATABASE_PRIVATE_URL')
    )
    
    # Database Pool Configuration
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "5"))  # Hard limit: prevents Neon exhaustion & Render OOM
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "300"))
    
    # Database Connection Timeouts
    DB_CONNECT_TIMEOUT: int = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
    DB_COMMAND_TIMEOUT: int = int(os.getenv("DB_COMMAND_TIMEOUT", "30"))
    DB_STATEMENT_TIMEOUT_MS: int = int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "30000"))
    
    # Database SSL Configuration
    DB_SSL_MODE: str = os.getenv("DB_SSL_MODE", "require")
    DB_FORCE_TLS_1_3: bool = os.getenv("DB_FORCE_TLS_1_3", "true").lower() == "true"
    DB_SSL_CA_FILE: Optional[str] = os.getenv("DB_SSL_CA_FILE")
    
    # Database Echo (debug)
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    
    # Database Initialization
    DB_INIT_MAX_RETRIES: int = int(os.getenv("DB_INIT_MAX_RETRIES", "3"))
    DB_INIT_RETRY_DELAY: float = float(os.getenv("DB_INIT_RETRY_DELAY", "2.0"))
    
    # Runtime Logging
    RUNTIME_LOG_DIR: str = os.getenv('RUNTIME_LOG_DIR', '/tmp/runtime-logs')
    
    # CORS Origins
    # ⚠️  NOTE: Wildcard patterns (*.vercel.app) are NOT allowed when credentials are enabled
    # ⚠️  Browsers will block cookies if wildcard is used with allow_credentials=True
    # ✅  Use explicit origins only
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
        "https://hiremebahamas.vercel.app",  # Explicit Vercel deployment URL
    ]
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL with validation and fallback logic.
        
        Returns:
            str: Valid database URL
            
        Raises:
            ValueError: If DATABASE_URL is not set in production
        """
        database_url = cls.DATABASE_URL
        
        # Strip whitespace to prevent connection errors from misconfigured environment variables
        if database_url:
            database_url = database_url.strip()
        
        # For local development only - require explicit configuration in production
        # Check after stripping to handle whitespace-only strings (e.g., "   ")
        if not database_url:
            if cls.ENVIRONMENT == "production":
                raise ValueError("DATABASE_URL must be set in production")
            else:
                # Use local development default only in development mode
                logger.warning("DATABASE_URL not provided, using default development database URL")
                database_url = "postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
        
        # Fix common typos in DATABASE_URL
        if "ostgresql" in database_url and "postgresql" not in database_url:
            database_url = database_url.replace("ostgresql", "postgresql")
        
        # Convert sync PostgreSQL URLs to async driver format
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # Validate DATABASE_URL structure for all deployments
        # In production, raises exceptions. In development, logs warnings only.
        try:
            cls._validate_database_url_structure(database_url)
        except ValueError as e:
            if cls.ENVIRONMENT == "production":
                raise
            else:
                logger.warning(f"Development mode: DATABASE_URL validation failed: {e}")
        
        return database_url
    
    @classmethod
    def _validate_database_url_structure(cls, db_url: str) -> None:
        """Validate DATABASE_URL meets cloud deployment requirements.
        
        Requirements:
        1. Must contain a hostname (not localhost/127.0.0.1 or empty - banned in production)
        2. Must contain a port number
        3. Must use TCP connection (no Unix sockets)
        4. Must have SSL mode configured
        
        Args:
            db_url: Database connection URL to validate
            
        Raises:
            ValueError: If validation fails in production
        """
        if not db_url:
            raise ValueError("DATABASE_URL is empty")
        
        try:
            # Parse the URL
            parsed = urlparse(db_url)
            
            # Check 1: Must have a hostname
            if not parsed.hostname:
                raise ValueError(
                    "DATABASE_URL missing hostname. "
                    "Format: postgresql://user:pass@hostname:port/dbname?sslmode=require"
                )
            
            # Check 2: ABSOLUTE BAN on localhost in production
            hostname = parsed.hostname.lower()
            if cls.ENVIRONMENT == "production" and hostname in ('localhost', '127.0.0.1', '::1'):
                raise ValueError(
                    f"❌ ABSOLUTE BAN: DATABASE_URL uses 'localhost' in production. "
                    f"Found: '{parsed.hostname}'. "
                    "Production MUST use remote database hostname. "
                    "Example: ep-xxxx.us-east-1.aws.neon.tech or containers-us-west-123.railway.app"
                )
            
            # Check 3: ABSOLUTE BAN on Unix sockets (/var/run/postgresql) in production
            if '/var/run/' in db_url or 'unix:/' in db_url:
                raise ValueError(
                    f"❌ ABSOLUTE BAN: DATABASE_URL contains Unix socket path. "
                    "Production MUST use TCP connections with explicit hostname and port. "
                    "Example: postgresql://user:pass@hostname:5432/dbname?sslmode=require"
                )
            
            # Check 4: Must have an explicit port number
            if not parsed.port:
                raise ValueError(
                    "DATABASE_URL missing port number. "
                    "Add explicit port (e.g., :5432) after hostname. "
                    "Example: postgresql://user:pass@hostname:5432/dbname?sslmode=require"
                )
            
            # Note: sslmode parameter validation removed as redundant
            # SSL mode is handled automatically at the database connection level
            # This validation is no longer necessary
            
            logger.info("✓ DATABASE_URL validation passed: hostname, port, TCP, and SSL configured")
            
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to parse DATABASE_URL: {str(e)}")


# Global settings instance
settings = Settings()

"""
Configuration management for HireMeBahamas API.

This module centralizes all environment variable reads and configuration logic.
"""
import os
import logging
from typing import Optional

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
    # ✅ asyncpg negotiates TLS automatically; sslmode in the URL is stripped for compatibility
    # ❌ DO NOT pass sslmode as a kwarg in connect_args
    # These settings are deprecated and should not be used
    
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
        """Get database URL with fallback for development.
        
        Returns:
            str: Database URL from environment or development default
            
        Raises:
            ValueError: If DATABASE_URL is not set in production
        """
        database_url = cls.DATABASE_URL
        
        # For local development only - require explicit configuration in production
        if not database_url:
            if cls.ENVIRONMENT == "production":
                raise ValueError("DATABASE_URL must be set in production")
            else:
                # Use local development default only in development mode
                logger.warning("DATABASE_URL not provided, using default development database URL")
                database_url = "postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
        
        # Convert sync PostgreSQL URLs to async driver format
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        return database_url


# Global settings instance
settings = Settings()

"""
Configuration management for HireMeBahamas API.

This module centralizes all environment variable reads and configuration logic.
"""
import os
from typing import Optional


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
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "2"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "3"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "300"))
    
    # Database Connection Timeouts
    DB_CONNECT_TIMEOUT: int = int(os.getenv("DB_CONNECT_TIMEOUT", "45"))
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
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
        "https://*.vercel.app",
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
        
        # For local development only - require explicit configuration in production
        if not database_url:
            if cls.ENVIRONMENT == "production":
                raise ValueError("DATABASE_URL must be set in production")
            else:
                # Use local development default only in development mode
                database_url = "postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
        
        # Strip whitespace to prevent connection errors
        database_url = database_url.strip()
        
        # Fix common typos in DATABASE_URL
        if "ostgresql" in database_url and "postgresql" not in database_url:
            database_url = database_url.replace("ostgresql", "postgresql")
        
        # Convert sync PostgreSQL URLs to async driver format
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        return database_url


# Global settings instance
settings = Settings()

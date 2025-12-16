"""
Configuration module for HireMeBahamas - STEP 13
Centralized configuration for JWT authentication
"""
import os

# Environment configuration
ENV = os.getenv("ENV", "production")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Redis configuration (optional, for session storage)
REDIS_URL = os.getenv("REDIS_URL")

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

# Validation: Ensure critical settings are present in production
if ENV == "production" and not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required in production")

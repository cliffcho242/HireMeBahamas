# Requirements.txt Documentation

## Overview

The root `requirements.txt` file contains all necessary Python dependencies for the HireMeBahamas application. This file is used by deployment platforms (Railway, Vercel, Render) to install the required packages.

## Critical Dependencies

### Basic FastAPI Requirements

These are the core dependencies required for FastAPI to function:

```
fastapi==0.115.6
uvicorn[standard]==0.32.0
python-multipart==0.0.20
```

- **fastapi**: The main FastAPI framework (EXPLICITLY listed in Core Framework section)
- **uvicorn**: ASGI server for running FastAPI applications
- **python-multipart**: Required for form data and file upload handling

### Authentication & JWT

For user authentication and JWT token handling:

```
python-jose[cryptography]==3.5.0
passlib[bcrypt]==1.7.4
```

- **python-jose**: JWT token creation and verification (provides the `jose` module)
- **passlib[bcrypt]**: Password hashing with bcrypt support

### Database

For PostgreSQL database connectivity:

```
sqlalchemy[asyncio]==2.0.44
psycopg2-binary==2.9.11
asyncpg==0.30.0
```

- **sqlalchemy**: ORM for database operations
- **psycopg2-binary**: PostgreSQL adapter (binary distribution, no compilation needed)
- **asyncpg**: Async PostgreSQL driver for better performance

## Deployment Notes

### Railway Deployment
- Uses Flask backend (`final_backend_postgresql.py`)
- Installs all dependencies from `requirements.txt`

### Vercel Deployment
- Uses FastAPI backend (`api/backend_app/main.py`)
- Requires `mangum==0.19.0` for serverless handler
- All packages have binary wheels for Python 3.12

## Validation

To verify that requirements.txt contains all critical dependencies, run:

```bash
python validate_requirements.py
```

This will check for:
- ✅ All basic FastAPI dependencies
- ✅ All auth/JWT dependencies
- ✅ All database dependencies
- ✅ FastAPI is explicitly listed (not commented out)

## Installation

To install all dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

For production deployment with binary-only packages:

```bash
pip install --upgrade pip
pip install --only-binary=:all: -r requirements.txt
```

## Version Pinning

All dependencies are pinned to specific versions to ensure reproducible builds and prevent unexpected breakage from package updates.

## Additional Dependencies

The requirements.txt also includes:

- **Flask** components for Railway deployment
- **Pydantic** for data validation
- **Pillow** for image processing
- **Redis** for caching (optional)
- **Cloudinary** for media storage
- And other supporting libraries

Refer to the comments in `requirements.txt` for detailed information about each dependency category.

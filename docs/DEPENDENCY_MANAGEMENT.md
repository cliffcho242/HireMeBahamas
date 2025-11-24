# Dependency Management Guide

This guide explains how to install, check, and manage dependencies for the HireMeBahamas platform.

## Quick Start

### Automatic Installation (Recommended)

**Option 1: Using the installation script (requires sudo for system dependencies)**
```bash
# Install all dependencies (backend + frontend)
sudo ./scripts/install-dependencies.sh

# Install only backend dependencies
sudo ./scripts/install-dependencies.sh --backend-only

# Install only frontend dependencies (no sudo needed)
./scripts/install-dependencies.sh --frontend-only
```

**Option 2: Using the Python checker (can auto-install)**
```bash
# Check dependencies
python3 scripts/check-dependencies.py

# Check and automatically install missing dependencies
python3 scripts/check-dependencies.py --install

# Check only backend
python3 scripts/check-dependencies.py --backend-only

# Check only frontend
python3 scripts/check-dependencies.py --frontend-only
```

### Manual Installation

#### Backend Dependencies

1. **System Dependencies (Ubuntu/Debian)**
   ```bash
   sudo apt-get update
   sudo apt-get install -y \
     build-essential \
     gcc g++ make pkg-config \
     python3 python3-pip python3-dev \
     postgresql libpq-dev \
     libssl-dev libffi-dev \
     libjpeg-dev libpng-dev libwebp-dev zlib1g-dev
   ```

2. **Python Packages**
   ```bash
   # Upgrade pip
   python3 -m pip install --upgrade pip setuptools wheel
   
   # Install test tools
   pip install pytest pytest-flask pytest-asyncio
   
   # Install backend dependencies
   pip install -r requirements.txt
   pip install -r backend/requirements.txt
   ```

#### Frontend Dependencies

1. **Node.js Installation** (if not already installed)
   ```bash
   # Install Node.js 18.x LTS
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
   sudo apt-get install -y nodejs
   ```

2. **Frontend Packages**
   ```bash
   cd frontend
   
   # Clean install (recommended if package-lock.json exists)
   npm ci
   
   # Or regular install
   npm install
   ```

## Critical Dependencies

### Backend (Python/FastAPI)

#### Core Framework
- **fastapi**: Web framework for building APIs
- **uvicorn**: ASGI server for running FastAPI
- **sqlalchemy**: ORM for database operations
- **psycopg2-binary**: PostgreSQL adapter
- **asyncpg**: Async PostgreSQL driver

#### Authentication & Security
- **python-jose[cryptography]**: JWT token handling
- **passlib[bcrypt]**: Password hashing
- **google-auth**: Google OAuth authentication
- **PyJWT**: JWT token verification (for Apple OAuth)

#### Data Validation
- **pydantic**: Data validation and settings management
- **email-validator**: Email format validation

#### Async Support
- **aiosqlite**: Async SQLite support
- **asyncpg**: Async PostgreSQL support

### Frontend (React/TypeScript)

#### Core Libraries
- **react**: UI library
- **react-dom**: React DOM rendering
- **react-router-dom**: Routing
- **typescript**: Type safety

#### State Management & Forms
- **react-hook-form**: Form handling
- **zustand**: State management

#### API & HTTP
- **axios**: HTTP client
- **@tanstack/react-query**: Data fetching and caching

#### Authentication
- **@react-oauth/google**: Google OAuth integration
- **react-apple-signin-auth**: Apple Sign-in integration

#### UI Components
- **react-hot-toast**: Toast notifications
- **@headlessui/react**: Unstyled accessible UI components
- **@heroicons/react**: Icon library
- **framer-motion**: Animation library

#### Build Tools
- **vite**: Build tool and dev server
- **tailwindcss**: CSS framework

## Verification

### Verify Backend Installation

```bash
# Run dependency checker
python3 scripts/check-dependencies.py --backend-only

# Test backend imports manually
python3 -c "
from app.core.security import create_access_token
from app.models import User
from app.api.auth import router
print('✓ All backend modules loaded successfully')
"
```

### Verify Frontend Installation

```bash
# Run dependency checker
python3 scripts/check-dependencies.py --frontend-only

# Or check manually
cd frontend
npm list --depth=0
```

## Troubleshooting

### Backend Issues

**Issue: `ImportError: No module named 'jose'`**
```bash
pip install python-jose[cryptography]
```

**Issue: `pg_config executable not found`**
```bash
sudo apt-get install -y libpq-dev python3-dev
pip install psycopg2-binary
```

**Issue: `error: command 'gcc' failed`**
```bash
sudo apt-get install -y build-essential python3-dev
```

**Issue: Google OAuth imports fail**
```bash
pip install google-auth google-auth-oauthlib
```

### Frontend Issues

**Issue: `npm ERR! ERESOLVE unable to resolve dependency tree`**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

**Issue: `Module not found: Can't resolve '@react-oauth/google'`**
```bash
cd frontend
npm install @react-oauth/google
```

**Issue: TypeScript errors**
```bash
cd frontend
npm install --save-dev typescript @types/react @types/react-dom
```

## CI/CD Integration

The project includes automated dependency checking in GitHub Actions:

- **Workflow**: `.github/workflows/dependency-check.yml`
- **Triggers**: On push/PR to main, or manual workflow dispatch
- **Actions**:
  1. Installs system dependencies
  2. Installs Python and Node.js packages
  3. Verifies critical imports
  4. Generates dependency report

## Environment Setup

After installing dependencies, configure your environment:

1. **Backend Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your settings (database URL, secret keys, etc.)
   ```

2. **Frontend Configuration**
   ```bash
   cd frontend
   cp .env.example .env
   # Edit .env with API endpoints and OAuth client IDs
   ```

## Testing Dependencies

### Run Backend Tests
```bash
# All tests
python -m pytest backend/test_app.py -v

# Registration tests
python -m pytest test_registration.py -v

# Database integrity tests
python -m pytest backend/test_database_integrity.py -v
```

### Run Frontend Tests
```bash
cd frontend

# Lint
npm run lint

# Build
npm run build

# Type check
npm run type-check  # if available
```

## Updating Dependencies

### Backend
```bash
# Update a specific package
pip install --upgrade fastapi

# Update all packages (be careful!)
pip install --upgrade -r requirements.txt
```

### Frontend
```bash
cd frontend

# Update a specific package
npm update react

# Update all packages
npm update

# Check for outdated packages
npm outdated
```

## Security Considerations

1. **Regular Updates**: Keep dependencies updated to patch security vulnerabilities
2. **Dependency Scanning**: Use tools like `npm audit` and `safety` for Python
3. **Lock Files**: Commit `package-lock.json` and consider using `Pipfile.lock`
4. **Environment Variables**: Never commit secrets; use `.env` files (gitignored)

## Support

If you encounter issues with dependencies:

1. Check this guide's troubleshooting section
2. Run the dependency checker: `python3 scripts/check-dependencies.py`
3. Review the GitHub Actions logs for CI failures
4. Check package compatibility in requirements files

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Guide](https://vitejs.dev/guide/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

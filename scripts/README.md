# Scripts Directory

This directory contains automated dependency management and system maintenance scripts for HireMeBahamas.

## Quick Reference

### One-Click Setup (Recommended)

```bash
# Unix/Linux/macOS
./scripts/one_click_setup.sh

# Windows
scripts\one_click_setup.bat
```

This will install ALL dependencies, configure services, and verify everything automatically.

## Available Scripts

### Dependency Management

#### `check_dependencies.py`
**Purpose**: Comprehensive dependency verification system

**Usage**:
```bash
python scripts/check_dependencies.py
```

**What it checks**:
- ✅ Python packages (Flask, CORS, Limiter, etc.)
- ✅ Redis connection and latency
- ✅ Database connectivity (PostgreSQL/SQLite)
- ✅ Sentry SDK configuration
- ✅ Socket.IO availability
- ✅ Frontend dependencies
- ✅ Environment variables

**Output**: Creates `dependency_check_report.json`

**Exit codes**:
- `0` = All critical dependencies active
- `1` = Some dependencies missing

---

#### `activate_all_dependencies.py`
**Purpose**: Automatically install and activate all dependencies

**Usage**:
```bash
python scripts/activate_all_dependencies.py
```

**What it does**:
- 📦 Installs Python packages from requirements.txt
- ⚙️  Creates .env file with defaults
- 🔴 Tests Redis connection
- 🗄️  Verifies database setup
- 🎨 Installs frontend dependencies
- 📊 Generates activation report

---

#### `startup_init.py`
**Purpose**: Pre-startup dependency verification

**Usage**:
```bash
python scripts/startup_init.py
```

**When to use**:
- Before starting the application
- In deployment scripts
- As part of health checks

**What it does**:
- Verifies critical dependencies
- Initializes database connections
- Connects to Redis
- Sends startup notification to Sentry
- Logs all active dependencies

---

### Self-Healing & Recovery

#### `auto_recover.py`
**Purpose**: Self-healing system for service failures

**Usage**:
```bash
python scripts/auto_recover.py
```

**When to use**:
- After deployment
- When services become unresponsive
- As a cron job for monitoring

**What it does**:
- 🔍 Monitors Redis health
- 🔍 Monitors database health
- 🔍 Checks dependency integrity
- 🔄 Reinstalls corrupted packages
- 🔄 Clears cache on failures
- 🚨 Sends alerts to Sentry

---

### Configuration

#### `setup_env.py`
**Purpose**: Generate secure environment configuration

**Usage**:
```bash
python scripts/setup_env.py
```

**What it does**:
- 🔐 Generates secure SECRET_KEY
- 📝 Creates .env file with defaults
- ⚙️  Preserves existing values
- 📚 Adds helpful comments
- ✅ Ensures .env in .gitignore

**Generated variables**:
- `SECRET_KEY` - Auto-generated
- `FLASK_ENV` - Development/production
- `DATABASE_URL` - PostgreSQL (optional)
- `REDIS_URL` - Redis cache (optional)
- `SENTRY_DSN` - Error tracking (optional)

---

### Health Monitoring

#### `health_endpoint.py`
**Purpose**: Health check endpoint handler for Flask

**Usage**: Import in main application
```python
from scripts.health_endpoint import create_health_endpoint
create_health_endpoint(app)
```

**Endpoints created**:
- `GET /api/health` - Basic health check
- `GET /api/health/dependencies` - Comprehensive status

---

## Frontend Scripts

### `frontend/scripts/validate-deps.js`
**Purpose**: Validate frontend Node.js dependencies

**Usage**:
```bash
cd frontend
node scripts/validate-deps.js
```

**What it checks**:
- 📦 npm packages from package.json
- 📦 node_modules directory
- 📦 Critical dependencies (React, Socket.IO, etc.)
- 📦 TypeScript compilation
- 📦 Vite configuration
- 📦 Sentry integration
- 📦 PWA setup

**Features**:
- Auto-installs missing dependencies
- Generates JSON report
- Exit codes for CI/CD

---

## Setup Scripts

### `one_click_setup.sh` (Unix/Linux/macOS)
**Purpose**: Complete automated setup

**Steps performed**:
1. Install Python dependencies
2. Activate all dependencies
3. Install frontend dependencies
4. Run startup checks
5. Verify everything

**Usage**:
```bash
chmod +x scripts/one_click_setup.sh
./scripts/one_click_setup.sh
```

---

### `one_click_setup.bat` (Windows)
**Purpose**: Complete automated setup for Windows

**Usage**:
```cmd
scripts\one_click_setup.bat
```

Same functionality as .sh version but for Windows.

---

## Common Workflows

### First Time Setup
```bash
# 1. One-click setup (recommended)
./scripts/one_click_setup.sh

# OR manual setup
python scripts/activate_all_dependencies.py
python scripts/setup_env.py
python scripts/check_dependencies.py
```

### Daily Development
```bash
# Check status before starting work
python scripts/check_dependencies.py

# If issues found
python scripts/auto_recover.py
```

### Deployment
```bash
# 1. Install dependencies
python scripts/activate_all_dependencies.py

# 2. Verify everything
python scripts/check_dependencies.py

# 3. Start application (it runs startup checks)
python final_backend_postgresql.py
```

### Troubleshooting
```bash
# 1. Check what's wrong
python scripts/check_dependencies.py

# 2. Try auto-recovery
python scripts/auto_recover.py

# 3. Re-activate if needed
python scripts/activate_all_dependencies.py

# 4. Verify fix
python scripts/check_dependencies.py
```

---

## Environment Variables

### Required (auto-generated with defaults)
None! Everything works out of the box.

### Recommended for Production
```bash
SECRET_KEY=your-secure-key
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379
SENTRY_DSN=https://your-dsn@sentry.io/project
```

Use `scripts/setup_env.py` to generate these.

---

## Exit Codes

All scripts use standard exit codes:
- `0` = Success
- `1` = Failure or warnings

Use in CI/CD pipelines:
```bash
python scripts/check_dependencies.py
if [ $? -eq 0 ]; then
    echo "All dependencies OK"
else
    echo "Dependency issues found"
    exit 1
fi
```

---

## Cron Jobs

### Periodic Health Checks
```bash
# Check dependencies every 5 minutes
*/5 * * * * cd /path/to/project && python scripts/check_dependencies.py

# Auto-recover daily
0 0 * * * cd /path/to/project && python scripts/auto_recover.py
```

---

## CI/CD Integration

See `.github/workflows/dependencies-check.yml` for automated CI/CD checks.

The workflow runs on:
- Every push
- Every pull request
- Daily at midnight
- Manual trigger

---

## Logging

All scripts log to console with emoji indicators:
- ✅ Success
- ❌ Error
- ⚠️  Warning
- ℹ️  Info

Reports are saved as JSON for programmatic access.

---

## Support

### Common Issues

**Issue**: Missing dependencies
**Solution**: `python scripts/activate_all_dependencies.py`

**Issue**: Redis not available
**Solution**: App will use in-memory cache automatically

**Issue**: PostgreSQL connection failed
**Solution**: App will fall back to SQLite automatically

**Issue**: Permission denied
**Solution**: `chmod +x scripts/*.sh scripts/*.py`

### Getting Help

1. Check `dependency_check_report.json`
2. Review application logs
3. Run `python scripts/auto_recover.py`
4. See main documentation in `AUTOMATED_DEPENDENCIES.md`

---

## Contributing

When adding new dependencies:
1. Add to requirements.txt or package.json
2. Update check_dependencies.py
3. Test with `python scripts/check_dependencies.py`
4. Update documentation

---

**Last Updated**: 2025-01-20  
**Maintainer**: HireMeBahamas Development Team

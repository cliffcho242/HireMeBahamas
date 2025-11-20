# Automated Dependencies System Documentation

## Overview

The HireMeBahamas application now features a comprehensive automated dependency activation and verification system that ensures all dependencies are properly installed, enabled, active, and configured with **zero manual intervention** required.

## System Architecture

The automated dependency system consists of several interconnected components:

### Core Scripts

1. **`scripts/check_dependencies.py`** - Comprehensive dependency checker
2. **`scripts/activate_all_dependencies.py`** - Automatic dependency installer and activator
3. **`scripts/startup_init.py`** - Application startup initialization
4. **`scripts/auto_recover.py`** - Self-healing and auto-recovery system
5. **`scripts/setup_env.py`** - Environment configuration generator
6. **`frontend/scripts/validate-deps.js`** - Frontend dependency validator

### Setup Scripts

- **`scripts/one_click_setup.sh`** - Unix/Linux/macOS one-click setup
- **`scripts/one_click_setup.bat`** - Windows one-click setup

### Integration

- **`scripts/health_endpoint.py`** - Health check endpoint handler
- **`.github/workflows/dependencies-check.yml`** - CI/CD automated checks

## Quick Start

### One-Click Setup (Recommended)

#### Unix/Linux/macOS:
```bash
chmod +x scripts/one_click_setup.sh
./scripts/one_click_setup.sh
```

#### Windows:
```cmd
scripts\one_click_setup.bat
```

This single command will:
1. ✅ Install all Python dependencies
2. ✅ Configure environment variables
3. ✅ Install frontend dependencies
4. ✅ Verify all services
5. ✅ Generate dependency reports

### Manual Setup

If you prefer step-by-step setup:

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Activate all dependencies
python scripts/activate_all_dependencies.py

# 3. Setup environment
python scripts/setup_env.py

# 4. Install frontend dependencies (if applicable)
cd frontend
npm install
cd ..

# 5. Verify everything
python scripts/check_dependencies.py
```

## Script Details

### 1. Check Dependencies (`check_dependencies.py`)

**Purpose**: Verifies all dependencies are installed and active.

**Features**:
- ✅ Checks Python packages and versions
- ✅ Validates Flask extensions (CORS, Limiter, Caching)
- ✅ Tests Redis connection and latency
- ✅ Verifies database connectivity (PostgreSQL/SQLite)
- ✅ Checks Sentry SDK configuration
- ✅ Validates Socket.IO availability
- ✅ Tests Celery workers (if configured)
- ✅ Checks frontend dependencies
- ✅ Auto-fixes common issues (creates .env if missing)
- ✅ Generates comprehensive JSON report

**Usage**:
```bash
python scripts/check_dependencies.py
```

**Exit Codes**:
- `0` - All critical dependencies active
- `1` - Some dependencies missing or inactive

**Output**: Creates `dependency_check_report.json` with detailed status.

### 2. Activate All Dependencies (`activate_all_dependencies.py`)

**Purpose**: Automatically installs and activates all dependencies.

**Features**:
- 🔧 Installs Python packages from requirements.txt
- 🔧 Creates .env file with safe defaults
- 🔧 Initializes Redis connection
- 🔧 Sets up database connections
- 🔧 Configures Flask extensions
- 🔧 Tests Sentry integration
- 🔧 Installs frontend dependencies
- 🔧 Generates activation report

**Usage**:
```bash
python scripts/activate_all_dependencies.py
```

**What it does**:
1. Runs `pip install -r requirements.txt`
2. Creates `.env` from `.env.example` or generates new one
3. Tests Redis and database connections
4. Runs `npm install` in frontend directory
5. Reports success/failure for each step

### 3. Startup Initialization (`startup_init.py`)

**Purpose**: Runs on application startup to verify readiness.

**Features**:
- 🚀 Checks critical dependencies before app starts
- 🚀 Initializes database connections
- 🚀 Connects to Redis cache
- 🚀 Warms up application cache
- 🚀 Initializes Sentry error tracking
- 🚀 Logs all active dependencies with versions
- 🚀 Prevents startup if critical dependencies missing

**Usage**:
```python
# In your main application file
from scripts.startup_init import startup_check

if not startup_check():
    print("Critical dependencies missing - cannot start")
    sys.exit(1)

# Continue with app initialization
app = Flask(__name__)
# ...
```

**Or run standalone**:
```bash
python scripts/startup_init.py
```

### 4. Auto Recovery (`auto_recover.py`)

**Purpose**: Self-healing system that monitors and recovers from failures.

**Features**:
- 🔄 Monitors Redis health
- 🔄 Monitors database health
- 🔄 Checks dependency integrity
- 🔄 Auto-restarts failed services
- 🔄 Reinstalls corrupted packages
- 🔄 Clears cache on Redis failure
- 🔄 Falls back to SQLite if PostgreSQL unavailable
- 🔄 Sends alerts to Sentry for critical failures

**Usage**:
```bash
python scripts/auto_recover.py
```

**When to use**:
- After deployment
- When services become unresponsive
- In monitoring/health check scripts
- As a cron job for periodic checks

### 5. Setup Environment (`setup_env.py`)

**Purpose**: Generates secure .env configuration file.

**Features**:
- 🔐 Generates secure SECRET_KEY
- 🔐 Creates .env with safe defaults
- 🔐 Preserves existing values
- 🔐 Adds comments and documentation
- 🔐 Ensures .env in .gitignore

**Usage**:
```bash
python scripts/setup_env.py
```

**Generated Configuration**:
- `SECRET_KEY` - Auto-generated secure key
- `FLASK_ENV` - Development/production mode
- `DATABASE_URL` - PostgreSQL connection (optional)
- `REDIS_URL` - Redis connection (optional)
- `SENTRY_DSN` - Error tracking (optional)
- Security settings (cookies, CORS, etc.)

### 6. Frontend Validator (`validate-deps.js`)

**Purpose**: Validates frontend Node.js dependencies.

**Features**:
- 📦 Checks npm packages from package.json
- 📦 Validates node_modules directory
- 📦 Tests critical dependencies (React, Socket.IO, etc.)
- 📦 Checks TypeScript compilation
- 📦 Validates Vite configuration
- 📦 Verifies Sentry integration
- 📦 Checks PWA service workers
- 📦 Auto-installs missing dependencies

**Usage**:
```bash
cd frontend
node scripts/validate-deps.js
```

## Health Check Endpoints

### Basic Health Check

**Endpoint**: `GET /api/health`

**Response**:
```json
{
  "status": "healthy",
  "message": "HireMeBahamas API is running",
  "timestamp": "2025-01-20T04:20:13Z"
}
```

### Comprehensive Dependency Health

**Endpoint**: `GET /api/health/dependencies`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T04:20:13Z",
  "dependencies": {
    "backend": {
      "flask": {"active": true, "version": "2.3.3"},
      "redis": {"active": true, "connected": true, "latency_ms": 2},
      "database": {"active": true, "connected": true, "type": "postgresql"},
      "sentry": {"active": true, "dsn_configured": true},
      "socketio": {"active": true, "clients_connected": 0},
      "celery": {"active": false, "installed": true, "workers": 0}
    },
    "frontend": {
      "react": {"active": true, "version": "18.2.0"},
      "socketio_client": {"active": true, "connected": false},
      "sentry": {"active": false, "initialized": false}
    }
  },
  "missing_dependencies": [],
  "inactive_services": ["celery"]
}
```

## CI/CD Integration

### GitHub Actions Workflow

The system includes automated CI/CD checks that run on:
- Every push to `main` or `develop`
- Every pull request
- Daily at 00:00 UTC
- Manual trigger via `workflow_dispatch`

**Workflow Jobs**:

1. **check-python-dependencies**
   - Installs Python dependencies
   - Runs dependency checker
   - Uploads report artifacts
   - Comments on PRs if failures detected

2. **check-frontend-dependencies**
   - Installs Node.js dependencies
   - Validates frontend dependencies
   - Tests TypeScript compilation
   - Runs build process

3. **test-integrations**
   - Spins up Redis and PostgreSQL services
   - Tests service connections
   - Runs full dependency check with live services

4. **security-check**
   - Runs `safety` to check for vulnerable packages
   - Reports security issues

5. **report-status**
   - Aggregates all job results
   - Reports overall status

## Environment Variables

### Required Variables

None! The system works with defaults.

### Recommended Variables

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Database (optional - uses SQLite if not set)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis (optional - uses memory cache if not set)
REDIS_URL=redis://localhost:6379

# Sentry (optional - local logging if not set)
SENTRY_DSN=https://your-dsn@sentry.io/project
```

## Graceful Degradation

The system is designed to work even when optional services fail:

| Service | If Unavailable | Behavior |
|---------|---------------|----------|
| **Redis** | Uses in-memory cache | ✅ Works with SimpleCache |
| **PostgreSQL** | Falls back to SQLite | ✅ Works in dev mode |
| **Sentry** | Uses local logging | ✅ Logs to console/file |
| **Socket.IO** | Disables real-time | ✅ Works without WebSocket |
| **Celery** | Runs tasks inline | ✅ Works without background jobs |

## Troubleshooting

### Issue: Dependencies not installing

**Solution**:
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt --verbose
```

### Issue: Redis connection failed

**Solution**:
```bash
# Check if Redis is running
redis-cli ping

# Start Redis (Linux/macOS)
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:alpine
```

**Or**: The app will automatically fall back to in-memory cache.

### Issue: PostgreSQL connection failed

**Solution**:
```bash
# Check connection
psql $DATABASE_URL

# Or let the app use SQLite
unset DATABASE_URL
```

### Issue: Frontend dependencies not installing

**Solution**:
```bash
cd frontend

# Clear cache
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Or use yarn
yarn install
```

### Issue: Permission denied on scripts

**Solution**:
```bash
# Make scripts executable
chmod +x scripts/*.sh scripts/*.py
chmod +x frontend/scripts/*.js
```

## Monitoring and Alerts

### Continuous Monitoring

Set up a cron job to periodically check health:

```bash
# Add to crontab (check every 5 minutes)
*/5 * * * * /path/to/python /path/to/scripts/check_dependencies.py
```

### Sentry Integration

If Sentry is configured, the system automatically sends:
- Startup notifications
- Dependency failures
- Service recovery alerts
- Critical errors

## Best Practices

### Development

1. ✅ Run `python scripts/check_dependencies.py` before starting work
2. ✅ Use `python scripts/activate_all_dependencies.py` after pulling changes
3. ✅ Check `/api/health/dependencies` endpoint regularly
4. ✅ Review `dependency_check_report.json` for issues

### Production

1. ✅ Run health checks in CI/CD pipeline
2. ✅ Monitor `/api/health/dependencies` endpoint
3. ✅ Set up alerts for dependency failures
4. ✅ Schedule periodic `auto_recover.py` runs
5. ✅ Keep dependencies up-to-date

### Deployment

1. ✅ Run `one_click_setup.sh` on new servers
2. ✅ Configure production environment variables
3. ✅ Enable Sentry for error tracking
4. ✅ Set up Redis for production caching
5. ✅ Use PostgreSQL instead of SQLite

## Performance

The dependency system is optimized for speed:

- ⚡ Dependency checks complete in < 5 seconds
- ⚡ Health endpoint responds in < 100ms
- ⚡ Auto-recovery runs in < 10 seconds
- ⚡ Setup script completes in < 2 minutes

## Support

### Getting Help

1. Check this documentation
2. Review `dependency_check_report.json`
3. Check application logs
4. Run `python scripts/auto_recover.py`
5. Check GitHub Actions workflow logs

### Reporting Issues

When reporting issues, include:
- Output of `python scripts/check_dependencies.py`
- Contents of `dependency_check_report.json`
- Environment variables (redacted)
- Error messages from logs

## Version Compatibility

| Component | Minimum Version | Recommended |
|-----------|----------------|-------------|
| Python | 3.8 | 3.12 |
| Node.js | 16 | 20 LTS |
| Redis | 6.0 | 7.0 |
| PostgreSQL | 12 | 15 |
| Flask | 2.0 | 2.3.3 |

## Success Metrics

After setup, you should see:

- ✅ All critical dependencies: **ACTIVE**
- ✅ Health endpoint: **RESPONDING**
- ✅ Build process: **SUCCESSFUL**
- ✅ Tests: **PASSING**
- ✅ No missing dependencies
- ✅ All services connected

## Future Enhancements

Planned improvements:
- 🔮 Real-time dependency monitoring dashboard
- 🔮 Automatic dependency updates
- 🔮 Advanced alerting system
- 🔮 Performance metrics tracking
- 🔮 Dependency vulnerability scanning
- 🔮 Custom health check plugins

---

**Last Updated**: 2025-01-20  
**Version**: 1.0.0  
**Maintainer**: HireMeBahamas Development Team

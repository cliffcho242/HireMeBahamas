# Health Check System - Quick Reference

## Overview

The HireMeBahamas health check system provides comprehensive automated monitoring of your deployment infrastructure, database connectivity, environment configuration, and API endpoints.

## Components

### 1. Health Check Script (`scripts/health_check.py`)

A comprehensive Python script that checks:
- ✅ Database connectivity and performance
- ✅ Environment variable configuration
- ✅ File structure integrity
- ✅ API endpoint availability
- ✅ Deployment platform detection

### 2. GitHub Actions Workflow (`.github/workflows/health-check.yml`)

Automated workflow that:
- 🔄 Runs daily at 6 AM UTC
- ⚡ Can be triggered manually
- 📊 Generates detailed reports
- 🚨 Creates GitHub issues on critical failures
- 📈 Provides job summaries in GitHub Actions

## Usage

### Local Usage

```bash
# Run all health checks
python scripts/health_check.py

# Run with verbose output
python scripts/health_check.py --verbose

# Check specific category
python scripts/health_check.py --check files
python scripts/health_check.py --check environment
python scripts/health_check.py --check database
python scripts/health_check.py --check api

# Check deployed application
python scripts/health_check.py --url https://your-app.vercel.app

# Get JSON output (useful for CI/CD)
python scripts/health_check.py --format json
python scripts/health_check.py --format json > health-report.json
```

### GitHub Actions

#### Manual Trigger

1. Go to [Actions](../../actions/workflows/health-check.yml)
2. Click "Run workflow"
3. Optionally:
   - Enter deployment URL to check
   - Select specific check category
4. Click "Run workflow"

#### View Results

- **Latest status badge**: ![Health Check](https://github.com/cliffcho242/HireMeBahamas/actions/workflows/health-check.yml/badge.svg)
- **All runs**: [Health Check Workflow](../../actions/workflows/health-check.yml)
- **Job Summary**: Available in each workflow run
- **Report Artifact**: Download JSON report from workflow artifacts

## Check Categories

### Files Check (`--check files`)

Verifies presence of critical files:
- `api/index.py` - Main API entry point
- `api/requirements.txt` - API dependencies
- `frontend/package.json` - Frontend dependencies
- `vercel.json` - Vercel configuration

### Environment Check (`--check environment`)

Validates environment variables:
- **Critical**: `DATABASE_URL`, `SECRET_KEY`
- **Optional**: `JWT_SECRET_KEY`, `PORT`, `ENVIRONMENT`
- Checks for weak/default secret values
- Validates DATABASE_URL format
- Detects deployment platform (Railway, Vercel, Render, Local)

### Database Check (`--check database`)

Tests database connectivity:
- Connection test with timeout
- Query performance measurement
- Connection string validation
- Response time monitoring

**Requirements**: `asyncpg` must be installed

### API Check (`--check api`)

Tests remote API endpoints (requires `--url`):
- `/api/health` - Health endpoint
- `/api/status` - Status endpoint
- `/api/ready` - Readiness endpoint
- Response time measurement
- JSON response validation

**Requirements**: `requests` must be installed

## Output Formats

### Text Format (Default)

Colored, human-readable output:
```
🏥 HireMeBahamas Health Check
============================================================

📁 FILE STRUCTURE
------------------------------------------------------------
✅ File: api/index.py: Found - Main API entry point
...

📊 HEALTH CHECK SUMMARY
============================================================
Total Checks: 7
✅ Passed: 6
⚠️  Warnings: 1
```

### JSON Format

Structured output for automation:
```json
{
  "timestamp": 1234567890,
  "summary": {
    "total": 7,
    "passed": 6,
    "warned": 1,
    "failed": 0
  },
  "checks": [
    {
      "name": "File: api/index.py",
      "status": "pass",
      "message": "Found - Main API entry point",
      "details": {...},
      "duration_ms": null,
      "timestamp": 1234567890
    }
  ]
}
```

## Exit Codes

- `0` - All checks passed or warnings only
- `1` - Critical failures detected
- `130` - Interrupted by user (Ctrl+C)

## Status Values

- `pass` ✅ - Check passed successfully
- `warn` ⚠️ - Non-critical issue detected
- `fail` ❌ - Critical issue detected

## Automated Monitoring

### Schedule

The workflow runs automatically:
- **Daily**: 6:00 AM UTC
- **On push**: When workflow or health check files change
- **Manual**: Via GitHub Actions UI

### Failure Handling

When critical failures are detected:

1. **GitHub Issue Created**:
   - Title: "🚨 Automated Health Check Failed"
   - Labels: `health-check`, `automated`, `critical`, `bug`
   - Contains: Failed checks, warnings, and troubleshooting steps

2. **Job Summary**:
   - Detailed breakdown in GitHub Actions
   - Failed checks highlighted
   - Response times shown

3. **Artifact**:
   - JSON report uploaded
   - Available for 30 days
   - Can be downloaded for analysis

## Integration with Deployment

### Pre-Deployment Check

Run before deploying to catch issues early:
```bash
# Check environment configuration
python scripts/health_check.py --check environment

# Check database connectivity
python scripts/health_check.py --check database
```

### Post-Deployment Verification

Verify deployment after pushing to production:
```bash
# Check deployed application
python scripts/health_check.py --url https://your-app.vercel.app
```

### CI/CD Integration

In your CI/CD pipeline:
```yaml
- name: Health Check
  run: |
    python scripts/health_check.py --format json > health-report.json
    
- name: Upload Health Report
  uses: actions/upload-artifact@v4
  with:
    name: health-report
    path: health-report.json
```

## Dependencies

### Required

None - basic checks work without dependencies

### Optional

- `requests` - For remote API checks
- `asyncpg` - For database connectivity tests

Install with:
```bash
pip install requests asyncpg
```

## Troubleshooting

### Common Issues

**"asyncpg not installed"**
```bash
pip install asyncpg
```

**"requests library not available"**
```bash
pip install requests
```

**Database connection failed**
- Verify `DATABASE_URL` is set correctly
- Check database is running and accessible
- Verify connection string format
- Check firewall/network settings

**Environment variables not found**
- Set required variables in your environment
- Check `.env` file if using one
- Verify variables in deployment platform (Vercel/Railway)

### Debug Mode

Use verbose flag for detailed output:
```bash
python scripts/health_check.py --verbose
```

## Links

- **Workflow**: [.github/workflows/health-check.yml](../.github/workflows/health-check.yml)
- **Script**: [scripts/health_check.py](../scripts/health_check.py)
- **Latest Results**: [GitHub Actions](../../actions/workflows/health-check.yml)
- **Badge**: ![Health Check](https://github.com/cliffcho242/HireMeBahamas/actions/workflows/health-check.yml/badge.svg)

## Related Tools

- **Vercel Diagnostic Tool**: `diagnostic/check_vercel_connection.py`
- **Railway PostgreSQL Check**: `railway_postgres_check.py`
- **Startup Validation**: `validate_startup.py`
- **Vercel Postgres Migration**: `scripts/verify_vercel_postgres_migration.py`

## Support

For issues or questions:
1. Check [workflow logs](../../actions/workflows/health-check.yml)
2. Review [deployment guides](../DEPLOYMENT_GUIDE.md)
3. Open an issue with health check results

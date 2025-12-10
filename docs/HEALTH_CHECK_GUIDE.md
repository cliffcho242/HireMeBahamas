# Health Check Guide

Complete guide to understanding and using the automated health check pipeline for HireMeBahamas.

## Table of Contents

- [Overview](#overview)
- [Running Health Checks](#running-health-checks)
- [Understanding Results](#understanding-results)
- [Troubleshooting](#troubleshooting)
- [Adding Custom Checks](#adding-custom-checks)
- [CI/CD Integration](#cicd-integration)

## Overview

The automated health check pipeline validates the entire deployment stack before production deployment. It runs automatically every 6 hours and can be triggered manually or on pull requests.

### What Gets Checked

1. **Environment Configuration** - Validates environment variables and secrets
2. **Database Connectivity** - Tests PostgreSQL connection and queries
3. **Deployment Status** - Checks frontend and backend accessibility
4. **Security Audit** - Scans for security issues and misconfigurations
5. **Integration Tests** - Runs the test suite to verify functionality

### When Checks Run

- **Automatically**: Every 6 hours via scheduled workflow
- **On Pull Requests**: When opening or updating PRs to main
- **Manual Trigger**: Via GitHub Actions UI
- **Pre-Deployment**: As a prerequisite for deployment workflows

## Running Health Checks

### Local Pre-Deployment Check

Run this before pushing changes to catch issues early:

```bash
# Run all checks
python scripts/pre_deployment_check.py

# Verbose output
python scripts/pre_deployment_check.py --verbose

# Check specific component
python scripts/pre_deployment_check.py --check environment
python scripts/pre_deployment_check.py --check database
python scripts/pre_deployment_check.py --check security
```

### Quick Readiness Check

Shell script for fast system validation:

```bash
# Run all checks
./scripts/deployment_readiness.sh

# Verbose mode
./scripts/deployment_readiness.sh --verbose

# Quick check (skip database test)
./scripts/deployment_readiness.sh --quick
```

### Manual GitHub Workflow Trigger

1. Go to **Actions** tab in GitHub
2. Select **Automated Health Check Pipeline**
3. Click **Run workflow**
4. Select branch and options
5. Click **Run workflow** button

### In CI/CD Pipeline

Health checks run automatically as part of:
- Pull request validation
- Pre-deployment checks
- Scheduled monitoring

## Understanding Results

### Status Indicators

- ✅ **PASSING** - All checks passed, safe to deploy
- ⚠️ **WARNING** - Some warnings detected, review before deploying
- ❌ **FAILING** - Critical issues found, do NOT deploy

### Check Details

#### Environment Configuration

Validates:
- `DATABASE_URL` format and SSL mode
- `SECRET_KEY` is not using defaults
- `JWT_SECRET_KEY` is properly configured
- No placeholder values in secrets

**Example Output:**
```
✅ DATABASE_URL: Valid PostgreSQL format
✅ SSL Mode: Enabled (sslmode=require)
✅ SECRET_KEY: Custom value configured
✅ JWT_SECRET_KEY: Custom value configured

Result: 4/4 critical checks passed
```

#### Database Connectivity

Tests:
- Connection to PostgreSQL database
- Query execution
- Table access and permissions
- Response time measurement

**Example Output:**
```
✅ Connection successful (45ms)
✅ Query test passed
✅ Found 12 tables in database

Status: ✅ PASSED
```

#### Deployment Status

Checks:
- Frontend accessibility (if configured)
- Backend API endpoints
- Response times
- CORS configuration

**Example Output:**
```
✅ Frontend accessible
   Response time: 0.12s

✅ /api/health endpoint accessible
   Response time: 0.08s
```

#### Security Audit

Scans for:
- Hardcoded secrets in code
- SSL/TLS enforcement
- JWT configuration
- Rate limiting setup
- CSP headers

**Example Output:**
```
✅ No hardcoded secrets detected
✅ SSL/TLS enforcement found in configuration
✅ JWT algorithm configured
✅ Rate limiting configured

Overall Status: ✅ PASSED
```

#### Integration Tests

Runs:
- Existing test suite
- Authentication flow tests
- Data persistence validation
- API endpoint tests

**Example Output:**
```
✅ Tests executed: 24
✅ Passed: 24

Status: ✅ PASSED
```

### GitHub Actions Summary

After each run, check the workflow summary:

1. Go to **Actions** → **Automated Health Check Pipeline**
2. Click on the latest run
3. View the **Summary** section
4. Review individual job details

### Health Check Issues

Failed checks automatically create GitHub issues:

- **Standard Issues**: Created for general failures
- **Critical Issues**: Created for database or security failures
- **Auto-Closed**: Issues close when checks pass

## Troubleshooting

### Common Issues and Solutions

#### DATABASE_URL Not Set

**Problem:**
```
❌ DATABASE_URL: Not configured
```

**Solution:**
1. Add `DATABASE_URL` to GitHub Secrets
2. For Railway: Use Railway's injected `DATABASE_URL`
3. For Vercel: Use Vercel Postgres connection string
4. Ensure format: `postgresql://user:password@host:port/database?sslmode=require`

#### Database Connection Failed

**Problem:**
```
❌ Connection failed: could not connect to server
```

**Solutions:**
1. Verify database is running (not sleeping)
2. Check firewall/network settings
3. Validate DATABASE_URL format
4. Test connection manually:
   ```bash
   python railway_postgres_check.py
   ```

#### SSL/TLS Not Enforced

**Problem:**
```
⚠️ SSL Mode: Not explicitly required in DATABASE_URL
```

**Solution:**
Add `?sslmode=require` to your DATABASE_URL:
```
postgresql://user:pass@host:5432/db?sslmode=require
```

#### Hardcoded Secrets Detected

**Problem:**
```
⚠️ Found potential hardcoded secrets in 2 file(s)
```

**Solutions:**
1. Use environment variables:
   ```python
   SECRET_KEY = os.environ.get('SECRET_KEY')
   ```
2. Remove hardcoded values
3. Add sensitive files to `.gitignore`
4. Rotate compromised secrets

#### Integration Tests Failed

**Problem:**
```
⚠️ Some tests failed, check logs
```

**Solutions:**
1. Review test output in workflow logs
2. Run tests locally:
   ```bash
   pytest -v
   ```
3. Fix failing tests before deploying
4. Ensure test database is properly configured

### Debugging Steps

1. **Check Workflow Logs**
   - Go to Actions → Failed workflow
   - Click on failed job
   - Review detailed logs

2. **Run Local Checks**
   ```bash
   python scripts/pre_deployment_check.py --verbose
   ```

3. **Validate Environment**
   ```bash
   python validate_startup.py
   ```

4. **Test Database**
   ```bash
   python railway_postgres_check.py
   ```

5. **Check Vercel Connection** (if using Vercel)
   ```bash
   python diagnostic/check_vercel_connection.py
   ```

## Adding Custom Checks

### Add Check to Workflow

Edit `.github/workflows/health-check.yml`:

```yaml
custom-check:
  name: Custom Check
  runs-on: ubuntu-latest
  timeout-minutes: 5
  outputs:
    status: ${{ steps.check.outputs.status }}
  
  steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Run Custom Check
      id: check
      run: |
        echo "🔍 Running custom check..."
        
        # Your check logic here
        if [ condition ]; then
          echo "✅ Check passed" >> $GITHUB_STEP_SUMMARY
          echo "status=passed" >> $GITHUB_OUTPUT
        else
          echo "❌ Check failed" >> $GITHUB_STEP_SUMMARY
          echo "status=failed" >> $GITHUB_OUTPUT
          exit 1
        fi
```

### Add Check to Local Script

Edit `scripts/pre_deployment_check.py`:

```python
def check_custom(verbose: bool = False) -> tuple[int, int, int]:
    """
    Custom health check.
    Returns (passed, warnings, errors)
    """
    print_header("Custom Check")
    
    passed = 0
    warnings = 0
    errors = 0
    
    # Your check logic
    if condition:
        print_success("Custom check passed")
        passed += 1
    else:
        print_error("Custom check failed")
        errors += 1
    
    return (passed, warnings, errors)
```

Then add to `main()`:

```python
if args.check is None or args.check == 'custom':
    p, w, e = check_custom(args.verbose)
    total_passed += p
    total_warnings += w
    total_errors += e
```

## CI/CD Integration

### Pre-Deployment Requirements

Make health check a prerequisite for deployments:

Edit deployment workflow (e.g., `deploy-backend.yml`):

```yaml
jobs:
  health-check:
    uses: ./.github/workflows/health-check.yml
  
  deploy:
    needs: health-check
    if: needs.health-check.outputs.status == 'passed'
    runs-on: ubuntu-latest
    steps:
      # deployment steps...
```

### Pull Request Integration

Health checks run automatically on PRs and post results as comments:

```markdown
## ✅ Health Check PASSED

🟢 **Overall Status:** PASSED

**Results:** 5/5 checks passed
**Timestamp:** 2025-12-10 02:30:00 UTC

### Check Details
✅ Environment Configuration
✅ Database Connectivity
✅ Deployment Status
✅ Security Audit
✅ Integration Tests

[View full results](...)
```

### Issue Management

- **Failed Checks**: Automatically create issues with `health-check-failure` label
- **Critical Failures**: Create issues with `critical` label and assign maintainers
- **Resolved Issues**: Auto-close when checks pass

### Notifications

Configure notifications in `.github/workflows/health-check-alert.yml` to:
- Create GitHub issues
- Assign to maintainers
- Include diagnostic information

## Best Practices

1. **Run Locally First**
   - Use `scripts/pre_deployment_check.py` before pushing
   - Fix issues locally to save CI time

2. **Monitor Regularly**
   - Check scheduled run results
   - Address warnings promptly
   - Keep issues up to date

3. **Keep Secrets Secure**
   - Never commit secrets to code
   - Rotate secrets if exposed
   - Use GitHub Secrets for sensitive data

4. **Update Documentation**
   - Document custom checks
   - Update troubleshooting guide
   - Share solutions with team

5. **Review Before Deploy**
   - Always check health status
   - Address critical issues immediately
   - Don't deploy with failing checks

## Performance Targets

- **Complete Runtime**: < 5 minutes
- **Database Response**: < 1 second
- **API Response**: < 2 seconds
- **False Positive Rate**: < 1%

## Support

For help with health checks:

1. Check this guide
2. Review [existing issues](https://github.com/cliffcho242/HireMeBahamas/issues?q=label%3Ahealth-check-failure)
3. Run diagnostic scripts
4. Create an issue with logs

## Related Documentation

- [Railway PostgreSQL Setup](../RAILWAY_POSTGRES_QUICKFIX.md)
- [Deployment Guide](../DEPLOYMENT_GUIDE.md)
- [Pre-Flight Checks](../.github/workflows/preflight-check.yml)
- [Recovery Workflow](../.github/workflows/recovery.yml)

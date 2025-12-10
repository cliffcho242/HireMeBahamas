# HireMeBahamas Connection Diagnostic Tool

Comprehensive diagnostic tool to test and verify Vercel deployment connections for both frontend and backend.

## Overview

This tool performs automated checks on your HireMeBahamas Vercel deployment to ensure:
- Frontend is accessible and properly deployed
- Backend API endpoints are responding correctly
- Database connections are working
- Environment variables are configured
- Security settings are properly set

## Installation

1. Install Python dependencies:
```bash
pip install -r diagnostic/requirements.txt
```

Or install globally with:
```bash
pip install requests urllib3
```

## Usage

### Basic Usage

Test your production deployment:
```bash
python diagnostic/check_vercel_connection.py --url https://your-app.vercel.app
```

### Verbose Mode

Enable detailed logging to see request/response details:
```bash
python diagnostic/check_vercel_connection.py --url https://your-app.vercel.app --verbose
```

### Save Results to File

Save diagnostic results for sharing or analysis:
```bash
python diagnostic/check_vercel_connection.py --url https://your-app.vercel.app --output report.txt
```

### Test Specific Deployment

Test a specific Vercel preview deployment:
```bash
python diagnostic/check_vercel_connection.py --url https://hiremebahamas-git-branch-user.vercel.app
```

## What It Checks

### 📱 Frontend Tests
- ✅ Frontend URL is accessible
- ✅ Static assets load correctly
- ✅ Index.html contains React app markup
- ✅ No 404 errors on root path

### 🔧 Backend API Tests
- ✅ `/api/health` endpoint responds
- ✅ `/api/status` endpoint shows backend status
- ✅ `/api/ready` endpoint shows database status
- ✅ Proper JSON responses
- ✅ Response times < 5 seconds (with warnings for slow responses)

### ⚙️ Configuration Verification
- ✅ `vercel.json` routing is correct (inferred from API responses)
- ✅ `api/index.py` handler is properly configured
- ✅ Frontend API URL detection logic works
- ✅ CORS configuration is correct

### 💾 Database Connection
- ✅ Database URL is configured
- ✅ Database connection succeeds
- ✅ Can execute simple queries
- ✅ SSL mode is set correctly

### 🔐 Security
- ✅ JWT_SECRET_KEY is set (not default)
- ✅ SECRET_KEY is set (not default)
- ✅ Environment variables are properly configured

## Output Format

The tool provides color-coded output for easy scanning:

```
🔍 HireMeBahamas Connection Diagnostic
============================================================
Testing deployment: https://your-app.vercel.app

📱 FRONTEND TESTS
----------------------------------------
✅ Frontend accessible at: https://your-app.vercel.app
✅ React app detected
✅ Static assets endpoint responding
✅ No routing errors on root path

🔧 BACKEND API TESTS
----------------------------------------
✅ /api/health: Status 200 (120ms)
   - Backend: available
   - Database: connected
   - Platform: vercel-serverless

✅ /api/status: Status 200 (85ms)
   - Backend loaded: True
   - Capabilities: auth, posts, jobs, users, messages, notifications

✅ /api/ready: Status 200 (450ms)
   - Database: connected
   - Status: ready

⚙️  CONFIGURATION
----------------------------------------
✅ vercel.json: Routing configured correctly
✅ CORS: Properly configured
✅ Frontend API: Auto-detection should work

💾 DATABASE
----------------------------------------
✅ DATABASE_URL: Configured
✅ Connection: Successful
✅ SSL Mode: Configured correctly
✅ Query test: Passed

🔐 SECURITY
----------------------------------------
✅ JWT_SECRET_KEY: Set (not default)
✅ SECRET_KEY: Set (not default)
✅ ENVIRONMENT: Backend operational

📊 SUMMARY
========================================
✅ All systems operational (24/24 checks passed)
✅ Frontend-Backend connection: Working
✅ Database: Connected
✅ Ready for production use

Deployment URL: https://your-app.vercel.app
Health Check: https://your-app.vercel.app/api/health
```

## Error Handling

When errors occur, the tool provides:
- ❌ Clear error message
- 💡 Suggested fixes
- 📚 Links to documentation

Example error output:
```
❌ /api/health: Connection timeout
   Error: Request timeout after 60 seconds
   
💡 TROUBLESHOOTING SUGGESTIONS
========================================

🔧 Backend API Issues:
   • Verify DATABASE_URL is set in Vercel environment variables
   • Check Vercel function logs for errors
   • Ensure api/index.py is deployed correctly
   • Verify all Python dependencies are in requirements.txt
   • Check if serverless function is timing out (30s limit)

📚 Documentation: docs/BACKEND_CONNECTION_TROUBLESHOOTING.md
```

## Understanding Results

### Exit Codes
- `0` - All checks passed, deployment is healthy
- `1` - One or more checks failed
- `130` - Interrupted by user (Ctrl+C)

### Response Times
- **< 1 second**: Excellent (typical for health endpoints)
- **1-5 seconds**: Good (acceptable for API endpoints)
- **> 5 seconds**: Slow (may indicate cold start or performance issue)

The tool automatically warns about slow responses and includes timing information in verbose mode.

### Cold Starts

Vercel serverless functions have "cold starts" - the first request after inactivity can take 30-60 seconds. The diagnostic tool:
- Uses 60-second timeout to handle cold starts
- Implements retry logic for transient failures
- Reports actual response times for performance monitoring

## Common Issues and Solutions

### Frontend Not Accessible
**Symptoms**: 404 or connection error on root URL

**Solutions**:
1. Check Vercel build logs for build failures
2. Verify `vercel.json` has correct `outputDirectory`
3. Ensure frontend build completes successfully
4. Check `buildCommand` in `vercel.json`

### API Endpoints Not Responding
**Symptoms**: 404, 500, or timeout on /api/* endpoints

**Solutions**:
1. Verify `DATABASE_URL` is set in Vercel environment variables
2. Check Vercel function logs for Python errors
3. Ensure all dependencies are in `requirements.txt`
4. Verify `api/index.py` exists and is correct
5. Check if function is timing out (30s Vercel limit)

### Database Connection Failed
**Symptoms**: Database shows as "unavailable" or "error"

**Solutions**:
1. Ensure `DATABASE_URL` environment variable is set in Vercel
2. Verify database credentials are correct
3. Check if database accepts connections from Vercel IPs
4. Ensure `sslmode=require` is in DATABASE_URL
5. Verify database service is running

### JWT/Secret Keys Using Defaults
**Symptoms**: Security check shows "using default"

**Solutions**:
1. Set `JWT_SECRET_KEY` in Vercel environment variables
2. Set `SECRET_KEY` in Vercel environment variables
3. Use strong, random values (not "dev-secret-key-change-in-production")
4. Redeploy after setting environment variables

## Advanced Usage

### Testing Multiple Deployments

Test both production and preview:
```bash
# Test production
python diagnostic/check_vercel_connection.py --url https://hiremebahamas.com

# Test preview deployment
python diagnostic/check_vercel_connection.py --url https://hiremebahamas-git-feature.vercel.app
```

### Automated Monitoring

Use in CI/CD or monitoring scripts:
```bash
#!/bin/bash
if python diagnostic/check_vercel_connection.py --url https://your-app.vercel.app; then
    echo "✅ Deployment healthy"
else
    echo "❌ Deployment has issues - check logs"
    exit 1
fi
```

### Debugging with Verbose Mode

When troubleshooting issues, use verbose mode:
```bash
python diagnostic/check_vercel_connection.py \
  --url https://your-app.vercel.app \
  --verbose \
  --output debug-report.txt
```

This will:
- Show all HTTP requests and responses
- Display detailed timing information
- Show response headers and status codes
- Save everything to a file for analysis

## Integration with CI/CD

Add to your GitHub Actions workflow:

```yaml
name: Test Deployment
on:
  deployment_status:

jobs:
  test:
    runs-on: ubuntu-latest
    if: github.event.deployment_status.state == 'success'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r diagnostic/requirements.txt
      
      - name: Run diagnostic
        run: |
          python diagnostic/check_vercel_connection.py \
            --url ${{ github.event.deployment_status.target_url }} \
            --output deployment-test.txt
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: diagnostic-results
          path: deployment-test.txt
```

## Troubleshooting the Diagnostic Tool

### ImportError: No module named 'requests'
Install dependencies:
```bash
pip install -r diagnostic/requirements.txt
```

### Invalid URL Error
Ensure URL includes protocol:
```bash
# ❌ Wrong
python diagnostic/check_vercel_connection.py --url hiremebahamas.com

# ✅ Correct
python diagnostic/check_vercel_connection.py --url https://hiremebahamas.com
```

### SSL Certificate Errors
Update CA certificates:
```bash
pip install --upgrade certifi
```

## Support

For issues with the diagnostic tool or deployment:
1. Check the output for specific error messages
2. Run with `--verbose` flag for detailed logs
3. Review [BACKEND_CONNECTION_TROUBLESHOOTING.md](../docs/BACKEND_CONNECTION_TROUBLESHOOTING.md)
4. Check Vercel function logs in Vercel dashboard
5. Review GitHub issues for similar problems

## Development

### Running Tests
```bash
# Test against local development server
python diagnostic/check_vercel_connection.py --url http://localhost:3000 --verbose

# Test error handling
python diagnostic/check_vercel_connection.py --url https://invalid-url-that-does-not-exist.vercel.app
```

### Contributing

Improvements welcome! Key areas:
- Additional diagnostic checks
- Better error messages and suggestions
- Performance optimizations
- Enhanced reporting formats

## Version History

### v1.0.0 (Current)
- Initial release
- Frontend health checks
- Backend API health checks
- Database connection tests
- Configuration verification
- Security checks
- Colored terminal output
- Verbose mode
- File output support
- Comprehensive error handling
- Retry logic for cold starts
- Detailed troubleshooting suggestions

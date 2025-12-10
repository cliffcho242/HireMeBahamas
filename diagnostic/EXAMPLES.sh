#!/bin/bash
#
# Example usage of the Vercel Connection Diagnostic Tool
# 
# This script demonstrates different ways to run the diagnostic tool
# and shows expected output formats.
#

echo "=================================================="
echo "Vercel Connection Diagnostic Tool - Examples"
echo "=================================================="
echo ""

# Example 1: Basic usage
echo "Example 1: Basic Usage"
echo "----------------------"
echo "Command:"
echo "  python diagnostic/check_vercel_connection.py --url https://hiremebahamas.vercel.app"
echo ""
echo "This will:"
echo "  - Test frontend accessibility"
echo "  - Check all backend API endpoints"
echo "  - Verify database connections"
echo "  - Validate security configuration"
echo ""

# Example 2: Verbose mode
echo "Example 2: Verbose Mode (Detailed Logging)"
echo "-------------------------------------------"
echo "Command:"
echo "  python diagnostic/check_vercel_connection.py --url https://hiremebahamas.vercel.app --verbose"
echo ""
echo "This will:"
echo "  - Show all HTTP requests being made"
echo "  - Display response times for each request"
echo "  - Include detailed error messages"
echo "  - Show API response data"
echo ""

# Example 3: Save to file
echo "Example 3: Save Results to File"
echo "--------------------------------"
echo "Command:"
echo "  python diagnostic/check_vercel_connection.py --url https://hiremebahamas.vercel.app --output results.txt"
echo ""
echo "This will:"
echo "  - Run all diagnostic checks"
echo "  - Save results to results.txt"
echo "  - Useful for sharing or analysis"
echo ""

# Example 4: Test preview deployment
echo "Example 4: Test Preview Deployment"
echo "-----------------------------------"
echo "Command:"
echo "  python diagnostic/check_vercel_connection.py --url https://hiremebahamas-git-feature.vercel.app"
echo ""
echo "This will:"
echo "  - Test a specific preview deployment"
echo "  - Useful for testing before merging"
echo ""

# Example 5: Combined options
echo "Example 5: Combined Options"
echo "---------------------------"
echo "Command:"
echo "  python diagnostic/check_vercel_connection.py \\"
echo "    --url https://hiremebahamas.vercel.app \\"
echo "    --verbose \\"
echo "    --output deployment-test.txt"
echo ""
echo "This will:"
echo "  - Run with verbose logging"
echo "  - Save detailed results to file"
echo "  - Perfect for troubleshooting"
echo ""

# Example 6: Multiple deployments
echo "Example 6: Test Multiple Deployments"
echo "-------------------------------------"
echo "Script:"
cat << 'EOF'
#!/bin/bash
for url in \
  "https://hiremebahamas.vercel.app" \
  "https://hiremebahamas-staging.vercel.app" \
  "https://hiremebahamas-preview.vercel.app"
do
  echo "Testing $url..."
  python diagnostic/check_vercel_connection.py --url "$url" --output "test-$(basename $url).txt"
  echo ""
done
EOF
echo ""

# Example 7: CI/CD integration
echo "Example 7: CI/CD Integration (GitHub Actions)"
echo "----------------------------------------------"
echo "GitHub Actions workflow snippet:"
cat << 'EOF'
name: Test Deployment
on: [deployment_status]

jobs:
  test:
    runs-on: ubuntu-latest
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
            --output diagnostic-report.txt
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: diagnostic-results
          path: diagnostic-report.txt
EOF
echo ""

# Example 8: Expected output
echo "Example 8: Expected Output (Success)"
echo "-------------------------------------"
cat << 'EOF'
🔍 HireMeBahamas Connection Diagnostic
============================================================
Testing deployment: https://hiremebahamas.vercel.app

📱 FRONTEND TESTS
----------------------------------------
✅ Frontend accessible at: https://hiremebahamas.vercel.app
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

Deployment URL: https://hiremebahamas.vercel.app
Health Check: https://hiremebahamas.vercel.app/api/health
EOF
echo ""

echo "=================================================="
echo "For more information, see:"
echo "  diagnostic/README.md"
echo "=================================================="

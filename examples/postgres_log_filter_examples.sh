#!/bin/bash
# PostgreSQL Log Filter - Usage Examples
# =======================================
# This script demonstrates various ways to use the PostgreSQL log filter tool.
#
# Requirements:
#   - Python 3.6+ (use 'python3' or 'python' depending on your system)
#   - jq (for JSON processing in examples)
#
# Note: This script uses 'python3' by default. If your system uses 'python',
#       modify the PYTHON variable below.

set -e  # Exit on error

# Python executable - change to 'python' if needed
PYTHON="${PYTHON:-python3}"

echo "PostgreSQL Log Filter - Usage Examples"
echo "======================================"
echo ""

# Create sample log file
SAMPLE_LOGS=$(cat <<'EOF'
{"message":"2025-12-10 02:55:37.131 UTC [6] LOG:  database system is ready to accept connections","attributes":{"level":"error"},"timestamp":"2025-12-10T02:55:37.553Z"}
{"message":"2025-12-10 02:55:37.234 UTC [7] LOG:  autovacuum launcher started","attributes":{"level":"error"},"timestamp":"2025-12-10T02:55:37.234Z"}
{"message":"2025-12-10 02:55:38.456 UTC [10] ERROR:  relation \"users\" does not exist","attributes":{"level":"error"},"timestamp":"2025-12-10T02:55:38.456Z"}
{"message":"2025-12-10 02:55:39.123 UTC [11] WARNING:  deprecated configuration parameter","attributes":{"level":"warning"},"timestamp":"2025-12-10T02:55:39.123Z"}
{"message":"2025-12-10 03:00:00.000 UTC [8] LOG:  checkpoint starting: time","attributes":{"level":"error"},"timestamp":"2025-12-10T03:00:00.000Z"}
{"message":"2025-12-10 03:00:05.000 UTC [8] LOG:  checkpoint complete: wrote 42 buffers","attributes":{"level":"error"},"timestamp":"2025-12-10T03:00:05.000Z"}
{"message":"2025-12-10 03:02:00.000 UTC [12] FATAL:  password authentication failed for user \"testuser\"","attributes":{"level":"error"},"timestamp":"2025-12-10T03:02:00.000Z"}
EOF
)

# Example 1: Basic filtering (correct log levels)
echo "Example 1: Basic filtering - Correct log levels"
echo "------------------------------------------------"
echo "Command: $PYTHON filter_postgres_logs.py"
echo ""
echo "$SAMPLE_LOGS" | $PYTHON filter_postgres_logs.py | head -3
echo "..."
echo ""

# Example 2: Suppress benign messages
echo "Example 2: Suppress benign messages - Only show real errors/warnings"
echo "---------------------------------------------------------------------"
echo "Command: $PYTHON filter_postgres_logs.py --suppress-benign"
echo ""
echo "$SAMPLE_LOGS" | $PYTHON filter_postgres_logs.py --suppress-benign
echo ""

# Example 3: Statistics
echo "Example 3: Show statistics"
echo "--------------------------"
echo "Command: $PYTHON filter_postgres_logs.py --stats"
echo ""
echo "$SAMPLE_LOGS" | $PYTHON filter_postgres_logs.py --stats
echo ""

# Example 4: Real-world scenario - Docker Compose logs
echo "Example 4: Filter Docker Compose PostgreSQL logs"
echo "-------------------------------------------------"
echo "Command: docker-compose -f docker-compose.local.yml logs postgres 2>&1 | $PYTHON filter_postgres_logs.py --suppress-benign"
echo ""
echo "This would show only real PostgreSQL errors from your local Docker setup."
echo ""

# Example 5: Save filtered logs to file
echo "Example 5: Save filtered logs to file"
echo "--------------------------------------"
echo "Command: echo \"\$SAMPLE_LOGS\" | $PYTHON filter_postgres_logs.py > filtered_logs.json"
echo ""
echo "$SAMPLE_LOGS" | $PYTHON filter_postgres_logs.py > /tmp/filtered_logs.json
echo "✅ Saved to /tmp/filtered_logs.json"
ls -lh /tmp/filtered_logs.json
echo ""

# Example 6: Count real errors
echo "Example 6: Count real errors (excluding benign messages)"
echo "--------------------------------------------------------"
echo "Command: echo \"\$SAMPLE_LOGS\" | $PYTHON filter_postgres_logs.py --suppress-benign | wc -l"
echo ""
ERROR_COUNT=$(echo "$SAMPLE_LOGS" | $PYTHON filter_postgres_logs.py --suppress-benign | wc -l)
echo "Found $ERROR_COUNT real error(s)/warning(s)"
echo ""

# Example 7: Extract only error messages
echo "Example 7: Extract only actual ERROR messages"
echo "----------------------------------------------"
echo "Command: echo \"\$SAMPLE_LOGS\" | $PYTHON filter_postgres_logs.py --suppress-benign | jq 'select(.attributes.level == \"error\")'"
echo ""
echo "$SAMPLE_LOGS" | $PYTHON filter_postgres_logs.py --suppress-benign | jq 'select(.attributes.level == "error")'
echo ""

# Example 8: Check if there are any real errors
echo "Example 8: Check if there are any real errors (exit code based)"
echo "---------------------------------------------------------------"
echo "Command: echo \"\$SAMPLE_LOGS\" | $PYTHON filter_postgres_logs.py --suppress-benign | grep -q ERROR && echo 'Errors found!' || echo 'No errors'"
echo ""
if echo "$SAMPLE_LOGS" | $PYTHON filter_postgres_logs.py --suppress-benign | grep -q "ERROR"; then
    echo "⚠️ Real errors found in logs!"
else
    echo "✅ No real errors in logs"
fi
echo ""

# Example 9: Pretty print filtered logs
echo "Example 9: Pretty print filtered logs"
echo "--------------------------------------"
echo "Command: echo \"\$SAMPLE_LOGS\" | $PYTHON filter_postgres_logs.py --suppress-benign | jq ."
echo ""
echo "$SAMPLE_LOGS" | $PYTHON filter_postgres_logs.py --suppress-benign | jq . | head -20
echo "..."
echo ""

# Example 10: Monitor logs in real-time
echo "Example 10: Monitor logs in real-time (simulated)"
echo "------------------------------------------------"
echo "Command: tail -f app.log | $PYTHON filter_postgres_logs.py --suppress-benign"
echo ""
echo "This would monitor your application logs in real-time and show only real errors."
echo "(Use Ctrl+C to stop when running for real)"
echo ""

# Summary
echo "Summary"
echo "======="
echo "✅ All examples completed successfully!"
echo ""
echo "Common use cases:"
echo "  1. Filter Render/cloud platform logs"
echo "  2. Monitor local development logs"
echo "  3. Alert only on real errors (not benign messages)"
echo "  4. Generate statistics for log analysis"
echo "  5. Integration with monitoring systems"
echo ""
echo "See POSTGRES_LOG_FILTER_QUICK_REF.md for more details."

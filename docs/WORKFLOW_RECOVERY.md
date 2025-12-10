# Workflow Health Check and Recovery System

This document explains the new CI/CD resilience and automated recovery mechanisms added to prevent and handle the cascading workflow failures.

## Overview

The system consists of three main components:

1. **Pre-Flight Health Check** - Validates environment before workflows run
2. **Workflow Failure Recovery** - Automatically handles and recovers from failures
3. **Enhanced CI Pipeline** - Improved resilience with retry logic and better error reporting

## Components

### 1. Pre-Flight Health Check (`.github/workflows/preflight-check.yml`)

**Triggers:**
- Pull requests to `main`
- Pushes to `main`
- Manual workflow dispatch

**What it does:**
- ✅ Validates required files exist
- ✅ Checks Python syntax
- ✅ Validates Node.js configuration
- ✅ Checks for known breaking patterns
- ✅ Validates database connection patterns
- ✅ Creates GitHub issues on persistent failures

**Output:**
- Fast failure with clear error messages
- Prevents problematic code from entering the pipeline
- Workflow summary with pass/fail status

### 2. Workflow Failure Recovery (`.github/workflows/recovery.yml`)

**Triggers:**
- Automatically when CI workflow completes (success or failure)

**What it does:**

#### For Failures:
- 📊 Analyzes failure patterns using GitHub API
- 🔄 Automatically retries transient failures (up to 3 attempts)
- 🐛 Creates GitHub issues for persistent failures (>2 failed jobs)
- 📢 Sends notifications for critical failures (>5 failed jobs)

#### For Successes:
- ✅ Auto-closes resolved CI failure issues
- 💬 Adds success comment to closed issues

**Transient Error Detection:**
- Identifies installation and setup job failures
- Limits retries to reasonable thresholds (≤3 failed jobs)
- Avoids excessive retries on persistent issues

### 3. Enhanced CI Pipeline (`.github/workflows/ci.yml`)

**New Features:**

#### Smoke Tests Job
- Runs first before all other jobs
- Validates critical files exist
- Checks Python syntax without dependencies
- Fast failure to prevent wasted resources

#### Circuit Breaker
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```
- Prevents multiple workflows from cascading
- Cancels older runs when new commits are pushed

#### Retry Logic
All dependency installation steps now include automatic retries:
```yaml
for i in 1 2 3; do
  if npm ci; then
    echo "✅ Dependencies installed successfully"
    break
  else
    if [ $i -eq 3 ]; then
      echo "::error::❌ Failed after 3 attempts"
      exit 1
    fi
    echo "⚠️  Attempt $i failed, retrying..."
    sleep 5
  fi
done
```

#### Database Connection Improvements
- Waits for PostgreSQL to be ready (up to 30 seconds)
- Retries connections on temporary failures
- Uses correct credentials (testuser, not root)

#### Error Annotations
Clear error messages with troubleshooting guidance:
```
::error::API tests failed. Common issues:
::error::- Database connection problems (check credentials)
::error::- Missing dependencies (check requirements.txt)
::error::- Import errors (check module paths)
```

#### Job Dependencies
All jobs depend on `smoke-tests` passing first:
```yaml
needs: smoke-tests
```

## Usage

### For Developers

**When a PR fails:**
1. Check the workflow summary for specific errors
2. Look for error annotations in the logs
3. Follow the troubleshooting guidance provided
4. If it's a transient error, the system will auto-retry

**To test locally:**
```bash
# Run Python syntax validation
python3 -m py_compile api/index.py

# Check for known issues
grep -r "from backend_app import" api/

# Validate package.json
node -e "JSON.parse(require('fs').readFileSync('frontend/package.json', 'utf8'))"
```

### For Maintainers

**Monitor recovery system:**
1. Check for auto-created issues with label `ci-failure`
2. Review retry attempts in workflow logs
3. Monitor notifications for critical failures

**Adjust retry behavior:**
Edit `.github/workflows/recovery.yml`:
- Change max retries: `if (recentRetries.length < 3)`
- Adjust failure threshold: `analysis.total_failed > 2`
- Modify transient detection logic in `Analyze Failure Pattern` step

**Customize health checks:**
Edit `.github/workflows/preflight-check.yml`:
- Add new file validations
- Update breaking pattern checks
- Customize error messages

## Benefits

### Reduced Noise
- ❌ Before: 2,548+ failing runs
- ✅ After: Transient failures auto-retry, only real issues reported

### Faster Debugging
- Clear error messages with context
- Specific troubleshooting steps
- Workflow annotations

### Prevented Cascades
- Circuit breaker stops old runs
- Smoke tests catch issues early
- Pre-flight checks block bad code

### Automated Recovery
- Auto-retry transient failures
- Auto-create issues for problems
- Auto-close issues when fixed

## Monitoring

### Key Metrics to Track
1. **Retry Success Rate**: How many retries succeed?
2. **Issue Creation Rate**: How many auto-created issues?
3. **Time to Recovery**: How long until failures are fixed?
4. **False Positive Rate**: How many issues were transient?

### Where to Look
- **GitHub Actions**: Check workflow runs and job logs
- **Issues Tab**: Filter by `ci-failure`, `automated` labels
- **Workflow Summaries**: Check step summaries for details

## Troubleshooting

### Pre-Flight Check Fails
1. Review the specific check that failed
2. Fix the identified issue locally
3. Run validation commands locally before pushing
4. Push the fix

### Auto-Retry Not Working
1. Check if max retries exceeded (3 attempts)
2. Verify the failure is classified as transient
3. Review the `Analyze Failure Pattern` output

### Issues Not Auto-Closing
1. Verify the commit SHA matches
2. Check that the workflow succeeded
3. Ensure the issue has correct labels

## Configuration Files

| File | Purpose | Key Settings |
|------|---------|-------------|
| `.github/workflows/preflight-check.yml` | Pre-flight validation | File checks, syntax validation |
| `.github/workflows/recovery.yml` | Failure recovery | Retry logic, issue creation |
| `.github/workflows/ci.yml` | CI pipeline | Smoke tests, retries, annotations |

## Support

For issues with the recovery system:
1. Check workflow logs for error messages
2. Review auto-created GitHub issues
3. Check workflow summaries for diagnostics
4. Contact the team if issues persist

## Future Improvements

Potential enhancements:
- [ ] Machine learning for better transient error detection
- [ ] Slack/email notifications for critical failures
- [ ] Dashboard for recovery metrics
- [ ] Automatic PR comments with failure analysis
- [ ] Historical failure pattern analysis

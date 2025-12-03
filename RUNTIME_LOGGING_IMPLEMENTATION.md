# Runtime Logging Implementation

## Overview
This document explains the runtime logging implementation added to the HireMeBahamas project to address the "There are no runtime logs in this time range" issue.

## Problem
The CI workflow was creating a `/tmp/runtime-logs` directory but no logs were being written there. This caused monitoring systems looking for runtime logs to report "no runtime logs in this time range" errors.

## Solution
We implemented conditional file-based logging that:
1. Checks if the runtime logs directory exists (`/tmp/runtime-logs` by default)
2. If it exists, adds a FileHandler to write logs to files in that directory
3. If it doesn't exist, continues with stdout/stderr logging only (no changes to production behavior)

## Implementation Details

### Environment Variable
- `RUNTIME_LOG_DIR`: Path to the runtime logs directory (default: `/tmp/runtime-logs`)

### Log Files Generated
When the runtime logs directory exists:
- `backend-runtime.log`: Logs from the FastAPI backend (backend/app/main.py)
- `api-runtime.log`: Logs from the Vercel API handler (api/index.py)

### Modified Files

#### 1. backend/app/main.py
Added conditional file handler before `logging.basicConfig()`:

```python
runtime_log_dir = os.getenv('RUNTIME_LOG_DIR', '/tmp/runtime-logs')
log_handlers = [logging.StreamHandler()]

if os.path.exists(runtime_log_dir):
    runtime_log_file = os.path.join(runtime_log_dir, 'backend-runtime.log')
    try:
        file_handler = logging.FileHandler(runtime_log_file, mode='a')
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        log_handlers.append(file_handler)
    except Exception as e:
        print(f"Warning: Could not create runtime log file: {e}")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=log_handlers
)
```

#### 2. api/index.py
Same implementation as backend/app/main.py, but writes to `api-runtime.log`.

#### 3. .github/workflows/ci.yml
Added to both `test-api` and `test-backend` jobs:

**Environment Variable:**
```yaml
env:
  RUNTIME_LOG_DIR: /tmp/runtime-logs
```

**Directory Creation:**
```yaml
- name: Create runtime directories
  run: |
    mkdir -p /tmp/runtime-logs
    touch /tmp/runtime-logs/.gitkeep
```

**Artifact Upload:**
```yaml
- name: Upload runtime logs
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: backend-runtime-logs  # or api-runtime-logs
    path: /tmp/runtime-logs/
    if-no-files-found: ignore
    retention-days: 7
```

## Benefits

### For CI/CD
- Runtime logs are now captured during test runs
- Logs are uploaded as artifacts for debugging failed tests
- 7-day retention allows post-mortem analysis

### For Production
- No impact on production deployments (no runtime logs directory exists)
- Continues logging to stdout/stderr for Railway/Render log aggregation
- Can be enabled in production by setting RUNTIME_LOG_DIR and creating the directory

### For Development
- Developers can enable file logging by creating `/tmp/runtime-logs`
- Useful for local debugging and testing
- No changes needed to existing development workflows

## Usage

### In CI/CD
The runtime logs are automatically generated during test runs. To view them:
1. Go to the GitHub Actions run
2. Click on the job (e.g., "test-backend" or "test-api")
3. Scroll to "Artifacts" section
4. Download "backend-runtime-logs" or "api-runtime-logs"

### In Local Development
To enable file-based logging locally:

```bash
# Create the runtime logs directory
mkdir -p /tmp/runtime-logs

# Run your application
# Logs will now be written to /tmp/runtime-logs/backend-runtime.log
python backend/app/main.py

# View the logs
tail -f /tmp/runtime-logs/backend-runtime.log
```

### In Production (Optional)
To enable file logging in production:

```bash
# In Railway/Render environment variables
RUNTIME_LOG_DIR=/tmp/runtime-logs

# In your start command or Dockerfile
mkdir -p /tmp/runtime-logs
```

**Note:** For most production deployments, stdout/stderr logging (the default) is preferred as it integrates with platform log aggregation systems.

## Testing
A test suite is provided in `test_runtime_logging.py` that validates:
1. Logs are written when the directory exists
2. Logging works without file handler when directory is missing
3. RUNTIME_LOG_DIR environment variable is respected

Run tests:
```bash
python test_runtime_logging.py
```

## Troubleshooting

### Logs Not Being Generated
1. Verify the runtime logs directory exists:
   ```bash
   ls -la /tmp/runtime-logs/
   ```

2. Check that RUNTIME_LOG_DIR is set (if using custom location):
   ```bash
   echo $RUNTIME_LOG_DIR
   ```

3. Verify the application has write permissions:
   ```bash
   touch /tmp/runtime-logs/test.log
   ```

### Logs Empty or Missing in CI
1. Check the "Create runtime directories" step ran successfully
2. Verify the tests actually ran and generated logs
3. Check the artifact upload step didn't fail

### Production Impact Concerns
The implementation is designed to have **zero impact** on production:
- Only adds file handler if directory exists
- Falls back to stdout/stderr if directory missing or file creation fails
- No performance overhead when file logging is disabled

## Future Enhancements
Potential improvements for consideration:
1. Log rotation (prevent unlimited growth)
2. Compression of archived logs
3. Integration with centralized logging systems
4. Structured logging (JSON format)
5. Log level configuration per environment

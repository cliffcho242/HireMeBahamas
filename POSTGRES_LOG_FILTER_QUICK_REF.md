# PostgreSQL Log Filter Quick Reference

## Overview

The `filter_postgres_logs.py` script corrects PostgreSQL log level miscategorization issues where Render's managed PostgreSQL logs informational messages as "error" level.

## Quick Start

### Basic Usage

```bash
# Filter logs and correct levels
cat logs.json | python filter_postgres_logs.py

# Suppress benign messages (only show real errors)
cat logs.json | python filter_postgres_logs.py --suppress-benign

# Show statistics
cat logs.json | python filter_postgres_logs.py --stats
```

### Common Scenarios

#### 1. Render Logs Analysis

```bash
# Download logs from Render and filter them
render logs | python filter_postgres_logs.py --suppress-benign > filtered_logs.json
```

#### 2. Local Development

```bash
# Filter Docker Compose logs
docker-compose -f docker-compose.local.yml logs postgres 2>&1 | \
  python filter_postgres_logs.py --suppress-benign
```

#### 3. Monitoring Integration

```bash
# Send only real errors to monitoring system
tail -f app.log | python filter_postgres_logs.py --suppress-benign | \
  send_to_monitoring_system
```

## Options

| Option | Description |
|--------|-------------|
| `--suppress-benign` | Hide benign informational messages |
| `--no-correct-levels` | Don't correct log levels (just mark as benign) |
| `--stats` | Show statistics instead of filtered logs |

## What Gets Filtered?

### Benign Messages (Safe to Ignore)

These PostgreSQL messages are informational and will be marked as benign or suppressed:

- ✅ "database system is ready to accept connections"
- ✅ "database system was shut down"
- ✅ "checkpoint starting"
- ✅ "checkpoint complete"
- ✅ "autovacuum launcher started"
- ✅ "autovacuum launcher shutting down"
- ✅ "received shutdown request"
- ✅ "listening on [address]"
- ✅ "starting PostgreSQL"
- ✅ Query duration logs ("LOG: duration: ...")
- ✅ Statement logs ("LOG: statement: ...")

### Real Errors (Always Shown)

These will always be shown as they indicate actual problems:

- ⚠️ "ERROR: relation does not exist"
- ⚠️ "FATAL: password authentication failed"
- ⚠️ "ERROR: syntax error"
- ⚠️ "ERROR: constraint violation"
- ⚠️ Any actual PostgreSQL ERROR, FATAL, or PANIC messages

## Output Format

### Standard Mode

```json
{
  "message": "LOG: database system is ready",
  "attributes": {
    "level": "info",
    "benign": true,
    "original_level": "error"
  },
  "timestamp": "2025-12-10T02:55:37.553Z"
}
```

### Suppress Mode

Benign messages are not output at all. Only real errors are shown.

### Stats Mode

```
PostgreSQL Log Statistics
==================================================
Total entries:        100
Benign messages:      45
Corrected levels:     45
Errors:              5
Warnings:            3
Info:                47
==================================================
```

## Integration Examples

### With Sentry

```python
import subprocess
import json

def send_to_sentry(log_entry):
    if log_entry.get('attributes', {}).get('benign'):
        return  # Skip benign messages
    
    # Send to Sentry
    sentry_sdk.capture_message(log_entry['message'])

# Filter and process logs
proc = subprocess.Popen(
    ['python', 'filter_postgres_logs.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE
)

for line in proc.stdout:
    entry = json.loads(line)
    send_to_sentry(entry)
```

### With DataDog

```python
import datadog
from datadog import statsd

def process_log(log_entry):
    level = log_entry.get('attributes', {}).get('level', 'unknown')
    
    # Track metrics
    statsd.increment(f'postgres.logs.{level}')
    
    # Skip benign messages
    if log_entry.get('attributes', {}).get('benign'):
        return
    
    # Send to DataDog
    if level == 'error':
        datadog.api.Event.create(
            title='PostgreSQL Error',
            text=log_entry['message']
        )
```

### Bash Script Example

```bash
#!/bin/bash
# monitor_postgres.sh - Monitor PostgreSQL logs and alert on real errors

ERROR_COUNT=0

while IFS= read -r line; do
    # Check if it's a JSON log entry
    if echo "$line" | jq -e . >/dev/null 2>&1; then
        LEVEL=$(echo "$line" | jq -r '.attributes.level')
        BENIGN=$(echo "$line" | jq -r '.attributes.benign')
        
        if [ "$LEVEL" = "error" ] && [ "$BENIGN" != "true" ]; then
            ERROR_COUNT=$((ERROR_COUNT + 1))
            echo "🚨 Real Error Detected:"
            echo "$line" | jq .
        fi
    fi
done < <(python filter_postgres_logs.py)

if [ $ERROR_COUNT -gt 0 ]; then
    echo "⚠️ Found $ERROR_COUNT real errors"
    exit 1
else
    echo "✅ No real errors found"
    exit 0
fi
```

## Troubleshooting

### Problem: Script doesn't filter anything

**Solution**: Ensure your logs are in JSON format. The script expects one JSON object per line.

### Problem: All messages are being suppressed

**Solution**: Check if you're using `--suppress-benign`. Remove it to see all messages with corrected levels.

### Problem: Real errors are being marked as benign

**Solution**: This shouldn't happen. If it does, please report it. Check the `BENIGN_PATTERNS` in the script.

## Related Documentation

- `RAILWAY_POSTGRES_LOG_LEVEL_FIX.md` - Detailed explanation of the issue
- `render_postgres_check.py` - Checks PostgreSQL configuration
- `RAILWAY_POSTGRESQL_SETUP.md` - Render database setup guide

## See Also

- [PostgreSQL Error Reporting](https://www.postgresql.org/docs/current/runtime-config-logging.html)
- [Render Logs Documentation](https://docs.render.app/reference/logs)

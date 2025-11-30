# Monitoring and Maintenance Guide

This guide covers the monitoring, alerting, and maintenance setup for HireMeBahamas.

## Table of Contents

1. [Overview](#overview)
2. [Monitoring Tools](#monitoring-tools)
3. [Alerting](#alerting)
4. [Health Endpoints](#health-endpoints)
5. [Metrics](#metrics)
6. [Logging](#logging)
7. [Dependency Updates](#dependency-updates)
8. [External Monitoring Services](#external-monitoring-services)

---

## Overview

HireMeBahamas uses a multi-layered monitoring approach:

- **Application Metrics**: Prometheus-compatible metrics for detailed performance tracking
- **Health Checks**: Automated health monitoring via GitHub Actions
- **Error Tracking**: Sentry integration for error capture and alerting
- **Logging**: Structured logging with request tracking
- **Dependency Management**: Automated dependency update checks

## Monitoring Tools

### Sentry (Error Tracking)

Sentry is integrated for real-time error tracking in both backend and frontend.

**Backend Setup** (already configured):
```python
# In requirements.txt
sentry-sdk[flask]==2.45.0
sentry-sdk[fastapi]==2.45.0
```

Configure via environment variables:
```bash
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
```

**Frontend Setup**:
```typescript
// Already included in frontend dependencies
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.VITE_ENVIRONMENT,
});
```

### Prometheus Metrics

The backend exposes Prometheus-compatible metrics at `/metrics`.

**Available Metrics:**

| Metric | Type | Description |
|--------|------|-------------|
| `hiremebahamas_http_requests_total` | Counter | Total HTTP requests by method, endpoint, status |
| `hiremebahamas_http_request_duration_seconds` | Histogram | Request duration in seconds |
| `hiremebahamas_http_request_errors_total` | Counter | HTTP errors (4xx, 5xx) |
| `hiremebahamas_db_connections_active` | Gauge | Active database connections |
| `hiremebahamas_db_query_duration_seconds` | Histogram | Database query duration |
| `hiremebahamas_auth_attempts_total` | Counter | Authentication attempts |
| `hiremebahamas_app_uptime_seconds` | Gauge | Application uptime |

**Prometheus Configuration Example:**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'hiremebahamas'
    metrics_path: '/metrics'
    scrape_interval: 30s
    static_configs:
      - targets:
          - 'your-backend-url:8080'
```

### Grafana Dashboards

Create dashboards using the exposed metrics. Example queries:

**Request Rate:**
```promql
rate(hiremebahamas_http_requests_total[5m])
```

**Error Rate:**
```promql
rate(hiremebahamas_http_request_errors_total[5m]) / rate(hiremebahamas_http_requests_total[5m])
```

**P95 Latency:**
```promql
histogram_quantile(0.95, rate(hiremebahamas_http_request_duration_seconds_bucket[5m]))
```

## Alerting

### GitHub Actions Alerts

The `uptime-monitoring.yml` workflow:
- Runs every 15 minutes
- Checks backend health endpoints
- Creates GitHub Issues for critical failures
- Provides detailed status summaries

**Manual Trigger:**
```bash
gh workflow run uptime-monitoring.yml
```

### Alert Labels

When issues are created automatically, they include:
- `alert:downtime` - Service downtime detected
- `priority:high` - Requires immediate attention

### Setting Up Notifications

1. **Email Notifications**: Configure in GitHub Settings → Notifications
2. **Slack Integration**: Use GitHub's Slack app for real-time alerts
3. **PagerDuty**: Connect GitHub Actions to PagerDuty for on-call alerts

## Health Endpoints

### Backend Health Endpoints

| Endpoint | Description | Use Case |
|----------|-------------|----------|
| `/health/ping` | Fast ping (no DB check) | Load balancer health checks |
| `/health` | Full health check with DB | Monitoring dashboards |
| `/health/detailed` | Detailed health with stats | Debugging |
| `/api/database/ping` | Database keepalive | Prevent DB sleep |

**Example Response:**
```json
{
  "status": "healthy",
  "api": {
    "status": "healthy",
    "message": "HireMeBahamas API is running",
    "version": "1.0.0"
  },
  "database": {
    "status": "healthy",
    "response_time_ms": 15,
    "message": "Database connection is working"
  }
}
```

## Metrics

### Accessing Metrics

```bash
# Get Prometheus metrics
curl https://your-backend-url/metrics

# Get JSON health data
curl https://your-backend-url/health
```

### Custom Metrics in Code

```python
from backend.app.core.metrics import (
    record_request,
    record_auth_attempt,
    record_db_query
)

# Record an API request
record_request(method="POST", endpoint="/api/users", status_code=201)

# Record authentication attempt
record_auth_attempt(auth_type="login", success=True)

# Record database query
record_db_query(operation="select", duration=0.025)
```

## Logging

### Log Format

The backend uses structured logging with request tracking:

```
[{request_id}] --> GET /api/users from 192.168.1.1
[{request_id}] <-- 200 GET /api/users in 150ms
```

### Log Levels

| Level | Use Case |
|-------|----------|
| DEBUG | Detailed debugging info |
| INFO | General operational messages |
| WARNING | Slow requests, degraded performance |
| ERROR | Request failures, exceptions |

### Slow Request Detection

Requests exceeding thresholds are logged with warnings:
- `SLOW_REQUEST_THRESHOLD_MS = 3000` (3 seconds)
- `VERY_SLOW_REQUEST_THRESHOLD_MS = 10000` (10 seconds)

## Dependency Updates

### Automated Checks

The `dependency-updates.yml` workflow:
- Runs every Monday at 9:00 AM UTC
- Checks Python and Node.js dependencies
- Generates a summary of outdated packages
- Includes security audit results

**Manual Trigger:**
```bash
gh workflow run dependency-updates.yml
```

### Manual Updates

**Python Dependencies:**
```bash
# Check outdated packages
pip list --outdated

# Update a specific package
pip install --upgrade package-name

# Update requirements.txt
pip freeze > requirements.txt
```

**Node.js Dependencies:**
```bash
cd frontend

# Check outdated packages
npm outdated

# Update to latest minor/patch versions
npm update

# Security audit
npm audit
npm audit fix
```

### Security Considerations

1. **Review changelogs** before major version updates
2. **Run tests** after updating dependencies
3. **Check for breaking changes** in major version bumps
4. **Prioritize security updates** from Frogbot/Dependabot alerts

## External Monitoring Services

For production deployments, consider adding these external services:

### UptimeRobot (Free tier available)
- Monitor multiple endpoints
- Email/SMS/Slack alerts
- Response time tracking

### Pingdom
- Comprehensive uptime monitoring
- Transaction monitoring
- Root cause analysis

### Better Uptime
- Status pages
- On-call scheduling
- Incident management

### Configuration Example (UptimeRobot)

1. Create account at uptimerobot.com
2. Add monitors:
   - Main health: `https://your-backend-url/health`
   - Ping: `https://your-backend-url/ping`
   - API: `https://your-backend-url/api/health`
3. Configure alert contacts (email, Slack, etc.)
4. Set check interval (recommended: 5 minutes)

---

## Quick Reference

### Environment Variables for Monitoring

```bash
# Sentry Configuration
SENTRY_DSN=https://...@sentry.io/...
SENTRY_ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO

# Performance Thresholds
SLOW_REQUEST_THRESHOLD_MS=3000
LOGIN_REQUEST_TIMEOUT_SECONDS=25
```

### Key Workflows

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| `uptime-monitoring.yml` | Every 15 min | Health checks, alerting |
| `scheduled-ping.yml` | Every 10 min | Keep app awake |
| `keep-database-awake.yml` | Every 2 min | Prevent DB sleep |
| `dependency-updates.yml` | Weekly (Mon) | Check for updates |

### Useful Commands

```bash
# Check workflow status
gh run list --workflow=uptime-monitoring.yml

# View workflow logs
gh run view <run-id> --log

# Trigger manual health check
gh workflow run uptime-monitoring.yml
```

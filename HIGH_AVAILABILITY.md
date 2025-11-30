# High Availability Architecture

This document outlines the high availability (HA) architecture for HireMeBahamas, ensuring the application remains available, responsive, and resilient to failures.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Multi-Instance Deployment](#multi-instance-deployment)
3. [Load Balancing](#load-balancing)
4. [Auto-Scaling](#auto-scaling)
5. [Health Checks & Monitoring](#health-checks--monitoring)
6. [Database High Availability](#database-high-availability)
7. [Platform-Specific Configuration](#platform-specific-configuration)
8. [Disaster Recovery](#disaster-recovery)

---

## Architecture Overview

```
                                    ┌─────────────────────────────────┐
                                    │         CDN / Edge              │
                                    │      (Vercel Edge Network)      │
                                    └─────────────┬───────────────────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    │                             │                             │
                    ▼                             ▼                             ▼
        ┌───────────────────┐       ┌───────────────────┐       ┌───────────────────┐
        │   Frontend Pod 1  │       │   Frontend Pod 2  │       │   Frontend Pod N  │
        │   (Vercel Edge)   │       │   (Vercel Edge)   │       │   (Vercel Edge)   │
        └─────────┬─────────┘       └─────────┬─────────┘       └─────────┬─────────┘
                  │                           │                           │
                  └───────────────────────────┼───────────────────────────┘
                                              │
                                              ▼
                              ┌───────────────────────────────┐
                              │     Load Balancer             │
                              │   (Railway/Render Ingress)    │
                              └───────────────┬───────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    ▼                         ▼                         ▼
        ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
        │  Backend Pod 1    │   │  Backend Pod 2    │   │  Backend Pod N    │
        │  (Gunicorn +      │   │  (Gunicorn +      │   │  (Gunicorn +      │
        │   2 workers)      │   │   2 workers)      │   │   2 workers)      │
        └─────────┬─────────┘   └─────────┬─────────┘   └─────────┬─────────┘
                  │                       │                       │
                  └───────────────────────┼───────────────────────┘
                                          │
                                          ▼
                          ┌───────────────────────────────────┐
                          │        PostgreSQL Database        │
                          │       (Railway Managed DB)        │
                          │   - Connection Pooling (100 max)  │
                          │   - SSL/TLS Encryption            │
                          │   - Automatic Backups             │
                          └───────────────────────────────────┘
```

---

## Multi-Instance Deployment

### Backend Instances (Gunicorn Workers)

Each backend pod runs Gunicorn with multiple workers for concurrent request handling:

```python
# gunicorn.conf.py configuration
workers = 2              # 2 worker processes per pod
worker_class = "gthread" # Thread-based workers for I/O operations
threads = 8              # 8 threads per worker = 16 concurrent requests per pod
timeout = 55             # Request timeout (below platform gateway timeout)
max_requests = 500       # Worker recycling for memory management
max_requests_jitter = 50 # Staggered restarts
```

**Scaling formula:**
- Total concurrent connections per pod = workers × threads = 2 × 8 = **16**
- With 3 pods: 3 × 16 = **48 concurrent connections**

### Frontend Instances (Vercel Edge)

Vercel automatically deploys to edge locations worldwide:
- Automatic edge caching for static assets
- Global CDN distribution
- Zero-downtime deployments

---

## Load Balancing

### Backend Load Balancing

Both Railway and Render provide built-in load balancing:

| Feature | Railway | Render |
|---------|---------|--------|
| Algorithm | Round-robin | Round-robin |
| Health check integration | ✅ Yes | ✅ Yes |
| Session affinity | Optional | Optional |
| SSL termination | ✅ Yes | ✅ Yes |
| WebSocket support | ✅ Yes | ✅ Yes |

### Load Balancing Configuration

**Railway (`railway.json`):**
```json
{
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100
  }
}
```

**Render (`render.yaml`):**
```yaml
services:
  - type: web
    healthCheckPath: /health
    autoDeploy: true
```

### Frontend Load Balancing

Vercel handles frontend load balancing automatically:
- Edge network spans 30+ regions
- Automatic request routing to nearest edge
- Failover between edge locations

---

## Auto-Scaling

### Railway Auto-Scaling

Railway supports horizontal scaling on Pro and Enterprise plans:

1. **Configure replicas in Railway Dashboard:**
   - Navigate to your service settings
   - Set "Number of Replicas" (1-10 for Pro, unlimited for Enterprise)
   - Enable "Auto-scaling" if available on your plan

2. **Environment-based scaling:**
   ```
   # Railway Dashboard → Settings → Scaling
   Min Replicas: 1
   Max Replicas: 3 (or higher based on plan)
   Target CPU: 70%
   Target Memory: 80%
   ```

### Render Auto-Scaling

Render provides auto-scaling on Team and Enterprise plans:

1. **Configure in Render Dashboard:**
   - Go to Service → Settings → Scaling
   - Set min/max instances
   - Configure scaling triggers

2. **render.yaml configuration:**
   ```yaml
   services:
     - type: web
       plan: standard  # or pro for auto-scaling
       numInstances: 2  # Minimum instances
       scaling:
         minInstances: 1
         maxInstances: 5
         targetCPUPercent: 70
         targetMemoryPercent: 80
   ```

### Scaling Recommendations

| Traffic Level | Backend Instances | Gunicorn Workers | Total Capacity |
|--------------|-------------------|------------------|----------------|
| Low (<100 req/min) | 1 | 2 | 16 concurrent |
| Medium (100-500 req/min) | 2-3 | 2 | 32-48 concurrent |
| High (500-2000 req/min) | 3-5 | 3-4 | 72-160 concurrent |
| Very High (>2000 req/min) | 5+ | 4 | 160+ concurrent |

---

## Health Checks & Monitoring

### Health Check Endpoints

| Endpoint | Purpose | Response Time Target |
|----------|---------|---------------------|
| `/ping` | Basic liveness check | <100ms |
| `/health` | Quick health status | <500ms |
| `/api/health` | Comprehensive health (DB, cache, services) | <2s |
| `/api/database/ping` | Database connectivity | <1s |
| `/api/database/recovery-status` | Database recovery status | <1s |

### Health Check Response Format

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "database": {
    "status": "connected",
    "pool_size": 10,
    "active_connections": 3
  },
  "cache": {
    "type": "redis",
    "status": "connected"
  },
  "keepalive": {
    "running": true,
    "last_ping": "2024-01-15T10:29:00Z",
    "total_pings": 43200
  }
}
```

### Monitoring Workflows

The application uses a layered monitoring approach with different intervals:

| Workflow | Interval | Purpose |
|----------|----------|---------|
| **Health Monitoring** | Every 5 min | Comprehensive service health (backends + frontend) |
| **Scheduled Ping** | Every 10 min | Keep application active on free-tier platforms |
| **Database Keepalive** | Every 2 min | Prevent PostgreSQL from sleeping (Railway/Render) |

**Health Monitoring (every 5 minutes):**
- Comprehensive health check across all services
- Monitors response times and database status
- Generates status reports in GitHub Actions
- See: `.github/workflows/health-monitoring.yml`

**Scheduled Ping (every 10 minutes):**
- Keeps application active on free-tier platforms
- Prevents cold starts
- See: `.github/workflows/scheduled-ping.yml`

**Database Keepalive (every 2 minutes):**
- Prevents PostgreSQL from sleeping
- Maintains connection pool
- See: `.github/workflows/keep-database-awake.yml`

### Alerting Setup

Configure alerts in your platform dashboard:

**Railway:**
1. Go to Project Settings → Integrations
2. Connect to Slack/Discord/PagerDuty
3. Set up alerts for:
   - Deploy failures
   - Service restarts
   - Memory/CPU thresholds

**Render:**
1. Go to Account Settings → Notifications
2. Configure notification channels
3. Enable alerts for:
   - Deploy status changes
   - Service health changes
   - Resource limits

---

## Database High Availability

### Connection Pooling

```python
# Database pool configuration
DB_POOL_MIN_CONNECTIONS = 2      # Minimum idle connections
DB_POOL_MAX_CONNECTIONS = 10     # Maximum concurrent connections
DB_CONNECTION_TIMEOUT = 20       # Connection timeout (seconds)
```

### TCP Keepalive Settings

Prevent SSL EOF errors and stale connections:

```python
# gunicorn/final_backend_postgresql.py
TCP_KEEPALIVE_ENABLED = 1
TCP_KEEPALIVE_IDLE = 20      # Start probing after 20s idle
TCP_KEEPALIVE_INTERVAL = 5   # Probe every 5 seconds
TCP_KEEPALIVE_COUNT = 3      # Mark dead after 3 failed probes
TCP_USER_TIMEOUT = 20000     # 20s timeout for TCP operations
```

### Database Keepalive Strategy

The application includes an aggressive keepalive mechanism:

1. **Startup Phase (first 5 minutes):**
   - Ping every 30 seconds
   - Multiple warmup queries to wake database

2. **Normal Operation:**
   - Ping every 2 minutes
   - Background cleanup of stale connections

3. **Recovery Mode:**
   - Automatic retry on connection failures
   - Exponential backoff (max 5 retries)

### Backup Strategy

Railway PostgreSQL includes:
- Point-in-time recovery (PITR)
- Daily automated backups
- Manual backup triggers via CLI

---

## Platform-Specific Configuration

### Railway Configuration

**File: `railway.json`**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "gunicorn final_backend_postgresql:application --config gunicorn.conf.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Environment Variables (set in Dashboard):**
```
DATABASE_URL=postgresql://...
SECRET_KEY=<your-secret>
JWT_SECRET_KEY=<your-jwt-secret>
ENVIRONMENT=production
WEB_CONCURRENCY=2
WEB_THREADS=8
```

### Render Configuration

**File: `render.yaml`**
```yaml
services:
  - type: web
    name: hiremebahamas-backend
    env: python
    region: oregon
    plan: free  # or 'standard' for production
    healthCheckPath: /health
    autoDeploy: true
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: WEB_CONCURRENCY
        value: 2
```

### Vercel Configuration

**File: `vercel.json`** (root)
```json
{
  "version": 2,
  "framework": "vite",
  "buildCommand": "cd frontend && npm ci && npm run build",
  "outputDirectory": "frontend/dist",
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    }
  ]
}
```

---

## Disaster Recovery

### Recovery Time Objectives (RTO)

| Component | Target RTO | Strategy |
|-----------|-----------|----------|
| Frontend (Vercel) | <1 minute | Automatic edge failover |
| Backend (Railway/Render) | <5 minutes | Health check + auto-restart |
| Database | <30 minutes | PITR + automated backups |

### Recovery Procedures

#### 1. Backend Service Failure

**Automatic Recovery:**
- Health checks detect failure within 30 seconds
- Platform automatically restarts service
- Load balancer routes to healthy instances

**Manual Recovery:**
```bash
# Railway
railway up --service hiremebahamas-backend

# Render
# Trigger redeploy from Render Dashboard or via Deploy Hook
curl -X POST "$RENDER_DEPLOY_HOOK"
```

#### 2. Database Connection Failure

**Automatic Recovery:**
- Connection pool retries with exponential backoff
- Keepalive worker restarts failed connections
- Application continues with graceful degradation

**Manual Recovery:**
```bash
# Check database status
curl https://your-backend.railway.app/api/database/recovery-status

# Force database ping
curl -X POST https://your-backend.railway.app/api/database/ping
```

#### 3. Complete Platform Outage

**Failover to Secondary Platform:**
1. Update DNS to point to backup platform (Render if Railway is down)
2. Verify database connectivity
3. Update frontend API URL if needed

### Backup Verification

Schedule regular backup verification:

```bash
# Weekly backup verification (add to CI/CD)
- name: Verify Backups
  run: |
    # Check Railway backup status
    railway backup list --service postgres
    
    # Test backup restoration (to temporary instance)
    railway backup restore --service postgres --backup-id latest --target temp-db
```

---

## Monitoring Dashboard

### Key Metrics to Track

| Metric | Warning Threshold | Critical Threshold |
|--------|-------------------|-------------------|
| Response Time (p95) | >2s | >5s |
| Error Rate | >1% | >5% |
| CPU Usage | >70% | >90% |
| Memory Usage | >80% | >95% |
| DB Connection Pool | >80% utilized | >95% utilized |
| Request Rate | N/A (monitor trends) | Sudden 10x spike |

### External Monitoring Recommendations

For production deployments, consider adding:

1. **Uptime Monitoring:**
   - UptimeRobot (free tier available)
   - Pingdom
   - Better Uptime

2. **APM (Application Performance Monitoring):**
   - New Relic
   - Datadog
   - Sentry (already integrated for error tracking)

3. **Log Aggregation:**
   - Railway Logs (built-in)
   - Render Logs (built-in)
   - Papertrail or Logtail for long-term retention

---

## Quick Reference

### Scaling Checklist

- [ ] Configure minimum 2 backend instances for production
- [ ] Set up health check endpoints in platform dashboard
- [ ] Configure alerting for service health
- [ ] Enable auto-scaling if available on your plan
- [ ] Set up external uptime monitoring
- [ ] Verify database backup schedule
- [ ] Test failover procedures quarterly

### Health Check URLs

```bash
# Quick health check
curl https://your-backend.railway.app/ping

# Detailed health check
curl https://your-backend.railway.app/api/health

# Database status
curl https://your-backend.railway.app/api/database/ping
```

### Emergency Contacts

Configure these in your monitoring tools:
- Primary On-Call: Set up in PagerDuty/OpsGenie
- Escalation: Define escalation policies
- Communication: Slack/Discord channel for incidents

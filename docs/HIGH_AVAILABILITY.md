# High Availability Architecture for HireMeBahamas

This document outlines the high availability (HA) architecture for the HireMeBahamas platform, covering load balancing, auto-scaling, and failover strategies using managed platforms.

## Overview

HireMeBahamas uses a multi-tier high availability architecture:

```
                                    ┌─────────────────────────────────────┐
                                    │         DNS (Cloudflare/Route53)    │
                                    │    hiremebahamas.com → CDN/LB       │
                                    └─────────────────┬───────────────────┘
                                                      │
                    ┌─────────────────────────────────┼─────────────────────────────────┐
                    │                                 │                                 │
          ┌─────────▼──────────┐           ┌─────────▼──────────┐           ┌─────────▼──────────┐
          │   Vercel Edge      │           │   Render/Railway   │           │   PostgreSQL       │
          │   (Frontend CDN)   │           │   (Backend API)    │           │   (Database)       │
          │                    │           │                    │           │                    │
          │ • Global CDN       │           │ • Auto-scaling     │           │ • High Availability│
          │ • Edge caching     │           │ • Load balancing   │           │ • Automatic backups│
          │ • DDoS protection  │           │ • Health checks    │           │ • Connection pool  │
          │ • SSL termination  │           │ • Zero-downtime    │           │ • Read replicas    │
          │ • Automatic HTTPS  │           │   deployments      │           │   (if needed)      │
          └────────────────────┘           └────────────────────┘           └────────────────────┘
```

## Table of Contents

1. [Load Balancing](#load-balancing)
2. [Auto-Scaling](#auto-scaling)
3. [Managed Platforms](#managed-platforms)
4. [Health Checks](#health-checks)
5. [Database High Availability](#database-high-availability)
6. [Failover Strategies](#failover-strategies)
7. [Monitoring and Alerts](#monitoring-and-alerts)
8. [Best Practices](#best-practices)

---

## Load Balancing

### Platform-Managed Load Balancing

Both Railway and Render provide built-in load balancing with their managed infrastructure:

#### Railway Load Balancing
- **Automatic load balancing** across multiple instances
- **Session affinity** (sticky sessions) for stateful applications
- **Health-based routing** to automatically route traffic away from unhealthy instances
- **Geographic distribution** based on deployment regions

#### Render Load Balancing
- **Zero-config load balancing** for web services
- **Automatic TLS termination** at the load balancer level
- **WebSocket support** with proper connection handling
- **HTTP/2 and HTTP/3 support** for improved performance

### Custom NGINX Load Balancing (for Self-Hosted)

For self-hosted deployments, we provide an NGINX configuration:

```nginx
# See docker/nginx-loadbalancer.conf for full configuration
upstream backend_servers {
    least_conn;  # Use least connections algorithm
    
    server backend1:8080 weight=1 max_fails=3 fail_timeout=30s;
    server backend2:8080 weight=1 max_fails=3 fail_timeout=30s;
    server backend3:8080 weight=1 max_fails=3 fail_timeout=30s backup;
    
    keepalive 32;  # Maintain persistent connections
}
```

### Load Balancing Algorithms

| Algorithm | Use Case | Configuration |
|-----------|----------|---------------|
| Round Robin | Equal capacity servers | Default |
| Least Connections | Varying request processing times | `least_conn;` |
| IP Hash | Session persistence without cookies | `ip_hash;` |
| Weighted | Different server capacities | `server backend:8080 weight=5;` |

---

## Auto-Scaling

### Render Auto-Scaling Configuration

Render supports automatic scaling based on resource usage. Configure in `render.yaml`:

```yaml
services:
  - type: web
    name: hiremebahamas-backend
    scaling:
      minInstances: 1
      maxInstances: 10
      targetCPUPercent: 70
      targetMemoryPercent: 80
```

> **Note**: Scaling requires a paid plan (Standard or higher). When CPU usage exceeds 70% or memory exceeds 80%, Render will automatically add instances up to maxInstances. When usage drops, it will scale down after a cooldown period (typically 5 minutes).

### Railway Auto-Scaling

Railway automatically scales based on traffic patterns. Key features:
- **Horizontal scaling**: Multiple replicas for high traffic
- **Sleep mode**: Scale to zero during inactivity (free tier)
- **Instant wake**: Fast cold starts when traffic resumes

### Scaling Triggers

| Metric | Threshold | Action |
|--------|-----------|--------|
| CPU Usage | > 70% | Scale up |
| Memory Usage | > 80% | Scale up |
| Request Queue | > 100 requests | Scale up |
| Response Time | > 500ms avg | Scale up |
| All metrics normal | 5 minutes | Scale down (one at a time) |

### Gunicorn Worker Configuration

Our `gunicorn.conf.py` is optimized for auto-scaling environments:

```python
# Workers scale with available CPU cores
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
worker_class = "gthread"
threads = int(os.environ.get("WEB_THREADS", "8"))

# Memory management for container environments
max_requests = 500
max_requests_jitter = 50
```

---

## Managed Platforms

### Vercel (Frontend)

**Automatic High Availability Features:**
- **Edge Network**: Global CDN with 18+ regions
- **Instant rollback**: One-click deployment rollback
- **Zero-downtime deployments**: Atomic deploys with instant switching
- **Automatic HTTPS**: SSL certificates managed automatically
- **DDoS protection**: Built-in protection against attacks

**Configuration (`vercel.json`):**
```json
{
  "framework": "vite",
  "regions": ["iad1", "sfo1", "fra1"],  // Multi-region deployment
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

### Railway (Backend)

**High Availability Features:**
- **Multi-region deployments**: Deploy to multiple regions
- **Automatic failover**: Traffic redirected on instance failure
- **Zero-downtime deploys**: Rolling updates
- **Health checks**: Automatic health monitoring
- **Persistent volumes**: Data survives restarts

**Configuration (`railway.json`):**
```json
{
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "numReplicas": 2
  }
}
```

### Render (Backend Alternative)

**High Availability Features:**
- **Auto-scaling**: Scale from 0 to N instances
- **Zero-downtime deploys**: Graceful deployment transitions
- **Private networking**: Secure internal communication
- **Health checks**: Configurable health endpoints
- **Managed PostgreSQL**: With automatic backups

**Configuration (`render.yaml`):**
```yaml
services:
  - type: web
    name: hiremebahamas-backend
    plan: standard
    healthCheckPath: /health
    autoscaling:
      minInstances: 1
      maxInstances: 10
      targetCPUPercent: 70
```

---

## Health Checks

### Backend Health Endpoint

Our `/health` endpoint provides comprehensive health information:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "database": {
    "status": "connected",
    "latency_ms": 5
  },
  "cache": {
    "status": "connected"
  },
  "uptime_seconds": 86400
}
```

### Health Check Configuration

| Platform | Path | Interval | Timeout | Unhealthy Threshold |
|----------|------|----------|---------|---------------------|
| Railway | `/health` | 30s | 10s | 3 failures |
| Render | `/health` | 30s | 10s | 3 failures |
| Docker | `/health` | 30s | 10s | 3 failures |

### Graceful Shutdown

Our application handles shutdown signals properly:

```python
# gunicorn.conf.py
graceful_timeout = 30  # Wait for requests to complete
timeout = 55  # Worker timeout before platform timeout

def worker_exit(server, worker):
    """Called when a worker is exiting - cleanup resources"""
    print(f"Worker {worker.pid} exiting...")
```

---

## Database High Availability

### PostgreSQL Configuration

For production deployments:

1. **Connection Pooling**: Use PgBouncer or internal pooling
2. **Read Replicas**: For read-heavy workloads
3. **Automatic Backups**: Daily with point-in-time recovery
4. **Connection Retry**: Automatic reconnection on failure

### Database Keepalive

We implement a keepalive mechanism to prevent connection drops:

```python
# Periodic health check query
SELECT 1;  # Every 30 seconds
```

### Managed Database Options

| Provider | Plan | Features |
|----------|------|----------|
| Railway PostgreSQL | Included | Auto-backups, connection pooling |
| Render PostgreSQL | $7/mo | Point-in-time recovery, read replicas |
| Supabase | Free tier | Real-time, auto-scaling |
| Neon | Free tier | Serverless, auto-scaling |

---

## Failover Strategies

### Automatic Failover

1. **Instance Failure**
   - Health check fails → Instance marked unhealthy
   - Traffic routed to healthy instances
   - New instance started automatically

2. **Region Failure**
   - DNS failover to alternate region
   - Database replica promotion
   - Automatic traffic rerouting

3. **Database Failure**
   - Automatic failover to replica
   - Connection retry with exponential backoff
   - Application-level error handling

### Manual Failover Procedures

1. **Backend Rollback**
   ```bash
   # Railway
   railway rollback
   
   # Render
   # Use dashboard: Settings > Rollback
   ```

2. **Frontend Rollback**
   ```bash
   # Vercel
   vercel rollback
   ```

---

## Monitoring and Alerts

### Recommended Monitoring Stack

1. **Application Performance Monitoring (APM)**
   - Sentry for error tracking
   - Custom metrics with Prometheus/Grafana

2. **Infrastructure Monitoring**
   - Platform dashboards (Railway, Render, Vercel)
   - Uptime monitoring (UptimeRobot, Pingdom)

3. **Alerting**
   - Slack/Discord notifications
   - Email alerts for critical issues
   - PagerDuty for on-call

### Key Metrics to Monitor

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Response Time | > 500ms | > 2s | Scale up, optimize queries |
| Error Rate | > 1% | > 5% | Investigate logs, rollback |
| CPU Usage | > 70% | > 90% | Scale up |
| Memory Usage | > 80% | > 95% | Scale up, check for leaks |
| Database Connections | > 80% pool | > 95% pool | Increase pool size |

---

## Best Practices

### 1. Deployment Best Practices

- ✅ Use blue-green or rolling deployments
- ✅ Always have health checks enabled
- ✅ Set appropriate timeout values
- ✅ Configure graceful shutdown handlers
- ✅ Use connection pooling for databases

### 2. Application Best Practices

- ✅ Design stateless applications (store state externally)
- ✅ Use proper error handling and retry logic
- ✅ Implement circuit breakers for external services
- ✅ Cache aggressively (CDN, application cache)
- ✅ Use async processing for heavy operations

### 3. Database Best Practices

- ✅ Use connection pooling
- ✅ Implement retry logic with exponential backoff
- ✅ Monitor connection health
- ✅ Set appropriate connection timeouts
- ✅ Use read replicas for heavy read workloads

### 4. Security Best Practices

- ✅ Use HTTPS everywhere
- ✅ Keep secrets in environment variables
- ✅ Enable DDoS protection
- ✅ Implement rate limiting
- ✅ Regular security audits

---

## Quick Start

### Enable High Availability on Render

1. Update `render.yaml`:
```yaml
autoscaling:
  minInstances: 1
  maxInstances: 5
  targetCPUPercent: 70
```

2. Push to main branch - Render auto-deploys with HA enabled

### Enable High Availability on Railway

1. Update `railway.json`:
```json
{
  "deploy": {
    "numReplicas": 2,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

2. Push to main branch - Railway auto-deploys with HA enabled

### Local Development with Docker

```bash
# Start with multiple backend replicas
docker-compose --profile production up --scale backend-flask=3
```

---

## Troubleshooting

### Common Issues

1. **Health Check Failures**
   - Check `/health` endpoint is responding
   - Verify database connectivity
   - Check for memory/CPU exhaustion

2. **Slow Response Times**
   - Review application logs
   - Check database query performance
   - Verify external service dependencies

3. **Connection Errors**
   - Check connection pool settings
   - Verify network configuration
   - Review SSL/TLS settings

### Getting Help

- Review platform documentation (Railway, Render, Vercel)
- Check application logs
- Contact platform support
- Open an issue on GitHub

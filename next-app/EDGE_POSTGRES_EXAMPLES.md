# Edge Functions + Postgres - Example Commands

## Local Development

### Start Server
```bash
cd next-app
npm run dev
```

### Test Info Endpoint
```bash
curl http://localhost:3000/api/edge-sql-demo?operation=info | jq
```

### Test SELECT Query
```bash
curl http://localhost:3000/api/edge-sql-demo?operation=select | jq
```

### Test COUNT Query
```bash
curl http://localhost:3000/api/edge-sql-demo?operation=count | jq
```

### Test JOIN Query
```bash
curl http://localhost:3000/api/edge-sql-demo?operation=join | jq
```

### Test INSERT (POST)
```bash
curl -X POST http://localhost:3000/api/edge-sql-demo \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "insert",
    "data": {
      "title": "Full Stack Developer",
      "company": "Bahamas Tech",
      "location": "Nassau, Bahamas",
      "description": "Exciting opportunity for a full stack developer",
      "jobType": "full-time"
    }
  }' | jq
```

### Test UPDATE (POST)
```bash
curl -X POST http://localhost:3000/api/edge-sql-demo \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "update",
    "data": {
      "id": 1,
      "updates": {
        "title": "Senior Full Stack Developer",
        "company": "Bahamas Tech Inc"
      }
    }
  }' | jq
```

---

## Production Testing

### Deploy to Vercel
```bash
cd next-app
npx vercel --prod
```

### Test with Timing
```bash
# Test response time from your location
curl -w "\nTotal time: %{time_total}s\n" \
  https://your-app.vercel.app/api/edge-sql-demo?operation=info
```

### Test All Operations
```bash
# Info
curl https://your-app.vercel.app/api/edge-sql-demo?operation=info | jq

# SELECT
curl https://your-app.vercel.app/api/edge-sql-demo?operation=select | jq

# COUNT
curl https://your-app.vercel.app/api/edge-sql-demo?operation=count | jq

# JOIN
curl https://your-app.vercel.app/api/edge-sql-demo?operation=join | jq
```

### Verify Edge Runtime
```bash
# Check response headers
curl -I https://your-app.vercel.app/api/edge-sql-demo?operation=info

# Look for:
# X-Runtime: edge
# X-Response-Time: <duration>ms
# X-Region: <region-code>
```

---

## Browser Testing

Open these URLs in your browser:

### Local
- http://localhost:3000/api/edge-sql-demo?operation=info
- http://localhost:3000/api/edge-sql-demo?operation=select
- http://localhost:3000/api/edge-sql-demo?operation=count
- http://localhost:3000/api/edge-sql-demo?operation=join

### Production
- https://your-app.vercel.app/api/edge-sql-demo?operation=info
- https://your-app.vercel.app/api/edge-sql-demo?operation=select
- https://your-app.vercel.app/api/edge-sql-demo?operation=count
- https://your-app.vercel.app/api/edge-sql-demo?operation=join

---

## Performance Testing

### Test from Multiple Regions

#### From USA (East Coast)
```bash
curl -w "\nLatency: %{time_total}s\n" \
  https://your-app.vercel.app/api/edge-sql-demo?operation=select
# Expected: < 0.050s (50ms)
```

#### From Europe
```bash
curl -w "\nLatency: %{time_total}s\n" \
  https://your-app.vercel.app/api/edge-sql-demo?operation=select
# Expected: < 0.060s (60ms)
```

#### From Asia Pacific
```bash
curl -w "\nLatency: %{time_total}s\n" \
  https://your-app.vercel.app/api/edge-sql-demo?operation=select
# Expected: < 0.080s (80ms)
```

### Load Testing (Apache Bench)
```bash
# Test 1000 requests with 10 concurrent
ab -n 1000 -c 10 \
  "https://your-app.vercel.app/api/edge-sql-demo?operation=info"
```

### Load Testing (wrk)
```bash
# Test with wrk (if installed)
wrk -t4 -c100 -d30s \
  "https://your-app.vercel.app/api/edge-sql-demo?operation=select"
```

---

## Monitoring

### Check Vercel Analytics
```bash
# View in dashboard
https://vercel.com/dashboard/<your-username>/<your-project>/analytics

# Look for:
# - Response time by region
# - Edge network usage (should be >99%)
# - Cache hit rates
# - Error rates
```

### Check Vercel Logs
```bash
# Real-time logs
npx vercel logs --follow

# Filter by function
npx vercel logs --follow | grep edge-sql-demo
```

### Check Database Connection
```bash
# Verify connection pooling is working
curl https://your-app.vercel.app/api/edge-sql-demo?operation=info | jq '.metadata'

# Should show:
# "connectionPooling": "automatic"
# "edgeRuntime": true
```

---

## Troubleshooting Commands

### Check Environment Variables
```bash
# List all env vars in Vercel
npx vercel env ls

# Pull env vars to local
npx vercel env pull .env.local
```

### Test Database Connection
```bash
# Use psql to connect directly
psql $POSTGRES_URL

# Or with individual components
psql -h <host> -U <user> -d <database>
```

### Check Build Output
```bash
cd next-app
npm run build 2>&1 | grep edge-sql-demo

# Should show:
# ƒ /api/edge-sql-demo    151 B    99.3 kB
```

---

## Example Responses

### Info Operation
```json
{
  "success": true,
  "operation": "INFO",
  "message": "Edge Function SQL Demo - Production Ready",
  "runtime": "edge",
  "package": "@vercel/postgres",
  "version": "0.10.0+",
  "capabilities": [
    "Direct SQL execution from Edge",
    "Global <50ms latency",
    "Automatic connection pooling",
    "Supports SELECT, INSERT, UPDATE, DELETE",
    "Transaction support",
    "Prepared statements (parameterized queries)"
  ],
  "performance": {
    "executionTimeMs": 15,
    "runtime": "edge",
    "region": "iad1"
  }
}
```

### SELECT Operation
```json
{
  "success": true,
  "operation": "SELECT",
  "rowCount": 10,
  "data": [
    {
      "id": 1,
      "title": "Software Engineer",
      "company": "Tech Corp",
      "location": "Nassau, Bahamas",
      "job_type": "full-time",
      "created_at": "2025-12-01T10:30:00Z"
    }
  ],
  "performance": {
    "executionTimeMs": 25,
    "runtime": "edge",
    "region": "iad1"
  }
}
```

### INSERT Operation
```json
{
  "success": true,
  "operation": "INSERT",
  "message": "Job created successfully",
  "data": {
    "id": 42,
    "title": "Full Stack Developer",
    "company": "Bahamas Tech",
    "location": "Nassau, Bahamas",
    "created_at": "2025-12-01T16:15:30Z"
  },
  "rowsAffected": 1,
  "performance": {
    "executionTimeMs": 30,
    "runtime": "edge",
    "region": "iad1"
  }
}
```

---

## Quick Reference

| Operation | Method | URL | Description |
|-----------|--------|-----|-------------|
| Info | GET | /api/edge-sql-demo?operation=info | System info |
| SELECT | GET | /api/edge-sql-demo?operation=select | Basic query |
| COUNT | GET | /api/edge-sql-demo?operation=count | Aggregates |
| JOIN | GET | /api/edge-sql-demo?operation=join | Multi-table |
| INSERT | POST | /api/edge-sql-demo | Create record |
| UPDATE | POST | /api/edge-sql-demo | Modify record |

---

For complete documentation, see:
- [EDGE_POSTGRES_README.md](../EDGE_POSTGRES_README.md)
- [EDGE_POSTGRES_GUIDE.md](./EDGE_POSTGRES_GUIDE.md)
- [EDGE_POSTGRES_QUICKREF.md](./EDGE_POSTGRES_QUICKREF.md)

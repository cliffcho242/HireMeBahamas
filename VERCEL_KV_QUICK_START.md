# ⚡ Quick Reference: Vercel KV Store & Edge Network Setup

**For detailed instructions, see:** [next-app/VERCEL_EDGE_SETUP.md](./next-app/VERCEL_EDGE_SETUP.md)

## 📋 Quick Checklist

### 1. Create Vercel KV Store
```bash
# In Vercel Dashboard:
1. Go to Storage → Create Database → KV
2. Name: hiremebahamas-kv
3. Region: Global
4. Connect to project: hiremebahamas
```

### 2. Environment Variables (Auto-Injected)
```bash
# Vercel automatically adds these when you connect KV:
KV_URL=redis://...
KV_REST_API_URL=https://...
KV_REST_API_TOKEN=...
KV_REST_API_READ_ONLY_TOKEN=...

# For local development:
npx vercel env pull .env.local
```

### 3. Verify KV Connection
```bash
# Test health endpoint (Edge runtime, <30ms)
curl https://hiremebahamas.com/api/health

# Expected response:
{
  "status": "healthy",
  "runtime": "edge",
  "checks": {
    "kv": {
      "status": "connected",
      "durationMs": 15
    }
  }
}
```

### 4. Test Edge Performance
```bash
cd next-app
./test-edge-performance.sh https://hiremebahamas.com

# Expected latencies:
# - Edge health: <50ms
# - Login (first): <150ms
# - Login (cached): <80ms
```

### 5. Enable Edge Network in Vercel
```bash
# In Vercel Dashboard:
1. Project → Settings → Speed Insights
2. Enable "Edge Network"
3. Select regions: All (for global coverage)
```

### 6. Monitor Performance
```bash
# Vercel Dashboard → Analytics
- Check: Response Time by Region
- Verify: >99% requests from Edge
- Monitor: P95 latency <100ms
```

## 🚀 Edge Routes in This App

| Route | Runtime | Latency Target | Purpose |
|-------|---------|----------------|---------|
| `/api/health` | Edge | <30ms | Health check & latency test |
| `/api/cron` | Edge | <100ms | Keep-alive cron (every 5 min) |
| `/api/auth/login` | Node.js + KV | <120ms (first)<br><60ms (cached) | User login with session cache |
| `/api/jobs` | Node.js + KV | <200ms (first)<br><100ms (cached) | Jobs list with KV cache |

## 📊 Performance Targets

| Region | Target | Technology |
|--------|--------|------------|
| Bahamas | <60ms | Edge Functions + KV |
| USA East | <40ms | Edge Functions + KV |
| USA West | <50ms | Edge Functions + KV |
| Europe | <60ms | Edge Functions + KV |

## 🔗 Related Documentation

- **Full Setup Guide**: [next-app/VERCEL_EDGE_SETUP.md](./next-app/VERCEL_EDGE_SETUP.md)
- **Deployment Checklist**: [next-app/DEPLOY_CHECKLIST.md](./next-app/DEPLOY_CHECKLIST.md)
- **Next.js README**: [next-app/README.md](./next-app/README.md)
- **Render Migration**: [RENDER_TO_VERCEL_MIGRATION.md](./RENDER_TO_VERCEL_MIGRATION.md)

## 💡 Key Features

1. **Vercel KV for Session Caching** - Repeat logins hit cache (50-60ms)
2. **Edge Health Endpoint** - Global health checks (<30ms)
3. **Multi-Region Distribution** - Node.js functions in 4+ regions
4. **Automatic Cache Invalidation** - Version-based cache keys
5. **Performance Monitoring** - Response time tracking per route

## 🎯 Success Criteria

- ✅ KV store connected and healthy
- ✅ Edge health endpoint returns <50ms
- ✅ Login latency <120ms first request, <80ms cached
- ✅ Vercel Analytics shows >99% Edge network usage
- ✅ No 502 or 499 errors (cold starts eliminated)

---

**Need Help?** See the [full setup guide](./next-app/VERCEL_EDGE_SETUP.md) for detailed instructions.

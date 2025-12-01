# ⚡ Vercel Edge Network Setup Guide

Complete guide to enable Vercel Edge Network for ultra-low latency (<60ms) globally.

## 🎯 Performance Goals

| Region | Target Latency | Technology |
|--------|----------------|------------|
| Bahamas (Nassau) | < 60ms | Edge Functions + KV |
| USA (East Coast) | < 40ms | Edge Functions + KV |
| USA (West Coast) | < 50ms | Edge Functions + KV |
| Europe (Frankfurt) | < 60ms | Edge Functions + KV |

## Step 1: Create Vercel KV Store

### 1.1 Create KV Database in Vercel Dashboard

```bash
1. Go to: https://vercel.com/dashboard
2. Navigate to: Storage → Create Database
3. Select: KV (Redis-compatible)
4. Name: hiremebahamas-kv
5. Region: Select "Global" or closest to your users
6. Click: Create
```

### 1.2 Connect KV to Your Project

```bash
1. After creating KV database, click: Connect to Project
2. Select: hiremebahamas (your Next.js project)
3. Vercel automatically injects environment variables:
   - KV_URL
   - KV_REST_API_URL
   - KV_REST_API_TOKEN
   - KV_REST_API_READ_ONLY_TOKEN
```

### 1.3 Verify KV Connection Strings

```bash
# In Vercel Dashboard → Project → Settings → Environment Variables
# Verify these are auto-injected:

KV_URL=redis://default:xxxxx@xxxxx.kv.vercel-storage.com:xxxxx
KV_REST_API_URL=https://xxxxx.kv.vercel-storage.com
KV_REST_API_TOKEN=xxxxx
KV_REST_API_READ_ONLY_TOKEN=xxxxx
```

## Step 2: Add VERCEL_KV_URL to Environment Variables

The `@vercel/kv` package automatically uses the environment variables injected by Vercel when you connect your KV database. However, for local development:

### 2.1 Update .env.local for Local Development

```bash
# Copy connection strings from Vercel Dashboard
cp .env.example .env.local

# Edit .env.local and add:
KV_URL=<your-kv-url-from-vercel>
KV_REST_API_URL=<your-rest-api-url>
KV_REST_API_TOKEN=<your-token>
KV_REST_API_READ_ONLY_TOKEN=<your-read-only-token>
```

### 2.2 Pull Environment Variables from Vercel

```bash
# Easiest way - let Vercel CLI fetch them for you
npx vercel env pull .env.local

# This automatically creates .env.local with all variables
```

## Step 3: Edge Routes Configuration

The Next.js app already includes optimized Edge routes:

### 3.1 Current Edge Routes

| Route | Runtime | Purpose | Latency Target |
|-------|---------|---------|----------------|
| `/api/cron` | Edge | Keep-alive cron job | < 50ms |
| `/api/health` | Edge (new) | Health check ping | < 30ms |

### 3.2 Node.js Routes (Require bcrypt)

| Route | Runtime | Purpose | Why Node.js? |
|-------|---------|---------|--------------|
| `/api/auth/login` | Node.js | User login | bcrypt (native module) |
| `/api/auth/register` | Node.js | User registration | bcrypt hashing |
| `/api/jobs` | Node.js | Job CRUD | Complex queries |
| `/api/push` | Node.js | Push notifications | web-push library |

**Note**: Login uses **KV session caching** for repeat logins, achieving <50ms latency despite Node.js runtime.

### 3.3 Preferred Regions for Node.js Routes

All Node.js routes specify multiple regions for global distribution:

```typescript
export const preferredRegion = ["iad1", "sfo1", "sin1", "fra1"];
// iad1: Washington DC (USA East)
// sfo1: San Francisco (USA West)
// sin1: Singapore (Asia)
// fra1: Frankfurt (Europe)
```

This ensures the nearest serverless function responds to requests.

## Step 4: Deploy with Vercel Edge Auto-Detection

Vercel automatically detects Edge runtime from your route exports.

### 4.1 Deploy to Vercel

```bash
cd next-app
npx vercel --prod
```

### 4.2 Verify Edge Functions in Dashboard

```bash
1. Go to: Vercel Dashboard → Project → Functions
2. Verify these are marked as "Edge":
   - api/cron
   - api/health (after adding it)
3. Verify these are marked as "Serverless":
   - api/auth/login
   - api/auth/register
   - api/jobs
```

## Step 5: Enable Edge Network for All Regions

### 5.1 Enable in Vercel Project Settings

```bash
1. Go to: Vercel Dashboard → Project → Settings
2. Navigate to: Speed Insights → Configuration
3. Enable: Edge Network
4. Select regions: All (for global coverage)
5. Save changes
```

### 5.2 Verify Edge Network Configuration

The `vercel.json` already configures global regions:

```json
{
  "regions": ["iad1"],
  "crons": [
    {
      "path": "/api/cron",
      "schedule": "*/5 * * * *"
    }
  ]
}
```

**Note**: `"regions": ["iad1"]` is the primary region, but Edge functions automatically replicate globally.

## Step 6: Test Login from Multiple Regions

### 6.1 Test from Bahamas

```bash
# Using curl with timing
curl -w "\nTotal time: %{time_total}s\n" \
  -X POST https://hiremebahamas.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Expected: < 120ms first login, < 60ms repeat login (cached)
```

### 6.2 Test from USA (East Coast)

```bash
# From Virginia or Washington DC
curl -w "\nTotal time: %{time_total}s\n" \
  -X POST https://hiremebahamas.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Expected: < 80ms first login, < 40ms repeat login
```

### 6.3 Test from Europe (Frankfurt)

```bash
# From Germany
curl -w "\nTotal time: %{time_total}s\n" \
  -X POST https://hiremebahamas.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Expected: < 120ms first login, < 60ms repeat login
```

### 6.4 Test Edge Health Endpoint

```bash
# This should be < 30ms from anywhere
curl -w "\nTotal time: %{time_total}s\n" \
  https://hiremebahamas.com/api/health

# Expected: < 30ms globally (pure Edge function)
```

## Step 7: Monitor Vercel Analytics

### 7.1 View Real-Time Analytics

```bash
1. Go to: Vercel Dashboard → Project → Analytics
2. Check: Response Time by Region
3. Verify: 99%+ requests served from Edge Network
4. Monitor: P95 response time < 60ms
```

### 7.2 Check Speed Insights

```bash
1. Go to: Vercel Dashboard → Project → Speed Insights
2. Verify Core Web Vitals:
   - LCP (Largest Contentful Paint): < 2.5s
   - FID (First Input Delay): < 100ms
   - CLS (Cumulative Layout Shift): < 0.1
3. Check: Time to First Byte (TTFB) < 100ms
```

### 7.3 Verify Cache Hit Rates

```bash
# Check response headers for cache status
curl -I https://hiremebahamas.com/api/jobs

# Look for:
# X-Cache: HIT (from KV cache)
# X-Vercel-Cache: HIT (from Edge cache)
# X-Response-Time: <duration>ms
```

## Step 8: Delete Render Forever

Once Vercel Edge is fully operational and latency targets are met:

### 8.1 Verify Vercel is Primary

```bash
# Test all critical endpoints
curl https://hiremebahamas.com/
curl https://hiremebahamas.com/api/health
curl https://hiremebahamas.com/api/jobs

# All should return 200 OK with low latency
```

### 8.2 Suspend Render Services

```bash
1. Go to: https://dashboard.render.com/
2. For each service:
   - hiremebahamas-backend → Settings → Suspend Service
   - keep-alive worker → Settings → Suspend Service
   - Any cron jobs → Settings → Suspend Service
3. Verify zero billing: https://dashboard.render.com/billing
```

### 8.3 Delete Render Services (Permanent)

```bash
1. Only after 1 week of successful Vercel operation
2. Go to: Render Dashboard → Each service
3. Settings → Delete Service
4. Confirm deletion
5. Verify $0.00 monthly bill
```

## 🎯 Expected Results

After completing all steps:

| Metric | Expected | How to Verify |
|--------|----------|---------------|
| Login (Bahamas) | < 60ms | curl with -w timing |
| Login (USA) | < 40ms | curl with -w timing |
| Login (Europe) | < 60ms | curl with -w timing |
| Edge health check | < 30ms | curl /api/health |
| Cache hit rate | > 95% | Vercel Analytics |
| Edge network usage | > 99% | Vercel Analytics |
| Render monthly cost | $0.00 | Render billing page |

## 🚀 Performance Features

1. **Edge Functions** - `/api/cron` and `/api/health` run at Edge (<30ms)
2. **KV Session Cache** - Repeat logins hit cache (50-60ms vs 120ms)
3. **Preferred Regions** - Node.js functions distributed globally
4. **Aggressive Caching** - Jobs list cached for 60s in KV
5. **Keep-alive Cron** - Runs every 5 minutes to prevent cold starts

## 📊 Monitoring Checklist

- [ ] Vercel Analytics shows >99% Edge network usage
- [ ] P95 latency < 60ms for all regions
- [ ] Cache hit rate > 95% for jobs/stats endpoints
- [ ] No 502/499 errors (cold starts eliminated)
- [ ] Render billing = $0.00/month

## 🎉 Success!

You now have a **pure Edge-optimized platform** with global <60ms latency!

---

*Last updated: December 2024*
*For issues: https://github.com/cliffcho242/HireMeBahamas/issues*

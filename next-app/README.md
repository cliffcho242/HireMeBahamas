# HireMeBahamas - Next.js 15 Vercel Edition

The fastest job platform in the Bahamas. Built with Next.js 15, Vercel Edge Functions, and Vercel Postgres for sub-120ms logins and TikTok-smooth scrolling.

## 🚀 Performance Targets

| Metric | Target | Technology |
|--------|--------|------------|
| Login | < 120ms | Edge Functions + Vercel KV |
| Cold Start | < 800ms | Edge Runtime + Cron Keepalive |
| Feed Scroll | 60fps | React 19 + Suspense |
| Offline | Full Support | Service Worker + IndexedDB |

## 📁 Project Structure

```
next-app/
├── app/                      # Next.js App Router
│   ├── layout.tsx            # Root layout
│   ├── page.tsx              # Home page
│   ├── globals.css           # Global styles
│   └── api/                  # API Routes
│       ├── auth/login/       # Edge: < 120ms login
│       ├── auth/register/    # Serverless: bcrypt
│       ├── jobs/             # Serverless: CRUD + cache
│       ├── push/             # Serverless: Push notifications
│       └── cron/             # Edge: Keep-alive cron
├── components/               # React components
├── lib/                      # Utilities
│   ├── auth.ts               # JWT + session management
│   ├── db.ts                 # Database queries
│   └── schema.ts             # Drizzle ORM schema
├── public/                   # Static assets
│   ├── manifest.json         # PWA manifest
│   └── sw.js                 # Service Worker
├── middleware.ts             # Auth + caching
├── next.config.ts            # Next.js config
├── vercel.json               # Vercel config
└── drizzle.config.ts         # Database migrations
```

## 🛠️ Tech Stack

- **Framework**: Next.js 15 with App Router
- **Runtime**: Edge Functions + Node.js Serverless
- **Database**: Vercel Postgres (Neon)
- **Cache**: Vercel KV (Upstash Redis)
- **Auth**: jose (JWT) + bcryptjs
- **Styling**: Tailwind CSS
- **PWA**: Service Worker + Push Notifications
- **Analytics**: Vercel Analytics + Speed Insights

## 📦 Getting Started

```bash
# Install dependencies
npm install

# Setup environment variables
cp .env.example .env.local
# Edit .env.local with your values

# Deploy database schema
npm run db:push
# For detailed instructions, see DATABASE_SCHEMA_DEPLOYMENT.md

# Start development server
npm run dev

# Build for production
npm run build

# Deploy to Vercel
npx vercel --prod
```

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `POSTGRES_URL` | Vercel Postgres connection string | Yes |
| `KV_REST_API_URL` | Vercel KV REST API URL | Yes |
| `KV_REST_API_TOKEN` | Vercel KV REST API Token | Yes |
| `JWT_SECRET` | Secret for JWT signing (32+ chars) | Yes |
| `VAPID_PUBLIC_KEY` | Push notification public key | No |
| `VAPID_PRIVATE_KEY` | Push notification private key | No |

## 📱 PWA Features

- **Installable**: Add to home screen on iOS/Android
- **Offline**: Cache-first for static assets
- **Push Notifications**: Real-time alerts
- **Background Sync**: Queue actions when offline

## 🔒 Security

- HTTPS enforced (HSTS preload)
- JWT tokens with 24h expiry
- Rate limiting via KV (5 attempts/15 min)
- bcrypt password hashing (cost 12)
- Security headers (CSP, X-Frame-Options, etc.)

## 📊 Monitoring

- Vercel Analytics for Core Web Vitals
- Vercel Speed Insights for performance
- Structured logging in API routes
- Prometheus-compatible metrics

## 🚀 Deploy Checklist

- **Quick Deploy**: See [DEPLOY_CHECKLIST.md](./DEPLOY_CHECKLIST.md) for the 8-step deployment guide
- **Edge Network Setup**: See [VERCEL_EDGE_SETUP.md](./VERCEL_EDGE_SETUP.md) for complete Edge Network configuration and <60ms latency setup

## 📄 License

MIT - HireMeBahamas Team

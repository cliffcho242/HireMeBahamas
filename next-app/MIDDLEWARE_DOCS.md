# Middleware Implementation Documentation

## Overview
The middleware implements Edge authentication, geo-location tracking, and A/B testing for the HireMeBahamas Next.js application.

## Features

### 1. Edge Authentication
- Uses `jose` library for JWT verification (Edge-compatible)
- Protects routes: `/dashboard`, `/profile`, `/messages`, `/post-job`, `/settings`
- Redirects unauthenticated users to `/login` with redirect parameter
- Protects API routes (POST, PUT, DELETE, PATCH) with 401 responses

### 2. A/B Testing
- Randomly assigns variant 'a' or 'b' to each request
- Sets `x-ab-test` header in response
- Can be used by frontend to display different UI variants
- Probability: 50/50 split

### 3. Geo-location Support
- Reads Vercel Edge runtime geo headers:
  - `x-vercel-ip-country`
  - `x-vercel-ip-city`
  - `x-vercel-ip-country-region`
- Sets response headers:
  - `x-geo-country`
  - `x-geo-city`
  - `x-geo-region`
- Defaults to "unknown" if geo data not available

### 4. Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

### 5. Performance Optimizations
- Cache headers for static assets (1 year)
- Cache headers for API responses (60s with stale-while-revalidate)
- Runs on Edge runtime (fast, distributed globally)

## Matcher Configuration

```typescript
export const config = {
  matcher: "/((?!api/auth|_next|favicon.ico).*)",
};
```

This excludes:
- `/api/auth/*` - Authentication endpoints (handled separately)
- `/_next/*` - Next.js internal routes
- `/favicon.ico` - Browser icon

## Testing Instructions

### Local Development
The middleware runs automatically with `npm run dev`. However, geo-location headers will show "unknown" locally.

### Production Testing on Vercel

#### Test A/B Testing Header
```bash
curl -I https://your-domain.vercel.app/ | grep x-ab-test
# Expected: x-ab-test: a  OR  x-ab-test: b
```

#### Test Geo-location Headers
```bash
curl -I https://your-domain.vercel.app/ | grep x-geo
# Expected:
# x-geo-country: BS (or your country code)
# x-geo-city: Nassau (or your city)
# x-geo-region: NP (or your region)
```

#### Test Dashboard Protection
```bash
curl -I https://your-domain.vercel.app/dashboard
# Expected: Location: /login?redirect=%2Fdashboard
```

#### Test Protected API Route
```bash
curl -X POST https://your-domain.vercel.app/api/jobs -H "Content-Type: application/json"
# Expected: {"success":false,"message":"Authentication required"}
```

#### Test with Valid Token
```bash
# First login
TOKEN=$(curl -X POST https://your-domain.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.token')

# Then access protected route
curl -I https://your-domain.vercel.app/dashboard \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200 OK (not redirected)
```

## Environment Variables

Required for full functionality:
- `JWT_SECRET` - Secret key for JWT signing/verification (32+ characters)
- Vercel automatically provides geo-location headers in Edge runtime

## Performance Metrics

Expected performance on Vercel Edge:
- Middleware execution: < 10ms
- Total response time (with middleware): < 50ms
- Bundle size: ~38 KB

## Implementation Notes

1. **Why not next-auth?**
   - The project already uses `jose` for JWT handling
   - `jose` is Edge-compatible and lightweight
   - Adding next-auth would be a major breaking change
   - Current implementation provides same functionality with minimal overhead

2. **Edge Runtime Compatibility**
   - Uses `jose` instead of `jsonwebtoken` (Node.js only)
   - No filesystem access or Node.js-specific APIs
   - Optimized for fast cold starts

3. **A/B Testing Implementation**
   - Simple random assignment on each request
   - For persistent variants, consider using cookies or database
   - Current implementation: stateless (no session required)

## Troubleshooting

### Middleware not running
- Check matcher pattern includes your route
- Verify middleware.ts is in the root of next-app directory
- Check build output for "ƒ Middleware" entry

### Geo headers showing "unknown"
- This is normal in local development
- Deploy to Vercel to test geo-location
- Vercel Edge runtime provides these headers automatically

### A/B test header missing
- Check response headers in browser DevTools
- Middleware runs on all matched routes
- Verify matcher pattern isn't excluding your route

## Future Enhancements

Possible improvements:
- Persistent A/B variants (cookie-based)
- Advanced geo-targeting logic
- Rate limiting per geo-location
- Custom analytics integration
- Feature flags per region

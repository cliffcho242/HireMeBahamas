# Performance Monitoring & Lighthouse 90+ Setup

This document explains the performance monitoring setup for HireMeBahamas, including Lighthouse CI integration, Sentry performance tracking, and CI/CD protection.

## 🎯 Performance Goals

- **Lighthouse Performance Score**: 90+
- **First Contentful Paint (FCP)**: < 1.8s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Cumulative Layout Shift (CLS)**: < 0.1
- **Total Blocking Time (TBT)**: < 200ms
- **Speed Index**: < 3.4s

## 📊 Monitoring Tools

### 1. Lighthouse CI

Lighthouse CI runs automated performance tests on every pull request to ensure performance standards are maintained.

**Configuration**: `.lighthouserc.js`

**GitHub Actions**: `.github/workflows/lighthouse-ci.yml`

**Key Features**:
- Runs on every PR and push to main
- Tests desktop performance with 3 runs (averaged)
- Enforces performance budgets
- Blocks PRs that degrade performance below 90
- Uploads detailed reports as artifacts

**Running Locally**:
```bash
# Install Lighthouse CI
npm install -g @lhci/cli

# Build the frontend
cd frontend && npm run build

# Run Lighthouse CI
cd .. && lhci autorun
```

### 2. Sentry Performance Monitoring

Sentry tracks real user performance metrics in production.

**Configuration**: `frontend/src/main.tsx`

**Web Vitals Tracking**: `frontend/src/utils/webVitals.ts`

**Key Features**:
- Real User Monitoring (RUM)
- Core Web Vitals tracking (FCP, LCP, CLS, FID, TTFB)
- Session replay for debugging
- Performance profiling
- Error tracking with performance context

**Environment Variables Required**:
```env
VITE_SENTRY_DSN=your_sentry_dsn_here
VITE_SENTRY_TRACES_SAMPLE_RATE=0.2
VITE_SENTRY_PROFILES_SAMPLE_RATE=0.1
```

## 🚀 Performance Optimizations Implemented

### Build Optimizations
- **Code Splitting**: Vendor, UI, Forms, Query, Utils chunks
- **Tree Shaking**: Dead code elimination
- **Minification**: Terser with aggressive settings
- **Compression**: Gzip and Brotli compression
- **Source Maps**: Disabled in production for smaller bundles

### Network Optimizations
- **Resource Hints**: DNS prefetch, preconnect for critical origins
- **Preloading**: Critical fonts and assets
- **Caching**: Aggressive caching for static assets (1 year)
- **CDN**: Vercel Edge Network with global distribution

### Runtime Optimizations
- **Lazy Loading**: Route-based code splitting
- **PWA**: Service Worker with intelligent caching
- **Image Optimization**: WebP/AVIF formats, lazy loading
- **Font Loading**: Preload critical fonts, font-display: swap

### Resource Budgets
- **JavaScript**: Max 300KB (compressed)
- **CSS**: Max 50KB (compressed)
- **Images**: Max 500KB per page
- **Fonts**: Max 100KB total

## 📈 CI/CD Protection

### Lighthouse CI Workflow

The Lighthouse CI workflow runs automatically on:
- Pull requests to main
- Pushes to main
- Manual workflow dispatch

**What it does**:
1. Builds the frontend in production mode
2. Runs Lighthouse audits (3 runs, averaged)
3. Checks performance against budgets
4. Fails the build if performance < 90
5. Posts results as PR comments
6. Uploads detailed reports

**PR Protection**:
- Performance scores must be 90+ or PR is blocked
- Core Web Vitals must meet thresholds
- Resource budgets must not be exceeded

### Sentry Release Tracking

On successful merge to main:
1. Creates a Sentry release
2. Associates errors with specific deployments
3. Tracks performance regressions between releases

## 🔧 Configuration Files

### `.lighthouserc.js`
Lighthouse CI configuration with:
- Performance budgets
- Assertion rules
- Report output settings

### `frontend/vite.config.ts`
Build optimizations:
- Code splitting strategy
- Compression settings
- PWA configuration
- Module preloading

### `frontend/src/utils/webVitals.ts`
Custom Web Vitals tracking:
- FCP, LCP, CLS, FID, TTFB monitoring
- Automatic reporting to Sentry
- Performance thresholds

### `frontend/index.html`
Performance optimizations:
- Resource hints (preconnect, dns-prefetch)
- Critical CSS inlining
- Font preloading
- SSR-like shell for instant feedback

## 📊 Monitoring Dashboard

### Sentry Dashboard
Access at: https://sentry.io/

**What to monitor**:
- Performance score trends
- Core Web Vitals distributions
- P75, P95, P99 percentiles
- Slow transactions
- Performance alerts

### Lighthouse CI Reports
Access in GitHub Actions artifacts

**What to review**:
- Performance score over time
- Opportunities for improvement
- Diagnostics and suggestions
- Resource budgets

## 🚨 Performance Alerts

### Sentry Alerts
Configure alerts for:
- Performance score drops below 90
- LCP > 2.5s
- CLS > 0.1
- Transaction duration > 3s

### GitHub Actions
- PR checks fail if performance degrades
- Workflow fails if budgets exceeded
- Notifications sent to PR reviewers

## 🛠️ Troubleshooting

### Lighthouse CI Fails

**Check**:
1. Are resource budgets exceeded?
2. Did new dependencies increase bundle size?
3. Are images optimized?
4. Is code splitting working correctly?

**Fix**:
```bash
# Analyze bundle
cd frontend && npm run build
du -sh dist/assets/*

# Check for large dependencies
npx vite-bundle-visualizer
```

### Sentry Not Tracking

**Check**:
1. Is VITE_SENTRY_DSN set?
2. Is DSN valid?
3. Are sample rates too low?

**Fix**:
```bash
# Test Sentry locally
VITE_SENTRY_DSN=your_dsn npm run dev
# Check browser console for Sentry initialization
```

### Poor Performance Scores

**Common Issues**:
1. Large images not optimized
2. Too many JavaScript dependencies
3. Render-blocking resources
4. Missing compression

**Solutions**:
- Use WebP/AVIF formats
- Lazy load non-critical components
- Move scripts to async/defer
- Enable compression in build

## 📚 Resources

- [Lighthouse CI Documentation](https://github.com/GoogleChrome/lighthouse-ci)
- [Sentry Performance Monitoring](https://docs.sentry.io/product/performance/)
- [Web Vitals Guide](https://web.dev/vitals/)
- [Vite Performance Guide](https://vitejs.dev/guide/build.html#build-optimizations)

## 🎓 Best Practices

1. **Monitor Regularly**: Check Sentry dashboard weekly
2. **Review PR Comments**: Read Lighthouse CI feedback
3. **Test Locally**: Run Lighthouse before pushing
4. **Optimize Images**: Always compress and use modern formats
5. **Code Split**: Keep bundles under budgets
6. **Cache Strategically**: Use appropriate cache headers
7. **Measure Impact**: Compare before/after metrics
8. **Stay Updated**: Keep dependencies current

## 🔐 Security

- No sensitive data in performance traces
- Sentry filters authentication tokens
- Source maps not exposed in production
- Sample rates prevent excessive data collection

## 📝 Changelog

### 2025-01-17
- ✅ Added Lighthouse CI workflow
- ✅ Enhanced Sentry with Web Vitals tracking
- ✅ Created custom Web Vitals monitoring utility
- ✅ Configured performance budgets
- ✅ Added CI/CD protection with PR checks
- ✅ Optimized resource hints in index.html
- ✅ Documented performance monitoring setup

# Lighthouse CI Setup Guide

This guide explains how to set up and use Lighthouse CI for automated performance testing in the HireMeBahamas project.

## 🎯 What is Lighthouse CI?

Lighthouse CI is an automated tool that runs Google Lighthouse audits on your application and enforces performance budgets in your CI/CD pipeline. It helps ensure your application maintains high performance standards over time.

## 📦 What's Included

This repository now has Lighthouse CI configured with:

- **Performance Budgets**: Enforces 90+ Lighthouse score
- **Core Web Vitals**: Monitors FCP, LCP, CLS, TBT, Speed Index
- **Resource Budgets**: Limits on JS, CSS, images, and fonts
- **GitHub Actions Integration**: Runs on every PR and push
- **PR Comments**: Posts results directly to pull requests

## 🚀 Quick Start

### Option 1: Run Locally

```bash
# Install Lighthouse CI globally
npm install -g @lhci/cli

# Build your frontend
cd frontend && npm run build

# Run Lighthouse CI
cd .. && lhci autorun
```

This will:
1. Build your app
2. Start a local server
3. Run Lighthouse audits (3 times, averaged)
4. Check against budgets
5. Generate reports in `lighthouse-reports/`

### Option 2: View in CI

Lighthouse CI runs automatically on GitHub Actions:

1. Create or update a pull request
2. Wait for the "Lighthouse CI - Performance Monitoring" check
3. View results in:
   - PR comments (automated)
   - GitHub Actions logs
   - Artifacts (detailed HTML reports)

## 📊 Understanding Results

### Lighthouse Scores

Each category is scored from 0-100:

- **90-100**: ✅ Green (Excellent)
- **50-89**: 🟡 Orange (Needs Improvement)
- **0-49**: 🔴 Red (Poor)

### Core Web Vitals

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **FCP** (First Contentful Paint) | < 1.8s | 1.8s - 3.0s | > 3.0s |
| **LCP** (Largest Contentful Paint) | < 2.5s | 2.5s - 4.0s | > 4.0s |
| **CLS** (Cumulative Layout Shift) | < 0.1 | 0.1 - 0.25 | > 0.25 |
| **TBT** (Total Blocking Time) | < 200ms | 200ms - 600ms | > 600ms |
| **Speed Index** | < 3.4s | 3.4s - 5.8s | > 5.8s |

### Resource Budgets

Current budgets configured:

- **JavaScript**: 300KB (compressed)
- **CSS**: 50KB (compressed)
- **Images**: 500KB per page
- **Fonts**: 100KB total

## 🔧 Configuration

### Lighthouse CI Config (`.lighthouserc.js`)

The main configuration file with:
- Collection settings (how many runs, which audits)
- Assertions (what must pass)
- Upload settings (where reports go)

**Key settings you might want to adjust:**

```javascript
module.exports = {
  ci: {
    collect: {
      numberOfRuns: 3, // Increase for more stable results
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }], // 90+ required
        // Add more assertions here
      },
    },
  },
};
```

### GitHub Actions Workflow (`.github/workflows/lighthouse-ci.yml`)

Runs Lighthouse CI automatically:
- On PRs to main
- On pushes to main
- Can be triggered manually

**To disable Lighthouse CI temporarily:**

Add to PR description:
```
[skip lighthouse]
```

Or modify the workflow file to add conditions.

## 📈 Improving Your Score

### Common Issues and Fixes

#### 1. Large JavaScript Bundles

**Problem**: Bundle size too large

**Solutions**:
- Enable code splitting
- Use dynamic imports for routes
- Remove unused dependencies
- Use tree shaking

```javascript
// Before
import { hugeLibrary } from 'huge-library';

// After (lazy load)
const hugeLibrary = () => import('huge-library');
```

#### 2. Render-Blocking Resources

**Problem**: CSS/JS blocks first paint

**Solutions**:
- Inline critical CSS
- Defer non-critical JavaScript
- Use preload for important resources

```html
<!-- Preload critical assets -->
<link rel="preload" href="/critical.css" as="style">
<link rel="preload" href="/main.js" as="script">
```

#### 3. Large Images

**Problem**: Unoptimized images slow load

**Solutions**:
- Use WebP/AVIF formats
- Implement lazy loading
- Use responsive images
- Compress images

```jsx
// Lazy load images
<img loading="lazy" src="image.webp" alt="Description" />
```

#### 4. Layout Shifts

**Problem**: Content moves as page loads

**Solutions**:
- Reserve space for images with width/height
- Avoid inserting content above existing content
- Use `transform` animations instead of properties that trigger layout

```css
/* Good - uses transform */
.element {
  transform: translateY(100px);
}

/* Bad - causes layout shift */
.element {
  margin-top: 100px;
}
```

## 🎛️ Advanced Configuration

### Custom Budgets

Edit `.lighthouserc.js` to adjust budgets:

```javascript
assertions: {
  // More strict performance requirement
  'categories:performance': ['error', { minScore: 0.95 }],
  
  // Stricter resource budgets
  'resource-summary:script:size': ['error', { maxNumericValue: 250000 }],
  
  // Allow more images
  'resource-summary:image:size': ['warn', { maxNumericValue: 750000 }],
}
```

### Multiple URLs

Test multiple pages:

```javascript
collect: {
  url: [
    'http://localhost:3000/',
    'http://localhost:3000/jobs',
    'http://localhost:3000/profile',
  ],
}
```

### CI Server (Optional)

For persistent reports, set up Lighthouse CI server:

```bash
# Deploy LHCI server (separate from your app)
npm install -g @lhci/server
lhci server --port 9001

# Update .lighthouserc.js
upload: {
  target: 'lhci',
  serverBaseUrl: 'https://your-lhci-server.com',
  token: 'YOUR_BUILD_TOKEN',
}
```

## 🔍 Debugging

### Lighthouse CI Fails Locally but Passes in CI

**Possible causes**:
- Different build settings
- Missing environment variables
- Different Node.js versions
- Browser extensions interfering

**Solutions**:
```bash
# Use same Node version as CI
nvm use 22

# Clear cache and rebuild
rm -rf node_modules package-lock.json
npm install
npm run build

# Run with debug output
LHCI_DEBUG=1 lhci autorun
```

### PR Check Fails

1. **View the logs**: Click "Details" on the failed check
2. **Check artifacts**: Download the Lighthouse reports
3. **Review the PR comment**: See which metrics failed
4. **Fix the issues**: See "Improving Your Score" section

### Reports Not Generated

**Check**:
1. Build completed successfully?
2. `dist/` directory exists?
3. `lighthouse-reports/` directory created?

**Debug**:
```bash
# Verbose output
lhci autorun --debug

# Check if server starts
cd frontend/dist && python -m http.server 9000
```

## 📚 Resources

- [Lighthouse CI Documentation](https://github.com/GoogleChrome/lighthouse-ci/blob/main/docs/getting-started.md)
- [Lighthouse Scoring Guide](https://web.dev/performance-scoring/)
- [Core Web Vitals](https://web.dev/vitals/)
- [Performance Budgets](https://web.dev/performance-budgets-101/)

## 🆘 Getting Help

If you run into issues:

1. Check the [Lighthouse CI Docs](https://github.com/GoogleChrome/lighthouse-ci)
2. Review recent [GitHub Actions runs](https://github.com/cliffcho242/HireMeBahamas/actions/workflows/lighthouse-ci.yml)
3. Read `PERFORMANCE_MONITORING.md` for overall setup
4. Check [Lighthouse Issues](https://github.com/GoogleChrome/lighthouse/issues)

## 📝 Best Practices

1. **Run locally before pushing**: Catch issues early
2. **Check reports regularly**: Don't wait for failures
3. **Set realistic budgets**: Too strict = constant failures
4. **Monitor trends**: Look for gradual degradation
5. **Fix regressions quickly**: Don't let them accumulate
6. **Update budgets carefully**: Document why limits changed
7. **Test on real devices**: Lighthouse is a simulation

## 🎉 Success Criteria

Your PR will pass Lighthouse CI when:

- ✅ Performance score ≥ 90
- ✅ All Core Web Vitals in "good" range
- ✅ Resource budgets not exceeded
- ✅ No critical errors in console
- ✅ Accessibility score ≥ 90 (warning)

Keep your scores green and your users happy! 🚀

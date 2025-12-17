# Performance Optimization - Quick Start Guide

## 🚀 Quick Commands

### Build & Analyze
```bash
cd frontend
npm run build          # Full build with sitemap + bundle analysis
npm run analyze-bundle # Standalone bundle analysis
npm run validate-seo   # Check SEO compliance
npm run generate-sitemap # Update sitemap.xml
```

## 📊 What's New

### 1. Automatic Sitemap Generation
- ✅ Runs on every build
- ✅ Updates to current date automatically
- ✅ 9 routes included
- 📄 Location: `frontend/public/sitemap.xml`

### 2. Bundle Size Analysis
- ✅ Runs after every build
- ✅ Color-coded warnings (Green/Yellow/Red)
- ✅ Performance budgets enforced
- 📄 Report: `frontend/dist/bundle-report.json`

### 3. SEO Validation
- ✅ 22/24 checks passed (92%)
- ✅ Meta tags verified
- ✅ Structured data validated
- ✅ JSON-LD syntax checked

### 4. Enhanced Lighthouse CI
- ✅ Runs on PR + push to main
- ✅ Actual scores in PR comments
- ✅ Bundle size tracking
- ✅ Artifacts uploaded (30 days)

## 📈 Current Performance

### Bundle Sizes (Compressed)
| Type | Original | Brotli | Savings |
|------|----------|--------|---------|
| JS | 1,442 KB | ~150 KB | 90% |
| CSS | 103 KB | ~13.5 KB | 87% |

### SEO Score
- ✅ 92% (22/24 checks passed)
- ✅ Open Graph complete
- ✅ Twitter Cards complete
- ✅ JSON-LD structured data

## 🎯 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Performance Score | 90+ | TBD (run Lighthouse) |
| Accessibility | 90+ | TBD |
| Best Practices | 90+ | TBD |
| SEO | 90+ | TBD |
| LCP | < 2.5s | TBD |
| FID | < 100ms | TBD |
| CLS | < 0.1 | TBD |

## 🔄 Build Pipeline

```
prebuild → build → postbuild
   ↓        ↓         ↓
 Validate  Vite     Analyze
 Sitemap   Build    Bundles
```

## 📝 Adding New Routes

Edit `frontend/scripts/generate-sitemap.js`:

```javascript
const routes = [
  // Add your route here
  {
    path: '/new-page',
    changefreq: 'weekly',
    priority: 0.7,
    description: 'New Page'
  }
];
```

Then run:
```bash
npm run generate-sitemap
```

## 🐛 Quick Troubleshooting

### Build Fails
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Bundle Too Large
Check: `frontend/dist/bundle-report.json`
- Review warnings
- Remove unused dependencies
- Use dynamic imports

### SEO Issues
```bash
npm run validate-seo
# Fix issues in index.html
# Re-run validation
```

## 📦 Files Changed

```
.github/workflows/lighthouse-ci.yml    # Enhanced workflow
frontend/index.html                    # SEO meta tags
frontend/package.json                  # New scripts
frontend/public/sitemap.xml           # Updated sitemap
frontend/scripts/
  ├── analyze-bundle.js               # Bundle analyzer
  ├── generate-sitemap.js             # Sitemap generator
  └── validate-seo.js                 # SEO validator
```

## ✅ Pre-Commit Checklist

- [ ] Run `npm run build`
- [ ] Check bundle analysis output
- [ ] Run `npm run validate-seo`
- [ ] Verify no TypeScript errors
- [ ] Test locally

## 🔗 Learn More

- Full docs: `FRONTEND_PERFORMANCE_FEATURES.md`
- Performance guide: `PERFORMANCE_OPTIMIZATION.md`
- Lighthouse config: `.lighthouserc.js`

## 💡 Tips

1. **Monitor Bundle Size**: Keep total JS under 800KB (uncompressed)
2. **Check SEO Regularly**: Run `validate-seo` before commits
3. **Review Lighthouse**: Check PR comments for scores
4. **Update Sitemap**: When adding new pages

---

**Quick Help**:
```bash
cd frontend
npm run --list  # Show all available scripts
```

**Last Updated**: 2025-12-17

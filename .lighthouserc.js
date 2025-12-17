module.exports = {
  ci: {
    collect: {
      // Run Lighthouse on the built static files
      staticDistDir: './frontend/dist',
      // Number of runs to perform (average results for consistency)
      numberOfRuns: 3,
      // Lighthouse settings
      settings: {
        // Use desktop settings for more consistent results
        preset: 'desktop',
        // Additional Lighthouse flags
        onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
        // Emulated form factor
        formFactor: 'desktop',
        throttling: {
          rttMs: 40,
          throughputKbps: 10240,
          cpuSlowdownMultiplier: 1,
        },
        screenEmulation: {
          mobile: false,
          width: 1350,
          height: 940,
          deviceScaleFactor: 1,
          disabled: false,
        },
      },
    },
    assert: {
      // Performance budget assertions
      assertions: {
        // Core Web Vitals
        'categories:performance': ['error', { minScore: 0.9 }], // 90+ performance score
        'categories:accessibility': ['warn', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.9 }],
        'categories:seo': ['warn', { minScore: 0.9 }],
        
        // Web Vitals thresholds
        'first-contentful-paint': ['error', { maxNumericValue: 1800 }], // 1.8s
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }], // 2.5s
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }], // 0.1
        'total-blocking-time': ['error', { maxNumericValue: 200 }], // 200ms
        'speed-index': ['error', { maxNumericValue: 3400 }], // 3.4s
        
        // Resource budgets
        'resource-summary:script:size': ['error', { maxNumericValue: 300000 }], // 300KB
        'resource-summary:stylesheet:size': ['error', { maxNumericValue: 50000 }], // 50KB
        'resource-summary:image:size': ['warn', { maxNumericValue: 500000 }], // 500KB
        'resource-summary:font:size': ['warn', { maxNumericValue: 100000 }], // 100KB
        
        // Best practices
        'uses-optimized-images': ['warn', { minScore: 0.9 }],
        'uses-text-compression': 'error',
        'uses-responsive-images': ['warn', { minScore: 0.9 }],
        'modern-image-formats': ['warn', { minScore: 0.8 }],
        'efficient-animated-content': 'warn',
        'unused-css-rules': 'warn',
        'unused-javascript': 'warn',
        
        // Network performance
        'render-blocking-resources': 'warn',
        'unminified-css': 'error',
        'unminified-javascript': 'error',
        
        // Caching
        'uses-long-cache-ttl': 'warn',
      },
    },
    upload: {
      // For now, output to filesystem
      // Can be configured to upload to Lighthouse CI server later
      target: 'filesystem',
      outputDir: './lighthouse-reports',
    },
  },
};

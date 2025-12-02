# Vercel Configuration Validation

## Overview

This document explains the Vercel configuration validation system implemented to prevent deployment failures due to invalid `vercel.json` configuration properties.

## Problem

Vercel's deployment system validates `vercel.json` files against a strict schema. Properties that start with underscores (like `_comment_memory`) or are not officially supported will cause validation errors and deployment failures.

### Common Error Messages
- `should NOT have additional property '_comment_memory'`
- `should NOT have additional property '_comment_...'`
- Unknown property warnings

## Solution

We've implemented a validation script that runs in the CI/CD pipeline to catch invalid properties before deployment.

### Validation Script

Location: `scripts/validate_vercel_config.py`

This script checks:
1. **No underscore-prefixed properties** - Properties starting with `_` are not allowed
2. **Valid top-level properties** - Only officially documented Vercel properties
3. **Valid function configuration** - Proper serverless function settings

### Files Validated

- `vercel.json` (root)
- `frontend/vercel.json`
- `next-app/vercel.json`
- `vercel_backend.json`
- `vercel_immortal.json`

## Usage

### Local Validation

Run the validation script locally before committing:

```bash
python3 scripts/validate_vercel_config.py
```

### CI/CD Integration

The validation runs automatically on every pull request and push to the main branch via the `validate-vercel-config` job in `.github/workflows/ci.yml`.

## Valid Vercel Properties

### Top-Level Properties

```json
{
  "version": 2,
  "name": "project-name",
  "framework": "vite",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm ci",
  "functions": { },
  "rewrites": [ ],
  "redirects": [ ],
  "headers": [ ],
  "env": { },
  "regions": [ ],
  "crons": [ ]
}
```

### Function Configuration

```json
{
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.12",
      "memory": 1024,
      "maxDuration": 10
    }
  }
}
```

## Best Practices

1. **Never use underscore-prefixed properties** for comments or metadata
2. **Use separate documentation files** instead of inline comments in JSON
3. **Refer to official Vercel documentation** for supported properties: https://vercel.com/docs/projects/project-configuration
4. **Run validation locally** before pushing changes

## Troubleshooting

### Validation Fails Locally

If validation fails:

1. Check the error message for the specific property causing issues
2. Remove any properties starting with `_`
3. Verify all properties are officially supported by Vercel
4. Re-run the validation script

### Validation Passes But Deployment Fails

If validation passes locally but deployment still fails:

1. Check Vercel's deployment logs for specific errors
2. Ensure you're using the latest Vercel schema
3. Verify environment variables are properly set in Vercel dashboard
4. Check for property value format issues (not just property names)

## References

- [Vercel Configuration Documentation](https://vercel.com/docs/projects/project-configuration)
- [Vercel Functions Documentation](https://vercel.com/docs/functions)
- [Vercel Deployment Documentation](https://vercel.com/docs/deployments/overview)

# Frogbot Configuration - Optional Feature

## Overview

Frogbot is an **optional** security scanning tool that integrates with JFrog's Xray platform to scan dependencies for vulnerabilities. The Frogbot workflows in this repository are configured to run **only when JFrog credentials are available**.

## Current Status

✅ **Workflows are configured but skipped by default**

The following workflows will automatically skip if JFrog secrets are not configured:
- `.github/workflows/frogbot-scan-and-fix.yml` - Scans main branch on push
- `.github/workflows/frogbot-pr-scan.yml` - Scans pull requests

## Why Workflows Are Skipped

These workflows require external JFrog platform credentials that are not included in the repository:
- `JF_URL` - Your JFrog platform URL (e.g., https://mycompany.jfrog.io)
- `JF_ACCESS_TOKEN` - Authentication token for JFrog platform

Without these secrets, the workflows will be **skipped** and won't cause CI failures.

## How to Enable Frogbot (Optional)

If you want to enable Frogbot scanning, follow these steps:

### 1. Sign up for JFrog Platform (Free Tier Available)
- Visit: https://jfrog.com/start-free/
- Create an account and get your platform URL

### 2. Generate Access Token
1. Log in to your JFrog platform
2. Go to: **Administration → User Management → Access Tokens**
3. Click **"Generate Token"**
4. Select scope: **"Xray"** with **"Read"** permission
5. Set expiration as needed
6. Copy the token (shown only once)

### 3. Add GitHub Secrets
Go to: `https://github.com/YOUR-ORG/YOUR-REPO/settings/secrets/actions`

Add these secrets:
```
Secret Name: JF_URL
Value: https://YOUR-COMPANY.jfrog.io

Secret Name: JF_ACCESS_TOKEN
Value: [Your generated token]
```

### 4. Verify
Push to main branch or open a PR. The Frogbot workflows will now run automatically.

## What Frogbot Does (When Enabled)

### On Push to Main:
- Scans Python dependencies (backend/requirements.txt)
- Scans Node.js dependencies (frontend/package.json)
- Analyzes for security vulnerabilities
- Performs license compliance checks
- Auto-creates PRs with fixes for vulnerabilities

### On Pull Requests:
- Scans PR changes for new vulnerabilities
- Comments on PR with security analysis
- Shows security impact before merge
- Helps prevent vulnerable code from reaching main

## Troubleshooting

### Workflows are being skipped
**This is expected behavior** when JFrog secrets are not configured. No action needed unless you want to enable Frogbot.

### Error: "JF_URL must be provided"
This error should no longer occur. If you see it, ensure you're using the latest version of the workflow files from this repository.

### I want to disable Frogbot completely
You can disable the workflows in GitHub:
1. Go to: **Repository → Actions**
2. Select the workflow
3. Click **"..."** → **"Disable workflow"**

## Additional Resources

- Full setup guide: `FROGBOT_SETUP.md`
- JFrog Documentation: https://docs.jfrog-applications.jfrog.io/jfrog-applications/frogbot
- JFrog Free Tier: https://jfrog.com/start-free/

## Summary

- ✅ Frogbot is **optional** and not required for CI to pass
- ✅ Workflows **skip automatically** when secrets are missing
- ✅ No CI failures due to missing JFrog credentials
- ✅ Can be enabled at any time by adding GitHub secrets
- ✅ Provides enhanced security scanning when enabled

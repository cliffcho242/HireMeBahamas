# FROGBOT SETUP — FINAL CONFIGURATION (2025)

## 🎯 ONE-TIME SETUP (4 STEPS)

### STEP 1: Get JFrog Platform Access
```
✓ Sign up: https://jfrog.com/start-free/
✓ Get your platform URL (format: https://YOUR-COMPANY.jfrog.io)
✓ Create Access Token with Xray read permissions
```

### STEP 2: Configure GitHub Secrets
Go to: `https://github.com/YOUR-ORG/YOUR-REPO/settings/secrets/actions`

**Add these secrets:**
```
Secret Name: JF_URL
Value: https://YOUR-COMPANY.jfrog.io
Example: https://mycompany.jfrog.io

Secret Name: JF_ACCESS_TOKEN
Value: YOUR-ACCESS-TOKEN-HERE
Example: eyJ2ZXIiOiIyIiwidHlwIjoiSldUIiwiYWxnIjoiUlMyNTYi...
```

### STEP 3: Verify Workflow Files
Ensure these files exist in your repository:
```
✓ .github/workflows/frogbot-scan-and-fix.yml
✓ .github/workflows/frogbot-pr-scan.yml
```

### STEP 4: Test It
```bash
# Push to main branch to trigger scan
git add .
git commit -m "Enable Frogbot scanning"
git push origin main

# Check Actions tab for workflow run
# URL: https://github.com/YOUR-ORG/YOUR-REPO/actions
```

---

## 📋 FINAL WORKFLOW FILES

### `.github/workflows/frogbot-scan-and-fix.yml`
```yaml
name: "Frogbot Scan and Fix"
on:
  push:
    branches: [ "main" ]
permissions:
  contents: write
  pull-requests: write
  security-events: write
jobs:
  create-fix-pull-requests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y build-essential libpq-dev python3-dev

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - uses: jfrog/frogbot@v2
        env:
          JF_URL: ${{ secrets.JF_URL }}
          JF_ACCESS_TOKEN: ${{ secrets.JF_ACCESS_TOKEN }}
          JF_GIT_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          JF_INSTALL_DEPS_CMD: "pip install -r backend/requirements.txt && cd frontend && npm ci"
```

### `.github/workflows/frogbot-pr-scan.yml`
```yaml
name: "Frogbot PR Scan"
on:
  pull_request_target:
    types: [ opened, synchronize ]
permissions:
  pull-requests: write
  contents: read
  security-events: write
jobs:
  scan-pull-request:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y build-essential libpq-dev python3-dev

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - uses: jfrog/frogbot@v2
        env:
          JF_URL: ${{ secrets.JF_URL }}
          JF_ACCESS_TOKEN: ${{ secrets.JF_ACCESS_TOKEN }}
          JF_GIT_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          JF_INSTALL_DEPS_CMD: "pip install -r backend/requirements.txt && cd frontend && npm ci"
```

---

## 🔧 JFROG PLATFORM URL FORMATS

### Cloud (SaaS) — RECOMMENDED
```
Format: https://YOUR-COMPANY.jfrog.io
Example: https://mycompany.jfrog.io
Example: https://acme-corp.jfrog.io
```

### Self-Hosted
```
Format: https://your-domain.com/artifactory
Example: https://jfrog.mycompany.com
Example: https://artifactory.internal.corp.com
```

### CRITICAL: NO TRAILING SLASH
```
✓ CORRECT: https://mycompany.jfrog.io
✗ WRONG:   https://mycompany.jfrog.io/
```

---

## 🚀 WHAT HAPPENS AFTER SETUP

### On Every Push to `main`:
1. ✅ Frogbot scans Python dependencies (backend/requirements.txt)
2. ✅ Frogbot scans Node.js dependencies (frontend/package.json)
3. ✅ Xray analyzes for vulnerabilities
4. ✅ License scanning checks compliance
5. ✅ Auto-creates PRs with fixes for vulnerabilities

### On Every Pull Request:
1. ✅ Frogbot scans PR changes
2. ✅ Comments on PR with vulnerability details
3. ✅ Shows security impact before merge
4. ✅ Prevents vulnerable code from reaching main

---

## 🎯 QUICK REFERENCE

### GitHub Secrets Required
| Secret Name | Where to Get | Example |
|------------|--------------|---------|
| `JF_URL` | JFrog Platform Dashboard | https://mycompany.jfrog.io |
| `JF_ACCESS_TOKEN` | JFrog Platform → Admin → Access Tokens | eyJ2ZXIiOi... |

### Get JFrog Access Token
```
1. Login to JFrog Platform
2. Go to: Administration → User Management → Access Tokens
3. Click "Generate Token"
4. Scope: Select "Xray" with "Read" permission
5. Expiration: Set to "Never expires" or appropriate duration
6. Copy the token (shown only once)
7. Add to GitHub Secrets as JF_ACCESS_TOKEN
```

---

## ✅ VERIFICATION CHECKLIST

After setup, verify these are working:

- [ ] GitHub Secrets are configured (JF_URL, JF_ACCESS_TOKEN)
- [ ] Push to main triggers Frogbot workflow
- [ ] Workflow completes without "JF_URL must be provided" error
- [ ] Frogbot comments on pull requests
- [ ] Vulnerability PRs are auto-created (if vulnerabilities found)
- [ ] Actions tab shows green checkmarks

---

## 🔥 TROUBLESHOOTING

### Error: "JF_URL must be provided"
**Solution:** Check GitHub Secrets
```
1. Go to repo Settings → Secrets → Actions
2. Verify JF_URL exists and has correct value
3. Format: https://YOUR-COMPANY.jfrog.io (no trailing slash)
4. Re-run workflow after fixing
```

### Error: "Authentication failed"
**Solution:** Check Access Token
```
1. Verify JF_ACCESS_TOKEN in GitHub Secrets
2. Token must have "Xray Read" permissions
3. Token must not be expired
4. Generate new token if needed
```

### Error: "Failed to install dependencies"
**Solution:** Check install command
```
Current: pip install -r backend/requirements.txt && cd frontend && npm ci
Verify: Both requirements.txt and package.json exist
Adjust: Update JF_INSTALL_DEPS_CMD if project structure differs
```

---

## 🎖️ SUCCESS CRITERIA

You know Frogbot is working when:

✅ No "JF_URL must be provided" errors
✅ Workflows complete successfully
✅ Vulnerability PRs are auto-created
✅ PR comments show security analysis
✅ Xray + license scanning active
✅ Green checkmarks in Actions tab

---

## 📚 ADDITIONAL RESOURCES

- JFrog Free Tier: https://jfrog.com/start-free/
- Frogbot Docs: https://docs.jfrog-applications.jfrog.io/jfrog-applications/frogbot
- GitHub Actions: https://github.com/features/actions
- Xray Scanning: https://jfrog.com/xray/

---

**DEPLOYMENT TIME: 60 SECONDS**
**RESULT: TOTAL DOMINATION** ✅

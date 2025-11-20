# Automated PR Status Check System

## Overview

This directory contains tools for monitoring and reporting the status of pull requests in the HireMeBahamas repository.

## Files

### `check_pr_status.py`
A Python script that checks the status of all open pull requests and reports issues.

**Features:**
- Fetches all open PRs via GitHub API
- Checks mergeable status (clean, dirty, unstable, blocked, behind)
- Identifies merge conflicts
- Detects failing CI checks
- Reports stale PRs (not updated in 7+ days)
- Provides severity-based reporting (critical, warning, info, healthy)

**Usage:**

```bash
# Basic usage (uses environment variables)
python scripts/check_pr_status.py

# Specify repository
python scripts/check_pr_status.py HireMeBahamas cliffcho242

# With GitHub token for higher API rate limits
GITHUB_TOKEN=your_token python scripts/check_pr_status.py

# In CI/CD (automatically uses GITHUB_TOKEN)
python scripts/check_pr_status.py
```

**Environment Variables:**
- `GITHUB_TOKEN` - Personal access token (optional, increases rate limit)
- `GITHUB_REPOSITORY_OWNER` - Repository owner (default: cliffcho242)
- `GITHUB_REPOSITORY` - Repository name (default: HireMeBahamas)

**Exit Codes:**
- `0` - All PRs are healthy or have non-critical issues
- `1` - One or more PRs have critical issues (merge conflicts)

**Example Output:**

```
Checking PRs for repository: cliffcho242/HireMeBahamas
Found 4 open pull request(s).

================================================================================
Pull Request Status Report - 2025-11-20 15:00:00
Repository: cliffcho242/HireMeBahamas
================================================================================

🔴 CRITICAL ISSUES:

PR #23: Automated Dependency Activation and Verification System
  Branch: copilot/add-automated-dependency-checker
  Base SHA: 7ed4eee
  Mergeable: False
  State: dirty
  ⚠️  Has merge conflicts with base branch
  ⚠️  Mergeable state: dirty

PR #24: Automate complete dependency installation
  Branch: copilot/automate-dependency-installation
  Base SHA: b5fd9c8
  Mergeable: False
  State: dirty
  ⚠️  Has merge conflicts with base branch
  ⚠️  Mergeable state: dirty

⚠️  WARNINGS:

PR #30: Fix frontend build failure caused by ESLint errors
  Branch: copilot/fix-frontend-build-error
  Base SHA: 7ed4eee
  Mergeable: Unknown
  State: unstable
  ⚠️  CI checks are failing or pending
  ⚠️  Mergeable state: unstable

================================================================================
Total PRs: 4
Critical: 2 | Warnings: 1 | Info: 0 | Healthy: 1
================================================================================
```

## Dependencies

**Required:**
- Python 3.6+
- `requests` library

**Installation:**
```bash
pip install requests
```

## Integration with CI/CD

You can add this script to your GitHub Actions workflow to automatically check PR status:

```yaml
name: PR Status Check

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:  # Manual trigger

jobs:
  check-prs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install requests
      
      - name: Check PR status
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python scripts/check_pr_status.py
```

## Limitations

### What This Tool CAN Do:
✅ Check PR mergeable status via GitHub API  
✅ Detect merge conflicts  
✅ Identify failing CI checks  
✅ Report stale PRs  
✅ Generate status reports  

### What This Tool CANNOT Do:
❌ Resolve merge conflicts automatically  
❌ Rebase branches (requires force push)  
❌ Push to other branches  
❌ Fix failing CI checks automatically  
❌ Update PR descriptions or labels  

### Why Automated Conflict Resolution Is Not Possible

Merge conflict resolution requires:
1. Checking out the PR branch
2. Rebasing onto the target branch
3. Manually resolving conflicts
4. Force pushing the rebased branch

**Force push is prohibited** for security reasons in automated environments. This must be done manually by repository maintainers.

## Manual Resolution Process

When the script reports critical issues (merge conflicts), follow these steps:

### For PRs with Merge Conflicts:

1. **Fetch latest changes:**
   ```bash
   git fetch origin
   ```

2. **Checkout the PR branch:**
   ```bash
   git checkout <pr-branch-name>
   ```

3. **Rebase onto main:**
   ```bash
   git rebase origin/main
   ```

4. **Resolve conflicts:**
   - Edit conflicting files
   - Use `git status` to see which files need attention
   - After resolving each file:
     ```bash
     git add <resolved-file>
     ```

5. **Continue rebase:**
   ```bash
   git rebase --continue
   ```

6. **Force push (CAUTION):**
   ```bash
   git push --force-with-lease origin <pr-branch-name>
   ```

   **Note:** Use `--force-with-lease` instead of `--force` for safety. It will fail if someone else pushed to the branch while you were rebasing.

### For PRs with Failing CI:

1. **Check the CI logs** in the PR's "Checks" tab
2. **Identify the failing test/lint/build**
3. **Fix the issue** in the PR branch
4. **Push the fix:**
   ```bash
   git add <fixed-files>
   git commit -m "Fix CI issue: <description>"
   git push origin <pr-branch-name>
   ```

## Related Documentation

- [PR_STATUS_REPORT.md](../PR_STATUS_REPORT.md) - Detailed analysis of current PR issues
- [INSTALLATION_COMPLETE.md](../docs/INSTALLATION_COMPLETE.md) - Installation instructions
- [AUTOMATED_DEPENDENCIES.md](../docs/AUTOMATED_DEPENDENCIES.md) - Dependency automation docs

## Support

For questions or issues with this tool:
1. Check the [PR_STATUS_REPORT.md](../PR_STATUS_REPORT.md) for current status
2. Review GitHub Actions logs if running in CI/CD
3. Ensure you have the required dependencies installed
4. Verify GitHub API rate limits (use GITHUB_TOKEN to increase limits)

## License

This tool is part of the HireMeBahamas project and follows the same license.

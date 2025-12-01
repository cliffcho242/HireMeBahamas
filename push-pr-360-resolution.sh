#!/bin/bash
# Helper script to push the resolved PR #360 branch
# Run this after resolve-pr-360-conflicts.sh

set -e

echo "==========================================="
echo "Pushing PR #360 Resolution to GitHub"
echo "==========================================="
echo ""

# Check if we're on the right branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "copilot/update-postgres-connection-strings" ]; then
    echo "Error: Not on correct branch"
    echo "Current branch: $current_branch"
    echo "Expected: copilot/update-postgres-connection-strings"
    echo ""
    echo "Run this command first:"
    echo "  git checkout copilot/update-postgres-connection-strings"
    exit 1
fi

echo "Current branch: $current_branch ✓"
echo ""

# Check if there's something to push
if git diff origin/copilot/update-postgres-connection-strings..HEAD --quiet; then
    echo "No changes to push - branch is already up to date!"
    exit 0
fi

echo "Changes detected. Preparing to push..."
echo ""

# Show what will be pushed
echo "Commits to be pushed:"
git log --oneline origin/copilot/update-postgres-connection-strings..HEAD
echo ""

# Confirm before pushing
read -p "Push these changes to origin? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Push cancelled"
    exit 0
fi

echo ""
echo "Pushing to origin..."
git push origin copilot/update-postgres-connection-strings

echo ""
echo "==========================================="
echo "✓ Successfully pushed to GitHub!"
echo "==========================================="
echo ""
echo "Next steps:"
echo "1. Go to https://github.com/cliffcho242/HireMeBahamas/pull/360"
echo "2. Verify PR #360 is now mergeable"
echo "3. Merge the PR!"
echo ""

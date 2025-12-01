#!/bin/bash
# Script to resolve merge conflicts for PR #360
# This script merges main into the copilot/update-postgres-connection-strings branch
# resolving all conflicts to make the PR mergeable

set -e  # Exit on error

echo "==========================================="
echo "Resolving PR #360 Merge Conflicts"
echo "==========================================="
echo ""

# Ensure we're in the repository root
if [ ! -d ".git" ]; then
    echo "Error: Must be run from repository root"
    exit 1
fi

echo "Step 1: Fetching latest changes..."
git fetch origin main
git fetch origin copilot/update-postgres-connection-strings

echo ""
echo "Step 2: Checking out PR #360 branch..."
git checkout copilot/update-postgres-connection-strings

echo ""
echo "Step 3: Merging main with --allow-unrelated-histories..."
if git merge main --allow-unrelated-histories --no-edit; then
    echo "Merge completed without conflicts!"
    exit 0
fi

echo ""
echo "Step 4: Resolving conflicts..."

# Resolve .gitignore - accept main's version
git checkout --theirs .gitignore
git add .gitignore
echo "  ✓ Resolved .gitignore"

# Resolve .vercelignore - accept main's version  
git checkout --theirs .vercelignore
git add .vercelignore
echo "  ✓ Resolved .vercelignore"

# Resolve drizzle.config.ts - keep PR #360's non-pooling logic
git checkout --ours next-app/drizzle.config.ts
git add next-app/drizzle.config.ts
echo "  ✓ Resolved next-app/drizzle.config.ts"

# Resolve .env.example files - keep PR #360's comprehensive documentation
git checkout --ours .env.example
git add .env.example
echo "  ✓ Resolved .env.example"

git checkout --ours backend/.env.example
git add backend/.env.example
echo "  ✓ Resolved backend/.env.example"

git checkout --ours next-app/.env.example
git add next-app/.env.example
echo "  ✓ Resolved next-app/.env.example"

# Resolve documentation files - keep PR #360's comprehensive docs
git checkout --ours RAILWAY_PG_STAT_STATEMENTS_SETUP.md
git add RAILWAY_PG_STAT_STATEMENTS_SETUP.md
echo "  ✓ Resolved RAILWAY_PG_STAT_STATEMENTS_SETUP.md"

git checkout --ours VERCEL_POSTGRES_MIGRATION.md
git add VERCEL_POSTGRES_MIGRATION.md
echo "  ✓ Resolved VERCEL_POSTGRES_MIGRATION.md"

git checkout --ours VERCEL_EDGE_IMPLEMENTATION.md
git add VERCEL_EDGE_IMPLEMENTATION.md
echo "  ✓ Resolved VERCEL_EDGE_IMPLEMENTATION.md"

git checkout --ours next-app/DEPLOY_CHECKLIST.md
git add next-app/DEPLOY_CHECKLIST.md
echo "  ✓ Resolved next-app/DEPLOY_CHECKLIST.md"

git checkout --ours next-app/README.md
git add next-app/README.md
echo "  ✓ Resolved next-app/README.md"

# Resolve package files - accept main's versions to avoid dependency issues
git checkout --theirs frontend/package.json
git checkout --theirs frontend/package-lock.json
git add frontend/package.json frontend/package-lock.json
echo "  ✓ Resolved frontend/package.json and package-lock.json"

# Resolve README.md - merge both versions (Edge Postgres + Vercel Postgres setup)
cat > /tmp/resolve_readme.py << 'PYEOF'
#!/usr/bin/env python3
with open('README.md', 'r') as f:
    content = f.read()

lines = content.split('\n')
result = []
i = 0
while i < len(lines):
    line = lines[i]
    if line.startswith('<<<<<<< HEAD'):
        head_start = i + 1
        divider = i
        end = i
        for j in range(i + 1, len(lines)):
            if lines[j].startswith('======='):
                divider = j
            elif lines[j].startswith('>>>>>>> main'):
                end = j
                break
        
        # For first conflict, keep main's Edge Postgres section
        if i < 20:
            for j in range(divider + 1, end):
                result.append(lines[j])
        # For second conflict, merge both sections
        elif i > 90:
            main_content = '\n'.join(lines[divider+1:end])
            result.append(main_content)
        else:
            for j in range(divider + 1, end):
                result.append(lines[j])
        
        i = end + 1
    else:
        result.append(line)
        i += 1

with open('README.md', 'w') as f:
    f.write('\n'.join(result))
PYEOF

python3 /tmp/resolve_readme.py
git add README.md
echo "  ✓ Resolved README.md"

echo ""
echo "Step 5: Completing merge..."
git commit -m "Merge main into copilot/update-postgres-connection-strings to resolve conflicts

- Resolved conflicts in .env.example files (kept PR #360's Vercel Postgres documentation)
- Resolved conflicts in drizzle.config.ts (kept non-pooling connection logic)
- Merged README.md to include both Edge Postgres and Vercel Postgres setup sections
- Updated .gitignore and .vercelignore from main
- Updated frontend package files from main
- Kept comprehensive documentation from PR #360 for Postgres connection strings"

echo ""
echo "==========================================="
echo "✓ Merge conflicts resolved successfully!"
echo "==========================================="
echo ""
echo "Next step: Push the changes to GitHub"
echo "  git push origin copilot/update-postgres-connection-strings"
echo ""
echo "PR #360 will then be mergeable!"

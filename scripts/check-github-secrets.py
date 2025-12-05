#!/usr/bin/env python3
"""
GitHub Actions Secrets Checker
Helps verify that required secrets are configured for automated Vercel deployment
"""
import sys
import os
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def print_section(text):
    """Print a section header."""
    print(f"\n🔍 {text}")

def main():
    """Check GitHub Actions setup for Vercel deployment."""
    print_header("🔐 GitHub Actions Secrets Verification Guide")
    
    print("\nThis script helps you verify that GitHub secrets are configured")
    print("for automated Vercel deployment via GitHub Actions.")
    
    print_section("Required GitHub Secrets")
    
    required_secrets = {
        "VERCEL_TOKEN": {
            "description": "Vercel authentication token",
            "how_to_get": [
                "1. Go to https://vercel.com/account/tokens",
                "2. Click 'Create' to generate a new token",
                "3. Give it a name (e.g., 'GitHub Actions')",
                "4. Copy the generated token"
            ],
            "scope": "Required to deploy to Vercel via API"
        },
        "VERCEL_ORG_ID": {
            "description": "Your Vercel organization/team ID",
            "how_to_get": [
                "1. Go to https://vercel.com/account or https://vercel.com/teams/[team-name]/settings",
                "2. Scroll to 'General' section",
                "3. Find 'Team ID' or 'Organization ID'",
                "4. Copy the ID (starts with 'team_' or similar)"
            ],
            "scope": "Identifies which Vercel account to deploy to"
        },
        "VERCEL_PROJECT_ID": {
            "description": "Your Vercel project ID",
            "how_to_get": [
                "1. Go to https://vercel.com/dashboard",
                "2. Click on your project",
                "3. Go to Settings > General",
                "4. Find 'Project ID' in the General section",
                "5. Copy the Project ID"
            ],
            "scope": "Identifies which Vercel project to deploy to"
        }
    }
    
    for secret_name, details in required_secrets.items():
        print(f"\n📌 {secret_name}")
        print(f"   Description: {details['description']}")
        print(f"   Scope: {details['scope']}")
        print(f"   How to get:")
        for step in details['how_to_get']:
            print(f"      {step}")
    
    print_section("How to Add Secrets to GitHub")
    
    print("""
1. Go to your GitHub repository
2. Click on 'Settings' tab
3. In the left sidebar, click 'Secrets and variables' > 'Actions'
4. Click 'New repository secret' for each required secret
5. Enter the name (e.g., VERCEL_TOKEN) and value
6. Click 'Add secret'

Repeat for all three required secrets:
   • VERCEL_TOKEN
   • VERCEL_ORG_ID
   • VERCEL_PROJECT_ID
""")
    
    print_section("Verifying Secrets Are Set")
    
    print("""
After adding secrets, you can verify they're configured:

1. Go to your repository's Actions tab
2. Click on a workflow run
3. In the workflow file, secrets show as ***
4. If a secret is missing, the workflow will fail with an error message

You CANNOT view secret values after they're set (for security).
If you need to update a secret, you must overwrite it with a new value.
""")
    
    print_section("Vercel Environment Variables")
    
    print("""
In addition to GitHub secrets, you also need to configure environment
variables in Vercel Dashboard for your application to work:

Required Vercel Environment Variables:
   • DATABASE_URL - PostgreSQL connection string
   • SECRET_KEY - Flask secret key (min 32 characters)
   • JWT_SECRET_KEY - JWT signing key (min 32 characters)
   • ENVIRONMENT - Set to 'production'

How to add them:
1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to Settings > Environment Variables
4. Add each variable with its value
5. Select 'Production', 'Preview', and 'Development' environments
6. Click 'Save'
""")
    
    print_section("Testing the Setup")
    
    print("""
Once secrets and environment variables are configured:

1. Make a small change to your repository
2. Commit and push to main branch:
   
   git add .
   git commit -m "Test deployment"
   git push origin main

3. Go to GitHub Actions tab
4. Watch the 'Deploy to Vercel' workflow run
5. If successful, check your deployment in Vercel Dashboard

If the workflow fails:
   • Check the error message in GitHub Actions logs
   • Verify all three secrets are set correctly
   • Ensure Vercel environment variables are configured
   • Review the deployment guide: VERCEL_DEPLOYMENT_404_FIX.md
""")
    
    print_section("Common Issues")
    
    print("""
❌ Error: "VERCEL_TOKEN secret is not set"
   → Add VERCEL_TOKEN secret to GitHub repository

❌ Error: "VERCEL_ORG_ID secret is not set"
   → Add VERCEL_ORG_ID secret to GitHub repository

❌ Error: "VERCEL_PROJECT_ID secret is not set"
   → Add VERCEL_PROJECT_ID secret to GitHub repository

❌ Error: "Build failed" in Vercel
   → Check Vercel environment variables are set
   → Review Vercel build logs for specific error

❌ 404: DEPLOYMENT_NOT_FOUND
   → See TROUBLESHOOTING_DEPLOYMENT_NOT_FOUND.md
   → Run: python3 scripts/verify-vercel-deployment.py
""")
    
    print_section("Quick Reference")
    
    print("""
GitHub Secrets (Repository > Settings > Secrets):
   ├── VERCEL_TOKEN         (from vercel.com/account/tokens)
   ├── VERCEL_ORG_ID        (from vercel.com/account or team settings)
   └── VERCEL_PROJECT_ID    (from project settings)

Vercel Env Variables (Project > Settings > Environment Variables):
   ├── DATABASE_URL         (PostgreSQL connection string)
   ├── SECRET_KEY           (32+ character random string)
   ├── JWT_SECRET_KEY       (32+ character random string)
   └── ENVIRONMENT          ('production')

Workflow File:
   .github/workflows/deploy-vercel.yml

Documentation:
   • VERCEL_DEPLOYMENT_404_FIX.md
   • FIX_SIGN_IN_DEPLOYMENT_GUIDE.md
   • TROUBLESHOOTING_DEPLOYMENT_NOT_FOUND.md
""")
    
    print_header("✅ Setup Checklist")
    
    checklist = [
        "[ ] Generated VERCEL_TOKEN from vercel.com/account/tokens",
        "[ ] Found VERCEL_ORG_ID in Vercel account/team settings",
        "[ ] Found VERCEL_PROJECT_ID in Vercel project settings",
        "[ ] Added all 3 secrets to GitHub repository",
        "[ ] Configured DATABASE_URL in Vercel environment variables",
        "[ ] Configured SECRET_KEY in Vercel environment variables",
        "[ ] Configured JWT_SECRET_KEY in Vercel environment variables",
        "[ ] Configured ENVIRONMENT=production in Vercel",
        "[ ] Pushed to main branch to trigger deployment",
        "[ ] Verified deployment succeeded in GitHub Actions",
        "[ ] Checked deployment status in Vercel Dashboard",
    ]
    
    for item in checklist:
        print(item)
    
    print("\n" + "=" * 60)
    print("📚 For more help, see:")
    print("   • FIX_SIGN_IN_DEPLOYMENT_GUIDE.md")
    print("   • DEPLOYMENT_CONNECTION_GUIDE.md")
    print("=" * 60 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

# Render Deployment Setup

This repository includes automated deployment to Render via GitHub Actions.

## How It Works

The deployment workflow (`.github/workflows/deploy.yml`) automatically triggers a deployment to Render when code is merged to the `main` branch.

## Setup Instructions

### 1. Get Your Render Deploy Hook

1. Log in to your [Render Dashboard](https://dashboard.render.com/)
2. Select your service (web service, backend, etc.)
3. Navigate to **Settings** → **Deploy Hook**
4. Copy the Deploy Hook URL (it looks like: `https://api.render.com/deploy/srv-xxx?key=xxx`)

### 2. Add Deploy Hook to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Set the following:
   - **Name**: `RENDER_DEPLOY_HOOK`
   - **Secret**: Paste your Render Deploy Hook URL
5. Click **Add secret**

### 3. Verify Setup

Once the secret is configured:

1. Merge a PR to `main` branch
2. The deployment workflow will automatically trigger
3. Check the **Actions** tab to see the deployment progress
4. Your Render service will be updated automatically

## Manual Deployment

You can also trigger a deployment manually:

1. Go to **Actions** tab in GitHub
2. Select **Deploy to Render** workflow
3. Click **Run workflow**
4. Select the `main` branch
5. Click **Run workflow**

## Troubleshooting

### Deployment Fails with "RENDER_DEPLOY_HOOK secret not set"

**Solution**: Follow the setup instructions above to add the secret.

### Deployment Triggered but Render Doesn't Update

**Possible causes**:
- Wrong Deploy Hook URL - verify it's copied correctly from Render
- Deploy Hook expired - regenerate it in Render settings
- Render service is in a failed state - check Render dashboard

### How to Disable Auto-Deployment

If you want to deploy manually only:

1. Delete or rename `.github/workflows/deploy.yml`
2. Or modify the workflow to remove the `push:` trigger, keeping only `workflow_dispatch:`

## Additional Notes

- The deployment workflow only runs on `main` branch
- It uses Render's webhook to trigger deployments
- Deployment time depends on your Render service configuration
- Check Render dashboard for detailed deployment logs

# 🚀 Auto-Deploy Setup Guide for HireMeBahamas

This guide explains how to enable automatic deployment to Vercel (frontend) and Render (backend) using GitHub Actions.

## 📋 Prerequisites

Before setting up auto-deploy, ensure you have:
- A GitHub account with this repository
- A Vercel account (for frontend deployment)
- A Render account (for backend deployment)

## 🔧 Setup Instructions

### 1. Vercel Setup (Frontend)

#### Step 1.1: Create Vercel Project
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New Project"**
3. Import your GitHub repository `cliffcho242/HireMeBahamas`
4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add environment variable:
   - **Name**: `VITE_API_URL`
   - **Value**: Your Render backend URL (e.g., `https://your-backend.render.app`)
6. Click **"Deploy"**

#### Step 1.2: Get Vercel Credentials
1. Go to [Vercel Tokens](https://vercel.com/account/tokens)
2. Create a new token named **"GitHub Actions Auto-Deploy"**
3. Copy the token (you'll need it for GitHub Secrets)

4. Get your Vercel Organization ID and Project ID:
   ```bash
   # Install Vercel CLI if not already installed
   npm i -g vercel

   # Login and link to your project
   cd frontend
   vercel link

   # Get your IDs from .vercel/project.json
   cat .vercel/project.json
   ```

### 2. Render Setup (Backend)

#### Step 2.1: Create Render Project
1. Go to [Render Dashboard](https://render.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository `cliffcho242/HireMeBahamas`
5. Render will auto-detect the Python app
6. Set environment variables:
   - `SECRET_KEY`: Generate a secure random key
   - `DATABASE_URL`: (Render provides PostgreSQL automatically if needed)
   
   📖 **[Complete DATABASE_URL Setup Guide](./RAILWAY_DATABASE_SETUP.md)** - Step-by-step instructions for adding PostgreSQL
   
7. Deploy and note your Render URL

#### Step 2.2: Get Render Token
1. Go to [Render Account Settings](https://render.app/account)
2. Navigate to **"Tokens"** section
3. Create a new token named **"GitHub Actions Auto-Deploy"**
4. Copy the token

#### Step 2.3: Get Render Project ID
```bash
# Install Render CLI
curl -fsSL https://render.app/install.sh | sh

# Login
render login

# Link to your project
render link

# Get project ID (it will be displayed)
render status
```

### 3. GitHub Secrets Configuration

Add the following secrets to your GitHub repository:

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** and add each of the following:

#### Vercel Secrets:
- **Name**: `VERCEL_TOKEN`
  - **Value**: Your Vercel token from Step 1.2
- **Name**: `VERCEL_ORG_ID`
  - **Value**: Your Vercel organization ID
- **Name**: `VERCEL_PROJECT_ID`
  - **Value**: Your Vercel project ID

#### Render Secrets:
- **Name**: `RAILWAY_TOKEN`
  - **Value**: Your Render token from Step 2.2
- **Name**: `RAILWAY_PROJECT_ID`
  - **Value**: Your Render project ID from Step 2.3

#### Optional Secrets:
- **Name**: `VITE_API_URL`
  - **Value**: Your Render backend URL (e.g., `https://your-backend.render.app`)

#### JFrog Secrets (for Frogbot security scanning - Optional):
If you want to enable automated security scanning with Frogbot:
- **Name**: `JF_URL`
  - **Value**: Your JFrog platform URL (e.g., `https://mycompany.jfrog.io/`)
- **Name**: `JF_ACCESS_TOKEN`
  - **Value**: Your JFrog access token with 'read' permissions on Xray service

**Note**: If you don't have JFrog credentials, the Frogbot workflow will fail but won't affect other workflows. You can disable it by removing or commenting out the workflow file, or use alternative security scanning tools like GitHub's Dependabot or CodeQL.

## 🎯 How Auto-Deploy Works

### Frontend Deployment (Vercel)
The workflow `.github/workflows/deploy-frontend.yml` triggers when:
- You push changes to the `main` branch
- Changes are made in the `frontend/` directory
- You manually trigger the workflow

### Backend Deployment (Render)
The workflow `.github/workflows/deploy-backend.yml` triggers when:
- You push changes to the `main` branch
- Changes are made in backend files
- You manually trigger the workflow

### Continuous Integration (CI)
The workflow `.github/workflows/ci.yml` runs on:
- Every pull request to `main`
- Every push to `main`
- Checks: Linting and building frontend, testing backend

### Security Scanning (Frogbot)
The workflow `.github/workflows/frogbot-scan-and-fix.yml` runs on:
- Every push to `main`
- Automatically scans dependencies for security vulnerabilities
- Requires JFrog platform credentials (JF_URL and JF_ACCESS_TOKEN)
- If you don't have JFrog credentials, you can disable this workflow or use alternative security scanning tools
- The workflow automatically installs all required system dependencies before scanning

## 🔄 Triggering Deployments

### Automatic Deployment
Simply push your changes to the `main` branch:
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

The GitHub Actions workflows will automatically:
1. Run CI checks (lint, build, test)
2. Deploy frontend to Vercel (if frontend files changed)
3. Deploy backend to Render (if backend files changed)

### Manual Deployment
You can also trigger deployments manually:
1. Go to your GitHub repository
2. Click **Actions** tab
3. Select the workflow you want to run:
   - **Deploy Frontend to Vercel**
   - **Deploy Backend to Render**
4. Click **"Run workflow"** → **"Run workflow"**

## 📊 Monitoring Deployments

### View GitHub Actions Status
1. Go to your repository on GitHub
2. Click the **Actions** tab
3. View running, completed, or failed workflows

### View Vercel Deployments
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your HireMeBahamas project
3. View deployment history and logs

### View Render Deployments
1. Go to [Render Dashboard](https://render.app/dashboard)
2. Select your HireMeBahamas project
3. View deployment status and logs

## 🐛 Troubleshooting

### Common Issues

#### "Invalid Vercel Token"
- Regenerate your Vercel token
- Update the `VERCEL_TOKEN` secret in GitHub

#### "Render deployment failed"
- Check Render token is valid
- Ensure `RAILWAY_PROJECT_ID` is correct
- Review Render logs for specific errors

#### "Build failed"
- Check the Actions logs for specific error messages
- Ensure all dependencies are listed in `package.json` or `requirements.txt`
- Verify environment variables are set correctly

#### "Frontend can't connect to backend"
- Ensure `VITE_API_URL` is set correctly in Vercel
- Check Render backend is running and accessible
- Verify CORS is enabled in backend

### Getting Help
- Check workflow logs in GitHub Actions tab
- Review Vercel deployment logs
- Review Render deployment logs
- Check the main README.md for general troubleshooting

## 🎉 Success!

Once configured, your deployments are fully automated! Every push to `main` will:
- ✅ Run automated tests
- ✅ Build your application
- ✅ Deploy to production
- ✅ Notify you of success or failure

## 📝 Alternative: Using Render.com Instead of Render

If you prefer Render.com for backend deployment:

1. The `render.yaml` file is already configured in the repository
2. Go to [Render Dashboard](https://render.com/dashboard)
3. Click **"New +"** → **"Blueprint"**
4. Connect your GitHub repository
5. Render will auto-deploy using `render.yaml` configuration
6. For GitHub Actions integration, use Render's Deploy Hooks:
   - Get your Render Deploy Hook URL from project settings
   - Add it as `RENDER_DEPLOY_HOOK` secret in GitHub
   - Create a simple workflow that calls the webhook

Example workflow for Render:
```yaml
name: Deploy Backend to Render

on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'
      - 'requirements.txt'
      - 'final_backend.py'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Render Deployment
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Vercel Deployment Documentation](https://vercel.com/docs)
- [Render Deployment Documentation](https://docs.render.app/)
- [Render Deployment Documentation](https://render.com/docs)

---

**Built with ❤️ for the Bahamas professional community**

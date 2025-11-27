# SonarCloud Setup Guide

This guide explains how to set up SonarCloud code quality analysis for the HireMeBahamas project.

## What is SonarCloud?

SonarCloud is a cloud-based code quality and security service that automatically analyzes your code for:
- Bugs and code smells
- Security vulnerabilities
- Code coverage
- Code duplication
- Best practices compliance

## Automated Configuration

The project is now pre-configured with SonarCloud integration:

### Configuration Files

1. **sonar-project.properties** - Main configuration file with project settings
2. **.github/workflows/sonarcloud.yml** - GitHub Actions workflow for automated analysis
3. **scripts/setup_sonarcloud.sh** - Setup script to help configure tokens

### Project Settings

- **Project Key**: `cliffcho242_HireMeBahamas`
- **Organization**: `cliffcho242`
- **Project Name**: HireMeBahamas

## Setup Instructions

### Step 1: Create SonarCloud Account

1. Go to [https://sonarcloud.io](https://sonarcloud.io)
2. Click "Log in" and choose "Log in with GitHub"
3. Authorize SonarCloud to access your GitHub account

### Step 2: Import the Project

1. In SonarCloud, click the **+** button in the top right
2. Select "Analyze new project"
3. Choose your GitHub organization: `cliffcho242`
4. Select the `HireMeBahamas` repository
5. Click "Set Up"

### Step 3: Generate a Token

1. Go to [https://sonarcloud.io/account/security/](https://sonarcloud.io/account/security/)
2. Enter a token name (e.g., "HireMeBahamas GitHub Actions")
3. Click "Generate"
4. **Copy the token** (you won't be able to see it again!)

### Step 4: Add Token to GitHub Secrets

1. Go to your GitHub repository settings:
   [https://github.com/cliffcho242/HireMeBahamas/settings/secrets/actions](https://github.com/cliffcho242/HireMeBahamas/settings/secrets/actions)
2. Click "New repository secret"
3. Name: `SONAR_TOKEN`
4. Value: [paste your token]
5. Click "Add secret"

### Step 5: Run the Setup Script (Optional for Local Testing)

If you want to run SonarCloud analysis locally:

```bash
# Run the setup script
./scripts/setup_sonarcloud.sh

# The script will guide you through setting up SONAR_TOKEN in your .env file
```

### Step 6: Trigger Analysis

The SonarCloud analysis will automatically run on:
- Every push to the `main` branch
- Every pull request to the `main` branch
- Manual workflow dispatch

To manually trigger:
1. Go to Actions tab in GitHub
2. Select "SonarCloud analysis" workflow
3. Click "Run workflow"

## Viewing Results

Once the analysis completes, you can view the results at:

**Project Dashboard**: [https://sonarcloud.io/project/overview?id=cliffcho242_HireMeBahamas](https://sonarcloud.io/project/overview?id=cliffcho242_HireMeBahamas)

The dashboard shows:
- Overall code quality rating
- Number of bugs
- Vulnerabilities
- Code smells
- Security hotspots
- Code coverage (if configured)
- Code duplication percentage

## Local Analysis (Optional)

To run SonarCloud analysis on your local machine:

### Prerequisites

1. Install SonarScanner CLI:
   - **macOS**: `brew install sonar-scanner`
   - **Linux**: Download from [https://docs.sonarcloud.io/advanced-setup/ci-based-analysis/sonarscanner-cli/](https://docs.sonarcloud.io/advanced-setup/ci-based-analysis/sonarscanner-cli/)
   - **Windows**: Download and add to PATH

2. Set SONAR_TOKEN in your `.env` file (use the setup script or add manually)

### Run Analysis

```bash
# From project root directory
sonar-scanner -Dsonar.login=$SONAR_TOKEN
```

The analysis will use settings from `sonar-project.properties`.

## Customizing Analysis

You can customize the SonarCloud analysis by editing `sonar-project.properties`:

### Common Customizations

```properties
# Exclude additional files/directories
sonar.exclusions=**/node_modules/**,**/dist/**,**/custom-folder/**

# Add test directories
sonar.tests=backend/tests,frontend/src/__tests__,custom-tests/

# Configure coverage reports
sonar.python.coverage.reportPaths=backend/coverage.xml
sonar.javascript.lcov.reportPaths=frontend/coverage/lcov.info

# Set Python version
sonar.python.version=3.9,3.10,3.11
```

After making changes, commit and push to trigger a new analysis.

## Troubleshooting

### Analysis Not Running

- Check that SONAR_TOKEN is correctly set in GitHub repository secrets
- Verify the workflow file exists: `.github/workflows/sonarcloud.yml`
- Check GitHub Actions tab for error messages

### Authentication Errors

- Ensure your SONAR_TOKEN is valid (tokens can expire)
- Regenerate the token in SonarCloud if needed
- Update the GitHub secret with the new token

### Project Not Found / "Could not find a default branch" Error

This error occurs when the project hasn't been imported into SonarCloud yet. The workflow will gracefully skip analysis and show setup instructions when this happens.

**To fix:**

1. Go to [https://sonarcloud.io](https://sonarcloud.io) and log in with GitHub
2. Click the **+** button in the top right corner
3. Select "Analyze new project"
4. Choose your GitHub organization: `cliffcho242`
5. Select the `HireMeBahamas` repository
6. Click "Set Up"
7. Once the project is created, re-run the SonarCloud workflow

**Additional checks:**

- Verify the project key in `sonar-project.properties` matches your SonarCloud project
- Check that the project is imported in SonarCloud
- Ensure the organization name is correct

### Analysis Fails with "No source files"

- Check that `sonar.sources` in `sonar-project.properties` points to correct directories
- Ensure the directories exist in the repository
- Verify file patterns in `sonar.exclusions` are not excluding everything

## Additional Resources

- **SonarCloud Documentation**: [https://docs.sonarcloud.io](https://docs.sonarcloud.io)
- **SonarCloud Community**: [https://community.sonarsource.com](https://community.sonarsource.com)
- **GitHub Actions for SonarCloud**: [https://github.com/SonarSource/sonarcloud-github-action](https://github.com/SonarSource/sonarcloud-github-action)

## Environment Variables

The following environment variables are used for SonarCloud:

| Variable | Required | Description | Where to Set |
|----------|----------|-------------|--------------|
| `SONAR_TOKEN` | Yes | Authentication token for SonarCloud API | GitHub Secrets (for CI/CD) or `.env` (for local) |
| `GITHUB_TOKEN` | Auto | GitHub authentication (automatically provided by GitHub Actions) | Automatic in workflows |

## Integration with CI/CD

The project is already configured for automated analysis:

1. **On Push to Main**: Full analysis of the main branch
2. **On Pull Request**: Analysis of changed code with PR decoration
3. **Manual Trigger**: Can be triggered via GitHub Actions UI

All configuration is handled automatically via:
- `sonar-project.properties` for project settings
- `.github/workflows/sonarcloud.yml` for workflow automation
- GitHub Secrets for secure token storage

No additional configuration is needed once the SONAR_TOKEN secret is set!

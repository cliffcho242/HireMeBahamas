#!/bin/bash

# SonarCloud Setup Script for HireMeBahamas
# This script helps configure SonarCloud integration

set -e

echo "🔧 SonarCloud Setup for HireMeBahamas"
echo "======================================"
echo ""

# Check if sonar-project.properties exists
if [ ! -f "sonar-project.properties" ]; then
    echo "❌ Error: sonar-project.properties not found!"
    echo "Please ensure you're running this script from the project root directory."
    exit 1
fi

echo "✅ Found sonar-project.properties"
echo ""

# Display project configuration
echo "📋 Project Configuration:"
echo "  Project Key: cliffcho242_HireMeBahamas"
echo "  Organization: cliffcho242"
echo ""

# Check if SONAR_TOKEN is set in environment
if [ -z "$SONAR_TOKEN" ]; then
    echo "⚠️  SONAR_TOKEN not found in environment variables"
    echo ""
    echo "To set up SonarCloud analysis, you need to:"
    echo ""
    echo "1. Go to https://sonarcloud.io and sign in with your GitHub account"
    echo "2. Import the HireMeBahamas project"
    echo "3. Generate a token at: https://sonarcloud.io/account/security/"
    echo "4. Add the token as a GitHub repository secret:"
    echo "   - Go to: https://github.com/cliffcho242/HireMeBahamas/settings/secrets/actions"
    echo "   - Click 'New repository secret'"
    echo "   - Name: SONAR_TOKEN"
    echo "   - Value: [your token]"
    echo ""
    echo "5. (Optional) For local analysis, set SONAR_TOKEN in your .env file"
    echo ""
    
    read -p "Do you want to add SONAR_TOKEN to .env for local testing? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your SonarCloud token: " token
        if [ -f ".env" ]; then
            if grep -q "SONAR_TOKEN=" .env; then
                echo "⚠️  SONAR_TOKEN already exists in .env file"
                read -p "Do you want to update it? (y/n) " -n 1 -r
                echo ""
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    # Update existing token (cross-platform compatible)
                    if sed --version >/dev/null 2>&1; then
                        # GNU sed (Linux)
                        sed -i "s|SONAR_TOKEN=.*|SONAR_TOKEN=$token|" .env
                    else
                        # BSD sed (macOS)
                        sed -i '' "s|SONAR_TOKEN=.*|SONAR_TOKEN=$token|" .env
                    fi
                    echo "✅ Updated SONAR_TOKEN in .env"
                fi
            else
                # Add new token
                echo "" >> .env
                echo "# SonarCloud Token (for local code quality analysis)" >> .env
                echo "SONAR_TOKEN=$token" >> .env
                echo "✅ Added SONAR_TOKEN to .env"
            fi
        else
            echo "⚠️  .env file not found. Creating from .env.example..."
            if [ -f ".env.example" ]; then
                cp .env.example .env
                echo "" >> .env
                echo "# SonarCloud Token (for local code quality analysis)" >> .env
                echo "SONAR_TOKEN=$token" >> .env
                echo "✅ Created .env and added SONAR_TOKEN"
            else
                echo "❌ .env.example not found. Please create .env manually and add:"
                echo "   SONAR_TOKEN=$token"
            fi
        fi
    fi
else
    echo "✅ SONAR_TOKEN is set in environment"
fi

echo ""
echo "📚 Next Steps:"
echo ""
echo "1. Ensure SONAR_TOKEN is added as a GitHub repository secret"
echo "2. Push changes to trigger the SonarCloud workflow"
echo "3. View analysis results at: https://sonarcloud.io/project/overview?id=cliffcho242_HireMeBahamas"
echo ""
echo "For local analysis (optional):"
echo "  - Install sonar-scanner: https://docs.sonarcloud.io/advanced-setup/ci-based-analysis/sonarscanner-cli/"
echo "  - Run: sonar-scanner -Dsonar.login=\$SONAR_TOKEN"
echo ""
echo "✅ Setup complete!"

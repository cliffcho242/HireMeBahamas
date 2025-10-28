#!/usr/bin/env python3
"""
Automated Deployment Preparation Script for HireMeBahamas
Prepares all configuration files and checks for production deployment
"""

import json
import os
import secrets
import subprocess
import sys
from pathlib import Path


class DeploymentPreparation:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.frontend_dir = self.root_dir / "frontend"
        self.errors = []
        self.warnings = []
        self.success = []

    def print_section(self, title):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")

    def print_success(self, message):
        """Print success message"""
        print(f"✅ {message}")
        self.success.append(message)

    def print_warning(self, message):
        """Print warning message"""
        print(f"⚠️  {message}")
        self.warnings.append(message)

    def print_error(self, message):
        """Print error message"""
        print(f"❌ {message}")
        self.errors.append(message)

    def generate_secret_key(self):
        """Generate a secure secret key for production"""
        return secrets.token_urlsafe(32)

    def create_env_file(self):
        """Create .env file for production"""
        self.print_section("Creating Environment Configuration")

        env_content = f"""# HireMeBahamas Production Environment Variables
# Generated on {subprocess.check_output(['date'], shell=True).decode().strip()}

# Backend Configuration
SECRET_KEY={self.generate_secret_key()}
FLASK_ENV=production
DATABASE_URL=sqlite:///hiremebahamas.db
PORT=9999

# Security Settings
JWT_EXPIRATION_DAYS=7
BCRYPT_LOG_ROUNDS=12

# CORS Origins (update with your production domain)
ALLOWED_ORIGINS=https://hiremebahamas.vercel.app,https://hiremebahamas.com,https://www.hiremebahamas.com

# File Upload Settings
MAX_UPLOAD_SIZE=5242880
UPLOAD_FOLDER=uploads

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# Email Configuration (add your SMTP settings)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Monitoring (optional)
SENTRY_DSN=
GOOGLE_ANALYTICS_ID=
"""

        env_path = self.root_dir / ".env"
        with open(env_path, "w") as f:
            f.write(env_content)

        self.print_success(f"Created .env file at {env_path}")
        self.print_warning("Remember to update SMTP settings and ALLOWED_ORIGINS!")

    def create_railway_config(self):
        """Create Railway deployment configuration"""
        self.print_section("Creating Railway Configuration")

        railway_json = {
            "$schema": "https://railway.app/railway.schema.json",
            "build": {
                "builder": "NIXPACKS",
                "buildCommand": "pip install -r requirements.txt",
            },
            "deploy": {
                "startCommand": "gunicorn -w 4 -b 0.0.0.0:$PORT final_backend:app --timeout 120",
                "restartPolicyType": "ON_FAILURE",
                "restartPolicyMaxRetries": 10,
            },
        }

        railway_path = self.root_dir / "railway.json"
        with open(railway_path, "w") as f:
            json.dump(railway_json, f, indent=2)

        self.print_success(f"Created railway.json at {railway_path}")

    def create_vercel_config(self):
        """Create Vercel deployment configuration"""
        self.print_section("Creating Vercel Configuration")

        vercel_json = {
            "buildCommand": "cd frontend && npm install && npm run build",
            "outputDirectory": "frontend/dist",
            "framework": "vite",
            "installCommand": "cd frontend && npm install",
            "devCommand": "cd frontend && npm run dev",
            "env": {"VITE_API_URL": "https://hiremebahamas-backend.railway.app"},
        }

        vercel_path = self.root_dir / "vercel.json"
        with open(vercel_path, "w") as f:
            json.dump(vercel_json, f, indent=2)

        self.print_success(f"Created vercel.json at {vercel_path}")

    def create_nixpacks_config(self):
        """Create Nixpacks configuration for Railway"""
        self.print_section("Creating Nixpacks Configuration")

        nixpacks_toml = """[phases.setup]
nixPkgs = ["python39", "gcc"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["python -c 'import final_backend; print(\"Backend OK\")'"]

[start]
cmd = "gunicorn -w 4 -b 0.0.0.0:$PORT final_backend:app --timeout 120"
"""

        nixpacks_path = self.root_dir / "nixpacks.toml"
        with open(nixpacks_path, "w") as f:
            f.write(nixpacks_toml)

        self.print_success(f"Created nixpacks.toml at {nixpacks_path}")

    def create_requirements_txt(self):
        """Create or update requirements.txt"""
        self.print_section("Creating Requirements File")

        requirements = """Flask==2.3.3
Flask-CORS==4.0.0
Flask-Limiter==3.5.0
Flask-Caching==2.1.0
PyJWT==2.8.0
bcrypt==4.0.1
python-dotenv==1.0.0
gunicorn==21.2.0
waitress==2.1.2
Werkzeug==2.3.7
"""

        req_path = self.root_dir / "requirements.txt"
        with open(req_path, "w") as f:
            f.write(requirements)

        self.print_success(f"Created requirements.txt at {req_path}")

    def create_procfile(self):
        """Create Procfile for Heroku compatibility"""
        self.print_section("Creating Procfile")

        procfile_content = """web: gunicorn -w 4 -b 0.0.0.0:$PORT final_backend:app --timeout 120
"""

        procfile_path = self.root_dir / "Procfile"
        with open(procfile_path, "w") as f:
            f.write(procfile_content)

        self.print_success(f"Created Procfile at {procfile_path}")

    def create_gitignore(self):
        """Create or update .gitignore"""
        self.print_section("Creating .gitignore")

        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/

# Environment variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite
*.sqlite3
hiremebahamas.db

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Frontend
frontend/node_modules/
frontend/dist/
frontend/build/
frontend/.vite/

# Uploads
uploads/
static/uploads/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Deployment
*.pem
*.key
.vercel
.railway
"""

        gitignore_path = self.root_dir / ".gitignore"
        with open(gitignore_path, "w") as f:
            f.write(gitignore_content)

        self.print_success(f"Created .gitignore at {gitignore_path}")

    def update_frontend_env(self):
        """Create frontend .env for production"""
        self.print_section("Creating Frontend Environment")

        if not self.frontend_dir.exists():
            self.print_warning("Frontend directory not found, skipping frontend config")
            return

        frontend_env = """# Frontend Production Environment
VITE_API_URL=https://hiremebahamas-backend.railway.app
VITE_SOCKET_URL=https://hiremebahamas-backend.railway.app
VITE_APP_NAME=HireMeBahamas
VITE_APP_VERSION=1.0.0
"""

        frontend_env_path = self.frontend_dir / ".env.production"
        with open(frontend_env_path, "w") as f:
            f.write(frontend_env)

        self.print_success(f"Created frontend .env.production")
        self.print_warning("Update VITE_API_URL with your actual Railway backend URL!")

    def create_privacy_policy(self):
        """Create privacy policy page"""
        self.print_section("Creating Legal Pages")

        privacy_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - HireMeBahamas</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; line-height: 1.6; }
        h1 { color: #2563eb; }
        h2 { color: #1e40af; margin-top: 30px; }
        .updated { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <h1>Privacy Policy</h1>
    <p class="updated">Last Updated: October 19, 2025</p>
    
    <h2>1. Information We Collect</h2>
    <p>HireMeBahamas collects information you provide directly, including name, email, phone number, and professional information when you create an account.</p>
    
    <h2>2. How We Use Your Information</h2>
    <p>We use your information to provide job matching services, facilitate connections between job seekers and employers, and improve our platform.</p>
    
    <h2>3. Information Sharing</h2>
    <p>We do not sell your personal information. We share information only as necessary to provide our services or as required by law.</p>
    
    <h2>4. Data Security</h2>
    <p>We implement industry-standard security measures to protect your information, including encryption and secure data storage.</p>
    
    <h2>5. Your Rights</h2>
    <p>You have the right to access, update, or delete your personal information at any time through your account settings.</p>
    
    <h2>6. Contact Us</h2>
    <p>For privacy concerns, contact us at: privacy@hiremebahamas.com</p>
</body>
</html>
"""

        privacy_path = self.root_dir / "privacy-policy.html"
        with open(privacy_path, "w") as f:
            f.write(privacy_html)

        self.print_success("Created privacy-policy.html")

    def create_terms_of_service(self):
        """Create terms of service page"""
        terms_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service - HireMeBahamas</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; line-height: 1.6; }
        h1 { color: #2563eb; }
        h2 { color: #1e40af; margin-top: 30px; }
        .updated { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <h1>Terms of Service</h1>
    <p class="updated">Last Updated: October 19, 2025</p>
    
    <h2>1. Acceptance of Terms</h2>
    <p>By accessing HireMeBahamas, you agree to these Terms of Service and our Privacy Policy.</p>
    
    <h2>2. User Accounts</h2>
    <p>You are responsible for maintaining the security of your account and for all activities under your account.</p>
    
    <h2>3. Acceptable Use</h2>
    <p>You agree to use HireMeBahamas only for lawful purposes. Prohibited activities include posting false information, harassment, or spam.</p>
    
    <h2>4. Job Postings</h2>
    <p>Employers are responsible for the accuracy of job postings. We reserve the right to remove any posting that violates our policies.</p>
    
    <h2>5. Limitation of Liability</h2>
    <p>HireMeBahamas is not responsible for the accuracy of job listings or the actions of users.</p>
    
    <h2>6. Changes to Terms</h2>
    <p>We may update these terms at any time. Continued use of the platform constitutes acceptance of updated terms.</p>
    
    <h2>7. Contact</h2>
    <p>For questions about these terms, contact: support@hiremebahamas.com</p>
</body>
</html>
"""

        terms_path = self.root_dir / "terms-of-service.html"
        with open(terms_path, "w") as f:
            f.write(terms_html)

        self.print_success("Created terms-of-service.html")

    def create_deployment_script(self):
        """Create automated deployment script"""
        self.print_section("Creating Deployment Scripts")

        deploy_script = """#!/bin/bash
# Automated Deployment Script for HireMeBahamas

echo "=========================================="
echo "  HireMeBahamas Automated Deployment"
echo "=========================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - HireMeBahamas"
fi

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
git add .
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

echo ""
echo "✅ Code pushed to GitHub!"
echo ""
echo "Next steps:"
echo "1. Deploy backend to Railway: https://railway.app"
echo "2. Deploy frontend to Vercel: https://vercel.com"
echo "3. Update environment variables with production URLs"
echo ""
echo "=========================================="
"""

        deploy_path = self.root_dir / "deploy.sh"
        with open(deploy_path, "w", encoding="utf-8") as f:
            f.write(deploy_script)

        self.print_success("Created deploy.sh")

        # Windows version
        deploy_bat = """@echo off
REM Automated Deployment Script for HireMeBahamas

echo ==========================================
echo   HireMeBahamas Automated Deployment
echo ==========================================
echo.

REM Check if git is initialized
if not exist .git (
    echo Initializing git repository...
    git init
    git add .
    git commit -m "Initial commit - HireMeBahamas"
)

REM Push to GitHub
echo.
echo Pushing to GitHub...
git add .
git commit -m "Deploy: %date% %time%"
git push origin main

echo.
echo ✅ Code pushed to GitHub!
echo.
echo Next steps:
echo 1. Deploy backend to Railway: https://railway.app
echo 2. Deploy frontend to Vercel: https://vercel.com
echo 3. Update environment variables with production URLs
echo.
echo ==========================================
pause
"""

        deploy_bat_path = self.root_dir / "DEPLOY.bat"
        with open(deploy_bat_path, "w", encoding="utf-8") as f:
            f.write(deploy_bat)

        self.print_success("Created DEPLOY.bat")

    def check_dependencies(self):
        """Check if required tools are installed"""
        self.print_section("Checking Dependencies")

        # Check Git
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            self.print_success("Git is installed")
        except:
            self.print_error(
                "Git is not installed! Download from: https://git-scm.com/"
            )

        # Check Python
        try:
            version = sys.version.split()[0]
            self.print_success(f"Python {version} is installed")
        except:
            self.print_error("Python check failed")

        # Check Node (for frontend)
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                self.print_success(f"Node.js {result.stdout.strip()} is installed")
            else:
                self.print_warning("Node.js not found - needed for frontend deployment")
        except:
            self.print_warning("Node.js not found - needed for frontend deployment")

    def create_readme(self):
        """Create deployment README"""
        self.print_section("Creating Deployment README")

        readme = """# 🚀 HireMeBahamas - Deployment Ready!

## ✅ Configuration Files Created

All deployment configuration files have been automatically generated:

- ✅ `.env` - Production environment variables
- ✅ `railway.json` - Railway deployment config
- ✅ `vercel.json` - Vercel frontend config
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Heroku compatibility
- ✅ `.gitignore` - Git ignore rules
- ✅ `privacy-policy.html` - Privacy policy page
- ✅ `terms-of-service.html` - Terms of service page
- ✅ `DEPLOY.bat` - Automated deployment script

## 🎯 Quick Deployment (5 Minutes!)

### Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit - HireMeBahamas"

# Create repository on GitHub and push
git remote add origin https://github.com/yourusername/HireMeBahamas.git
git push -u origin main
```

Or simply run: `DEPLOY.bat`

### Step 2: Deploy Backend to Railway

1. Go to: https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your HireMeBahamas repository
4. Railway will auto-detect `railway.json` and deploy!
5. Add environment variable: `SECRET_KEY` (copy from `.env` file)
6. Copy your Railway URL (e.g., `https://hiremebahamas-backend.railway.app`)

### Step 3: Deploy Frontend to Vercel

1. Go to: https://vercel.com
2. Click "New Project" → Import from GitHub
3. Select your HireMeBahamas repository
4. Set Root Directory to: `frontend`
5. Add environment variable:
   - `VITE_API_URL` = Your Railway backend URL
6. Click "Deploy"!
7. Your site will be live at: `https://hiremebahamas.vercel.app`

### Step 4: Test Production Site

1. Visit your Vercel URL
2. Test user registration
3. Test login
4. Test job posting
5. Verify all features work!

## 📱 App Store Submission

Once your website is live and tested:

### Required for App Stores:
- ✅ Live website URL
- ✅ Privacy Policy URL: `https://your-domain.com/privacy-policy.html`
- ✅ Terms of Service URL: `https://your-domain.com/terms-of-service.html`
- ✅ Support Email: support@hiremebahamas.com

### Mobile App Development:
1. Create React Native apps (iOS + Android)
2. Connect to same backend API
3. Test thoroughly
4. Submit to Apple App Store (7-14 days review)
5. Submit to Google Play Store (1-3 days review)

## 🔒 Security Checklist

Before going live:
- [ ] Update `SECRET_KEY` in Railway environment variables
- [ ] Update `ALLOWED_ORIGINS` in `.env` to your production domain
- [ ] Enable HTTPS (automatic on Railway & Vercel)
- [ ] Test all authentication flows
- [ ] Set up error monitoring (Sentry)
- [ ] Configure backup strategy for database
- [ ] Set up domain name (optional but recommended)

## 📊 Monitoring

Add to your production deployment:
- **Uptime Monitoring**: UptimeRobot (free)
- **Error Tracking**: Sentry (free tier)
- **Analytics**: Google Analytics
- **Performance**: Vercel Analytics (built-in)

## 💰 Cost Breakdown

### Free Tier (Perfect for Launch):
- Railway Backend: FREE (500 hours/month)
- Vercel Frontend: FREE (unlimited)
- Total: $0/month

### Paid (When You Scale):
- Railway: $5/month
- Vercel Pro: $20/month
- Domain: $12/year
- Total: ~$25/month + domain

## 🆘 Troubleshooting

### Backend won't deploy on Railway?
- Check `railway.json` syntax
- Verify `requirements.txt` has all dependencies
- Check Railway logs for errors

### Frontend won't deploy on Vercel?
- Verify `frontend` directory structure
- Check `VITE_API_URL` environment variable
- Review Vercel deployment logs

### CORS errors in production?
- Update `ALLOWED_ORIGINS` in backend `.env`
- Redeploy backend after changes
- Clear browser cache and test again

## 📞 Support

- **Email**: support@hiremebahamas.com
- **Documentation**: This file
- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs

## 🎉 You're Ready!

Your HireMeBahamas platform is ready for deployment!

Run `DEPLOY.bat` to get started, or follow the manual steps above.

Good luck with your launch! 🚀🇧🇸
"""

        readme_path = self.root_dir / "DEPLOYMENT_READY.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme)

        self.print_success("Created DEPLOYMENT_READY.md")

    def print_summary(self):
        """Print final summary"""
        print("\n" + "=" * 60)
        print("  DEPLOYMENT PREPARATION COMPLETE!")
        print("=" * 60 + "\n")

        if self.success:
            print("✅ Successfully Created:")
            for item in self.success:
                print(f"   • {item}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for item in self.warnings:
                print(f"   • {item}")

        if self.errors:
            print("\n❌ Errors:")
            for item in self.errors:
                print(f"   • {item}")

        print("\n" + "=" * 60)
        print("  NEXT STEPS:")
        print("=" * 60)
        print("1. Review .env file and update settings")
        print("2. Run: DEPLOY.bat")
        print("3. Deploy backend to Railway: https://railway.app")
        print("4. Deploy frontend to Vercel: https://vercel.com")
        print("5. Test your live site!")
        print("\nRead DEPLOYMENT_READY.md for detailed instructions")
        print("=" * 60 + "\n")

    def run(self):
        """Run all preparation steps"""
        print("\n🚀 HireMeBahamas Deployment Automation")
        print("=" * 60 + "\n")

        try:
            self.check_dependencies()
            self.create_env_file()
            self.create_railway_config()
            self.create_vercel_config()
            self.create_nixpacks_config()
            self.create_requirements_txt()
            self.create_procfile()
            self.create_gitignore()
            self.update_frontend_env()
            self.create_privacy_policy()
            self.create_terms_of_service()
            self.create_deployment_script()
            self.create_readme()
            self.print_summary()

        except Exception as e:
            self.print_error(f"Unexpected error: {str(e)}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    prep = DeploymentPreparation()
    prep.run()

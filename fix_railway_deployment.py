#!/usr/bin/env python3
"""
Backend Deployment Fix
Fix the Railway deployment to serve the correct Flask backend
"""

import subprocess
import sys
from pathlib import Path


def check_railway_config():
    """Check Railway deployment configuration"""
    print("🔍 Checking Railway deployment configuration...")

    # Check Procfile
    procfile = Path("Procfile")
    if procfile.exists():
        with open(procfile, "r") as f:
            content = f.read().strip()
        print(f"✅ Procfile found: {content}")

        # Check if it points to the right backend
        if "final_backend:app" in content:
            print("✅ Procfile correctly points to final_backend:app")
        else:
            print("❌ Procfile may be pointing to wrong backend")

    else:
        print("❌ No Procfile found")

    # Check requirements.txt
    requirements = Path("requirements.txt")
    if requirements.exists():
        print("✅ requirements.txt found")
    else:
        print("❌ No requirements.txt found")

    # Check if final_backend.py exists
    backend_file = Path("final_backend.py")
    if backend_file.exists():
        print("✅ final_backend.py exists")

        # Check if it has the app variable
        with open(backend_file, "r", encoding="utf-8") as f:
            content = f.read()

        if "app = Flask" in content:
            print("✅ Flask app properly defined")
        else:
            print("❌ Flask app not found in final_backend.py")

    else:
        print("❌ final_backend.py not found")


def test_local_backend():
    """Test if the backend works locally"""
    print("\n🧪 Testing backend locally...")

    try:
        # Import and test the backend
        sys.path.append(".")
        import final_backend

        app = final_backend.app

        # Test app creation
        with app.test_client() as client:
            # Test health endpoint
            health_response = client.get("/health")
            print(f"✅ Health endpoint: {health_response.status_code}")

            # Test auth endpoints
            login_response = client.options("/api/auth/login")
            print(f"✅ Login OPTIONS: {login_response.status_code}")

            register_response = client.options("/api/auth/register")
            print(f"✅ Register OPTIONS: {register_response.status_code}")

            return True

    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False


def create_deployment_fix():
    """Create files to fix deployment"""
    print("\n🔧 Creating deployment fix files...")

    # Create or update Procfile
    procfile_content = (
        "web: gunicorn -w 4 -b 0.0.0.0:$PORT final_backend:app --timeout 120\n"
    )

    with open("Procfile", "w") as f:
        f.write(procfile_content)
    print("✅ Updated Procfile")

    # Create railway.json for Railway configuration
    railway_config = {
        "build": {"builder": "NIXPACKS"},
        "deploy": {
            "startCommand": "gunicorn -w 4 -b 0.0.0.0:$PORT final_backend:app --timeout 120"
        },
    }

    import json

    with open("railway.json", "w") as f:
        json.dump(railway_config, f, indent=2)
    print("✅ Created railway.json")

    # Create requirements.txt if it doesn't exist
    if not Path("requirements.txt").exists():
        requirements = """Flask==2.3.3
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.0.5
Flask-JWT-Extended==4.5.2
Werkzeug==2.3.7
gunicorn==21.2.0
psycopg2-binary==2.9.7
python-dotenv==1.0.0
Pillow==10.0.0
requests==2.31.0
"""
        with open("requirements.txt", "w") as f:
            f.write(requirements)
        print("✅ Created requirements.txt")

    # Create .env template
    env_template = """# Railway Environment Variables
PORT=5000
DATABASE_URL=postgresql://username:password@hostname:port/database
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# CORS Settings
FRONTEND_URL=https://hiremebahamas.vercel.app
"""

    with open(".env.example", "w") as f:
        f.write(env_template)
    print("✅ Created .env.example")


def create_railway_redeploy_script():
    """Create script to redeploy to Railway"""
    script_content = '''#!/usr/bin/env python3
"""
Railway Redeploy Script
"""

import subprocess
import sys

def run_command(cmd):
    """Run command and show output"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
        
    return result.returncode == 0

def main():
    print("🚀 Redeploying to Railway...")
    
    # Check if railway CLI is installed
    if not run_command("railway --version"):
        print("❌ Railway CLI not installed")
        print("Install with: npm install -g @railway/cli")
        return
    
    # Check if logged in
    if not run_command("railway whoami"):
        print("❌ Not logged into Railway")
        print("Login with: railway login")
        return
    
    # Deploy
    print("🚀 Starting deployment...")
    if run_command("railway up"):
        print("✅ Deployment successful!")
        print("🌐 Your backend should be available at:")
        print("https://hiremebahamas-backend.railway.app/health")
    else:
        print("❌ Deployment failed")

if __name__ == "__main__":
    main()
'''

    with open("railway_redeploy.py", "w") as f:
        f.write(script_content)
    print("✅ Created railway_redeploy.py")


def create_manual_deployment_guide():
    """Create manual deployment guide"""
    guide = """# 🚀 Manual Railway Deployment Fix

## Problem
The Railway deployment is serving the default Railway page instead of our Flask backend.

## Quick Fix Steps

### 1. Verify Files
Ensure these files exist:
- ✅ `final_backend.py` (main Flask app)
- ✅ `Procfile` (deployment command)
- ✅ `requirements.txt` (Python dependencies)

### 2. Railway CLI Deployment
```bash
# Install Railway CLI (if not installed)
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy
railway up
```

### 3. Web Dashboard Deployment
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Find your `hiremebahamas-backend` project
3. Go to Settings → Deploy
4. Click "Deploy Latest Commit"

### 4. Verify Deployment
Test these endpoints after deployment:
- https://hiremebahamas-backend.railway.app/health (should return "OK")
- https://hiremebahamas-backend.railway.app/api/auth/login (should accept OPTIONS/POST)

## Environment Variables
Ensure these are set in Railway dashboard:
- `PORT` (automatically set by Railway)
- `DATABASE_URL` (your database connection)
- `SECRET_KEY` (Flask secret key)
- `JWT_SECRET_KEY` (JWT signing key)

## Troubleshooting
If deployment still fails:
1. Check Railway logs in dashboard
2. Verify `final_backend.py` has no syntax errors
3. Ensure all dependencies are in `requirements.txt`
4. Check that Flask app is properly exported as `app`

## After Successful Deployment
1. Test login at: https://hiremebahamas.vercel.app
2. Check browser DevTools for API calls
3. Verify 405 errors are resolved
"""

    with open("RAILWAY_DEPLOYMENT_FIX.md", "w") as f:
        f.write(guide)
    print("✅ Created RAILWAY_DEPLOYMENT_FIX.md")


def main():
    """Main function"""
    print("🔧 Backend Deployment Diagnostic & Fix")
    print("=" * 50)

    # Check current configuration
    check_railway_config()

    # Test backend locally
    backend_works = test_local_backend()

    if backend_works:
        print("\n✅ Backend works locally - fixing deployment...")

        # Create fix files
        create_deployment_fix()
        create_railway_redeploy_script()
        create_manual_deployment_guide()

        print("\n" + "=" * 50)
        print("🎯 DEPLOYMENT FIX READY!")
        print("=" * 50)
        print("Next steps:")
        print("1. Run: python railway_redeploy.py")
        print("2. Or follow guide in: RAILWAY_DEPLOYMENT_FIX.md")
        print("3. Test: https://hiremebahamas-backend.railway.app/health")
        print("=" * 50)

    else:
        print("\n❌ Backend has issues locally - fix backend first")


if __name__ == "__main__":
    main()

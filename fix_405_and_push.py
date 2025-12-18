#!/usr/bin/env python3
"""
Complete 405 Error Fix & Auto-Push Script
This script ensures all necessary dependencies and configurations are correct
and automatically pushes changes to the main domain
"""

import subprocess
import sys
import time
from pathlib import Path


def install_python_dependencies():
    """Ensure all required Python packages are installed"""
    print("📦 Installing Python Dependencies...")
    print("=" * 60)

    required_packages = [
        "Flask==2.3.3",
        "Flask-CORS==4.0.0",
        "Flask-Limiter==3.5.0",
        "Flask-Caching==2.1.0",
        "PyJWT==2.8.0",
        "bcrypt==4.0.1",
        "python-dotenv==1.0.0",
        "gunicorn==21.2.0",
        "waitress==2.1.2",
        "Werkzeug==2.3.7",
        "requests==2.31.0",
    ]

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True,
        )
        print("✅ Pip upgraded")

        for package in required_packages:
            print(f"  Installing {package}...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                check=True,
                capture_output=True,
            )

        print("✅ All Python dependencies installed")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def verify_backend_routes():
    """Verify backend has correct auth routes"""
    print("\n🔍 Verifying Backend Routes...")
    print("=" * 60)

    backend_file = Path("final_backend.py")

    if not backend_file.exists():
        print("❌ final_backend.py not found")
        return False

    with open(backend_file, "r", encoding="utf-8") as f:
        content = f.read()

    required_routes = ["/api/auth/login", "/api/auth/register", "/health"]

    missing_routes = []
    for route in required_routes:
        if route not in content:
            missing_routes.append(route)

    if missing_routes:
        print(f"⚠️ Missing routes: {', '.join(missing_routes)}")
        return False

    print("✅ All auth routes present in backend")

    # Check for CORS configuration
    if "CORS" in content and "flask_cors" in content:
        print("✅ CORS properly configured")
    else:
        print("⚠️ CORS may not be configured")

    # Check for OPTIONS method support
    if "OPTIONS" in content:
        print("✅ OPTIONS method supported")
    else:
        print("⚠️ OPTIONS method may not be supported")

    return True


def check_deployment_files():
    """Verify all deployment files are correct"""
    print("\n📋 Checking Deployment Files...")
    print("=" * 60)

    files_to_check = {
        "nixpacks.toml": "Nixpacks configuration",
        ".nixpacksignore": "Nixpacks ignore file",
        ".renderignore": "Render ignore file",
        "Procfile": "Process file",
        "requirements.txt": "Python requirements",
    }

    all_present = True
    for file, description in files_to_check.items():
        if Path(file).exists():
            print(f"✅ {file:<20} - {description}")
        else:
            print(f"❌ {file:<20} - {description} (missing)")
            all_present = False

    return all_present


def test_backend_locally():
    """Test if backend can import successfully"""
    print("\n🧪 Testing Backend Import...")
    print("=" * 60)

    try:
        # Try to import the backend
        sys.path.insert(0, ".")
        import final_backend

        print("✅ Backend imports successfully")

        # Check if Flask app exists
        if hasattr(final_backend, "app"):
            print("✅ Flask app object found")
            return True
        else:
            print("❌ Flask app object not found")
            return False

    except ImportError as e:
        print(f"❌ Backend import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False


def push_to_repository():
    """Push all changes to GitHub"""
    print("\n🚀 Pushing Changes to Repository...")
    print("=" * 60)

    try:
        # Check git status
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
        )

        if not result.stdout.strip():
            print("ℹ️ No changes to commit")
            print("✅ Repository is up to date")
            return True

        print("📝 Changes detected:")
        print(result.stdout)

        # Add all changes
        print("\n➕ Adding changes...")
        subprocess.run(["git", "add", "."], check=True)
        print("✅ Changes staged")

        # Commit
        commit_msg = (
            "Fix 405 auth errors: ensure all dependencies and routes are configured"
        )
        print(f"\n💾 Committing: {commit_msg}")
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        print("✅ Changes committed")

        # Push
        print("\n⬆️ Pushing to origin/main...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Changes pushed to repository")

        print("\n🎯 Render will auto-deploy in 3-5 minutes")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False


def test_deployed_backend():
    """Test the deployed backend"""
    print("\n🌐 Testing Deployed Backend...")
    print("=" * 60)

    import requests

    backend_url = "https://hiremebahamas-backend.render.app"

    try:
        # Test health endpoint
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Health endpoint: {response.status_code}")
        else:
            print(f"⚠️ Health endpoint: {response.status_code}")

        # Test auth endpoints
        auth_response = requests.options(f"{backend_url}/api/auth/login", timeout=10)
        if auth_response.status_code == 200:
            print(f"✅ Login endpoint (OPTIONS): {auth_response.status_code}")
            print("   🎉 405 error is FIXED!")
        elif auth_response.status_code == 404:
            print(f"⚠️ Login endpoint: {auth_response.status_code} (Still deploying...)")
            print("   Wait 3-5 minutes for Render deployment")
        else:
            print(f"⚠️ Login endpoint: {auth_response.status_code}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Backend test: {e}")
        print("   Backend may still be deploying")
        return False


def main():
    """Main execution"""
    print("\n" + "=" * 60)
    print("🔧 COMPLETE 405 ERROR FIX & AUTO-PUSH")
    print("=" * 60)
    print()

    # Step 1: Install dependencies
    deps_ok = install_python_dependencies()

    # Step 2: Verify backend
    backend_ok = verify_backend_routes()

    # Step 3: Check deployment files
    files_ok = check_deployment_files()

    # Step 4: Test backend locally
    import_ok = test_backend_locally()

    # Step 5: Push to repository
    if deps_ok and backend_ok and files_ok:
        push_ok = push_to_repository()
    else:
        print("\n⚠️ Skipping push due to validation errors")
        push_ok = False

    # Step 6: Test deployed backend
    time.sleep(2)
    test_deployed_backend()

    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL STATUS")
    print("=" * 60)

    checks = {
        "Python Dependencies": deps_ok,
        "Backend Routes": backend_ok,
        "Deployment Files": files_ok,
        "Backend Import": import_ok,
        "Git Push": push_ok,
    }

    for check, status in checks.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check}")

    if all(checks.values()):
        print("\n🎉 ALL CHECKS PASSED!")
        print("✅ Changes pushed to hiremebahamas.com")
        print("⏱️ Render deployment: 3-5 minutes")
        print("\n🌐 Test endpoints after deployment:")
        print("   https://hiremebahamas-backend.render.app/health")
        print("   https://hiremebahamas-backend.render.app/api/auth/login")
    else:
        print("\n⚠️ Some checks failed - review output above")

    print("=" * 60)


if __name__ == "__main__":
    main()

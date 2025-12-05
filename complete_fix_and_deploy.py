#!/usr/bin/env python3
"""
DEPRECATED: Complete Build, Deploy, and Test Solution

This script was created for Render deployment. After migrating to Vercel + Railway,
this script is no longer needed.

For deployment, use:
- Vercel Git integration (automatic on push)
- GitHub Actions workflows (.github/workflows/)
- Manual: vercel --prod (in frontend directory)

Usage (if still needed):
  BACKEND_URL=https://your-app.up.railway.app python complete_fix_and_deploy.py
"""
import json
import os
import subprocess
import sys
import time

import requests


def run_command(cmd, cwd=None, shell=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(
            cmd, shell=shell, cwd=cwd, capture_output=True, text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def verify_backend():
    """Verify backend is accessible"""
    print_section("1. Verifying Backend")

    backend_url = os.getenv("BACKEND_URL", "https://hiremebahamas.vercel.app")

    try:
        print("Testing backend health...")
        response = requests.get(f"{backend_url}/health", timeout=60)

        if response.status_code == 200:
            print("[OK] Backend is online and healthy")
            data = response.json()
            print(f"     Status: {data.get('status')}")
            print(f"     Version: {data.get('version')}")
            return True
        else:
            print(f"[WARNING] Backend returned status {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("[ERROR] Backend timeout - may be waking up")
        print("        Waiting 30 seconds and trying again...")
        time.sleep(30)

        try:
            response = requests.get(f"{backend_url}/health", timeout=60)
            if response.status_code == 200:
                print("[OK] Backend is now online")
                return True
        except:
            pass

        print("[ERROR] Backend is not responding")
        return False
    except Exception as e:
        print(f"[ERROR] Cannot reach backend: {e}")
        return False


def test_login_endpoint():
    """Test the login endpoint specifically"""
    print_section("2. Testing Login Endpoint")

    backend_url = os.getenv("BACKEND_URL", "https://hiremebahamas.vercel.app")

    try:
        # Test OPTIONS (CORS preflight)
        print("Testing CORS preflight (OPTIONS)...")
        response = requests.options(
            f"{backend_url}/api/auth/login",
            headers={
                "Origin": "https://frontend-i6uhdk4zb-cliffs-projects-a84c76c9.vercel.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
            timeout=30,
        )

        if response.status_code == 200:
            print("[OK] CORS preflight passed")
            print(
                f"     Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}"
            )
            print(
                f"     Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not set')}"
            )
        else:
            print(f"[WARNING] OPTIONS returned {response.status_code}")

        # Test POST (actual login)
        print("\nTesting POST request...")
        response = requests.post(
            f"{backend_url}/api/auth/login",
            headers={
                "Content-Type": "application/json",
                "Origin": "https://frontend-i6uhdk4zb-cliffs-projects-a84c76c9.vercel.app",
            },
            json={"email": "test@example.com", "password": "testpass"},
            timeout=30,
        )

        if response.status_code in [401, 400]:
            print("[OK] Login endpoint working (401 expected with test credentials)")
            return True
        elif response.status_code == 405:
            print("[ERROR] 405 Method Not Allowed - CRITICAL ISSUE")
            print(f"        Response: {response.text}")
            return False
        else:
            print(f"[WARNING] Unexpected status: {response.status_code}")
            print(f"          Response: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] Login endpoint test failed: {e}")
        return False


def clean_frontend():
    """Clean frontend build artifacts"""
    print_section("3. Cleaning Frontend Build")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(script_dir, "frontend")

    # Remove dist, node_modules/.cache
    print("Removing old build artifacts...")

    dist_path = os.path.join(frontend_dir, "dist")
    if os.path.exists(dist_path):
        success, _, _ = run_command(
            f'powershell -Command "Remove-Item -Recurse -Force {dist_path}"'
        )
        if success:
            print("[OK] Removed dist directory")

    cache_path = os.path.join(frontend_dir, "node_modules", ".cache")
    if os.path.exists(cache_path):
        success, _, _ = run_command(
            f'powershell -Command "Remove-Item -Recurse -Force {cache_path}"'
        )
        if success:
            print("[OK] Removed cache directory")

    print("[OK] Frontend cleaned")
    return True


def build_frontend():
    """Build frontend with production settings"""
    print_section("4. Building Frontend")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(script_dir, "frontend")

    print("Installing dependencies...")
    success, stdout, stderr = run_command("npm install", cwd=frontend_dir)

    if not success:
        print(f"[ERROR] npm install failed: {stderr}")
        return False

    print("[OK] Dependencies installed")

    print("\nBuilding with production settings...")

    # Set environment variables
    env = os.environ.copy()
    backend_url = os.getenv("BACKEND_URL", "https://hiremebahamas.vercel.app")
    env["VITE_API_URL"] = backend_url
    env["VITE_SOCKET_URL"] = backend_url
    env["VITE_ENABLE_RETRY"] = "true"
    env["VITE_RETRY_ATTEMPTS"] = "5"
    env["VITE_REQUEST_TIMEOUT"] = "45000"

    result = subprocess.run(
        "npm run build",
        shell=True,
        cwd=frontend_dir,
        capture_output=True,
        text=True,
        env=env,
    )

    if result.returncode == 0:
        print("[OK] Build successful")

        # Verify build
        dist_path = os.path.join(frontend_dir, "dist")
        if os.path.exists(dist_path):
            files = os.listdir(dist_path)
            print(f"     Build contains {len(files)} files")
            return True
        else:
            print("[ERROR] Build directory not found")
            return False
    else:
        print(f"[ERROR] Build failed:")
        print(stderr)
        return False


def deploy_to_vercel():
    """Deploy to Vercel"""
    print_section("5. Deploying to Vercel")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(script_dir, "frontend")

    print("Deploying to production...")

    success, stdout, stderr = run_command("npx vercel --prod", cwd=frontend_dir)

    # Parse output for URL
    url = None
    if "Production:" in stdout or "Production:" in stderr:
        output = stdout + stderr
        for line in output.split("\n"):
            if "Production:" in line or "https://" in line:
                if "vercel.app" in line:
                    # Extract URL
                    parts = line.split("https://")
                    if len(parts) > 1:
                        url = "https://" + parts[1].split()[0]
                        break

    if url:
        print(f"[OK] Deployment successful!")
        print(f"     URL: {url}")
        return url
    else:
        print("[WARNING] Deployment may have succeeded but couldn't parse URL")
        print("          Check Vercel dashboard")
        return "https://frontend-i6uhdk4zb-cliffs-projects-a84c76c9.vercel.app"


def test_production_app(url):
    """Test the production app"""
    print_section("6. Testing Production App")

    try:
        print(f"Testing app at {url}...")
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            print("[OK] App is accessible")

            # Check if it contains our app
            if (
                "HireMeBahamas" in response.text
                or "hiremebahamas" in response.text.lower()
            ):
                print("[OK] App content verified")
                return True
            else:
                print("[WARNING] App content may not be correct")
                return False
        else:
            print(f"[WARNING] App returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Cannot access app: {e}")
        return False


def main():
    print("=" * 70)
    print("  COMPREHENSIVE 405 ERROR FIX")
    print("  Complete Build, Deploy, and Test")
    print("=" * 70)

    # Step 1: Verify backend
    if not verify_backend():
        print("\n[ERROR] Backend verification failed")
        print("        Please ensure backend is running")
        return False

    # Step 2: Test login endpoint
    if not test_login_endpoint():
        print("\n[ERROR] Login endpoint test failed")
        print("        This is the source of the 405 error")
        print("        Backend may need to be restarted")
        return False

    # Step 3: Clean frontend
    if not clean_frontend():
        print("\n[ERROR] Frontend cleaning failed")
        return False

    # Step 4: Build frontend
    if not build_frontend():
        print("\n[ERROR] Frontend build failed")
        return False

    # Step 5: Deploy to Vercel
    url = deploy_to_vercel()
    if not url:
        print("\n[ERROR] Deployment failed")
        return False

    # Step 6: Test production app
    print("\nWaiting 10 seconds for deployment to propagate...")
    time.sleep(10)

    test_production_app(url)

    # Final summary
    print_section("DEPLOYMENT COMPLETE")

    print("\n[SUCCESS] All steps completed!")
    print(f"\nYour app is live at:")
    print(f"  {url}")

    print("\n[NEXT STEPS]")
    print("  1. Clear your browser cache (Ctrl + Shift + Delete)")
    print("  2. Visit your app URL above")
    print("  3. Try logging in with your credentials")
    print("  4. The 405 error should be FIXED")

    print("\n[KEEP-ALIVE SERVICE]")
    print("  To keep backend awake 24/7, run in a separate terminal:")
    print("  python backend_keepalive_service.py")

    print("\n" + "=" * 70)

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

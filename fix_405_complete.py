#!/usr/bin/env python3
"""
HireMeBahamas 405 Error Fix - Complete Solution
Uses IntelliSense and automated fixes to resolve login/signup 405 errors

DEPRECATED: This script was created for Render deployment issues.
After migrating to Vercel + Render, 405 errors should not occur.

If you're experiencing 405 errors, check:
1. VITE_API_URL points to correct backend (Render or Vercel)
2. Backend is deployed and accessible
3. CORS is properly configured in backend
"""

import json
import os
import requests
from pathlib import Path
from datetime import datetime
import subprocess
import time

class HireBahamas405Fix:
    def __init__(self):
        self.backend_url = os.getenv("BACKEND_URL", "https://hiremebahamas.vercel.app")
        self.fixes_applied = []
        self.verification_results = []
        
    def log_fix(self, fix_name: str, status: str, details: str = ""):
        """Log applied fixes"""
        fix_result = {
            "timestamp": datetime.now().isoformat(),
            "fix": fix_name,
            "status": status,
            "details": details
        }
        self.fixes_applied.append(fix_result)
        
        # Print with colors
        status_colors = {
            "APPLIED": "\033[92m✅",  # Green
            "FAILED": "\033[91m❌",   # Red
            "SKIPPED": "\033[93m⏭️",  # Yellow
        }
        
        color = status_colors.get(status, "")
        reset = "\033[0m"
        
        print(f"{color} {fix_name}: {status}{reset}")
        if details:
            print(f"   {details}")
        print()

    def fix_vercel_configuration(self) -> bool:
        """Fix Vercel configuration for proper SPA routing and API URL"""
        print("� Fixing Vercel Configuration...")
        
        vercel_config_path = Path("vercel.json")
        
        if not vercel_config_path.exists():
            self.log_fix("Vercel Config", "SKIPPED", "vercel.json not found")
            return False
            
        try:
            # Read current config
            with open(vercel_config_path, 'r') as f:
                config = json.load(f)
            
            # Update API URL to use backend_url from class
            old_api_url = config.get("env", {}).get("VITE_API_URL", "")
            correct_api_url = self.backend_url
            
            if old_api_url != correct_api_url:
                config["env"] = config.get("env", {})
                config["env"]["VITE_API_URL"] = correct_api_url
                self.log_fix("API URL Fix", "APPLIED", f"Changed from {old_api_url} to {correct_api_url}")
            else:
                self.log_fix("API URL Check", "SKIPPED", "API URL already correct")
            
            # Add SPA rewrites if missing
            if "rewrites" not in config:
                config["rewrites"] = [
                    {
                        "source": "/((?!api/.*).*)",
                        "destination": "/index.html"
                    }
                ]
                self.log_fix("SPA Rewrites", "APPLIED", "Added SPA routing support")
            else:
                self.log_fix("SPA Rewrites Check", "SKIPPED", "Rewrites already configured")
            
            # Write updated config
            with open(vercel_config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            return True
            
        except Exception as e:
            self.log_fix("Vercel Config", "FAILED", f"Error: {str(e)}")
            return False

    def fix_frontend_environment(self) -> bool:
        """Fix frontend environment variables"""
        print("🔧 Fixing Frontend Environment...")
        
        frontend_path = Path("frontend")
        if not frontend_path.exists():
            self.log_fix("Frontend Check", "FAILED", "Frontend directory not found")
            return False
        
        correct_api_url = self.backend_url
        env_files = [".env", ".env.local", ".env.production"]
        
        for env_file in env_files:
            env_path = frontend_path / env_file
            if env_path.exists():
                try:
                    # Read current env file
                    with open(env_path, 'r') as f:
                        lines = f.readlines()
                    
                    # Update API URL
                    updated = False
                    new_lines = []
                    
                    for line in lines:
                        if line.startswith("VITE_API_URL="):
                            current_url = line.split("=", 1)[1].strip()
                            if current_url != correct_api_url:
                                new_lines.append(f"VITE_API_URL={correct_api_url}\n")
                                updated = True
                                self.log_fix(f"Env File {env_file}", "APPLIED", f"Updated API URL to {correct_api_url}")
                            else:
                                new_lines.append(line)
                        else:
                            new_lines.append(line)
                    
                    # Add API URL if not found
                    if not any(line.startswith("VITE_API_URL=") for line in lines):
                        new_lines.append(f"VITE_API_URL={correct_api_url}\n")
                        updated = True
                        self.log_fix(f"Env File {env_file}", "APPLIED", f"Added API URL: {correct_api_url}")
                    
                    # Write updated file if changes were made
                    if updated:
                        with open(env_path, 'w') as f:
                            f.writelines(new_lines)
                    else:
                        self.log_fix(f"Env File {env_file}", "SKIPPED", "Already correct")
                        
                except Exception as e:
                    self.log_fix(f"Env File {env_file}", "FAILED", f"Error: {str(e)}")
                    
        return True
VITE_ENABLE_RETRY=true
VITE_RETRY_ATTEMPTS=3
VITE_REQUEST_TIMEOUT=30000
"""

    with open(env_path, "w") as f:
        f.write(env_content)
    print("✅ .env file configured correctly")

    # Step 2: Clean previous build
    print("\n🧹 Step 2: Cleaning previous build...")
    if os.path.exists("frontend/dist"):
        subprocess.run(
            ["powershell", "-Command", "Remove-Item -Recurse -Force frontend/dist"],
            capture_output=True,
        )
    print("✅ Previous build cleaned")

    # Step 3: Rebuild with environment variables
    print("\n🔨 Step 3: Building with production backend...")
    os.chdir("frontend")

    # Set environment variables for the build
    env = os.environ.copy()
    backend_url = os.getenv("BACKEND_URL", "https://hiremebahamas.vercel.app")
    env["VITE_API_URL"] = backend_url
    env["VITE_SOCKET_URL"] = backend_url

    result = subprocess.run(
        ["powershell", "-Command", "npm run build"],
        capture_output=True,
        text=True,
        env=env,
        shell=True,
    )

    if result.returncode == 0:
        print("✅ Build successful!")
    else:
        print("❌ Build failed:")
        print(result.stderr)
        return

    # Step 4: Verify build contains correct URL
    print("\n🔍 Step 4: Verifying build configuration...")
    # Check the index.js for the API URL
    assets_dir = "dist/assets"
    if os.path.exists(assets_dir):
        js_files = [f for f in os.listdir(assets_dir) if f.endswith(".js")]
        found_correct_url = False

        for js_file in js_files:
            with open(os.path.join(assets_dir, js_file), "r", encoding="utf-8") as f:
                content = f.read()
                # Check if production backend URL is present
                if self.backend_url in content:
                    found_correct_url = True
                    print(f"✅ Found production URL in {js_file}")
                    break
                elif (
                    "localhost" in content
                    or "127.0.0.1" in content
                    or "9999" in content
                ):
                    print(f"⚠️  Found localhost URL in {js_file}")

        if not found_correct_url:
            print("⚠️  Could not verify production URL in build files")

    # Step 5: Deploy to Vercel
    print("\n🚀 Step 5: Deploying to Vercel...")
    result = subprocess.run(
        ["powershell", "-Command", "npx vercel --prod"],
        capture_output=True,
        text=True,
        shell=True,
    )

    if "Production:" in result.stdout:
        print("✅ Deployment successful!")
        # Extract URL
        for line in result.stdout.split("\n"):
            if "Production:" in line:
                url = line.split("Production:")[1].strip()
                print(f"\n🌐 Live URL: {url}")
    else:
        print("❌ Deployment failed:")
        print(result.stderr)
        return

    # Step 6: Test the backend
    print("\n🧪 Step 6: Testing backend connection...")
    try:
        import requests

        backend_url = os.getenv("BACKEND_URL", "https://hiremebahamas.vercel.app")
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is online and responding")
        else:
            print(f"⚠️  Backend returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")

    print("\n" + "=" * 70)
    print("  ✅ Fix Complete!")
    print("=" * 70)
    print("\n📋 Next Steps:")
    print("1. Visit the deployment URL above")
    print("2. Clear browser cache (Ctrl + Shift + Delete)")
    print("3. Try logging in again")
    print("4. If still getting 405, open DevTools (F12) and check Network tab")
    print("\n💡 Tip: Use Incognito mode (Ctrl + Shift + N) to avoid cache issues")


if __name__ == "__main__":
    main()

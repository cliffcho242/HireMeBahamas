"""
Fix Network and Login Issues for HireBahamas Platform
Handles Vite import errors and ensures all files are properly set up
"""

import os
import subprocess
import time
from pathlib import Path


def fix_frontend_issues():
    """Fix common frontend import issues"""
    print("🔧 Fixing Frontend Import Issues...")

    frontend_dir = Path("C:/Users/Dell/OneDrive/Desktop/HireBahamas/frontend/src")

    # Check if App.css exists
    app_css = frontend_dir / "App.css"
    if not app_css.exists():
        print("✅ Creating missing App.css...")
        with open(app_css, "w") as f:
            f.write(
                """/* App.css - Main application styles */

.App {
  text-align: center;
  min-height: 100vh;
  background: #f0f2f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

.social-feed-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Loading and error states */
.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50vh;
  font-size: 18px;
  color: #65676b;
}

.error {
  background: #ffebee;
  border: 1px solid #f44336;
  border-radius: 8px;
  padding: 16px;
  margin: 16px;
  color: #d32f2f;
  text-align: center;
}
"""
            )
        print("✅ App.css created successfully")
    else:
        print("✅ App.css already exists")

    # Check SocialFeed component
    social_feed_tsx = frontend_dir / "components" / "SocialFeed.tsx"
    social_feed_css = frontend_dir / "components" / "SocialFeed.css"

    if social_feed_tsx.exists():
        print("✅ SocialFeed.tsx exists")
    else:
        print("❌ SocialFeed.tsx missing")

    if social_feed_css.exists():
        print("✅ SocialFeed.css exists")
    else:
        print("❌ SocialFeed.css missing")


def restart_frontend():
    """Restart the frontend server to apply fixes"""
    print("\n🔄 Restarting Frontend Server...")

    workspace = Path("C:/Users/Dell/OneDrive/Desktop/HireBahamas")
    frontend_dir = workspace / "frontend"

    # Kill any existing npm processes (Windows)
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "node.exe"], capture_output=True, check=False
        )
        time.sleep(2)
    except:
        pass

    # Start fresh frontend server
    try:
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(frontend_dir),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
        )
        print(f"✅ Frontend restarted (PID: {frontend_process.pid})")
        return True
    except Exception as e:
        print(f"❌ Frontend restart failed: {e}")
        return False


def check_backend():
    """Ensure backend is running"""
    print("\n🔍 Checking Backend Status...")

    import socket

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(("127.0.0.1", 8008))
        sock.close()

        if result == 0:
            print("✅ Backend is running on port 8008")
            return True
        else:
            print("❌ Backend not responding on port 8008")
            return False
    except:
        print("❌ Cannot check backend status")
        return False


def start_backend():
    """Start the backend server"""
    print("🚀 Starting Backend Server...")

    workspace = Path("C:/Users/Dell/OneDrive/Desktop/HireBahamas")
    backend_script = workspace / "facebook_like_backend.py"
    venv_python = workspace / ".venv" / "Scripts" / "python.exe"

    if not backend_script.exists():
        print("❌ Backend script not found")
        return False

    python_exe = str(venv_python) if venv_python.exists() else "python"

    try:
        backend_process = subprocess.Popen(
            [python_exe, str(backend_script)],
            cwd=str(workspace),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
        )
        print(f"✅ Backend started (PID: {backend_process.pid})")
        return True
    except Exception as e:
        print(f"❌ Backend start failed: {e}")
        return False


def main():
    print("=" * 60)
    print("🛠️ HireBahamas Platform - Network & Login Fix")
    print("=" * 60)

    # Fix frontend issues
    fix_frontend_issues()

    # Check backend
    if not check_backend():
        start_backend()
        time.sleep(5)

    # Restart frontend to apply fixes
    restart_frontend()

    print("\n⏳ Waiting for servers to stabilize...")
    time.sleep(10)

    # Final status check
    print("\n📊 Final Status Check:")
    backend_ok = check_backend()

    # Check frontend
    import socket

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        frontend_ok = sock.connect_ex(("localhost", 3000)) == 0
        sock.close()
    except:
        frontend_ok = False

    print(f"Backend (8008): {'✅ RUNNING' if backend_ok else '❌ OFFLINE'}")
    print(f"Frontend (3000): {'✅ RUNNING' if frontend_ok else '❌ OFFLINE'}")

    if backend_ok and frontend_ok:
        print("\n🎉 SUCCESS! Platform is operational!")
        print("🌐 Frontend: http://localhost:3000")
        print("🚀 Backend: http://127.0.0.1:8008")
        print("👤 Login: admin@hirebahamas.com / AdminPass123!")

        # Open browser
        if os.name == "nt":
            time.sleep(2)
            os.system("start http://localhost:3000")
    else:
        print("\n❌ Some issues remain. Check the console outputs.")

    print("=" * 60)


if __name__ == "__main__":
    main()

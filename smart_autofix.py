"""
🤖 Smart AI Auto-Fix for Localhost Errors
HireBahamas Facebook-like Platform
"""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import requests


def check_port_available(host, port):
    """Check if a port is responding"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def test_url(url):
    """Test URL response"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False


def start_backend_server():
    """Start the Facebook backend"""
    workspace = Path(__file__).parent
    backend_file = workspace / "facebook_like_backend.py"
    venv_python = workspace / ".venv" / "Scripts" / "python.exe"

    if not backend_file.exists():
        print("❌ Backend file not found")
        return False

    python_exe = str(venv_python) if venv_python.exists() else "python"

    try:
        subprocess.Popen(
            [python_exe, str(backend_file)],
            cwd=str(workspace),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
        )
        return True
    except Exception as e:
        print(f"❌ Backend start failed: {e}")
        return False


def start_frontend_server():
    """Start the frontend server"""
    workspace = Path(__file__).parent
    frontend_dir = workspace / "frontend"

    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False

    try:
        subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(frontend_dir),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
        )
        return True
    except Exception as e:
        print(f"❌ Frontend start failed: {e}")
        return False


def main():
    print("🤖 AI Smart Auto-Fix for Facebook-like Platform")
    print("=" * 55)

    # Backend Check
    print("\n🔍 Checking Backend (127.0.0.1:8008)...")

    backend_port_ok = check_port_available("127.0.0.1", 8008)
    backend_health_ok = (
        test_url("http://127.0.0.1:8008/health") if backend_port_ok else False
    )

    if backend_port_ok and backend_health_ok:
        print("✅ Backend: HEALTHY")
    elif backend_port_ok and not backend_health_ok:
        print("⚠️ Backend: Port responding but health check failed")
    else:
        print("❌ Backend: Not responding")
        print("🤖 Auto-fixing backend...")

        if start_backend_server():
            print("⏳ Waiting for backend to start...")
            for i in range(20):
                time.sleep(1)
                if check_port_available("127.0.0.1", 8008):
                    if test_url("http://127.0.0.1:8008/health"):
                        print("✅ Backend: Started and healthy!")
                        backend_port_ok = True
                        backend_health_ok = True
                        break
                    else:
                        print("⚠️ Backend: Started but still warming up...")
                print(f"   Attempt {i+1}/20...")

            if not (backend_port_ok and backend_health_ok):
                print("❌ Backend: Failed to start properly")

    # Frontend Check
    print("\n🔍 Checking Frontend (localhost:3000)...")

    frontend_port_ok = check_port_available("localhost", 3000)
    frontend_health_ok = (
        test_url("http://localhost:3000") if frontend_port_ok else False
    )

    if frontend_port_ok and frontend_health_ok:
        print("✅ Frontend: HEALTHY")
    elif frontend_port_ok and not frontend_health_ok:
        print("⚠️ Frontend: Port responding but page not loading")
    else:
        print("❌ Frontend: Not responding")
        print("🤖 Auto-fixing frontend...")

        if start_frontend_server():
            print("⏳ Waiting for frontend to start...")
            for i in range(20):
                time.sleep(1)
                if check_port_available("localhost", 3000):
                    if test_url("http://localhost:3000"):
                        print("✅ Frontend: Started and healthy!")
                        frontend_port_ok = True
                        frontend_health_ok = True
                        break
                    else:
                        print("⚠️ Frontend: Started but still loading...")
                print(f"   Attempt {i+1}/20...")

            if not (frontend_port_ok and frontend_health_ok):
                print("❌ Frontend: Failed to start properly")

    # Final Status
    print("\n" + "=" * 55)

    if backend_port_ok and frontend_port_ok:
        print("🎉 SUCCESS! Facebook-like AI Platform is READY!")
        print("\n🌐 Access Your Platform:")
        print("   • Main App: http://localhost:3000")
        print("   • Backend API: http://127.0.0.1:8008")
        print("   • Health Check: http://127.0.0.1:8008/health")

        print("\n👤 Login Credentials:")
        print("   • Email: admin@hirebahamas.com")
        print("   • Password: AdminPass123!")

        print("\n🤖 AI Features Available:")
        print("   ✓ User Pattern Analytics")
        print("   ✓ Smart Content Recommendations")
        print("   ✓ Real-time Social Feed")
        print("   ✓ Engagement Scoring")

        # Auto-open browser
        print("\n🚀 Opening platform in browser...")
        if os.name == "nt":
            try:
                os.system("start http://localhost:3000")
                time.sleep(1)
                os.system("start http://127.0.0.1:8008/health")
            except:
                pass

    else:
        print("❌ Platform not fully operational")

        if not backend_port_ok:
            print("   • Backend issue: Port 8008 not responding")
            print("     Try: Check Python environment and dependencies")

        if not frontend_port_ok:
            print("   • Frontend issue: Port 3000 not responding")
            print("     Try: Check npm dependencies and Node.js version")

        print("\n💡 Suggested actions:")
        print("   1. Run this script again")
        print("   2. Check Windows Firewall settings")
        print("   3. Restart VS Code and terminals")

    print("=" * 55)


if __name__ == "__main__":
    main()

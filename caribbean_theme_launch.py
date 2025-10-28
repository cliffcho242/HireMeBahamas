#!/usr/bin/env python3
"""
🌴 Caribbean Theme Test & Launch
Tests the new Caribbean-themed interface and launches the browser
"""
import time
import webbrowser

import requests


def test_systems():
    """Test backend and frontend"""
    try:
        # Test backend
        response = requests.get("http://127.0.0.1:8008/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend not running")
            return False, None

        # Test frontend
        ports = [3000, 3001, 3002, 3003]
        frontend_port = None
        for port in ports:
            try:
                response = requests.get(f"http://localhost:{port}", timeout=3)
                if response.status_code == 200:
                    frontend_port = port
                    break
            except:
                continue

        if not frontend_port:
            print("❌ Frontend not running")
            return False, None

        return True, frontend_port

    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None


def main():
    print("🌴 CARIBBEAN THEME LAUNCH")
    print("=" * 50)

    print("🔧 Testing systems...")
    systems_ok, port = test_systems()

    if not systems_ok:
        print("\n❌ Systems not ready!")
        print("Please ensure:")
        print("1. Backend: python clean_backend.py")
        print("2. Frontend: cd frontend && npm run dev")
        return

    print(f"✅ All systems ready!")
    print(f"Backend: http://127.0.0.1:8008")
    print(f"Frontend: http://localhost:{port}")

    print("\n🎨 CARIBBEAN THEME FEATURES:")
    print("- ✅ Tropical gradient backgrounds")
    print("- ✅ Caribbean color palette (cyan, teal, coral)")
    print("- ✅ Palm tree and beach-themed elements")
    print("- ✅ Island-style animations and effects")
    print("- ✅ Professional Paradise branding")
    print("- ✅ Bahamas-specific content and imagery")

    print(f"\n🌺 Opening Caribbean Paradise Interface...")
    url = f"http://localhost:{port}"
    webbrowser.open(url)

    print(f"\n🏖️ WELCOME TO PARADISE!")
    print(f"Experience the beautiful Caribbean-themed job platform:")
    print(f"• Tropical login page with beach vibes")
    print(f"• Paradise dashboard with island colors")
    print(f"• Caribbean-inspired job cards and buttons")
    print(f"• Professional yet relaxed island atmosphere")

    print(f"\n🌊 Demo Login: admin@hirebahamas.com / admin123")
    print(f"Enjoy your Caribbean career journey! 🌴")


if __name__ == "__main__":
    main()

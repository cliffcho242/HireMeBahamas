#!/usr/bin/env python3
"""
Quick Frontend Fix - Run npm commands from correct directory
"""

import os
import sys
import subprocess

def main():
    print("🔧 Quick Frontend Fix")
    print("=" * 30)

    # Check if we're in the right directory
    if not os.path.exists('frontend'):
        print("❌ frontend directory not found!")
        print("Please run this from the HireBahamas root directory")
        return 1

    # Change to frontend directory
    os.chdir('frontend')

    if not os.path.exists('package.json'):
        print("❌ package.json not found in frontend directory!")
        return 1

    print("✅ Found package.json in frontend directory")
    print("📦 Installing dependencies...")

    # Run npm install
    try:
        npm_cmd = r"C:\Program Files\nodejs\npm.cmd"
        result = subprocess.run([npm_cmd, 'install'],
                              check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return 1

    print("🚀 Starting development server...")
    print("Note: This will run in the background.")
    print("Press Ctrl+C to stop the server when done.")

    # Run npm run dev
    try:
        subprocess.run([npm_cmd, 'run', 'dev'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start dev server: {e}")
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
#!/usr/bin/env python3
"""
Ultimate Node.js/npm Automated Fix
Permanently installs Node.js and adds to PATH if missing
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import tempfile
import shutil
import winreg
import ctypes
from pathlib import Path

class NodeJSInstaller:
    def __init__(self):
        self.node_version = "20.18.0"  # Latest LTS
        self.install_dir = Path("C:\\Program Files\\nodejs")
        self.temp_dir = Path(tempfile.gettempdir()) / "nodejs_install"

    def is_admin(self):
        """Check if running as administrator"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_command(self, cmd, shell=True, capture_output=True):
        """Run a command and return result"""
        try:
            result = subprocess.run(cmd, shell=shell, capture_output=capture_output, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def check_nodejs(self):
        """Check if Node.js and npm are available"""
        print("Checking Node.js installation...")

        # Check node
        success, stdout, stderr = self.run_command("node --version")
        if success:
            print(f"Node.js found: {stdout.strip()}")
            node_version = stdout.strip()
        else:
            print("Node.js not found")
            return False

        # Check npm
        success, stdout, stderr = self.run_command("npm --version")
        if success:
            print(f"npm found: {stdout.strip()}")
            return True
        else:
            print("npm not found")
            return False

    def download_nodejs(self):
        """Download Node.js installer"""
        print(f"Downloading Node.js {self.node_version}...")

        url = f"https://nodejs.org/dist/v{self.node_version}/node-v{self.node_version}-x64.msi"
        installer_path = self.temp_dir / f"nodejs-{self.node_version}.msi"

        try:
            # Create temp directory
            self.temp_dir.mkdir(exist_ok=True)

            # Download
            with urllib.request.urlopen(url) as response:
                with open(installer_path, 'wb') as f:
                    shutil.copyfileobj(response, f)

            print(f"Downloaded to: {installer_path}")
            return installer_path

        except Exception as e:
            print(f"Download failed: {e}")
            return None

    def install_nodejs(self, installer_path):
        """Install Node.js using MSI installer"""
        print("Installing Node.js...")

        # Run MSI installer silently
        cmd = f'msiexec /i "{installer_path}" /quiet /norestart'
        success, stdout, stderr = self.run_command(cmd)

        if success:
            print("Node.js installed successfully")
            return True
        else:
            print(f"Installation failed: {stderr}")
            return False

    def add_to_path(self):
        """Add Node.js to system PATH permanently"""
        print("Adding Node.js to system PATH...")

        node_path = str(self.install_dir)
        npm_path = str(self.install_dir)

        try:
            # Open registry
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                               0, winreg.KEY_READ | winreg.KEY_WRITE)

            # Get current PATH
            current_path, _ = winreg.QueryValueEx(key, "PATH")

            # Check if already in PATH
            if node_path.lower() in current_path.lower():
                print("Node.js already in PATH")
                winreg.CloseKey(key)
                return True

            # Add to PATH
            new_path = current_path + ";" + node_path
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)

            # Broadcast environment change
            result = ctypes.windll.user32.SendMessageTimeoutW(
                0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, None
            )

            print("Node.js added to system PATH")
            print("Please restart your terminal/command prompt for PATH changes to take effect")
            return True

        except Exception as e:
            print(f"Failed to add to PATH: {e}")
            return False

    def verify_installation(self):
        """Verify Node.js and npm are working"""
        print("Verifying installation...")

        # Test node
        success, stdout, stderr = self.run_command("node --version")
        if success:
            print(f"Node.js: {stdout.strip()}")
        else:
            print("Node.js verification failed")
            return False

        # Test npm
        success, stdout, stderr = self.run_command("npm --version")
        if success:
            print(f"npm: {stdout.strip()}")
        else:
            print("npm verification failed")
            return False

        return True

    def cleanup(self):
        """Clean up temporary files"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                print("Cleaned up temporary files")
        except Exception as e:
            print(f"Cleanup warning: {e}")

    def install(self):
        """Main installation process"""
        print("Ultimate Node.js Automated Fix")
        print("=" * 40)

        # Check if already installed
        if self.check_nodejs():
            print("Node.js and npm are already installed and working!")
            return True

        # Check admin rights
        if not self.is_admin():
            print("Administrator privileges required for installation")
            print("Please run this script as Administrator (Right-click > Run as administrator)")
            return False

        try:
            # Download
            installer_path = self.download_nodejs()
            if not installer_path:
                return False

            # Install
            if not self.install_nodejs(installer_path):
                return False

            # Add to PATH
            if not self.add_to_path():
                return False

            # Verify
            if not self.verify_installation():
                return False

            print("\nNode.js installation completed successfully!")
            print("Please restart your terminal/command prompt to use npm")
            return True

        finally:
            self.cleanup()

def main():
    """Main function"""
    installer = NodeJSInstaller()

    if installer.install():
        print("\nSUCCESS: Node.js and npm are now permanently installed!")
        print("You can now run: npm install, npm run dev, etc.")
        return 0
    else:
        print("\nFAILED: Could not install Node.js")
        print("Try running as Administrator or install manually from https://nodejs.org")
        return 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""Comprehensive System Diagnostic"""

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import requests


class SystemDiagnostic:
    def __init__(self):
        self.base_dir = Path("C:/Users/Dell/OneDrive/Desktop/HireBahamas")
        self.issues = []
        self.fixes = []

    def log_issue(self, issue):
        self.issues.append(issue)
        print(f"❌ ISSUE: {issue}")

    def log_fix(self, fix):
        self.fixes.append(fix)
        print(f"✅ FIX: {fix}")

    def check_python_environment(self):
        print("\n=== PYTHON ENVIRONMENT CHECK ===")
        venv_python = self.base_dir / ".venv" / "Scripts" / "python.exe"

        if not venv_python.exists():
            self.log_issue(f"Virtual environment Python not found at {venv_python}")
            return False

        # Test Python installation
        try:
            result = subprocess.run(
                [str(venv_python), "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            print(f"✅ Python: {result.stdout.strip()}")
        except Exception as e:
            self.log_issue(f"Python execution failed: {e}")
            return False

        # Check required packages
        packages = ["flask", "flask-cors", "bcrypt", "pyjwt", "requests"]
        for package in packages:
            try:
                result = subprocess.run(
                    [str(venv_python), "-c", f"import {package.replace('-', '_')}"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    print(f"✅ Package {package}: OK")
                else:
                    self.log_issue(f"Package {package} missing or broken")
            except Exception as e:
                self.log_issue(f"Failed to check package {package}: {e}")

        return True

    def check_database(self):
        print("\n=== DATABASE CHECK ===")
        db_path = self.base_dir / "hirebahamas.db"

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Check if users table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
            )
            if cursor.fetchone():
                print("✅ Users table exists")

                # Check admin user
                cursor.execute(
                    "SELECT email FROM users WHERE email='admin@hirebahamas.com'"
                )
                if cursor.fetchone():
                    print("✅ Admin user exists")
                else:
                    self.log_issue("Admin user missing from database")
            else:
                self.log_issue("Users table missing from database")

            conn.close()
        except Exception as e:
            self.log_issue(f"Database error: {e}")

    def check_backend_files(self):
        print("\n=== BACKEND FILES CHECK ===")

        backend_files = [
            "working_backend_final.py",
            "stable_login_backend.py",
            "ultra_simple_backend.py",
        ]

        for file in backend_files:
            file_path = self.base_dir / file
            if file_path.exists():
                print(f"✅ {file} exists")

                # Check if file can be parsed as Python
                try:
                    with open(file_path, "r") as f:
                        compile(f.read(), file_path, "exec")
                    print(f"✅ {file} syntax is valid")
                except SyntaxError as e:
                    self.log_issue(f"Syntax error in {file}: {e}")
                except Exception as e:
                    self.log_issue(f"Error reading {file}: {e}")
            else:
                self.log_issue(f"Backend file missing: {file}")

    def check_frontend_files(self):
        print("\n=== FRONTEND FILES CHECK ===")

        frontend_dir = self.base_dir / "frontend"

        # Check key files
        key_files = [
            "package.json",
            "src/App.tsx",
            "src/main.tsx",
            "src/pages/Login.tsx",
            "src/contexts/AuthContext.tsx",
            "src/services/api.ts",
            ".env",
        ]

        for file in key_files:
            file_path = frontend_dir / file
            if file_path.exists():
                print(f"✅ {file} exists")
            else:
                self.log_issue(f"Frontend file missing: {file}")

        # Check package.json
        try:
            with open(frontend_dir / "package.json", "r") as f:
                package_data = json.load(f)
            print(f"✅ Package.json valid: {package_data.get('name', 'Unknown')}")
        except Exception as e:
            self.log_issue(f"Package.json error: {e}")

        # Check .env file
        env_path = frontend_dir / ".env"
        if env_path.exists():
            try:
                with open(env_path, "r") as f:
                    env_content = f.read()
                if "VITE_API_URL" in env_content:
                    print("✅ .env has API URL")
                else:
                    self.log_issue(".env missing VITE_API_URL")
            except Exception as e:
                self.log_issue(f".env read error: {e}")

    def test_backend_start(self):
        print("\n=== BACKEND START TEST ===")

        venv_python = self.base_dir / ".venv" / "Scripts" / "python.exe"
        backend_file = self.base_dir / "working_backend_final.py"

        if not backend_file.exists():
            self.log_issue("Backend file missing for start test")
            return False

        try:
            # Try to start backend briefly
            process = subprocess.Popen(
                [str(venv_python), str(backend_file)],
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait a bit and then kill it
            import time

            time.sleep(3)
            process.terminate()

            stdout, stderr = process.communicate(timeout=5)

            if "Serving Flask app" in stdout or "running on" in stdout.lower():
                print("✅ Backend can start")
                return True
            else:
                self.log_issue(
                    f"Backend start failed. Stdout: {stdout[:200]}... Stderr: {stderr[:200]}..."
                )
                return False

        except Exception as e:
            self.log_issue(f"Backend start test failed: {e}")
            return False

    def test_frontend_dependencies(self):
        print("\n=== FRONTEND DEPENDENCIES TEST ===")

        frontend_dir = self.base_dir / "frontend"

        try:
            # Check if node_modules exists
            if (frontend_dir / "node_modules").exists():
                print("✅ node_modules exists")
            else:
                self.log_issue("node_modules missing - need to run npm install")

            # Try npm list to check for issues
            result = subprocess.run(
                ["npm", "list", "--depth=0"],
                cwd=str(frontend_dir),
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                print("✅ NPM dependencies OK")
            else:
                self.log_issue(f"NPM dependency issues: {result.stderr[:200]}")

        except Exception as e:
            self.log_issue(f"Frontend dependency check failed: {e}")

    def create_fixes(self):
        print("\n=== GENERATING FIXES ===")

        # Create a comprehensive fix script
        fix_script = f"""#!/usr/bin/env python3
'''Automated Fix Script for HireBahamas'''

import os
import subprocess
import sqlite3
import bcrypt
from pathlib import Path

def fix_database():
    print("Fixing database...")
    db_path = "hirebahamas.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop and recreate users table
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            user_type TEXT DEFAULT 'client',
            location TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create admin user
    password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
    cursor.execute('''
        INSERT INTO users (email, password_hash, first_name, last_name, user_type)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin@hirebahamas.com', password_hash, 'Admin', 'User', 'admin'))
    
    conn.commit()
    conn.close()
    print("✅ Database fixed")

def fix_frontend_env():
    print("Fixing frontend .env...")
    env_content = '''VITE_API_URL=http://127.0.0.1:8008
VITE_APP_NAME=HireBahamas
'''
    with open("frontend/.env", "w") as f:
        f.write(env_content)
    print("✅ Frontend .env fixed")

def install_dependencies():
    print("Installing Python dependencies...")
    python_exe = "{str(self.base_dir / '.venv' / 'Scripts' / 'python.exe')}"
    
    packages = ['flask', 'flask-cors', 'bcrypt', 'pyjwt', 'requests']
    for package in packages:
        subprocess.run([python_exe, "-m", "pip", "install", package], check=True)
    
    print("Installing frontend dependencies...")
    subprocess.run(["npm", "install"], cwd="frontend", check=True)
    print("✅ Dependencies installed")

if __name__ == "__main__":
    fix_database()
    fix_frontend_env()
    install_dependencies()
    print("\\n🎉 ALL FIXES APPLIED!")
"""

        with open(self.base_dir / "fix_all_issues.py", "w") as f:
            f.write(fix_script)

        self.log_fix("Created comprehensive fix script")

    def run_diagnosis(self):
        print("🔍 COMPREHENSIVE HIREBAHAMAS DIAGNOSTIC")
        print("=" * 60)

        self.check_python_environment()
        self.check_database()
        self.check_backend_files()
        self.check_frontend_files()
        self.test_backend_start()
        self.test_frontend_dependencies()

        print("\n" + "=" * 60)
        print(f"📊 DIAGNOSTIC COMPLETE")
        print(f"❌ Issues found: {len(self.issues)}")
        print(f"✅ Fixes available: {len(self.fixes)}")

        if self.issues:
            print("\n🚨 CRITICAL ISSUES TO FIX:")
            for i, issue in enumerate(self.issues, 1):
                print(f"{i}. {issue}")

        self.create_fixes()

        return len(self.issues) == 0


if __name__ == "__main__":
    diagnostic = SystemDiagnostic()
    success = diagnostic.run_diagnosis()

    if not success:
        print("\n🔧 Run the fix script: python fix_all_issues.py")
    else:
        print("\n✅ System appears healthy!")

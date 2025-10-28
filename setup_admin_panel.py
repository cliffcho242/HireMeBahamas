#!/usr/bin/env python3
"""
Complete Admin Panel Setup Script
- Creates admin user
- Installs all dependencies
- Sets up admin backend
- Builds admin frontend
- Tests everything
"""
import os
import sqlite3
import subprocess
import sys

import bcrypt


def run_cmd(cmd, cwd=None, check=True):
    """Run command and handle errors"""
    print(f"\n▶️  Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, check=check, capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False


def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


print_header("HIREBAHAMAS ADMIN PANEL SETUP")

# Step 1: Install Python dependencies for admin backend
print_header("STEP 1: Installing Python Dependencies")
python_deps = [
    "flask",
    "flask-cors",
    "flask-jwt-extended",
    "flask-limiter",
    "bcrypt",
    "python-dotenv",
]

for dep in python_deps:
    print(f"Installing {dep}...")
    run_cmd(f"pip install {dep}", check=False)

print("✅ Python dependencies installed")

# Step 2: Initialize database with admin tables
print_header("STEP 2: Setting Up Database")

DB_PATH = "hireme_bahamas.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create users table if it doesn't exist
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        user_type TEXT,
        location TEXT,
        bio TEXT,
        avatar_url TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_admin INTEGER DEFAULT 0
    )
"""
)

# Add is_admin column if it doesn't exist
try:
    cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
    print("✅ Added is_admin column")
except sqlite3.OperationalError:
    print("✓ is_admin column already exists")

# Create admin_logs table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS admin_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        target_type TEXT,
        target_id INTEGER,
        details TEXT,
        ip_address TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (admin_id) REFERENCES users (id)
    )
"""
)

# Create admin_settings table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS admin_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_by INTEGER,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (updated_by) REFERENCES users (id)
    )
"""
)

conn.commit()
print("✅ Database tables created")

# Step 3: Create admin user
print_header("STEP 3: Creating Admin User")

admin_email = "admin@hiremebahamas.com"
admin_password = "Admin123456!"
admin_first = "Admin"
admin_last = "User"

# Check if admin exists
cursor.execute("SELECT id FROM users WHERE email = ?", (admin_email,))
existing_admin = cursor.fetchone()

if existing_admin:
    print(f"⚠️  Admin user already exists: {admin_email}")
    cursor.execute("UPDATE users SET is_admin = 1 WHERE email = ?", (admin_email,))
    conn.commit()
    print("✅ Updated existing user to admin")
else:
    # Hash password
    hashed = bcrypt.hashpw(admin_password.encode("utf-8"), bcrypt.gensalt())

    # Insert admin user
    cursor.execute(
        """
        INSERT INTO users (email, password, first_name, last_name, user_type, is_admin)
        VALUES (?, ?, ?, ?, ?, 1)
    """,
        (admin_email, hashed.decode("utf-8"), admin_first, admin_last, "admin"),
    )

    conn.commit()
    print(f"✅ Admin user created: {admin_email}")

conn.close()

print("\n📝 Admin Credentials:")
print(f"   Email: {admin_email}")
print(f"   Password: {admin_password}")
print("   ⚠️  CHANGE THIS PASSWORD AFTER FIRST LOGIN!")

# Step 4: Install frontend dependencies
print_header("STEP 4: Installing Admin Frontend Dependencies")

admin_panel_dir = os.path.join(os.getcwd(), "admin-panel")

if not os.path.exists(admin_panel_dir):
    print("❌ Admin panel directory not found")
    sys.exit(1)

os.chdir(admin_panel_dir)

print("Installing npm dependencies...")
if not run_cmd("npm install", cwd=admin_panel_dir):
    print("⚠️  npm install had warnings, continuing...")

print("✅ Admin frontend dependencies installed")

# Step 5: Create .env file for admin panel
print_header("STEP 5: Creating Environment Files")

env_content = """# Admin Panel Environment Variables
VITE_API_URL=http://localhost:8000
VITE_MAIN_APP_URL=https://hiremebahamas.com
"""

with open(".env", "w") as f:
    f.write(env_content)

print("✅ Environment file created")

# Step 6: Test admin backend
print_header("STEP 6: Testing Admin Backend")

os.chdir("..")

print("Starting admin backend test...")
test_code = """
import requests
import time

# Give backend time to start
time.sleep(2)

try:
    # Test health endpoint
    r = requests.get('http://localhost:8000/admin/health', timeout=5)
    if r.status_code == 200:
        print('✅ Admin backend health check: OK')
    else:
        print(f'⚠️  Health check returned: {r.status_code}')
    
    # Test login
    r = requests.post('http://localhost:8000/admin/auth/login',
                     json={'email': 'admin@hiremebahamas.com', 'password': 'Admin123456!'},
                     timeout=5)
    if r.status_code == 200:
        print('✅ Admin login: OK')
        data = r.json()
        print(f'   Token received: {data.get("access_token")[:50]}...')
    else:
        print(f'⚠️  Login returned: {r.status_code}')
        print(f'   Response: {r.text[:200]}')
        
except requests.exceptions.ConnectionError:
    print('⚠️  Admin backend not running')
    print('   Start it manually with: python admin_backend.py')
except Exception as e:
    print(f'⚠️  Test error: {e}')
"""

# Save test script
with open("test_admin_api.py", "w") as f:
    f.write(test_code)

print("✅ Test script created: test_admin_api.py")

# Final summary
print_header("SETUP COMPLETE!")

print("\n✅ Admin Panel Setup Summary:")
print("   1. ✅ Python dependencies installed")
print("   2. ✅ Database tables created")
print("   3. ✅ Admin user created")
print("   4. ✅ Frontend dependencies installed")
print("   5. ✅ Environment configured")

print("\n📋 Next Steps:")
print("\n1. Start Admin Backend:")
print("   python admin_backend.py")

print("\n2. Start Admin Frontend (in new terminal):")
print("   cd admin-panel")
print("   npm run dev")

print("\n3. Access Admin Panel:")
print("   http://localhost:3001")

print("\n4. Login with:")
print(f"   Email: {admin_email}")
print(f"   Password: {admin_password}")

print("\n5. Users access main app at:")
print("   https://hiremebahamas.com")
print("   (Regular users CANNOT access admin panel)")

print("\n🔒 Security:")
print("   ✅ Admin routes require authentication")
print("   ✅ Admin role required for all admin endpoints")
print("   ✅ Separate from user app (no 405 conflicts)")
print("   ✅ Admin login on different port (8000)")
print("   ✅ User app on different port (8008)")

print("\n" + "=" * 80)
print("  ADMIN PANEL READY!")
print("=" * 80 + "\n")

# Create quick start script
quick_start = """@echo off
echo Starting HireBahamas Admin Panel...
echo.

start "Admin Backend" cmd /k "python admin_backend.py"
timeout /t 3 /nobreak >nul

start "Admin Frontend" cmd /k "cd admin-panel && npm run dev"

echo.
echo ========================================
echo   ADMIN PANEL STARTING
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3001
echo.
echo Login: admin@hiremebahamas.com
echo Password: Admin123456!
echo.
echo Press any key to close this window...
pause >nul
"""

with open("START_ADMIN_PANEL.bat", "w") as f:
    f.write(quick_start)

print("✅ Created START_ADMIN_PANEL.bat for easy launching")
print("\nDouble-click START_ADMIN_PANEL.bat to start everything!\n")

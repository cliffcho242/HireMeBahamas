"""
Railway Backend Troubleshooting & Auto-Fix Script
Diagnoses and attempts to fix Railway deployment issues
"""

import subprocess
import sys

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_git_status():
    """Ensure all changes are committed"""
    print_section("1. Checking Git Status")
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            print("⚠️ You have uncommitted changes:")
            print(result.stdout)
            print("\nCommitting changes...")
            subprocess.run(["git", "add", "."])
            subprocess.run([
                "git", "commit", "-m",
                "Auto-commit: Railway deployment troubleshooting"
            ])
            subprocess.run(["git", "push", "origin", "main"])
            print("✅ Changes committed and pushed")
        else:
            print("✅ Git status clean")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def display_current_config():
    """Show current configuration files"""
    print_section("2. Current Configuration")
    
    configs = {
        "railway.json": None,
        "Procfile": None,
        "nixpacks.toml": "[start] section"
    }
    
    try:
        with open("railway.json", "r") as f:
            import json
            data = json.load(f)
            print("\n📄 railway.json:")
            print(f"   Start Command: {data.get('deploy', {}).get('startCommand', 'Not set')}")
            configs["railway.json"] = data.get('deploy', {}).get('startCommand')
    except Exception as e:
        print(f"❌ railway.json error: {e}")
    
    try:
        with open("Procfile", "r") as f:
            content = f.read().strip()
            print(f"\n📄 Procfile:")
            print(f"   {content}")
            configs["Procfile"] = content
    except Exception as e:
        print(f"❌ Procfile error: {e}")
    
    try:
        with open("nixpacks.toml", "r") as f:
            content = f.read()
            if "[start]" in content:
                start_section = content.split("[start]")[1].split("[")[0]
                print(f"\n📄 nixpacks.toml [start]:")
                print(f"   {start_section.strip()}")
                configs["nixpacks.toml"] = start_section
    except Exception as e:
        print(f"❌ nixpacks.toml error: {e}")
    
    return configs

def check_wsgi_application():
    """Verify WSGI application is correctly defined"""
    print_section("3. Verifying WSGI Application")
    
    try:
        with open("final_backend.py", "r") as f:
            content = f.read()
            
        has_app = "app = Flask(__name__)" in content
        has_application = "application = app" in content
        has_migration = "migrate_user_columns()" in content
        
        print(f"   Flask app defined: {'✅' if has_app else '❌'}")
        print(f"   WSGI application alias: {'✅' if has_application else '❌'}")
        print(f"   Migration function: {'✅' if has_migration else '❌'}")
        
        if not has_application:
            print("\n⚠️ CRITICAL: 'application = app' not found!")
            print("   This is required for gunicorn")
            
        return has_app and has_application
        
    except Exception as e:
        print(f"❌ Error reading final_backend.py: {e}")
        return False

def suggest_fixes():
    """Provide actionable fix suggestions"""
    print_section("4. Recommended Actions")
    
    print("""
🔧 RAILWAY DASHBOARD CHECKS:

1. Go to: https://railway.app/dashboard
2. Select your backend service
3. Check these settings:

   Settings Tab:
   ✓ Public Networking: ENABLED
   ✓ Domain Generation: ENABLED  
   ✓ Copy the public domain URL

   Deployments Tab:
   ✓ Latest deployment should be "Active" (green)
   ✓ Click on deployment to see build logs
   ✓ Look for "Initializing Flask app..." in logs
   
   Variables Tab:
   ✓ Check if PORT is set (should be 8080 or auto)
   
4. If deployment is "Failed" or "Crashed":
   - Click "Redeploy" button
   - Wait 3-5 minutes for build
   
5. If still not working:
   - Click "..." menu → "Restart"
   - Or try "Redeploy from Source"

🔍 LOCAL TESTING:

Run these commands to verify configuration:
   
   python -c "import final_backend; print('App loads:', final_backend.app)"
   python find_railway_backend.py

📝 CONFIGURATION FILES:

All three files (railway.json, Procfile, nixpacks.toml) should use:
   final_backend:application

NOT:
   final_backend:app

🚀 FORCE REDEPLOY:

If Railway is cached, try:
   
   1. Make a small change (add comment to final_backend.py)
   2. git add . && git commit -m "Force rebuild" && git push
   3. Wait for Railway to rebuild (watch logs)
   
""")

def main():
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║   RAILWAY BACKEND TROUBLESHOOTING & AUTO-FIX                   ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Run checks
    check_git_status()
    configs = display_current_config()
    wsgi_ok = check_wsgi_application()
    
    # Provide fixes
    suggest_fixes()
    
    print_section("Summary")
    
    if wsgi_ok:
        print("✅ Code configuration looks correct")
        print("⚠️  Issue is likely in Railway dashboard settings")
        print("\n👉 Next step: Check Railway dashboard (see instructions above)")
    else:
        print("❌ Code configuration has issues")
        print("\n👉 Next step: Fix code issues first, then redeploy")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

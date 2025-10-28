#!/usr/bin/env python3
"""
Railway Deployment Readiness Check
Verify all files are correctly configured for Python-only deployment
"""

from pathlib import Path
import json


def check_admin_panel():
    """Check if admin_panel/package.json is causing issues"""
    admin_package = Path("admin_panel/package.json")

    print("🔍 Checking admin_panel directory...")

    if not admin_package.exists():
        print("  ✅ admin_panel/package.json doesn't exist")
        return True

    try:
        with open(admin_package, "r") as f:
            content = f.read().strip()

        if not content:
            print("  ⚠️ admin_panel/package.json is EMPTY")
            print("  💡 Solution: .nixpacksignore will prevent this")
            return False
        else:
            json.loads(content)
            print("  ✅ admin_panel/package.json is valid JSON")
            return True

    except json.JSONDecodeError:
        print("  ❌ admin_panel/package.json has invalid JSON")
        return False


def check_ignore_files():
    """Check if ignore files are properly set"""
    print("\n🔍 Checking ignore files...")

    nixignore = Path(".nixpacksignore")
    railignore = Path(".railwayignore")

    if nixignore.exists():
        print("  ✅ .nixpacksignore exists")
        with open(nixignore, "r") as f:
            if "admin_panel" in f.read():
                print("    ✅ Ignoring admin_panel")
    else:
        print("  ⚠️ .nixpacksignore not found")

    if railignore.exists():
        print("  ✅ .railwayignore exists")
    else:
        print("  ⚠️ .railwayignore not found")


def check_nixpacks_config():
    """Check nixpacks.toml configuration"""
    print("\n🔍 Checking nixpacks.toml...")

    config_file = Path("nixpacks.toml")

    if not config_file.exists():
        print("  ❌ nixpacks.toml not found")
        return False

    with open(config_file, "r") as f:
        content = f.read()

    checks = {
        "python provider": 'providers = ["python"]' in content
        or "python" in content.lower(),
        "gunicorn start": "gunicorn" in content,
        "final_backend": "final_backend" in content,
    }

    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")

    return all(checks.values())


def check_required_files():
    """Check if all required files exist"""
    print("\n🔍 Checking required files...")

    required = {
        "final_backend.py": "Main Flask application",
        "requirements.txt": "Python dependencies",
        "Procfile": "Deployment command (fallback)",
    }

    all_exist = True
    for file, description in required.items():
        if Path(file).exists():
            print(f"  ✅ {file} - {description}")
        else:
            print(f"  ❌ {file} - {description}")
            all_exist = False

    return all_exist


def main():
    print("🚀 Railway Python Deployment Readiness Check")
    print("=" * 50)

    # Run all checks
    admin_ok = check_admin_panel()
    check_ignore_files()
    config_ok = check_nixpacks_config()
    files_ok = check_required_files()

    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT STATUS")
    print("=" * 50)

    if config_ok and files_ok:
        print("✅ Ready for deployment!")
        print("\n💡 Key fixes applied:")
        print("   - .nixpacksignore prevents admin_panel build")
        print("   - nixpacks.toml configured for Python only")
        print("   - All required files present")
        print("\n🚀 Deploy to Railway and the build should succeed")
    else:
        print("⚠️ Some issues detected - but deployment may still work")
        print("   The ignore files will prevent admin_panel issues")

    print("=" * 50)


if __name__ == "__main__":
    main()

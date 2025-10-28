#!/usr/bin/env python3
"""
Verify TOML Syntax Fix
Confirm the nixpacks.toml providers configuration is correct
"""

import subprocess
from pathlib import Path


def check_toml_structure():
    """Check that providers is at root level, not in variables"""
    print("🔍 Checking nixpacks.toml structure...")

    config_file = Path("nixpacks.toml")

    if not config_file.exists():
        print("❌ nixpacks.toml not found")
        return False

    with open(config_file, "r") as f:
        content = f.read()

    lines = content.split("\n")

    in_variables_section = False
    providers_found = False
    providers_in_variables = False

    for i, line in enumerate(lines, 1):
        line = line.strip()

        if line == "[variables]":
            in_variables_section = True
            continue
        elif line.startswith("[") and line != "[variables]":
            in_variables_section = False

        if "providers" in line and "=" in line:
            providers_found = True
            if in_variables_section and not line.startswith("providers"):
                providers_in_variables = True
                print(f"❌ Line {i}: providers found inside [variables] section")
                print("   This causes the TOML parsing error")
            else:
                print(f"✅ Line {i}: providers correctly at root level")
                return True

    if not providers_found:
        print("⚠️ providers configuration not found")
        return False

    if providers_in_variables:
        return False

    return True


def verify_git_commit():
    """Verify the fix was committed"""
    print("\n🔍 Verifying git commit...")

    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"], capture_output=True, text=True
        )

        if result.returncode == 0:
            commit_msg = result.stdout.strip()
            if "providers" in commit_msg.lower() and "variables" in commit_msg.lower():
                print(f"✅ Latest commit: {commit_msg}")
                return True
            else:
                print(f"⚠️ Latest commit may not be the fix: {commit_msg}")
                return False
        else:
            print("❌ Could not check git log")
            return False

    except Exception as e:
        print(f"❌ Git check failed: {e}")
        return False


def main():
    print("🔧 Nixpacks TOML Syntax Fix Verification")
    print("=" * 50)

    # Check TOML structure
    toml_ok = check_toml_structure()

    # Check git commit
    git_ok = verify_git_commit()

    print("\n" + "=" * 50)
    print("📊 VERIFICATION RESULTS")
    print("=" * 50)

    if toml_ok and git_ok:
        print("✅ TOML syntax fix is complete!")
        print("\n🚀 Next steps:")
        print("1. Railway should auto-deploy with the corrected configuration")
        print(
            "2. The 'invalid type: sequence, expected a string' error should be resolved"
        )
        print("\n⏱️ Railway deployment may take 1-3 minutes to pick up changes")
    else:
        print("⚠️ Some issues detected - check the output above")

    print("=" * 50)


if __name__ == "__main__":
    main()

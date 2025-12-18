#!/usr/bin/env python3
"""Simple TOML syntax checker for nixpacks.toml"""


def check_toml_syntax():
    """Check basic TOML syntax"""
    print("🔍 Checking nixpacks.toml syntax...")

    try:
        with open("nixpacks.toml", "r") as f:
            lines = f.readlines()

        print(f"✅ File readable ({len(lines)} lines)")

        # Check for common TOML issues
        issues = []
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Check for unmatched quotes
            if line.count('"') % 2 != 0:
                issues.append(f"Line {i}: Unmatched quotes")
            if line.count("'") % 2 != 0:
                issues.append(f"Line {i}: Unmatched single quotes")

            # Check for bracket balance in sections
            if line.startswith("[") and not line.endswith("]"):
                issues.append(f"Line {i}: Unmatched bracket in section")

        if issues:
            print("❌ Syntax issues found:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("✅ Basic syntax looks good")
            return True

    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False


def show_config():
    """Show the current configuration"""
    print("\n📋 Current nixpacks.toml:")
    try:
        with open("nixpacks.toml", "r") as f:
            content = f.read()
        print(content)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if check_toml_syntax():
        show_config()
        print("✅ Ready for Render deployment!")
    else:
        print("❌ Fix syntax errors before deploying")

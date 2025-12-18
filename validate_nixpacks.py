#!/usr/bin/env python3
"""Validate nixpacks.toml syntax"""

import toml
from pathlib import Path


def validate_nixpacks():
    """Validate the nixpacks.toml file"""
    nixpacks_file = Path("nixpacks.toml")

    if not nixpacks_file.exists():
        print("❌ nixpacks.toml not found")
        return False

    try:
        with open(nixpacks_file, "r") as f:
            config = toml.load(f)

        print("✅ nixpacks.toml syntax is valid")
        print("📋 Configuration:")

        # Display config sections
        for section, content in config.items():
            print(f"  [{section}]")
            if isinstance(content, dict):
                for key, value in content.items():
                    print(f"    {key} = {value}")
            else:
                print(f"    {content}")
            print()

        return True

    except toml.TomlDecodeError as e:
        print(f"❌ TOML syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False


if __name__ == "__main__":
    print("🔍 Validating nixpacks.toml...")
    if validate_nixpacks():
        print("✅ Ready for Render deployment!")
    else:
        print("❌ Fix syntax errors before deploying")

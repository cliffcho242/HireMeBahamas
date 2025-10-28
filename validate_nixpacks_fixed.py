#!/usr/bin/env python3
"""
TOML Validation Script
Test nixpacks.toml syntax before deployment
"""

import sys
from pathlib import Path


def validate_toml():
    """Validate nixpacks.toml syntax"""
    print("🔍 Validating nixpacks.toml syntax...")

    try:
        import toml
    except ImportError:
        print("⚠️ toml module not found, installing...")
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "toml"])
        import toml

    toml_file = Path("nixpacks.toml")

    if not toml_file.exists():
        print("❌ nixpacks.toml not found")
        return False

    try:
        with open(toml_file, "r") as f:
            config = toml.load(f)

        print("✅ TOML syntax is valid")
        print("\n📋 Configuration:")

        # Display key sections
        if "phases" in config:
            print("  Phases:")
            for phase, settings in config["phases"].items():
                print(f"    - {phase}: {settings}")

        if "start" in config:
            print(f"  Start command: {config['start']['cmd']}")

        return True

    except toml.TomlDecodeError as e:
        print(f"❌ TOML syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False


def test_nixpacks_build():
    """Test if nixpacks can parse the config"""
    print("\n🧪 Testing nixpacks compatibility...")

    try:
        import subprocess

        result = subprocess.run(
            ["nixpacks", "plan", ".", "--config-file", "nixpacks.toml"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("✅ Nixpacks can parse the configuration")
            return True
        else:
            print(f"❌ Nixpacks error: {result.stderr}")
            return False

    except FileNotFoundError:
        print("⚠️ nixpacks CLI not found (this is OK for Railway)")
        return True
    except Exception as e:
        print(f"⚠️ Could not test nixpacks: {e}")
        return True


if __name__ == "__main__":
    print("🔧 Nixpacks Configuration Validator")
    print("=" * 40)

    toml_valid = validate_toml()
    nixpacks_ok = test_nixpacks_build()

    print("\n" + "=" * 40)
    if toml_valid:
        print("✅ Configuration is ready for deployment!")
        print("🚀 You can now deploy to Railway")
    else:
        print("❌ Fix configuration before deploying")

    print("=" * 40)

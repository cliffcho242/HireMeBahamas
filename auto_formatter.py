#!/usr/bin/env python3
"""
Automated Code Formatter
This script formats all code files in the workspace using appropriate formatters
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


class CodeFormatter:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.stats = {"formatted": 0, "errors": 0, "skipped": 0}

    def run_command(self, cmd: List[str], cwd: Path = None) -> tuple:
        """Run a command and return success status and output"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.workspace_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def format_python_files(self) -> None:
        """Format Python files using Black"""
        print("🐍 Formatting Python files with Black...")

        python_files = list(self.workspace_root.rglob("*.py"))
        if not python_files:
            print("   No Python files found")
            return

        # Try Black first
        success, stdout, stderr = self.run_command(
            ["python", "-m", "black", "--line-length", "88", "--quiet", "."]
        )

        if success:
            print(f"   ✅ Formatted {len(python_files)} Python files with Black")
            self.stats["formatted"] += len(python_files)
        else:
            print(f"   ⚠️ Black failed, trying autopep8...")
            # Fallback to autopep8
            for file in python_files:
                success, _, _ = self.run_command(
                    [
                        "python",
                        "-m",
                        "autopep8",
                        "--in-place",
                        "--aggressive",
                        "--aggressive",
                        "--max-line-length",
                        "88",
                        str(file),
                    ]
                )
                if success:
                    self.stats["formatted"] += 1
                else:
                    self.stats["errors"] += 1

    def format_js_ts_files(self) -> None:
        """Format JavaScript/TypeScript files using Prettier"""
        print("📝 Formatting JS/TS files with Prettier...")

        patterns = [
            "*.js",
            "*.ts",
            "*.jsx",
            "*.tsx",
            "*.json",
            "*.css",
            "*.html",
            "*.md",
        ]
        files = []
        for pattern in patterns:
            files.extend(self.workspace_root.rglob(pattern))

        if not files:
            print("   No JS/TS files found")
            return

        # Check if prettier is available
        success, _, _ = self.run_command(["npx", "prettier", "--version"])
        if not success:
            print("   ⚠️ Prettier not available, installing...")
            install_success, _, _ = self.run_command(
                ["npm", "install", "-g", "prettier"]
            )
            if not install_success:
                print("   ❌ Failed to install Prettier")
                self.stats["errors"] += len(files)
                return

        # Format files
        success, stdout, stderr = self.run_command(
            [
                "npx",
                "prettier",
                "--write",
                "--config",
                ".prettierrc",
                "**/*.{js,ts,jsx,tsx,json,css,html,md}",
            ]
        )

        if success:
            print(f"   ✅ Formatted files with Prettier")
            self.stats["formatted"] += len(files)
        else:
            print(f"   ❌ Prettier failed: {stderr}")
            self.stats["errors"] += len(files)

    def format_powershell_files(self) -> None:
        """Format PowerShell files"""
        print("💻 Checking PowerShell files...")

        ps_files = list(self.workspace_root.rglob("*.ps1"))
        if not ps_files:
            print("   No PowerShell files found")
            return

        # PowerShell formatting is typically done in VS Code
        print(f"   📝 Found {len(ps_files)} PowerShell files")
        print("   💡 Use VS Code's PowerShell extension for formatting")
        self.stats["skipped"] += len(ps_files)

    def organize_imports(self) -> None:
        """Organize imports in Python files"""
        print("📚 Organizing Python imports with isort...")

        success, _, _ = self.run_command(["python", "-m", "isort", "--check-only", "."])
        if success:
            print("   ✅ Imports are already organized")
            return

        success, stdout, stderr = self.run_command(
            ["python", "-m", "isort", "--profile", "black", "--line-length", "88", "."]
        )

        if success:
            print("   ✅ Organized Python imports")
        else:
            print("   ⚠️ isort not available, skipping import organization")

    def run_eslint_fix(self) -> None:
        """Run ESLint with --fix for JavaScript/TypeScript files"""
        print("🔧 Running ESLint fixes...")

        # Check if we're in a frontend directory or have eslint config
        eslint_configs = [
            ".eslintrc.js",
            ".eslintrc.json",
            ".eslintrc.yml",
            ".eslintrc.yaml",
            "eslint.config.js",
        ]

        has_eslint_config = any(
            (self.workspace_root / config).exists() for config in eslint_configs
        )

        frontend_dir = self.workspace_root / "frontend"
        if frontend_dir.exists():
            success, _, _ = self.run_command(
                ["npx", "eslint", "--fix", "**/*.{js,ts,jsx,tsx}"], cwd=frontend_dir
            )

            if success:
                print("   ✅ Fixed ESLint issues in frontend")
            else:
                print("   ⚠️ ESLint fix completed with warnings")
        else:
            print("   📝 No ESLint configuration found")

    def format_all(self) -> None:
        """Format all supported file types"""
        print("🚀 Starting automated code formatting...")
        print("=" * 50)

        # Format different file types
        self.format_python_files()
        self.format_js_ts_files()
        self.format_powershell_files()
        self.organize_imports()
        self.run_eslint_fix()

        # Print summary
        print("\n" + "=" * 50)
        print("📊 FORMATTING SUMMARY")
        print("=" * 50)
        print(f"✅ Files formatted: {self.stats['formatted']}")
        print(f"⚠️ Files skipped: {self.stats['skipped']}")
        print(f"❌ Errors: {self.stats['errors']}")
        print("=" * 50)

        if self.stats["errors"] == 0:
            print("🎉 All formatting completed successfully!")
        else:
            print("⚠️ Some files had formatting issues. Check the output above.")


def main():
    """Main function"""
    if len(sys.argv) > 1:
        workspace_root = sys.argv[1]
    else:
        workspace_root = "."

    formatter = CodeFormatter(workspace_root)
    formatter.format_all()


if __name__ == "__main__":
    main()

# Format on Save Configuration
# This file contains all the formatter configurations

## Installed Extensions:
# ✅ Prettier - Code formatter (esbenp.prettier-vscode)
# ✅ Black Formatter (ms-python.black-formatter) 
# ✅ autopep8 (ms-python.autopep8)
# ✅ ESLint (dbaeumer.vscode-eslint)

## Configuration Files:
# - .prettierrc - Prettier configuration
# - .prettierignore - Files to ignore from Prettier
# - pyproject.toml - Python formatting configuration
# - .vscode/settings.json - VS Code formatter settings

## Supported File Types:
# Python (.py) - Black formatter + isort
# JavaScript (.js) - Prettier + ESLint
# TypeScript (.ts, .tsx) - Prettier + ESLint  
# JSON (.json) - Prettier
# CSS (.css, .scss) - Prettier
# HTML (.html) - Prettier
# Markdown (.md) - Prettier

## Keyboard Shortcuts:
# Ctrl+Shift+F - Format entire workspace
# Ctrl+Alt+F - Format current document
# Ctrl+Shift+Alt+F - Format selection
# Ctrl+Shift+O - Organize imports

## VS Code Tasks:
# "Format All Code" - Formats all files in workspace
# "Format Python Files Only" - Python only
# "Format Frontend Files" - JS/TS only
# "Fix ESLint Issues" - ESLint fixes

## PowerShell Commands:
# .\simple_formatter.ps1 - Run complete formatting
# .\auto_formatter.ps1 -PythonOnly - Python only formatting

## Python Commands:
# python auto_formatter.py - Run Python formatter script
# python -m black . - Format with Black
# python -m isort . - Organize imports

## npm Commands (in frontend folder):
# npx prettier --write "src/**/*" - Format frontend
# npx eslint --fix "src/**/*" - Fix ESLint issues

## Automatic Formatting:
# ✅ Format on Save - Enabled for all file types
# ✅ Format on Paste - Enabled
# ✅ Format on Type - Enabled
# ✅ Auto fix ESLint issues on save
# ✅ Auto organize imports on save
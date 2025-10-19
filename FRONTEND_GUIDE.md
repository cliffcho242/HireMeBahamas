# Frontend Development Guide

## Problem Solved

The npm error "Could not read package.json" occurred because npm was being run from the wrong directory.

## Solution

The `package.json` file is located in the `frontend/` subdirectory, not in the root directory.

## How to Run Frontend Commands

### Option 1: Use the Automated Script (Recommended)

```bash
# From the HireBahamas root directory
python automated_frontend_fix.py
```

### Option 2: Use the Batch File

```bash
# From the HireBahamas root directory
start_frontend.bat
```

### Option 3: Manual Commands

```bash
# Change to frontend directory first
cd frontend
npm install
npm run dev
```

### Option 4: Use Root Package.json Scripts

```bash
# From the HireBahamas root directory
npm run dev          # Runs frontend dev server
npm run install-frontend  # Installs frontend dependencies
```

## Directory Structure

```text
HireBahamas/
├── package.json          # Root package.json (convenience scripts)
├── frontend/
│   ├── package.json      # Actual frontend package.json
│   ├── src/
│   └── ...
└── ...
```

## Important Notes

- Always run npm commands from the `frontend/` directory, OR
- Use the automated scripts that handle directory navigation automatically
- The root `package.json` is just for convenience and redirects to the frontend directory

## Quick Start

```bash
# One command to rule them all
python automated_frontend_fix.py AUTOMATE
```

This will check Node.js, install dependencies, and start both frontend and backend servers.
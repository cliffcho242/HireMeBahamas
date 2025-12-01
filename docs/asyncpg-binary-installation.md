# asyncpg Binary Installation Fix

## Problem
When asyncpg was installed from source in CI/CD workflows, the C compiler generated a warning:
```
asyncpg/pgproto/pgproto.c:23886:18: warning: '__pyx_f_7asyncpg_7pgproto_7pgproto_json_encode' defined but not used [-Wunused-function]
```

This warning occurred because:
1. Workflows installed `build-essential`, `gcc`, `libpq-dev`, and `python3-dev`
2. These dependencies enabled asyncpg to be compiled from source
3. The Cython-generated C code contained an unused function that triggered the warning

## Solution
Force pip to use only pre-built binary wheels (not source distributions) by:
1. Adding `--only-binary=:all:` flag to all `pip install` commands
2. Removing unnecessary build dependencies that enabled source compilation

## Changes Made

### Affected Workflows
- `.github/workflows/ci.yml`
- `.github/workflows/dependency-check.yml`
- `.github/workflows/dependency-updates.yml`
- `.github/workflows/frogbot-pr-scan.yml`
- `.github/workflows/frogbot-scan-and-fix.yml`

### Before
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y build-essential libpq-dev python3-dev

- name: Install dependencies
  run: |
    pip install -r requirements.txt
```

### After
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y libjpeg-dev libpng-dev libwebp-dev zlib1g-dev

- name: Install dependencies
  run: |
    pip install --only-binary=:all: -r requirements.txt
```

## Benefits
1. **No compilation warnings**: asyncpg installs from pre-built wheels
2. **Faster installation**: Binary wheels install ~10x faster than source builds
3. **Smaller attack surface**: Fewer build tools installed = reduced security risk
4. **Simpler dependencies**: No need for C compiler, libpq-dev, or python3-dev

## Notes
- Image processing libraries (libjpeg-dev, libpng-dev, etc.) are kept for Pillow
- All modern Python packages provide binary wheels for Linux x86_64
- The `--only-binary=:all:` flag is documented in requirements.txt

## Testing
Verified that:
- asyncpg 0.29.0 installs without compilation
- All packages in requirements.txt install from binary wheels
- YAML syntax is valid for all modified workflows

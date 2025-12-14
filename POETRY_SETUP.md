# Poetry Dependency Management Setup

## Overview

HireMeBahamas now uses [Poetry](https://python-poetry.org/) for dependency management. Poetry provides:
- Deterministic dependency resolution
- Easy dependency updates
- Separate development and production dependencies
- Automatic virtual environment management

## Installation

### Install Poetry

```bash
pip install poetry
```

Or using the official installer:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## Usage

### Install Dependencies

Install all dependencies from `poetry.lock`:
```bash
poetry install
```

Install without development dependencies:
```bash
poetry install --no-dev
```

### Add New Dependencies

Add a production dependency:
```bash
poetry add package-name
```

Add a development dependency:
```bash
poetry add --group dev package-name
```

### Update Dependencies

Update all dependencies:
```bash
poetry update
```

Update a specific dependency:
```bash
poetry update package-name
```

### Run Commands

Run Python with Poetry environment:
```bash
poetry run python script.py
```

Run gunicorn:
```bash
poetry run gunicorn app:application --config gunicorn.conf.py
```

Activate the virtual environment:
```bash
poetry shell
```

### Show Dependencies

Show all installed packages:
```bash
poetry show
```

Show details of a specific package:
```bash
poetry show package-name
```

## Current Configuration

The project includes:
- **Python**: ^3.11 (compatible with 3.11+)
- **Gunicorn**: ^21.2.0 (WSGI HTTP Server for production)
- All existing dependencies from requirements.txt

See `pyproject.toml` for the complete dependency list.

## Deployment

### Railway Deployment

Railway automatically detects `pyproject.toml` and `poetry.lock`. If you need to use pip instead, you can still use the existing `requirements.txt` file.

### Render Deployment

Render recommends Poetry for Python projects. The build command should be:
```bash
poetry install
```

And the start command:
```bash
poetry run gunicorn final_backend_postgresql:application --config gunicorn.conf.py
```

### Vercel Deployment

For Vercel serverless functions, you may need to keep `requirements.txt` for compatibility. You can generate it from Poetry:
```bash
# Install the export plugin
poetry self add poetry-plugin-export

# Export dependencies
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Troubleshooting

### Poetry not found after installation
Add Poetry to your PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Lock file out of sync
Regenerate the lock file:
```bash
poetry lock --no-update
```

### Install fails
Clear Poetry cache and try again:
```bash
poetry cache clear pypi --all
poetry install
```

## Migration Notes

This project was migrated from pip to Poetry. The original `requirements.txt` is preserved for compatibility with deployment platforms that don't yet support Poetry.

### Files Changed
- `pyproject.toml`: Converted to Poetry format
- `poetry.lock`: Generated dependency lock file (new)
- `requirements.txt`: Preserved for backward compatibility

### Benefits of Poetry
1. **Deterministic builds**: `poetry.lock` ensures everyone uses the same dependency versions
2. **Dependency resolution**: Poetry resolves conflicts automatically
3. **Easier updates**: Update dependencies with a single command
4. **Better security**: Easy to audit and update vulnerable dependencies

# System Dependencies Guide

## Overview
This document explains how to properly add and manage system dependencies in the HireMeBahamas project, particularly in GitHub Actions workflows.

## Current System Dependencies

### For All Workflows
The following base dependencies are installed in all workflows:
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y build-essential
```

### For Python/Backend Workflows
Python-related workflows require additional dependencies:
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y build-essential libpq-dev python3-dev
```

### For Comprehensive Dependency Scanning (Frogbot)
The Frogbot workflow includes a comprehensive list of dependencies:
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends \
      build-essential \
      pkg-config \
      postgresql-client \
      libpq-dev \
      python3-dev \
      libssl-dev \
      libffi-dev \
      libjpeg-dev \
      libpng-dev \
      zlib1g-dev \
      libevent-dev \
      libxml2-dev \
      libxslt1-dev
```

## How to Add New System Dependencies

### Step 1: Verify Package Availability
Before adding a system dependency, verify it exists in Ubuntu repositories:
```bash
apt-cache search <package-name>
apt-cache show <package-name>
```

### Step 2: Add to Appropriate Workflow(s)
Add the package to the installation command in the relevant workflow file:
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y \
      build-essential \
      <your-new-package>
```

### Step 3: Test the Workflow
- Create a test branch
- Push changes to trigger the workflow
- Verify the package installs successfully

## Common Dependencies by Use Case

### Database Support
- PostgreSQL: `libpq-dev`, `postgresql-client`
- SQLite: `libsqlite3-dev`
- MySQL: `libmysqlclient-dev`

### Image Processing
- JPEG: `libjpeg-dev`
- PNG: `libpng-dev`
- General: `zlib1g-dev`

### Cryptography/Security
- OpenSSL: `libssl-dev`
- FFI (Foreign Function Interface): `libffi-dev`

### Build Tools
- Essential: `build-essential` (includes gcc, g++, make)
- Package config: `pkg-config`

### Python-specific
- Python headers: `python3-dev`
- Event handling: `libevent-dev`

## Note on Non-Standard Packages

If you need to install a package that is **not** available in standard Ubuntu repositories:

1. **Use PPA (Personal Package Archive):**
   ```yaml
   - name: Add PPA and install package
     run: |
       sudo add-apt-repository ppa:repository/name
       sudo apt-get update
       sudo apt-get install -y <package-name>
   ```

2. **Download and install .deb files:**
   ```yaml
   - name: Install custom package
     run: |
       wget <url-to-deb-file>
       sudo dpkg -i <package-name>.deb
       sudo apt-get install -f  # Fix dependencies
   ```

3. **Use Docker containers:**
   Consider using Docker if the package has complex dependencies or is not available for Ubuntu.

## Invalid Package Example

**❌ Invalid:** `sudo apt-get install teamhood`

"teamhood" is not a standard Ubuntu package. Teamhood is actually a project management and collaboration SaaS (Software as a Service) tool available at teamhood.com, not a system package that can be installed via apt-get.

If you encountered this in a requirement:
1. Verify the correct package name - it may be a typo
2. Check if it's referring to a different package (e.g., "thread-related" libraries)
3. Determine if it requires a custom repository or installation method
4. If you need project management tools, consider alternatives like:
   - OpenProject
   - Taiga
   - Redmine
   - GitLab (for project management features)
5. Document the proper installation method for the actual intended package

## Best Practices

1. **Always update before install:** Include `sudo apt-get update` before installing packages
2. **Use specific package names:** Avoid wildcards or ambiguous names
3. **Document why packages are needed:** Comment complex dependencies
4. **Keep workflows consistent:** Use similar dependency lists across related workflows
5. **Use `--no-install-recommends`:** For faster builds with only required packages
6. **Test locally:** Use Docker or VM to test package installations before committing

## Troubleshooting

### Package Not Found
```
E: Unable to locate package <name>
```
**Solution:** Verify package name with `apt-cache search`, check Ubuntu version compatibility, or find alternative package.

### Dependency Conflicts
**Solution:** Use `apt-get install -f` to fix broken dependencies, or specify compatible versions.

### Build Failures
**Solution:** Check if all required development headers are installed (packages ending in `-dev`).

## References

- [Ubuntu Package Management](https://help.ubuntu.com/community/AptGet/Howto)
- [GitHub Actions - Ubuntu Runner](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners)
- [HireMeBahamas Copilot Instructions](../.github/copilot-instructions.md)

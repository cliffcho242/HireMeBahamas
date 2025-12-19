# GitHub Copilot Instructions for HireMeBahamas

## Project Overview
HireMeBahamas is a job platform application built with:
- **Frontend**: React (Vite)
- **Backend**: Flask/Python
- **Database**: PostgreSQL
- **Deployment**: Render (backend), Vercel (frontend)

## Development Guidelines

### System Dependencies
All GitHub Actions workflows should include system dependency installation:
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y build-essential
```

For Python backends, also include:
```yaml
sudo apt-get install -y libpq-dev python3-dev
```

### Runtime Directories
When running tests or builds that may generate logs, ensure runtime directories exist:
```yaml
- name: Create runtime directories
  run: |
    mkdir -p /tmp/runtime-logs
    touch /tmp/runtime-logs/.gitkeep
```

### Error Handling
- For truly optional commands, use `|| true` instead of `|| echo "..."` to avoid masking failures
- Use conditional execution with `if` statements for better control flow
- For artifact uploads, make them conditional: `if: always()` or check file existence first
- Never fail CI/CD pipelines for missing optional artifacts
- Consider using `continue-on-error: true` for non-critical jobs

Example of safe optional command:
```yaml
- name: Optional cleanup
  run: rm -rf /tmp/cache || true
  
- name: Conditional artifact upload
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: logs
    path: /tmp/logs
    if-no-files-found: ignore
```

### Testing
- Backend tests: `python -m pytest backend/test_app.py`
- Frontend build: `cd frontend && npm run build`
- Frontend lint: `cd frontend && npm run lint`

### Security
- Never commit secrets to the repository
- Use GitHub Secrets for sensitive data
- Review dependencies for vulnerabilities using Frogbot

## Workflow Best Practices
1. Always install system dependencies before installing project dependencies
2. Create necessary directories before running processes that write logs
3. Use conditional artifact uploads to prevent failures on missing files
4. Validate YAML syntax before committing workflow changes

## AI Model Compatibility

### Model Selection
- GitHub Copilot automatically selects appropriate models based on your plan
- Do not hardcode specific model names in configurations
- Standard GitHub Copilot access is sufficient for all repository tasks

### Error Handling
If you encounter "HTTP error 400: no endpoints available for this model":
1. This indicates the requested AI model is not available in your GitHub plan
2. The error is plan-related, not a code issue in this repository
3. See [GITHUB_COPILOT_MODEL_ERROR.md](../GITHUB_COPILOT_MODEL_ERROR.md) for detailed troubleshooting
4. Standard features work with all GitHub Copilot plans (Individual, Business, Enterprise)

### Best Practices
- Use default model selection (don't specify models explicitly)
- Implement fallback logic for AI API calls
- Test features with standard GitHub access
- Document any premium model requirements clearly

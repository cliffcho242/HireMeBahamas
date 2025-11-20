# GitHub Copilot Workspace Information

## About Copilot Workspace Runtime Logs

When using GitHub Copilot Workspace to work on this repository, you may see warnings about missing artifact files:

```
Warning: No files were found with the provided path: /home/runner/work/_temp/runtime-logs/blocked.jsonl
/home/runner/work/_temp/runtime-logs/blocked.md. No artifacts will be uploaded.
```

### What This Means

- **This is expected behavior** and does not indicate a problem with your repository
- These files are part of Copilot Workspace's firewall monitoring system
- The files (`blocked.jsonl` and `blocked.md`) track network requests that were blocked during the session
- They are created in the GitHub Actions runner's temporary directory, not in your repository

### Why The Warning Appears

The warning appears when:
1. Copilot Workspace's dynamic workflow tries to upload runtime logs as artifacts
2. The files don't exist yet (because no network requests were blocked)
3. The artifact upload action issues a warning but continues normally

### Impact

- **No impact on your application** - this is purely informational
- **No impact on CI/CD** - this warning doesn't affect your repository's workflows  
- **No action required** - the warning is harmless and can be ignored

### Firewall Monitoring

Copilot Workspace uses eBPF-based firewall monitoring to:
- Track network access during command execution
- Log blocked connection attempts
- Help diagnose connectivity issues
- Provide security insights

When network requests are blocked, the `blocked.jsonl` and `blocked.md` files will contain information about:
- Which domains were blocked
- Which commands triggered the blocks
- Whether blocks were DNS-based or connection-based

### Repository CI/CD

For actual CI/CD workflows specific to this repository, see:
- `.github/workflows/ci.yml` - Main CI pipeline
- `.github/workflows/` - Other workflow configurations

These repository workflows are independent of Copilot Workspace's internal monitoring and logging.

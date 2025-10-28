# PowerShell Execution Policy Configuration Fix
# This script ensures proper execution policy without conflicts

Write-Host "PowerShell Configuration Fix" -ForegroundColor Cyan

# Check current execution policy
$currentPolicy = Get-ExecutionPolicy
Write-Host "Current Execution Policy: $currentPolicy" -ForegroundColor Yellow

# If policy is too restrictive, try to set it appropriately
if ($currentPolicy -eq "Restricted" -or $currentPolicy -eq "AllSigned") {
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "Execution policy set to RemoteSigned for CurrentUser" -ForegroundColor Green
    }
    catch {
        Write-Host "Could not change execution policy. Running with current policy." -ForegroundColor Yellow
    }
}

Write-Host "PowerShell configuration is ready!" -ForegroundColor Green
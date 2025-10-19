# PowerShell Diagnostic Script
# Run this to verify PowerShell functionality

Write-Host "PowerShell Diagnostic Test" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

# Check PowerShell version
Write-Host "PowerShell Version:" $PSVersionTable.PSVersion

# Check execution policy
Write-Host "Execution Policy:" (Get-ExecutionPolicy)

# Test basic functionality
Write-Host "Basic test passed!" -ForegroundColor Green

# Test module loading
try {
    Import-Module Microsoft.PowerShell.Management -ErrorAction Stop
    Write-Host "Module loading test passed!" -ForegroundColor Green
} catch {
    Write-Host "Module loading test failed:" $_.Exception.Message -ForegroundColor Red
}

Write-Host "Diagnostic complete!" -ForegroundColor Green